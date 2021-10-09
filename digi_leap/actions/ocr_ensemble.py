"""Find "best" labels from ensembles of OCR results of each label."""

import json
import os
import re
from argparse import Namespace
from collections import defaultdict
from multiprocessing import Pool
from pathlib import Path

import pandas as pd
import tqdm
from PIL import Image, ImageDraw

from digi_leap.pylib import (
    font,
    ocr_results as results,
    ocr_rows as rows,
    util,
)


def build_all_ensembles(args: Namespace) -> None:
    """Group OCR output paths by label."""
    create_dirs(args.ensemble_images, args.ensemble_text)

    paths = group_files(args.ocr_dir)
    paths = filter_files(paths, args.limit, args.label_filter)

    all_records = process_batches(
        paths,
        args.batch_size,
        args.cpus,
        args.prepared_dir,
        args.ensemble_text,
        args.ensemble_images,
        args.line_space,
    )

    if args.winners_jsonl:
        with open(args.winners_jsonl, "w") as jsonl_file:
            for record in all_records:
                jsonl_file.write(json.dumps(record) + "\n")


def filter_files(paths, limit, label_filter) -> list[tuple[str, list[Path]]]:
    """Filter files for debugging specific labels."""
    if label_filter:
        paths = [(k, v) for k, v in paths if re.search(label_filter, k)]
    paths = paths[:limit] if limit else paths
    return paths


def create_dirs(ensemble_image_dir, ensemble_text_dir):
    """Create output directories."""
    if ensemble_image_dir:
        os.makedirs(ensemble_image_dir, exist_ok=True)
    if ensemble_text_dir:
        os.makedirs(ensemble_text_dir, exist_ok=True)


def process_batches(
    paths,
    batch_size,
    cpus,
    prepared_label_dir,
    ensemble_text_dir,
    ensemble_image_dir,
    line_space,
):
    """Process batches of label ensembles."""
    all_records = []

    batches = [paths[i : i + batch_size] for i in range(0, len(paths), batch_size)]
    with Pool(processes=cpus) as pool, tqdm.tqdm(total=len(batches)) as bar:
        all_results = [
            pool.apply_async(
                ensemble_batch,
                args=(
                    b,
                    prepared_label_dir,
                    ensemble_text_dir,
                    ensemble_image_dir,
                    line_space,
                ),
                callback=lambda _: bar.update(),
            )
            for b in batches
        ]

        for results_list in [r.get() for r in all_results]:
            all_records += results_list

    return all_records


def ensemble_batch(
    batch, prepared_label_dir, ensemble_text_dir, ensemble_image_dir, line_space
):
    """Find the "best" label on a batch of OCR results."""
    all_records = []
    for path_tuple in batch:
        records = build_ensemble(
            path_tuple,
            prepared_label_dir,
            ensemble_text_dir,
            ensemble_image_dir,
            line_space,
        )
        all_records += records
    return all_records


def build_ensemble(
    path_tuple,
    prepared_label_dir,
    ensemble_text_dir,
    ensemble_image_dir,
    line_space,
):
    """Build the "best" label output given the ensemble of OCR results."""
    stem, paths = path_tuple
    paths = [Path(p) for p in paths]

    df = get_boxes(paths)
    if df.shape[0] == 0:
        return []

    df = results.merge_bounding_boxes(df)
    df = rows.find_rows_of_text(df)
    df["stem"] = stem

    if ensemble_text_dir:
        build_ensemble_text(stem, df, ensemble_text_dir)

    if ensemble_image_dir:
        build_ensemble_images(
            stem, df, prepared_label_dir, ensemble_image_dir, line_space
        )

    records = df.loc[:, ["text", "method", "winners", "score", "stem"]].to_dict(
        "records"
    )
    return records


def build_ensemble_text(stem, df, ensemble_text_dir):
    """Build the "best" text output given the ensemble of OCR results."""
    lines = [" ".join(b.text) + "\n" for _, b in df.groupby("row")]
    path = Path(ensemble_text_dir) / f"{stem}.txt"
    with open(path, "w") as out_file:
        out_file.writelines(lines)


def build_ensemble_images(stem, df, prepared_label_dir, ensemble_image_dir, line_space):
    """Build the "best" image output given the ensemble of OCR results."""
    label = Image.open(Path(prepared_label_dir) / f"{stem}.jpg").convert("RGB")
    width, height = label.size
    recon = Image.new("RGB", label.size, color="white")

    row_df = results.merge_rows_of_text(df)
    row_df["font_size"] = font.BASE_FONT_SIZE
    row_df["height"] = row_df["bottom"] - row_df["top"]

    draw_recon = ImageDraw.Draw(recon)

    for idx, row in row_df.iterrows():
        for font_size in range(row.font_size, 16, -1):
            text_left, text_top, text_right, text_bottom = draw_recon.textbbox(
                (row.left, row.top), row.text, font=font.FONTS[font_size], anchor="lt"
            )
            if row.right >= text_right and row.bottom >= text_bottom:
                row_df.at[idx, "font_size"] = font_size
                row_df.at[idx, "height"] = text_bottom - text_top
                break

    row_df.iloc[1:-1, 5] = row_df.iloc[1:-1, 5].min()
    row_df.iloc[1:-1, 6] = row_df.iloc[1:-1, 6].min()

    row_top = line_space
    for _, row in row_df.iterrows():
        draw_recon.text(
            (row.left, row_top),
            row.text,
            font=font.FONTS[int(row.font_size)],
            fill="black",
            anchor="lt",
        )
        row_top += row.height + line_space

    if width > height:
        recon = recon.crop((0, 0, recon.width, row_top))
        image = Image.new("RGB", (width, height + row_top))
        image.paste(label, (0, 0))
        image.paste(recon, (0, height))
    else:
        image = Image.new("RGB", (2 * width, height))
        image.paste(label, (0, 0))
        image.paste(recon, (width, 0))

    path = Path(ensemble_image_dir) / f"{stem}.jpg"
    image.save(path)


def get_boxes(paths):
    """Get all the bounding boxes from the ensemble."""
    boxes = []
    for path in paths:
        df = results.get_results_df(path)
        df.text = df.text.astype(str)
        boxes.append(df)
    return pd.concat(boxes)


def group_files(
    ocr_dirs: list[Path], glob: str = "*.csv"
) -> list[tuple[str, list[Path]]]:
    """Find files that represent then same label and group them."""
    path_dict = defaultdict(list)

    dirs = []
    for ocr_dir in util.as_list(ocr_dirs):
        path = Path(ocr_dir)
        root = Path(path.root) if path.root else Path(".")
        pattern = ocr_dir[len(path.root) :]
        dirs.extend([p for p in root.glob(pattern)])

    for ocr_dir in dirs:
        paths = ocr_dir.glob(glob)
        for path in paths:
            label = path.stem
            path_dict[label].append(str(path))
    path_tuples = [(k, v) for k, v in path_dict.items()]
    path_tuples = sorted(path_tuples, key=lambda p: p[0])
    return path_tuples

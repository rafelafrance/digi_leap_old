#!/usr/bin/env python3
import io
import json
import os
import tempfile
import warnings
from pathlib import Path
from subprocess import check_call
from typing import Optional

from fastapi import Depends
from fastapi import FastAPI
from fastapi import File
from fastapi import HTTPException
from fastapi import UploadFile
from PIL import Image
from pydantic import BaseModel

from digi_leap.pylib import consts


app = FastAPI()

IMAGE_SIZE = 640

KEYS = consts.DATA_DIR / "secrets" / "api_keys.json"

with open(KEYS) as key_file:
    KEY = json.load(key_file)
KEY = KEY["key"]


class FindLabels(BaseModel):
    magic_word: str  # TODO: Use passwords or OAuth2?
    conf: Optional[float] = None


@app.post("/find-labels")
async def find_labels(
    params: FindLabels = Depends(),
    files: list[UploadFile] = File(...),
):
    print(params)
    auth(params.magic_word)

    results = {}
    scales = {}

    with tempfile.TemporaryDirectory(prefix="yolo_") as yolo_dir:
        in_dir, out_dir = await create_dirs(yolo_dir)

        for file_ in files:
            contents = await file_.read()
            stem = Path(file_.filename).stem
            scales[stem] = await save_image(contents, file_, in_dir)

        await run_yolo(in_dir, out_dir, params.conf)

        label_dir = out_dir / "exp" / "labels"
        for path in label_dir.glob("*.txt"):
            await get_all_bboxes(path, results, scales)

    return json.dumps(results)


def auth(magic_word):
    if magic_word != KEY:
        raise HTTPException(status_code=401, detail="There is no magic in that word")


async def create_dirs(yolo_dir):
    temp_dir = Path(yolo_dir)
    in_dir = temp_dir / "images"
    out_dir = temp_dir / "results"
    os.mkdir(in_dir)
    os.mkdir(out_dir)
    return in_dir, out_dir


async def save_image(contents, file, in_dir):
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning)  # No EXIF warnings
        image = Image.open(io.BytesIO(contents)).convert("RGB")
    scale_x, scale_y = image.size
    image = image.resize((IMAGE_SIZE, IMAGE_SIZE))
    image_path = in_dir / file.filename
    image.save(image_path)
    return scale_x, scale_y


async def run_yolo(in_dir, out_dir, conf):
    cmd = [
        "python3",
        "yolov7/detect.py",
        "--weights=data/models/yolov7.pt",
        "--nosave",
        "--save-txt",
        "--save-conf",
        "--exist-ok",
        "--no-trace",
        f"--conf-thres={conf}",
        f"--source={in_dir}",
        f"--project={out_dir}",
    ]
    cmd = " ".join(cmd)
    check_call(cmd, shell=True)


async def get_all_bboxes(path, results, scales):
    stem = path.stem
    scale_x, scale_y = scales[stem]
    results[stem] = []
    with open(path) as txt_file:
        for line in txt_file.readlines():
            bbox = get_bbox(line, scale_x, scale_y)
            results[stem].append(bbox)


def get_bbox(line, scale_x, scale_y):
    row = line.split()
    cls = row[0]
    left, top, wide, high, conf = (float(v) for v in row[1:])
    bbox = {
        "class": consts.CLASS2NAME[int(cls)],
        "left": int(left * scale_x),
        "top": int(top * scale_y),
        "right": int((left + wide) * scale_x),
        "bottom": int((top + high) * scale_y),
        "conf": float(conf),
    }
    return bbox

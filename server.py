#!/usr/bin/env python3
import json
import tempfile
from pathlib import Path

from fastapi import FastAPI
from fastapi import File
from fastapi import Form
from fastapi import UploadFile

from digi_leap.pylib.ocr.ensemble import Ensemble
from digi_leap.pylib.server import common
from digi_leap.pylib.server import label_finder as finder

app = FastAPI()


@app.post("/find-labels")
async def find_labels(
    magic: str = Form(),
    conf: float = Form(0.1),
    files: list[UploadFile] = File(),
):
    common.auth(magic)

    results = {}
    scales = {}

    with tempfile.TemporaryDirectory(prefix="yolo_") as yolo_dir:
        in_dir, out_dir = await finder.create_dirs(yolo_dir)

        for file_ in files:
            stem = Path(file_.filename).stem
            contents = await file_.read()
            scales[stem] = await finder.save_image(contents, file_, in_dir)

        await finder.run_yolo(in_dir, out_dir, conf)

        label_dir = out_dir / "exp" / "labels"
        for path in label_dir.glob("*.txt"):
            await finder.get_all_bboxes(path, results, scales)

    return json.dumps(results)


@app.post("/ocr-labels")
async def ocr_labels(magic: str = Form(), files: list[UploadFile] = File(...)):
    common.auth(magic)

    results = {}
    ensemble = Ensemble(
        none_easyocr=True,
        none_tesseract=True,
        deskew_easyocr=True,
        deskew_tesseract=True,
        binarize_tesseract=True,
        denoise_tesseract=True,
        pre_process=True,
        post_process=True,
    )
    for file_ in files:
        stem = Path(file_.filename).stem
        contents = await file_.read()
        image = await common.get_image(contents)
        text = await ensemble.run(image)
        results[stem] = text

    return json.dumps(results)

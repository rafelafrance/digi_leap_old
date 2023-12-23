#!/usr/bin/env python3
import json
import tempfile
from datetime import datetime
from hashlib import blake2b
from pathlib import Path

import uvicorn
from fastapi import File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from digi_leap.pylib import common
from digi_leap.pylib import label_finder as finder
from old.db import db  # TODO Convert to static/cache.json
from old.ocr.ensemble import Ensemble

app = common.setup()
app.mount("/static", StaticFiles(directory="static"), name="static")

TEMPLATES = Jinja2Templates(directory="static")

CACHE = Path("data") / "cache.sqlite"


class Label(BaseModel):
    left: int = 0
    top: int = 0
    right: int = 0
    bottom: int = 0
    conf: float = 1.0
    type: str = ""
    text: str = ""


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return TEMPLATES.TemplateResponse("client.html", {"request": request})


@app.get("/client-instructions", response_class=HTMLResponse)
async def instructions(request: Request):
    return TEMPLATES.TemplateResponse("client-instructions.html", {"request": request})


@app.post("/find-labels")
async def find_labels(
    sheet: UploadFile = File(),
    conf: float = Form(0.1),
):
    results = []

    with tempfile.TemporaryDirectory(prefix="yolo_") as yolo_dir:
        in_dir, out_dir = await finder.create_dirs(yolo_dir)

        contents = await sheet.read()
        scale = await finder.save_image(contents, sheet, in_dir)

        hasher = blake2b()
        hasher.update(contents)
        hash_ = hasher.hexdigest()

        with db.connect(CACHE) as cxn:
            cache = db.canned_select(cxn, "cache", path=sheet.filename, hash=hash_)

        if cache and cache[0]["labels"]:
            data = json.loads(cache[0]["labels"])
            conf = data["conf"]
            results = data["results"]
        else:
            await finder.run_yolo(in_dir, out_dir, conf)

            label_dir = out_dir / "exp" / "labels"
            for path in label_dir.glob("*.txt"):
                results += await finder.get_all_bboxes(path, scale)

    output = json.dumps(
        {
            "post": "/find-labels",
            "date": datetime.now().isoformat(sep=" ", timespec="seconds"),
            "sheet": sheet.filename,
            "conf": conf,
            "results": results,
        }
    )

    if not cache:
        with db.connect(CACHE) as cxn:
            batch = [
                {
                    "hash": hash_,
                    "path": sheet.filename,
                    "labels": output,
                    "ocr": "",
                }
            ]
            db.canned_insert(cxn, "cache", batch)

    return output


@app.post("/ocr-labels")
async def ocr_labels(
    labels: str = Form(""),
    extract: str = Form("typewritten"),
    sheet: UploadFile = File(),
):
    label_list = json.loads(labels) if labels else []

    results = []

    ocr_options = {
        "none_easyocr": True,
        "none_tesseract": True,
        "deskew_easyocr": True,
        "deskew_tesseract": True,
        "binarize_easyocr": False,
        "binarize_tesseract": True,
        "denoise_easyocr": False,
        "denoise_tesseract": True,
        "pre_process": True,
        "post_process": True,
    }

    ensemble = Ensemble(**ocr_options)

    image = await sheet.read()

    hasher = blake2b()
    hasher.update(image)
    hash_ = hasher.hexdigest()

    image = await common.get_image(image)

    with db.connect(CACHE) as cxn:
        cache = db.canned_select(cxn, "cache", path=sheet.filename, hash=hash_)

    if cache and cache[0]["ocr"]:
        data = json.loads(cache[0]["ocr"])
        extract = data["extract"]
        labels = data["labels"]
        results = data["results"]
    else:
        if not label_list:
            text = await ensemble.run(image)
            results.append(
                {
                    "type": "unknown",
                    "left": 0,
                    "top": 0,
                    "right": image.size[0] - 1,
                    "bottom": image.size[1] - 1,
                    "conf": 1.0,
                    "text": text,
                }
            )

        else:
            for lb in label_list:
                label = image.crop((lb["left"], lb["top"], lb["right"], lb["bottom"]))
                if extract == "all" or lb["type"].lower() == extract.lower():
                    text = await ensemble.run(label)
                else:
                    text = ""
                results.append(
                    {
                        "type": lb["type"],
                        "left": lb["left"],
                        "top": lb["top"],
                        "right": lb["right"],
                        "bottom": lb["bottom"],
                        "conf": lb["conf"],
                        "text": text,
                    }
                )

    output = json.dumps(
        {
            "post": "/ocr-labels",
            "date": datetime.now().isoformat(sep=" ", timespec="seconds"),
            "labels": labels,
            "extract": extract,
            "sheet": sheet.filename,
            "ocr_options": ocr_options,
            "results": results,
        }
    )

    if not cache:
        pass

    elif not cache[0]["ocr"]:
        with db.connect(CACHE) as cxn:
            sql = """update cache set ocr = :ocr where hash = :hash and path = :path"""
            db.update(cxn, sql, ocr=output, hash=hash_, path=sheet.filename)

    return output


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

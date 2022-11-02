#!/usr/bin/env python3
import json
import tempfile

from fastapi import Depends
from fastapi import File
from fastapi import Form
from fastapi import Request
from fastapi import UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from digi_leap.pylib.ocr.ensemble import Ensemble
from digi_leap.pylib.server import common
from digi_leap.pylib.server import label_finder as finder


app = common.setup()
app.mount("/static", StaticFiles(directory="static"), name="static")

TEMPLATES = Jinja2Templates(directory="static")


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


@app.post("/find-labels")
async def find_labels(
    _: str = Depends(common.auth),
    sheet: UploadFile = File(),
    conf: float = Form(0.1),
):
    results = []

    with tempfile.TemporaryDirectory(prefix="yolo_") as yolo_dir:
        in_dir, out_dir = await finder.create_dirs(yolo_dir)

        contents = await sheet.read()
        scale = await finder.save_image(contents, sheet, in_dir)

        await finder.run_yolo(in_dir, out_dir, conf)

        label_dir = out_dir / "exp" / "labels"
        for path in label_dir.glob("*.txt"):
            results += await finder.get_all_bboxes(path, scale)

    return json.dumps(results)


@app.post("/ocr-labels")
async def ocr_labels(
    _: str = Depends(common.auth),
    labels: str = Form(""),
    sheet: UploadFile = File(),
):
    labels = json.loads(labels) if labels else None

    results = []

    ensemble = Ensemble(
        none_easyocr=True,
        none_tesseract=True,
        deskew_easyocr=True,
        deskew_tesseract=True,
        binarize_easyocr=False,
        binarize_tesseract=True,
        denoise_easyocr=False,
        denoise_tesseract=True,
        pre_process=True,
        post_process=True,
    )

    contents = await sheet.read()
    image = await common.get_image(contents)

    if labels is None:
        text = await ensemble.run(sheet)
        results.append(
            {
                "type": "unknown",
                "left": 0,
                "top": 0,
                "right": image.size[0] - 1,
                "bottom": image.size[1] - 1,
                "text": text,
            }
        )

    else:
        for lb in labels:
            label = image.crop((lb["left"], lb["top"], lb["right"], lb["bottom"]))
            if lb["type"].lower() == "typewritten":
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
                    "text": text,
                }
            )

    return json.dumps(results)

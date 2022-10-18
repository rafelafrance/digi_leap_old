#!/usr/bin/env python3
import io
import os
import tempfile
import warnings
from pathlib import Path
from subprocess import check_call

from fastapi import FastAPI
from fastapi import File
from fastapi import UploadFile
from PIL import Image

# from pydantic import BaseModel

app = FastAPI()

IMAGE_SIZE = 640


@app.post("/find-labels")
async def find_labels(file: UploadFile = File(...)):
    contents = await file.read()

    with tempfile.TemporaryDirectory(prefix="yolo_") as yolo_dir:
        temp_dir = Path(yolo_dir)
        in_dir = temp_dir / "images"
        out_dir = temp_dir / "results"
        os.mkdir(in_dir)
        os.mkdir(out_dir)

        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=UserWarning)  # No EXIF warnings
            image = Image.open(io.BytesIO(contents)).convert("RGB")

        size = image.size
        image = image.resize((IMAGE_SIZE, IMAGE_SIZE))

        image_path = in_dir / file.filename
        image.save(image_path)

        cmd = [
            "python3 yolov7/detect.py",
            "--weights data/models/yolov7.pt",
            "--nosave",
            "--save-txt",
            "--save-conf",
            "--exist-ok",
            "--conf-thres 0.1",
            "--no-trace",
            f"--source {in_dir}",
            f"--project {out_dir}",
        ]
        cmd = " ".join(cmd)
        check_call(cmd, shell=True)

        label_dir = out_dir / "exp" / "labels"
        for path in label_dir.glob("*.txt"):
            with open(path) as txt_file:
                print(txt_file.read())

    return {"file_name": file.filename, "size": size}


# python yolov7/detect.py --weights data/models/yolov7.pt --source inference_other/
#   --save-txt --save-conf --project runs/inference-640/yolov7_e100/ --exist-ok
#   --nosave --name other_2022-10-04 --conf-thres 0.1 --no-trace

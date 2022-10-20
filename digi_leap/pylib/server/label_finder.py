import os
from pathlib import Path
from subprocess import check_call
from subprocess import DEVNULL

from . import common
from ...pylib import consts

YOLO_SIZE = 640


async def create_dirs(yolo_dir):
    temp_dir = Path(yolo_dir)
    in_dir = temp_dir / "images"
    out_dir = temp_dir / "results"
    os.mkdir(in_dir)
    os.mkdir(out_dir)
    return in_dir, out_dir


async def save_image(contents, file, image_dir):
    image = await common.get_image(contents)
    scale_x, scale_y = image.size
    image = image.resize((YOLO_SIZE, YOLO_SIZE))
    image_path = image_dir / file.filename
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
    check_call(cmd, shell=True, stdout=DEVNULL, stderr=DEVNULL)


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

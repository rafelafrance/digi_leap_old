import io
import json
import warnings

from fastapi import HTTPException
from PIL import Image

from .. import consts


KEYS = consts.DATA_DIR / "secrets" / "api_keys.json"
with open(KEYS) as key_file:
    KEY = json.load(key_file)
KEY = KEY["key"]


def auth(magic):
    if magic != KEY:
        raise HTTPException(status_code=401, detail="There is no magic in that word")


async def get_image(contents):
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning)  # No EXIF warnings
        image = Image.open(io.BytesIO(contents)).convert("RGB")
    return image

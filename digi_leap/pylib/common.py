import io
import json
import secrets
import warnings
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from PIL import Image


def api_key():
    keys = Path("server") / "data" / "secrets" / "api_keys.json"
    with open(keys) as key_file:
        key = json.load(key_file)
    return key["key"]


KEY = api_key().encode()

security = HTTPBasic()


def setup():
    with open("./digi_leap/pylib/server/description.md") as in_file:
        description = in_file.read()

    return FastAPI(
        title="Digi-Leap",
        description=description,
        url="http://localhost:8000",  # TODO??
        version="0.1.0",
        contact={},
        license_info={
            "name": "MIT License",
            # TODO: Tag a release and use its URL
            "url": "https://github.com/rafelafrance/digi_leap/blob/main/LICENSE",
        },
    )


def auth(credentials: HTTPBasicCredentials = Depends(security)):
    curr_password = credentials.password.encode("utf8")
    correct_password = secrets.compare_digest(curr_password, KEY)
    if not correct_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


async def get_image(contents):
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning)  # No EXIF warnings
        return Image.open(io.BytesIO(contents)).convert("RGB")

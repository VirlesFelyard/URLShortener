from datetime import time
from typing import Annotated

from pydantic import BaseModel, Field, HttpUrl


class RegisterReq(BaseModel):
    name: str
    email: str
    password: str


class LoginReq(BaseModel):
    email: str
    password: str


class UrlAddReq(BaseModel):
    original_url: HttpUrl
    short_code: Annotated[
        str, Field(min_length=3, max_length=16, pattern=r"^[a-zA-Z0-9_-]+$")
    ]
    password: str | None = None
    valid_from: time | None = None
    valid_until: time | None = None
    allow_proxy: bool = True

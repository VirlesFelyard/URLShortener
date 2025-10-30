from datetime import datetime, time
from typing import Annotated, Optional

from pydantic import BaseModel, EmailStr, Field, HttpUrl


class RegisterReq(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginReq(BaseModel):
    email: EmailStr
    password: str


class UrlAddReq(BaseModel):
    original_url: HttpUrl
    short_code: Annotated[
        str, Field(min_length=3, max_length=16, pattern=r"^[a-zA-Z0-9_-]+$")
    ]
    password: Optional[str] = None
    valid_from: Optional[time] = None
    valid_until: Optional[time] = None
    expires_at: Optional[datetime] = None
    allow_proxy: bool = True


class UrlUpdateReq(BaseModel):
    original_url: Optional[HttpUrl] = None
    short_code: Optional[
        Annotated[str, Field(min_length=3, max_length=16, pattern=r"^[a-zA-Z0-9_-]+$")]
    ] = None

    password: Optional[str] = None
    valid_from: Optional[time] = None
    valid_until: Optional[time] = None
    expires_at: Optional[datetime] = None
    allow_proxy: Optional[bool] = None

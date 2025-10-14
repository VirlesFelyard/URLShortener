from datetime import datetime, time
from ipaddress import ip_address

from fastapi import FastAPI, Header, HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl, constr

from database.api_keys import akey_validate, regenerate_api_key
from database.base import db_close, db_connect, db_get
from database.ips import ip_add, ip_fetchrow
from database.tables import init_tables
from database.urls import url_add
from database.users import user_add, user_login


security: HTTPBearer = HTTPBearer()
app: FastAPI = FastAPI()

async def get_user_id_from_api_key(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> int:
    token = credentials.credentials
    status, msg = await akey_validate(token)
    if not status or msg is None:
        raise HTTPException(status_code=401, detail="Invalid or expired api-key")
    return msg

class RegisterReq(BaseModel):
    name: str
    email: str
    password: str


class LoginReq(BaseModel):
    email: str
    password: str


class UrlAddReq(BaseModel):
    original_url: HttpUrl
    short_code: constr(max_length=16)
    password: str | None = None
    valid_from: time | None = None
    valid_until: time | None = None
    allow_proxy: bool = True


@app.get("/")
async def root():
    return {"message": "Hello there!"}


@app.post("/auth/register")
async def register(data: RegisterReq) -> dict:
    status, msg = await user_add(data.name, data.email, data.password)
    if status != 200:
        raise HTTPException(status_code=status, detail=msg)
    return {"message": msg}


@app.post("/auth/login")
async def login(data: LoginReq) -> dict:
    status, msg = await user_login(data.email, data.password)
    if status != 200:
        raise HTTPException(status_code=status, detail=msg)
    return {"message": "user logged in successfully!"}

@app.post("/auth/akey-generate")
async def akey_generate(data: LoginReq) -> dict:
    status, msg = await user_login(data.email, data.password)
    if status != 200:
        raise HTTPException(status_code=status, detail=msg)
    api_key: str = await regenerate_api_key(msg)
    return {"message": "Your new API-key: " + api_key}

@app.post("/url/add")
async def add(
    data: UrlAddReq,
    user_id: int = Depends(get_user_id_from_api_key),
) -> dict:
    status, msg = await url_add(
        user_id=user_id,
        original_url=str(data.original_url),
        short_code=data.short_code,
        password=data.password,
        valid_from=data.valid_from,
        valid_until=data.valid_until,
        allow_proxy=data.allow_proxy,
    )
    if status != 201:
        raise HTTPException(status_code=status, detail=msg)
    return {"message": msg}


@app.get("/{short_code}")
async def redirect_by_code(short_code: str, request: Request):
    try:
        ip = ip_address(request.client.host)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid IP address")

    if ip.is_loopback:
        ip_info = None
    else:
        await ip_add(ip)
        ip_info = await ip_fetchrow(ip, "is_proxy")

    pool = await db_get()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT original_url, expires_at, valid_from, valid_until, allow_proxy
            FROM urls
            WHERE short_code = $1
        """,
            short_code,
        )

        if not row:
            raise HTTPException(status_code=404, detail="Short code not found")
        if ip_info and ip_info.get("is_proxy") and not row["allow_proxy"]:
            raise HTTPException(status_code=403, detail="Access denied: proxy detected")

        now = datetime.utcnow()
        now_time = now.time()

        if row["expires_at"] < now:
            raise HTTPException(status_code=410, detail="Link expired")

        if row["valid_from"] and now_time < row["valid_from"]:
            raise HTTPException(status_code=403, detail="Access not yet allowed")

        if row["valid_until"] and now_time > row["valid_until"]:
            raise HTTPException(status_code=403, detail="Access time window closed")

        return RedirectResponse(url=row["original_url"])


@app.on_event("startup")
async def startup() -> None:
    await db_connect()
    await init_tables()


@app.on_event("shutdown")
async def shutdown() -> None:
    await db_close()

from datetime import datetime
from ipaddress import ip_address

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse

from config import get_hash, verify_hash
from database.ips import ip_add, ip_fetchrow
from database.urls import url_add, url_fetchrow
from dto.schemas import UrlAddReq
from utils.security import authorize_user

router: APIRouter = APIRouter()


@router.post("/api/url/add")
async def add(data: UrlAddReq, user_id: int = Depends(authorize_user)):
    status, msg = await url_add(
        user_id=user_id,
        original_url=str(data.original_url),
        short_code=data.short_code,
        password=get_hash(data.password) if data.password is not None else None,
        valid_from=data.valid_from,
        valid_until=data.valid_until,
        allow_proxy=data.allow_proxy,
    )
    if status != 201:
        raise HTTPException(status_code=status, detail=msg)
    return {"message": msg}


@router.get("/{short_code}")
async def redirect(short_code: str, request: Request, password: str | None = None):
    if not request.client or not request.client.host:
        raise HTTPException(status_code=400, detail="Missing client IP")

    try:
        ip = ip_address(request.client.host)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid IP address")

    if ip.is_loopback:
        ip_info = None
    else:
        await ip_add(ip)
        ip_info = await ip_fetchrow(ip, "is_proxy")

    r = await url_fetchrow(
        short_code,
        "original_url",
        "valid_from",
        "valid_until",
        "password",
        "expires_at",
        "allow_proxy",
    )

    if not r:
        raise HTTPException(status_code=404, detail="Short code not found")
    if ip_info and ip_info.get("is_proxy") and not r["allow_proxy"]:
        raise HTTPException(status_code=403, detail="Access denied: proxy detected")

    now = datetime.utcnow()
    now_time = now.time()

    if r["password"]:
        if not password:
            raise HTTPException(status_code=401, detail="Password required")
        if not verify_hash(password, r["password"]):
            raise HTTPException(status_code=401, detail="Invalid password")

    if r["expires_at"] < now:
        raise HTTPException(status_code=410, detail="Link expired")

    if r["valid_from"] and now_time < r["valid_from"]:
        raise HTTPException(status_code=403, detail="Access not yet allowed")

    if r["valid_until"] and now_time > r["valid_until"]:
        raise HTTPException(status_code=403, detail="Access time window closed")

    return RedirectResponse(url=r["original_url"])

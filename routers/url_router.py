from ipaddress import ip_address

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse

from dto.schemas import UrlAddReq
from services import url_service
from utils.exceptions import ServiceError
from utils.security import authorize_user

router = APIRouter()


@router.post("/api/url/add")
async def add(
    data: UrlAddReq, request: Request, user_id: int = Depends(authorize_user)
):
    url_service = request.app.state.url_service

    try:
        await url_service.create_short_url(
            user_id=user_id,
            original_url=str(data.original_url),
            short_code=data.short_code,
            password=data.password,
            valid_from=data.valid_from,
            valid_until=data.valid_until,
            allow_proxy=data.allow_proxy,
        )
        return {"message": "Short URL created successfully"}
    except ServiceError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.delete("/api/url{short_code}")
async def delete(
    short_code: str, request: Request, user_id: int = Depends(authorize_user)
):
    url_service = request.app.state.url_service
    try:
        await url_service.delete_short_url(user_id, short_code)
        return {"message", "Short URL deleted successfully"}
    except ServiceError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/{short_code}")
async def redirect(short_code: str, request: Request, password: str | None = None):
    url_service = request.app.state.url_service
    ip_service = request.app.state.ip_service

    if not request.client or not request.client.host:
        raise HTTPException(status_code=400, detail="Missing client IP")

    try:
        ip = ip_address(request.client.host)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid IP address")

    is_proxy = None
    if not ip.is_loopback:
        is_proxy = await ip_service.is_proxy(ip)

    try:
        original_url = await url_service.resolve_redirect(
            short_code=short_code,
            password=password,
            is_proxy=is_proxy,
        )
        return RedirectResponse(url=original_url)
    except ServiceError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

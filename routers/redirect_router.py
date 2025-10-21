from ipaddress import ip_address

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse

from utils.exceptions import ServiceError

router: APIRouter = APIRouter()


@router.get("/{short_code}")
async def redirect(short_code: str, request: Request, password: str | None = None):
    redirect_service = request.app.state.redirect_service

    if not request.client or not request.client.host:
        raise HTTPException(status_code=400, detail="Missing client IP")

    try:
        ip = ip_address(request.client.host)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid IP address")

    try:
        original_url = await redirect_service.resolve_redirect(
            short_code=short_code,
            password=password,
            ip_address=ip,
            user_agent=request.headers.get("user-agent"),
        )
        return RedirectResponse(url=original_url)
    except ServiceError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

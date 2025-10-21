from fastapi import APIRouter, Depends, HTTPException, Request

from dto.schemas import UrlAddReq
from utils.exceptions import ServiceError
from utils.security import authorize_user

router: APIRouter = APIRouter()


@router.post("")
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


@router.get("")
async def get_all_urls_by_user(
    request: Request, user_id: int = Depends(authorize_user)
):
    url_service = request.app.state.url_service

    try:
        return await url_service.fetch_user_urls(user_id)
    except ServiceError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.delete("")
async def delete_all_urls_by_user(
    request: Request, user_id: int = Depends(authorize_user)
):
    url_service = request.app.state.url_service
    r: int = await url_service.delete_by_user(user_id)
    return {"message": f"Deleted {r} shortened URLs"}


@router.get("/{short_code}")
async def get_by_shortcode(
    short_code: str, request: Request, user_id: int = Depends(authorize_user)
):
    url_service = request.app.state.url_service
    try:
        return await url_service.fetch_by_shortcode(user_id, short_code)
    except ServiceError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.delete("/{short_code}")
async def delete_by_shortcode(
    short_code: str, request: Request, user_id: int = Depends(authorize_user)
):
    url_service = request.app.state.url_service
    try:
        await url_service.delete_short_url(user_id, short_code)
        return {"message": "Short URL deleted successfully"}
    except ServiceError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from utils.exceptions import ServiceError
from utils.security import authorize_user

router: APIRouter = APIRouter(tags=["Statistics"])


@router.get("/browsers")
async def get_browser_stats_by_shortcode(
    short_code: str,
    request: Request,
    period: Optional[str] = Query(default=None, enum=["day", "week", "month"]),
    user_id: int = Depends(authorize_user),
):
    statistic_service = request.app.state.statistic_service
    try:
        return await statistic_service.get_browsers_stats(user_id, short_code, period)
    except ServiceError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/os")
async def get_OS_stats_by_shortcode(
    short_code: str,
    request: Request,
    period: Optional[str] = Query(default=None, enum=["day", "week", "month"]),
    user_id: int = Depends(authorize_user),
):
    statistic_service = request.app.state.statistic_service
    try:
        return await statistic_service.get_os_stats(user_id, short_code, period)
    except ServiceError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/devices")
async def get_devices_stats_by_shortcode(
    short_code: str,
    request: Request,
    period: Optional[str] = Query(default=None, enum=["day", "week", "month"]),
    user_id: int = Depends(authorize_user),
):
    statistic_service = request.app.state.statistic_service
    try:
        return await statistic_service.get_devices_stats(user_id, short_code, period)
    except ServiceError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/countries")
async def get_countries_stats_by_shortcode(
    short_code: str,
    request: Request,
    period: Optional[str] = Query(default=None, enum=["day", "week", "month"]),
    user_id: int = Depends(authorize_user),
):
    statistic_service = request.app.state.statistic_service
    try:
        return await statistic_service.get_countries_stats(user_id, short_code, period)
    except ServiceError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/guests")
async def get_guests_stats_by_shortcode(
    short_code: str,
    request: Request,
    period: Optional[str] = Query(default=None, enum=["day", "week", "month"]),
    user_id: int = Depends(authorize_user),
):
    statistic_service = request.app.state.statistic_service
    try:
        return await statistic_service.get_guests_stats(user_id, short_code, period)
    except ServiceError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

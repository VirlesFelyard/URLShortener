from typing import Optional

from services.click_service import ClickService
from services.url_service import URLService
from utils.exceptions import ServiceError


class StatisticService:
    def __init__(self, click_service: ClickService, url_service: URLService):
        self.click_service = click_service
        self.url_service = url_service

    async def _resolve_url_id(self, user_id: int, short_code: str) -> int:
        row = await self.url_service.url_repo.fetchrow_by_shortcode(
            short_code, fields=["id", "user_id"]
        )
        if row is None:
            raise ServiceError("Short code not found", status_code=404)
        if row["user_id"] != user_id:
            raise ServiceError(
                "You do not have permission to see the statistics of this URL",
                status_code=403,
            )
        return row["id"]

    async def get_browsers_stats(
        self, user_id: int, short_code: str, period: Optional[str] = None
    ) -> dict:
        url_id = await self._resolve_url_id(user_id, short_code)
        return await self.click_service.get_field_stats(url_id, "browser", period)

    async def get_os_stats(
        self, user_id: int, short_code: str, period: Optional[str] = None
    ) -> dict:
        url_id = await self._resolve_url_id(user_id, short_code)
        return await self.click_service.get_field_stats(url_id, "os", period)

    async def get_devices_stats(
        self, user_id: int, short_code: str, period: Optional[str] = None
    ) -> dict:
        url_id = await self._resolve_url_id(user_id, short_code)
        return await self.click_service.get_field_stats(url_id, "device", period)

    async def get_countries_stats(
        self, user_id: int, short_code: str, period: Optional[str] = None
    ) -> dict:
        url_id = await self._resolve_url_id(user_id, short_code)
        return await self.click_service.get_countries_stats(url_id, period)

    async def get_guests_stats(
        self, user_id: int, short_code: str, period: Optional[str] = None
    ) -> dict:
        url_id = await self._resolve_url_id(user_id, short_code)
        return await self.click_service.get_guests_stats(url_id, period)

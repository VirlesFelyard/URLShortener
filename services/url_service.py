from datetime import time
from typing import Optional

from repositories.url_repository import URLRepository
from utils.exceptions import ServiceError


class URLService:
    def __init__(self, url_repo: URLRepository) -> None:
        self.url_repo: URLRepository = url_repo

    async def delete_short_url(
        self,
        user_id: int,
        short_code: str,
    ) -> None:
        row = await self.url_repo.fetchrow_by_shortcode(short_code, fields=["user_id"])
        if row is None:
            raise ServiceError(message="Short code not found", status_code=404)
        if row["user_id"] != user_id:
            raise ServiceError(
                message="You do not have permission to delete this URL", status_code=403
            )

        await self.url_repo.delete(short_code)

    async def create_short_url(
        self,
        user_id: int,
        original_url: str,
        short_code: str,
        password: Optional[str],
        valid_from: Optional[time],
        valid_until: Optional[time],
        allow_proxy: bool,
    ) -> int:
        if await self.url_repo.shortcode_exists(short_code):
            raise ServiceError(message="Short code already in use", status_code=409)
        if await self.url_repo.exists_by_user_and_url(user_id, original_url):
            raise ServiceError(
                message="URL already added by this user", status_code=409
            )
        if valid_from and valid_until and valid_from >= valid_until:
            raise ServiceError(
                message="valid_from must be earlier than valid_until", status_code=422
            )

        return await self.url_repo.add(
            user_id,
            original_url,
            short_code,
            password,
            valid_from,
            valid_until,
            allow_proxy,
        )

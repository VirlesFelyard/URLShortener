from datetime import datetime, time
from typing import Optional

from config import verify_hash
from repositories.url_repository import URLRepository
from utils.exceptions import ServiceError


class URLService:
    def __init__(self, url_repo: URLRepository) -> None:
        self.url_repo: URLRepository = url_repo

    async def resolve_redirect(
        self,
        short_code: str,
        password: Optional[str],
        is_proxy: Optional[bool],
    ) -> str:
        row = await self.url_repo.fetchrow_by_shortcode(
            short_code,
            fields=[
                "original_url",
                "valid_from",
                "valid_until",
                "password",
                "expires_at",
                "allow_proxy",
            ],
        )

        if not row:
            raise ServiceError("Short code not found", 404)

        if is_proxy and not row["allow_proxy"]:
            raise ServiceError("Access denied: proxy detected", 403)

        now = datetime.utcnow()
        now_time = now.time()
        print("now_time =", now_time)
        print("valid_from =", row["valid_from"])
        print("valid_until =", row["valid_until"])

        if row["password"]:
            if not password:
                raise ServiceError("Password required", 401)
            if not verify_hash(password, row["password"]) is True:
                raise ServiceError("Invalid password", 401)

        if row["expires_at"] < now:
            raise ServiceError("Link expired", 410)

        if row["valid_from"] and now_time < row["valid_from"]:
            raise ServiceError("Access not yet allowed", 403)

        if row["valid_until"] and now_time > row["valid_until"]:
            raise ServiceError("Access time window closed", 403)

        return row["original_url"]

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

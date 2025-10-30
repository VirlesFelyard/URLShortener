from datetime import datetime, time, timedelta, timezone
from typing import Any, Dict, List, Optional

from config import EDITABLE_URL_FIELDS as allowed_keys
from repositories.url_repository import URLRepository
from utils.exceptions import ServiceError


class URLService:
    def __init__(self, url_repo: URLRepository) -> None:
        self.url_repo: URLRepository = url_repo

    async def create_short_url(
        self,
        user_id: int,
        original_url: str,
        short_code: str,
        password: Optional[str],
        valid_from: Optional[time],
        valid_until: Optional[time],
        expires_at: Optional[datetime],
        allow_proxy: bool,
    ) -> int:
        if await self.url_repo.shortcode_exists(short_code):
            raise ServiceError(message="Short code already in use", status_code=409)
        if await self.url_repo.exists_by_user_and_url(user_id, original_url):
            raise ServiceError(
                message="URL already added by this user", status_code=409
            )

        if expires_at:
            now = datetime.utcnow().replace(tzinfo=None)
            if expires_at.tzinfo is not None:
                expires_at = expires_at.replace(tzinfo=None)
            if expires_at < now:
                raise ServiceError(
                    message="Expiration date cannot be in the past", status_code=422
                )
            if expires_at - now > timedelta(days=30):
                raise ServiceError(
                    message="URL lifetime cannot exceed 30 days", status_code=422
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
            expires_at,
            allow_proxy,
        )

    async def update_short_url(
        self,
        user_id: int,
        short_code: str,
        fields: Dict[str, Any],
    ) -> None:
        fields: Dict[str, Any] = {
            key: value for key, value in fields.items() if key in allowed_keys
        }
        row: Optional[dict] = await self.url_repo.fetchrow_by_shortcode(
            short_code, fields=["user_id"]
        )
        if "expires_at" in fields:
            now = datetime.utcnow().replace(tzinfo=None)
            expires_at = fields["expires_at"]
            if expires_at.tzinfo is not None:
                fields["expires_at"] = expires_at.replace(tzinfo=None)
            if expires_at < now:
                raise ServiceError(
                    message="Expiration date cannot be in the past", status_code=422
                )
            if expires_at - now > timedelta(days=30):
                raise ServiceError(
                    message="URL lifetime cannot exceed 30 days", status_code=422
                )
        if row is None:
            raise ServiceError(message="Short code not found", status_code=404)
        if row["user_id"] != user_id:
            raise ServiceError(
                message="You do not have permission to edit this URL", status_code=403
            )
        if fields.get(
            "original_url"
        ) is not None and await self.url_repo.exists_by_user_and_url(
            user_id, str(fields["original_url"])
        ):
            raise ServiceError(message="URL already added by this user")
        if (
            fields.get("short_code") is not None
            and fields["short_code"] != short_code
            and await self.url_repo.shortcode_exists(fields["short_code"])
        ):
            raise ServiceError(message="Short code already in use", status_code=409)
        if (
            "valid_from" in fields
            and "valid_until" in fields
            and fields["valid_from"] >= fields["valid_until"]
        ):
            raise ServiceError("valid_from must be earlier than valid_until", 422)

        await self.url_repo.update_by_shortcode(short_code, fields)

    async def fetch_user_urls(self, user_id: int) -> List[dict]:
        rows: List[dict] = await self.url_repo.fetch_by_user_id(user_id)
        if not rows:
            raise ServiceError(message="User has no shortened URLs", status_code=404)
        return [
            {key: value for key, value in row.items() if key not in ("id", "user_id")}
            for row in rows
        ]

    async def fetch_by_shortcode(self, user_id: int, short_code: str) -> dict:
        row: Optional[dict] = await self.url_repo.fetchrow_by_shortcode(
            short_code,
            fields=[
                "user_id",
                "original_url",
                "password",
                "created_at",
                "expires_at",
                "valid_from",
                "valid_until",
                "allow_proxy",
            ],
        )
        if row is None:
            raise ServiceError(message="Short code not found", status_code=404)
        if row["user_id"] != user_id:
            raise ServiceError(
                message="You do not have permission to see the info about this URL",
                status_code=403,
            )
        return {key: value for key, value in row.items() if key != "user_id"}

    async def delete_short_url(
        self,
        user_id: int,
        short_code: str,
    ) -> None:
        row: Optional[dict] = await self.url_repo.fetchrow_by_shortcode(
            short_code, fields=["user_id"]
        )
        if row is None:
            raise ServiceError(message="Short code not found", status_code=404)
        if row["user_id"] != user_id:
            raise ServiceError(
                message="You do not have permission to delete this URL", status_code=403
            )

        await self.url_repo.delete_by_shortcode(short_code)

    async def delete_by_user(self, user_id: int) -> int:
        return await self.url_repo.delete_by_user_id(user_id)

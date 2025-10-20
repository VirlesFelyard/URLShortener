from datetime import datetime
from ipaddress import IPv4Address, IPv6Address, ip_address
from typing import Optional

from config import verify_hash
from services.click_service import ClickService
from services.ip_service import IpService
from services.url_service import URLService
from utils.exceptions import ServiceError


class RedirectService:
    def __init__(
        self,
        url_service: URLService,
        click_service: ClickService,
        ip_service: IpService,
    ) -> None:
        self.url_service = url_service
        self.click_service = click_service
        self.ip_service = ip_service

    async def resolve_redirect(
        self,
        short_code: str,
        password: Optional[str],
        ip_address: IPv4Address | IPv6Address,
        user_agent: str,
    ) -> str:
        is_proxy = None
        ip_id = None
        if not ip_address.is_loopback:
            is_proxy = await self.ip_service.is_proxy(ip_address)
            ip_id = await self.ip_service.get_ip_id(ip_address)

        row = await self.url_service.url_repo.fetchrow_by_shortcode(
            short_code,
            fields=[
                "id",
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

        if row["password"]:
            if not password:
                raise ServiceError("Password required", 401)
            if not verify_hash(password, row["password"]):
                raise ServiceError("Invalid password", 401)

        if row["expires_at"] < now:
            raise ServiceError("Link expired", 410)

        if row["valid_from"] and now_time < row["valid_from"]:
            raise ServiceError("Access not yet allowed", 403)

        if row["valid_until"] and now_time > row["valid_until"]:
            raise ServiceError("Access time window closed", 403)

        await self.click_service.insert_click(row["id"], user_agent, ip_id)

        return row["original_url"]

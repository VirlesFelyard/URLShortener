from datetime import datetime, timedelta
from typing import Optional

from user_agents import parse

from repositories.click_repository import ClickRepository


class ClickService:
    def __init__(self, click_repo: ClickRepository) -> None:
        self.click_repo = click_repo

    async def insert_click(self, url_id: int, user_agent: str, ip: int) -> None:
        ua = parse(user_agent)

        browser: Optional[str] = ua.browser.family or None
        os: Optional[str] = ua.os.family or None
        device: Optional[str] = None
        if ua.is_mobile:
            device = "phone"
        elif ua.is_tablet:
            device = "tablet"
        elif ua.is_pc:
            device = "computer"
        elif ua.is_bot:
            device = "bot"

        await self.click_repo.add(
            url_id=url_id,
            ip=ip,
            browser=browser,
            os=os,
            device=device,
        )

    def _resolve_since(self, period: Optional[str]) -> Optional[datetime]:
        now = datetime.utcnow()
        if period == "day":
            return now - timedelta(days=1)
        elif period == "week":
            return now - timedelta(days=7)
        elif period == "month":
            return now - timedelta(days=30)
        return None

    async def get_field_stats(
        self,
        url_id: int,
        field: Optional[str],
        period: Optional[str],
    ) -> dict:
        since = self._resolve_since(period)
        rows = await self.click_repo.get_field_stats(url_id, field, since)
        return {
            row[field] or "unknown": {"total": row["total"], "unique": row["unique"]}
            for row in rows
        }

    async def get_countries_stats(self, url_id: int, period: Optional[str]) -> dict:
        since = self._resolve_since(period)
        rows = await self.click_repo.get_countries_stats(url_id, since)
        return {
            row["country"]
            or "unknown": {"total": row["total"], "unique": row["unique"]}
            for row in rows
        }

    async def get_guests_stats(self, url_id: int, period: Optional[str]) -> dict:
        since = self._resolve_since(period)
        row = await self.click_repo.get_guests_stats(url_id, since)
        return dict(row) if row else {}

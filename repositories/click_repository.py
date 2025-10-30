from datetime import datetime
from typing import Optional

from asyncpg import Pool


class ClickRepository:
    def __init__(self, pool: Pool) -> None:
        self.pool = pool

    async def add(
        self,
        url_id: int,
        ip: int,
        browser: Optional[str],
        device: Optional[str],
        os: Optional[str],
    ) -> None:
        async with self.pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO clicks(url_id, ip, browser, device, os) VALUES ($1, $2, $3, $4, $5)",
                url_id,
                ip,
                browser,
                device,
                os,
            )

    async def get_field_stats(
        self, url_id: int, field: Optional[str], since: Optional[datetime]
    ) -> list:
        async with self.pool.acquire() as conn:
            return await conn.fetch(
                f"""
                SELECT {field}, COUNT(*) AS total, COUNT(DISTINCT ip) AS unique
                FROM clicks
                WHERE url_id = $1 AND ($2::timestamp IS NULL OR clicked_at >= $2)
                GROUP BY {field}
                ORDER BY total DESC
                """,
                url_id,
                since,
            )

    async def get_countries_stats(self, url_id: int, since: Optional[datetime]) -> list:
        async with self.pool.acquire() as conn:
            return await conn.fetch(
                """
                SELECT i.country, COUNT(*) AS total, COUNT(DISTINCT c.ip) AS unique
                FROM clicks c
                LEFT JOIN ip_addresses i ON c.ip = i.id
                WHERE c.url_id = $1 AND ($2::timestamp IS NULL OR c.clicked_at >= $2)
                GROUP BY i.country
                ORDER BY total DESC
                """,
                url_id,
                since,
            )

    async def get_guests_stats(
        self, url_id: int, since: Optional[datetime]
    ) -> Optional[dict]:
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(
                """
                SELECT
                    COUNT(*) AS total,
                    COUNT(DISTINCT c.ip) AS unique,
                    COUNT(DISTINCT CASE WHEN i.is_proxy THEN c.ip END) AS proxy
                FROM clicks c
                LEFT JOIN ip_addresses i ON c.ip = i.id
                WHERE c.url_id = $1 AND ($2::timestamp IS NULL OR c.clicked_at >= $2)
                """,
                url_id,
                since,
            )

from typing import List

from asyncpg import Pool, Record


class ClickRepository:
    def __init__(self, pool: Pool) -> None:
        self.pool = pool

    async def add(
        self,
        url_id: int,
        user_agent: str,
        ip: int,
    ) -> None:
        async with self.pool.acquire() as conn:
            return await conn.execute(
                "INSERT INTO clicks(url_id, user_agent, ip) VALUES ($1, $2, $3)",
                url_id,
                user_agent,
                ip,
            )

    async def fetch_clicks_by_url(
        self,
        url_id: int,
    ) -> List[dict]:
        async with self.pool.acquire() as conn:
            row: List[Record] = await conn.fetch(
                "SELECT clicked_at, user_agent, ip FROM clicks WHERE url_id = $1",
                url_id,
            )
            return [dict(r) for r in row]

    async def fetch_clicks_by_ip(
        self,
        ip: int,
    ) -> List[dict]:
        async with self.pool.acquire() as conn:
            row: List[Record] = await conn.fetch(
                "SELECT clicked_at, user_agent, url_id FROM clicks WHERE ip = $1", ip
            )
            return [dict(r) for r in row]

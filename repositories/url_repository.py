from datetime import time
from typing import List, Optional

from asyncpg import Pool, Record


class URLRepository:
    def __init__(self, pool: Pool) -> None:
        self.pool: Pool = pool

    async def shortcode_exists(self, short_code: str) -> bool:
        async with self.pool.acquire() as conn:
            return await conn.fetchval(
                "SELECT EXISTS (SELECT 1 FROM urls WHERE short_code = $1)", short_code
            )

    async def exists_by_user_and_url(self, user_id: int, original_url: str) -> bool:
        async with self.pool.acquire() as conn:
            return await conn.fetchval(
                "SELECT EXISTS (SELECT 1 FROM urls WHERE user_id = $1 AND original_url = $2)",
                user_id,
                original_url,
            )

    async def add(
        self,
        user_id: int,
        original_url: str,
        short_code: str,
        password: Optional[str],
        valid_from: Optional[time],
        valid_until: Optional[time],
        allow_proxy: bool,
    ) -> int:
        async with self.pool.acquire() as conn:
            return await conn.fetchval(
                """
                INSERT INTO urls (
                    user_id, original_url, short_code,
                    password, valid_from, valid_until, allow_proxy
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, $7
                ) RETURNING id
                """,
                user_id,
                original_url,
                short_code,
                password,
                valid_from,
                valid_until,
                allow_proxy,
            )

    async def fetchrow_by_shortcode(
        self, short_code: str, fields: List[str]
    ) -> Optional[dict]:
        if not fields:
            return None
        field_list: str = ", ".join(fields)
        async with self.pool.acquire() as conn:
            row: Record = await conn.fetchrow(
                f"SELECT {field_list} FROM urls WHERE short_code = $1", short_code
            )
            return dict(row) if row else None

    async def fetch_by_user_id(
        self,
        user_id: int,
    ) -> List[dict]:
        async with self.pool.acquire() as conn:
            rows: List[Record] = await conn.fetch(
                "SELECT * FROM urls WHERE user_id = $1", user_id
            )
            return [dict(row) for row in rows]

    async def delete_by_user_id(self, user_id: int) -> int:
        async with self.pool.acquire() as conn:
            r: str = await conn.execute("DELETE FROM urls WHERE user_id = $1", user_id)
            return int(r.split(" ")[1])

    async def delete_by_shortcode(self, short_code: str) -> None:
        async with self.pool.acquire() as conn:
            await conn.execute("DELETE FROM urls WHERE short_code = $1", short_code)

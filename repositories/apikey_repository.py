from typing import Optional

from asyncpg import Pool


class ApiKeyRepository:
    def __init__(self, pool) -> None:
        self.pool: Pool = pool

    async def exists_by_id(self, user_id: int) -> bool:
        async with self.pool.acquire() as conn:
            return await conn.fetchval(
                "SELECT EXISTS (SELECT 1 FROM api_keys WHERE user_id = $1)", user_id
            )

    async def validate(self, hashed_key: str) -> Optional[int]:
        async with self.pool.acquire() as conn:
            return await conn.fetchval(
                "SELECT user_id FROM api_keys WHERE key = $1 AND is_active = TRUE",
                hashed_key,
            )

    async def upsert(self, user_id: int, hashed_key: str) -> None:
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO api_keys (
                    user_id, key
                ) VALUES (
                    $1, $2
                ) ON CONFLICT (user_id)
                DO UPDATE SET
                    key = EXCLUDED.key,
                    created_at = CURRENT_TIMESTAMP,
                    is_active = TRUE
                """,
                user_id,
                hashed_key,
            )

from asyncpg import Pool

from database.base import db_get


async def akey_exists(user_id: int) -> bool:
    pool: Pool = await db_get()
    async with pool.acquire() as conn:
        r = await conn.fetchval("SELECT id FROM api_keys WHERE user_id = $1", user_id)
        return r is not None


async def akey_upsert(user_id: int, hashed_api_key: str) -> None:
    pool: Pool = await db_get()
    async with pool.acquire() as conn:
        await conn.execute(
            """
                INSERT INTO api_keys(
                    user_id, key
                ) VALUES (
                    $1, $2
                ) ON CONFLICT (user_id)
                  DO UPDATE SET
                    key = EXCLUDED.key,
                    created_at = CURRENT_TIMESTAMP,
                    expires_at = CURRENT_TIMESTAMP + INTERVAL '30 days',
                    is_active = TRUE
            """,
            user_id,
            hashed_api_key,
        )


async def akey_delete(user_id: int) -> None:
    pool: Pool = await db_get()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM api_keys WHERE user_id = $1", user_id)

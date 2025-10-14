from typing import Optional, Tuple

from asyncpg import Pool
from config import verify_hash, gen_api_key, get_hash

from database.base import db_get


async def akey_exists(user_id: int) -> bool:
    pool: Pool = await db_get()
    async with pool.acquire() as conn:
        r = await conn.fetchval("SELECT id FROM api_keys WHERE user_id = $1", user_id)
        return r is not None


async def akey_validate(api_key: str) -> Tuple[bool, Optional[int]]:
    pool: Pool = await db_get()
    async with pool.acquire() as conn:
        r = await conn.fetchval(
            "SELECT user_id FROM api_keys WHERE key = $1 AND is_active = TRUE", 
            get_hash(api_key)
        )
        print(r, api_key, get_hash(api_key))
        return r is not None, r


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
                    is_active = TRUE
            """,
            user_id,
            hashed_api_key
        )


async def regenerate_api_key(user_id: int) -> str:
    akey, hashed_api_key = gen_api_key()
    await akey_upsert(user_id, hashed_api_key)
    return akey


async def akey_delete(user_id: int) -> None:
    pool: Pool = await db_get()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM api_keys WHERE user_id = $1", user_id)

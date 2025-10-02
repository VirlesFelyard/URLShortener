from typing import Tuple

from asyncpg import Pool
from config import *

from database.api_keys import akey_upsert
from database.base import db_get


async def user_exists(email: str) -> bool:
    pool: Pool = await db_get()
    async with pool.acquire() as conn:
        r = await conn.fetchval("select id from users where email = $1", email)
        return r is not None


async def user_add(name: str, email: str, password: str) -> Tuple[int, str]:
    if await user_exists(email):
        return (409, "user already exists!")

    pool: Pool = await db_get()
    async with pool.acquire() as conn:
        await conn.execute(
            """
            insert into users (
                name, email, password
            ) values (
                $1, $2, $3
            )
            """,
            name,
            email,
            await get_hash(password),
        )
        return (200, "user created successfully!")


async def user_login(email: str, password: str) -> Tuple[int, str]:
    pool: Pool = await db_get()
    async with pool.acquire() as conn:
        r = await conn.fetchrow(
            "select id, password from users where email = $1", email
        )
        if r is None:
            return (404, "user doesn't exist!")

        if not await verify_hash(password, r[1]):
            return (401, "wrong password!")

        akey, hashed_api_key = await gen_api_key()
        await akey_upsert(r[0], hashed_api_key)
        return (200, akey)

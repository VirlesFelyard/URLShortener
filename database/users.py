from typing import Tuple, Optional

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
            get_hash(password),
        )
        return (200, "user created successfully!")


async def user_login(email: str, password: str) -> Tuple[int, Optional[int]]:
    pool: Pool = await db_get()
    async with pool.acquire() as conn:
        r = await conn.fetchrow(
            "SELECT id, password FROM users WHERE email = $1", email
        )
        if r is None:
            return 404, None

        if not verify_hash(password, r["password"]):
            return 401, None

        return 200, r["id"]
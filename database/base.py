from typing import Optional

import asyncpg

from config import DATABASE

pool: Optional[asyncpg.Pool] = None


async def db_connect() -> None:
    global pool
    pool = await asyncpg.create_pool(
        user=DATABASE["USER"],
        password=DATABASE["PASSWORD"],
        database=DATABASE["NAME"],
        host=DATABASE["HOST"],
        port=DATABASE["PORT"],
    )

    print(f"🐁 -> 🛢️ Database '{DATABASE['NAME']}' sucessfully connected!")


async def db_close() -> None:
    global pool
    if pool:
        await pool.close()

    print(f"🐁 -> 🛢️ Database '{DATABASE['NAME']}' sucessfully disconnected!")


async def db_get() -> asyncpg.Pool:
    global pool
    if pool is None:
        await db_connect()
    return pool

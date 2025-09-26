from typing import Optional

import asyncpg

pool: Optional[asyncpg.Pool] = None


async def db_connect() -> None:
    global pool
    pool = await asyncpg.create_pool(
        user="postgres",
        password="postgres",
        database="urlshortener",
        host="localhost",
        port=5432,
    )

    print("🐁 -> 🛢️ Database 'urlshortener' sucessfully connected!")


async def db_close() -> None:
    global pool
    if pool:
        await pool.close()

    print("🐁 -> 🛢️ Database 'urlshortener' sucessfully disconnected!")


async def db_get() -> asyncpg.Pool:
    global pool
    if pool is None:
        await db_connect()
    return pool

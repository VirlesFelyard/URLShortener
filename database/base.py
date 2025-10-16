from asyncpg import Pool, create_pool
from fastapi import FastAPI

from config import DATABASE_URL


async def db_connect(app: FastAPI) -> None:
    app.state.pool: Pool = await create_pool(DATABASE_URL)


async def db_close(app: FastAPI) -> None:
    await app.state.pool.close()

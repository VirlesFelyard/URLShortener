from fastapi import FastAPI

from database.base import db_close, db_connect
from database.tables import init_tables
from routers.auth import router as auth_router
from routers.url import router as url_router

app: FastAPI = FastAPI()

app.include_router(auth_router, prefix="/api/auth")
app.include_router(url_router)


@app.on_event("startup")
async def startup() -> None:
    await db_connect()
    await init_tables()


@app.on_event("shutdown")
async def shutdown() -> None:
    await db_close()

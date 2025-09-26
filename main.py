from fastapi import FastAPI

from database.base import db_close, db_connect
from database.tables import init_tables

app: FastAPI = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello there!"}


@app.on_event("startup")
async def startup() -> None:
    await db_connect()
    await init_tables()


@app.on_event("shutdown")
async def shutdown() -> None:
    await db_close()

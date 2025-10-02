from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from database.base import db_close, db_connect
from database.tables import init_tables
from database.users import user_add, user_login

app: FastAPI = FastAPI()


class RegisterReq(BaseModel):
    name: str
    email: str
    password: str


class LoginReq(BaseModel):
    email: str
    password: str


@app.get("/")
async def root():
    return {"message": "Hello there!"}


@app.post("/auth/register")
async def register(data: RegisterReq) -> dict:
    status, msg = await user_add(data.name, data.email, data.password)
    if status != 200:
        raise HTTPException(status_code=status, detail=msg)
    return {"message": msg}


@app.post("/auth/login")
async def login(data: LoginReq) -> dict:
    status, msg = await user_login(data.email, data.password)
    if status != 200:
        raise HTTPException(status_code=status, detail=msg)
    return {"api_key": msg}


@app.on_event("startup")
async def startup() -> None:
    await db_connect()
    await init_tables()


@app.on_event("shutdown")
async def shutdown() -> None:
    await db_close()

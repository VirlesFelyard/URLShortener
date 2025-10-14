from fastapi import APIRouter, HTTPException

from database.api_keys import regenerate_api_key
from database.users import user_add, user_login
from dto.schemas import LoginReq, RegisterReq

router: APIRouter = APIRouter()


@router.post("/register")
async def register(data: RegisterReq):
    status, msg = await user_add(data.name, data.email, data.password)
    if status != 200:
        raise HTTPException(status_code=status, detail=msg)
    return {"message": msg}


@router.post("/login")
async def login(data: LoginReq):
    status, msg = await user_login(data.email, data.password)
    if status != 200:
        raise HTTPException(status_code=status, detail=msg)
    return {"message": "user logged in successfully!"}


@router.post("/akey-generate")
async def akey_generate(data: LoginReq) -> dict:
    status, msg = await user_login(data.email, data.password)
    if status != 200:
        raise HTTPException(status_code=status, detail=msg)
    api_key: str = await regenerate_api_key(msg)
    return {"message": "Your new API-key generated successfully!", "api_key": api_key}

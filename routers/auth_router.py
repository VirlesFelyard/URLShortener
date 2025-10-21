from fastapi import APIRouter, HTTPException, Request

from dto.schemas import LoginReq, RegisterReq
from utils.exceptions import ServiceError

router = APIRouter(tags=["Authentication"])


@router.post("/register")
async def register(data: RegisterReq, request: Request):
    user_service = request.app.state.user_service
    try:
        await user_service.register_user(data.name, data.email, data.password)
        return {"message": "User registered successfully"}
    except ServiceError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/login")
async def login(data: LoginReq, request: Request):
    user_service = request.app.state.user_service
    try:
        await user_service.login_user(data.email, data.password)
        return {"message": "User logged in successfully"}
    except ServiceError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/akey-generate")
async def akey_generate(data: LoginReq, request: Request):
    user_service = request.app.state.user_service
    apikey_service = request.app.state.apikey_service
    try:
        user_id = await user_service.login_user(data.email, data.password)
        api_key = await apikey_service.generate_akey(user_id)
        return {
            "message": "Your new API-key generated successfully!",
            "api_key": api_key,
        }
    except ServiceError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

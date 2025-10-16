from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from utils.exceptions import ServiceError

security = HTTPBearer()


async def authorize_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> int:
    token = credentials.credentials
    apikey_service = request.app.state.apikey_service
    try:
        return await apikey_service.validate_akey(token)
    except ServiceError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

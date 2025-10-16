from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security = HTTPBearer()


async def authorize_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> int:
    token = credentials.credentials
    apikey_service = request.app.state.apikey_service
    return await apikey_service.validate_akey(token)

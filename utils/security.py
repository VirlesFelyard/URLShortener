from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from database.api_keys import akey_validate

security = HTTPBearer()


async def authorize_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> int:
    token = credentials.credentials
    status, msg = await akey_validate(token)
    if not status or msg is None:
        raise HTTPException(status_code=401, detail="Invalid or expired api-key")
    return msg

from config import gen_api_key, get_hash
from repositories.apikey_repository import ApiKeyRepository
from utils.exceptions import ServiceError


class ApiKeyService:
    def __init__(self, apikey_repo: ApiKeyRepository):
        self.apikey_repo: ApiKeyRepository = apikey_repo

    async def generate_akey(self, user_id: int) -> str:
        key, hashed_key = gen_api_key()
        await self.apikey_repo.upsert(user_id, hashed_key)
        return key

    async def validate_akey(self, key: str) -> int:
        user_id = await self.apikey_repo.validate(get_hash(key))
        if not user_id:
            raise ServiceError("Invalid or expired api-key", 401)
        return user_id

    async def has_akey(self, user_id: int) -> bool:
        return await self.apikey_repo.exists_by_id(user_id)

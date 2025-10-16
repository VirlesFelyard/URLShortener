from config import get_hash, verify_hash
from repositories.user_repository import UserRepository
from utils.exceptions import ServiceError


class UserService:
    def __init__(self, user_repo: UserRepository) -> None:
        self.user_repo = user_repo

    async def register_user(self, name: str, email: str, password: str) -> int:
        if await self.user_repo.exists_by_email(email):
            raise ServiceError(
                message="User with this email already exists", status_code=409
            )
        return await self.user_repo.add(name, email, get_hash(password))

    async def login_user(self, email: str, password: str) -> int:
        row = await self.user_repo.get_password_by_email(email)
        if not row:
            raise ServiceError(message="User not found", status_code=404)
        if not verify_hash(password, row["password"]):
            raise ServiceError(message="Incorrect password", status_code=401)
        return row["id"]

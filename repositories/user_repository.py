from typing import Optional

from asyncpg import Pool, Record


class UserRepository:
    def __init__(self, pool: Pool) -> None:
        self.pool = pool

    async def exists_by_email(self, email: str) -> bool:
        async with self.pool.acquire() as conn:
            return await conn.fetchval(
                "SELECT EXISTS (SELECT 1 FROM users WHERE email = $1)", email
            )

    async def get_password_by_email(self, email: str) -> Optional[Record]:
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(
                "SELECT id, password FROM users WHERE email = $1", email
            )

    async def add(self, name: str, email: str, password: str) -> int:
        async with self.pool.acquire() as conn:
            return await conn.fetchval(
                "INSERT INTO users (name, email, password) VALUES ($1, $2, $3) RETURNING id",
                name,
                email,
                password,
            )

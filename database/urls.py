from datetime import time
from typing import Tuple
from urllib.parse import urlparse

from database.base import db_get


async def url_shortcode_exists(short_code: str) -> bool:
    pool = await db_get()
    async with pool.acquire() as conn:
        return (
            await conn.fetchval("SELECT 1 FROM urls WHERE short_code = $1", short_code)
            is not None
        )


def validate_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("Invalid URL format")
    return url.strip()


async def url_add(
    user_id: int,
    original_url: str,
    short_code: str,
    password: str | None = None,
    valid_from: time | None = None,
    valid_until: time | None = None,
    allow_proxy: bool = True,
) -> Tuple[int, str]:
    if await url_shortcode_exists(short_code):
        return 409, "Short code already exists!"

    try:
        original_url = validate_url(original_url)
    except ValueError as e:
        return 400, str(e)

    if valid_from and valid_until and valid_from >= valid_until:
        return 422, "valid_from must be earlier than valid_until"

    pool = await db_get()
    async with pool.acquire() as conn:
        async with conn.transaction():
            exists = await conn.fetchval(
                """
                SELECT 1 FROM urls
                WHERE user_id = $1 AND original_url = $2
            """,
                user_id,
                original_url,
            )
            if exists:
                return 409, "URL already added by this user"

            await conn.execute(
                """
                INSERT INTO urls (
                    user_id, original_url, short_code,
                    password, valid_from, valid_until, allow_proxy
                ) VALUES (
                    $1, $2, $3,
                    $4, $5, $6, $7
                )
            """,
                user_id,
                original_url,
                short_code,
                password,
                valid_from,
                valid_until,
                allow_proxy,
            )

    return 201, "URL added successfully"

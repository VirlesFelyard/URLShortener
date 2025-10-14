import asyncio
from ipaddress import IPv4Address, IPv6Address, ip_address
from typing import Any, Dict

import aiohttp
from asyncpg import Pool

from database.base import db_get
from database.tables import get_fields


async def ip_exists(ip: IPv4Address | IPv6Address) -> bool:
    pool: Pool = await db_get()
    async with pool.acquire() as conn:
        r = await conn.fetchval(
            "SELECT id FROM ip_addresses WHERE ip_address = $1", str(ip)
        )
        return r is not None


async def ip_fetchrow(
    ip: IPv4Address | IPv6Address, *fields: str
) -> Dict[str, Any] | None:
    if not fields:
        return None
    await ip_add(ip)
    allow_fields: List[str] = await get_fields("ip_addresses")
    field_list: str = ", ".join(filter(lambda f: f in allow_fields, fields))

    pool: Pool = await db_get()
    async with pool.acquire() as conn:
        r = await conn.fetchrow(
            f"SELECT {field_list} FROM ip_addresses WHERE ip_address = $1", ip
        )
        return dict(r)


async def ip_delete(ip: IPv4Address | IPv6Address) -> None:
    pool: Pool = await db_get()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM ip_addresses WHERE ip_address = $1", ip)


async def ip_add(ip: IPv4Address | IPv6Address) -> None:
    if await ip_exists(ip):
        return

    async with aiohttp.ClientSession() as session:
        async with session.get("https://proxycheck.io/v3/" + str(ip)) as resp:
            ip_json: dict = await resp.json()
            ip_json: dict = ip_json[str(ip)]
            timezone: str = ip_json["location"]["timezone"]
            provider: str = ip_json["network"]["provider"]
            country: str = ip_json["location"]["country_name"]
            region: str = ip_json["location"]["region_name"]
            city: str = ip_json["location"]["city_name"]
            try:
                latitude: float = float(ip_json["location"]["latitude"])
                longitude: float = float(ip_json["location"]["longitude"])
            except ValueError:
                latitude = longitude = None
            is_proxy: bool = (
                ip_json["detections"]["proxy"] or ip_json["detections"]["hosting"]
            )

    pool: Pool = await db_get()
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO ip_addresses(
                ip_address, timezone, provider, country,
                region, city, latitude, longitude, is_proxy
            ) VALUES (
                $1, $2, $3, $4, $5, 
                $6, $7, $8, $9
            )
            """,
            ip,
            timezone,
            provider,
            country,
            region,
            city,
            latitude,
            longitude,
            is_proxy,
        )


async def test() -> None:
    new_ip = ip_address("72.14.201.51")
    await ip_exists(new_ip)
    await ip_add(new_ip)
    print(await ip_fetchrow(new_ip, "id", "ip_address", "country", "longitude"))


if __name__ == "__main__":
    asyncio.run(test())

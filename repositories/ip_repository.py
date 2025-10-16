from ipaddress import IPv4Address, IPv6Address
from typing import List, Optional

from asyncpg import Pool


class IpRepository:
    def __init__(self, pool: Pool) -> None:
        self.pool = pool

    async def exists_by_address(self, ip_address: IPv4Address | IPv6Address) -> bool:
        async with self.pool.acquire() as conn:
            return await conn.fetchval(
                "SELECT EXISTS (SELECT 1 FROM ip_addresses WHERE ip_address = $1)",
                ip_address,
            )

    async def fetchrow_by_ip(
        self, ip_address: IPv4Address | IPv6Address, fields: List[str]
    ) -> Optional[dict]:
        if not fields:
            return None
        field_list: str = ", ".join(fields)
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                f"SELECT {field_list} FROM ip_addresses WHERE ip_address = $1",
                ip_address,
            )
            return dict(row) if row else None

    async def add(
        self,
        ip_address: IPv4Address | IPv6Address,
        longitude: float,
        latitude: float,
        is_proxy: bool,
        timezone: str,
        provider: str,
        country: str,
        region: str,
        city: str,
    ) -> None:
        async with self.pool.acquire() as conn:
            return await conn.execute(
                """
                INSERT INTO ip_addresses(
                    ip_address, longitude, latitude, is_proxy,
                    timezone, provider, country, region, city
                ) VALUES (
                    $1, $2, $3, $4,
                    $5, $6, $7, $8, $9
                )
                """,
                ip_address,
                longitude,
                latitude,
                is_proxy,
                timezone,
                provider,
                country,
                region,
                city,
            )

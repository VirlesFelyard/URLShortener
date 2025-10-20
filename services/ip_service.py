from ipaddress import IPv4Address, IPv6Address

from aiohttp import ClientSession

from repositories.ip_repository import IpRepository


class IpService:
    def __init__(self, ip_repo: IpRepository) -> None:
        self.ip_repo: IpRepository = ip_repo

    async def ensure_ip(self, ip_address: IPv4Address | IPv6Address) -> None:
        if await self.ip_repo.exists_by_address(ip_address):
            return

        data: dict = await self._fetch_ip_data(str(ip_address))

        await self.ip_repo.add(
            ip_address=ip_address,
            longitude=data["longitude"],
            latitude=data["latitude"],
            is_proxy=data["is_proxy"],
            timezone=data["timezone"],
            provider=data["provider"],
            country=data["country"],
            region=data["region"],
            city=data["city"],
        )

    async def is_proxy(self, ip_address: IPv4Address | IPv6Address) -> bool:
        await self.ensure_ip(ip_address)
        row = await self.ip_repo.fetchrow_by_ip(ip_address, fields=["is_proxy"])
        return row["is_proxy"]

    async def _fetch_ip_data(self, ip: str) -> dict:
        async with ClientSession() as session:
            async with session.get(f"https://proxycheck.io/v3/{ip}") as resp:
                ip_json: dict = await resp.json()
                ip_data = ip_json[ip]

                try:
                    latitude = float(ip_data["location"]["latitude"])
                    longitude = float(ip_data["location"]["longitude"])
                except ValueError:
                    latitude = longitude = None

                return {
                    "longitude": longitude,
                    "latitude": latitude,
                    "is_proxy": ip_data["detections"]["proxy"]
                    or ip_data["detections"]["hosting"],
                    "timezone": ip_data["location"]["timezone"],
                    "provider": ip_data["network"]["provider"],
                    "country": ip_data["location"]["country_name"],
                    "region": ip_data["location"]["region_name"],
                    "city": ip_data["location"]["city_name"],
                }

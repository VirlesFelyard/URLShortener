from repositories.click_repository import ClickRepository


class ClickService:
    def __init__(self, click_repo: ClickRepository) -> None:
        self.click_repo = click_repo

    async def insert_click(self, url_id: int, user_agent: str, ip: int) -> None:
        await self.click_repo.add(url_id, user_agent, ip)

    async def count_clicks(self, url_id: int) -> int:
        clicks: int = await self.click_repo.fetch_clicks_by_url(url_id)
        return len(clicks)

from asyncpg import Pool
from fastapi import FastAPI

from database.base import db_close, db_connect
from database.tables import init_tables
from repositories.apikey_repository import ApiKeyRepository
from repositories.click_repository import ClickRepository
from repositories.ip_repository import IpRepository
from repositories.url_repository import URLRepository
from repositories.user_repository import UserRepository
from routers.auth_router import router as auth_route
from routers.url_router import router as url_route
from services.apikey_service import ApiKeyService
from services.click_service import ClickService
from services.ip_service import IpService
from services.redirect_service import RedirectService
from services.url_service import URLService
from services.user_service import UserService

app: FastAPI = FastAPI()

app.include_router(auth_route, prefix="/api/auth")
app.include_router(url_route)


@app.on_event("startup")
async def startup() -> None:
    await db_connect(app)
    pool: Pool = app.state.pool

    await init_tables(pool)

    user_repo: UserRepository = UserRepository(pool)
    apikey_repo: ApiKeyRepository = ApiKeyRepository(pool)
    url_repo: URLRepository = URLRepository(pool)
    ip_repo: IpRepository = IpRepository(pool)
    click_repo: ClickRepository = ClickRepository(pool)

    app.state.user_service: UserService = UserService(user_repo)
    app.state.apikey_service: ApiKeyService = ApiKeyService(apikey_repo)
    app.state.url_service: URLService = URLService(url_repo)
    app.state.ip_service: IpService = IpService(ip_repo)
    app.state.click_service: ClickService = ClickService(click_repo)
    app.state.redirect_service: RedirectService = RedirectService(
        app.state.url_service,
        app.state.click_service,
        app.state.ip_service,
    )


@app.on_event("shutdown")
async def shutdown() -> None:
    await db_close(app)

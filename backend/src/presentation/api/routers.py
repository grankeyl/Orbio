from fastapi import FastAPI

from src.presentation.api.admin.router import admin_router
from src.presentation.api.history.router import history_router
from src.presentation.api.market.router import market_router
from src.presentation.api.star.router import star_router
from src.presentation.api.user.router import user_router
from src.presentation.api.wallet.router import wallet_router
from src.presentation.api.nfts.router import nfts_router
from src.presentation.api.app.router import app_router


def setup_routers(app: FastAPI) -> None:
    app.include_router(user_router)
    app.include_router(market_router)
    app.include_router(wallet_router)
    app.include_router(history_router)
    app.include_router(star_router)
    app.include_router(admin_router)
    app.include_router(nfts_router)
    app.include_router(app_router)
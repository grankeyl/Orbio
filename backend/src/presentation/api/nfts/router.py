import json
import redis.asyncio as redis

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Query

from src.entrypoint.config import Config
from src.application.interactors.nfts import NftsInteractor
from src.domain.entities.history import ActivityDM, HistoryDM


nfts_router = APIRouter(prefix="/nfts", tags=["Nfts"])


async def read_nfts_from_redis():
    config = Config()
    redis_client = redis.from_url(config.redis.REDIS_URL)

    data = await redis_client.get("nfts:gifts:with_floors")
    await redis_client.aclose()

    if data:
        gifts = json.loads(data)
        return gifts
    else:
        return None


@nfts_router.get("", response_model=None)
async def get_nfts() -> any:
    """Get nfts"""
    gifts = await read_nfts_from_redis()
    if not gifts:
        pass
    else:
        return gifts
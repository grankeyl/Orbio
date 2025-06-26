import asyncio
import sys
import json
from pathlib import Path

import redis.asyncio as redis

BASE_DIR = Path(__file__).resolve().parents[3]
sys.path.append(str(BASE_DIR))

from src.entrypoint.config import Config  # noqa: E402
from src.infrastructure.database.session import new_session_maker  # noqa: E402
from src.application.interactors.nfts import NftsInteractor


async def start_get_nfts() -> None:
    config = Config()
    session_maker = new_session_maker(config.postgres)
    redis_client = redis.from_url(config.redis.REDIS_URL)

    async with session_maker() as session:
        nfts_interactor = NftsInteractor()

        gifts = await nfts_interactor.get_nfts()
        if not gifts:
            return

        await redis_client.set("nfts:gifts", json.dumps(gifts, default=str))

        floors = await nfts_interactor.get_floors()
        floors_map = dict(floors)
        print(floors_map)

        gifts_with_floors = []
        for gift in gifts:
            try:
                gift_lover = gift["type"].lower().replace(" ", "")
                floor_data = floors_map['floorPrices'][gift_lover]
                gift_with_floor = {**gift, "floor": floor_data}
                gifts_with_floors.append(gift_with_floor)
                print("Adding floor to gift: " + gift["type"] + " with floor: " + floor_data)
            except:
                pass

        await redis_client.set("nfts:gifts:with_floors", json.dumps(gifts_with_floors, default=str))

    await redis_client.aclose()


if __name__ == "__main__":
    asyncio.run(start_get_nfts())
import httpx
from typing import Any
from src.application.interfaces.interactor import Interactor


async def get_nft_info(type: str) -> Any:
    timeout = httpx.Timeout(15.0)
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "identity",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }

    async with httpx.AsyncClient(timeout=timeout, headers=headers) as client:
        response = await client.get("https://api.changes.tg/gift/" + type)
        response.raise_for_status()
        gift = response.json()
        
    return gift


class NftsInteractor:
    async def get_nfts(self) -> Any:
        giftsArray = []

        timeout = httpx.Timeout(15.0)
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "identity",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        }

        async with httpx.AsyncClient(timeout=timeout, headers=headers) as client:
            response = await client.get("https://api.changes.tg/gifts")
            response.raise_for_status()
            gifts = response.json()

        for gift in gifts:
            info = await get_nft_info(gift)
            print("Adding gift: " + gift)

            giftsArray.append({
                "type": gift,
                "info": info
            })
        
        return giftsArray

    async def get_floors(self) -> Any:
        timeout = httpx.Timeout(15.0)
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "identity",
            "Accept-Language": "ru",
            "Authorization": "tma user=%7B%22id%22%3A2106187940%2C%22first_name%22%3A%22Grankeyl%22%2C%22last_name%22%3A%22%22%2C%22username%22%3A%22oaole%22%2C%22language_code%22%3A%22ru%22%2C%22is_premium%22%3Atrue%2C%22allows_write_to_pm%22%3Atrue%2C%22photo_url%22%3A%22https%3A%5C%2F%5C%2Ft.me%5C%2Fi%5C%2Fuserpic%5C%2F320%5C%2FRxorCh8pIvxePpBZObmQqHhfbZ1-0XS1r-4kQ1-e_kA.svg%22%7D&chat_instance=5742971387824700247&chat_type=private&auth_date=1750681080&signature=YvGQr_Rw4HjsHcmvKyGFs0e_C9eXsnkC7j2Hiygm1AnMclhzNHgEfxbXWlAWgaMB-mgfp58XNHaGjwPU7MaCBA&hash=0fdd10aabe4982fd73bfe5b345f31303b35218362d7256282d4cbf176d1f0f67",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Referer": "https://portals-market.com/",
            "User-Agent": "Mozilla/5.0 ..."
        }

        async with httpx.AsyncClient(timeout=timeout, headers=headers) as client:
            response = await client.get("https://portals-market.com/api/collections/floors")
            response.raise_for_status()
            floors = response.json()

        return floors
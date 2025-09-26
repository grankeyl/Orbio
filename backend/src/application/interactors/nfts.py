import json
import httpx
from typing import Any
from src.application.interfaces.interactor import Interactor
from src.entrypoint.config import Config

config = Config()

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
            "Authorization": f"tma {config.sites.PORTAL_AUTHORIZATION}",
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
    
    async def get_tonnel_info(self, id: str) -> Any:
        print(f"Getting tonnel info for id: {id}")
        url = f"https://gifts3.tonnel.network/api/giftData/{id}"
        timeout = httpx.Timeout(15.0)
        headers = {
            "Accept": "*/*",
            "Accept-Language": "ru",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "Origin": "https://marketplace.tonnel.network",
            "Pragma": "no-cache",
            "Referer": "https://marketplace.tonnel.network/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko)"
        }

        data = {
            "ref": "",
            "authData": f"{config.sites.TONNEL_AUTHORIZATION}"
        }

        async with httpx.AsyncClient(timeout=timeout, headers=headers) as client:
            response = await client.post(url, json=data)
            response.raise_for_status()
            if not response.text.strip():
                print("❌ Пустой ответ от сервера")
                return {"error": "Empty response from server"}
            try:
                return response.json()
            except json.JSONDecodeError as e:
                print("❌ Не удалось распарсить JSON:", e)
                print("Ответ сервера:", response.text)
                return {"error": "Invalid JSON response"}
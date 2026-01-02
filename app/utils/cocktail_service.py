import httpx
from app.config import COCKTAIL_API_KEY, COCKTAIL_BASE_URL

async def fetch_cocktail_list(name: str):
    url = f"{COCKTAIL_BASE_URL}/{COCKTAIL_API_KEY}/search.php"
    params = {"s": name}

    async with httpx.AsyncClient() as client:
        res = await client.get(url, params=params)
        res.raise_for_status()
        return res.json()

async def fetch_cocktail_detail(cocktail_id: str):
    url = f"{COCKTAIL_BASE_URL}/{COCKTAIL_API_KEY}/lookup.php"
    params = {"i": cocktail_id}

    async with httpx.AsyncClient() as client:
        res = await client.get(url, params=params)
        res.raise_for_status()
        return res.json()

async def fetch_cocktails_by_letter(letter: str):
    url = f"{COCKTAIL_BASE_URL}/{COCKTAIL_API_KEY}/search.php"
    params = {"f": letter}

    async with httpx.AsyncClient() as client:
        res = await client.get(url, params=params)
        res.raise_for_status()
        return res.json()
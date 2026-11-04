import aiohttp
from config import COC_API_TOKEN, CLAN_TAG

async def get_clan_members():
    tag = CLAN_TAG.replace("#", "%23")
    url = f"https://api.clashofclans.com/v1/clans/{tag}/members"
    headers = {
        "Authorization": f"Bearer {COC_API_TOKEN}",
        "Accept": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("items", [])
                else:
                    print(f"[API ERROR] Status: {response.status}")
                    return None
        except Exception as e:
            print(f"[API EXCEPTION] {e}")
            return None

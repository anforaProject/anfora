from typing import Dict
from utils import load_config
import aiohttp

config = load_config()

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.json()

async def fetch_media_by_id(ident:str) -> Dict:
    """
    Fetch media json given it's id
    """
    async with aiohttp.ClientSession() as session:
        data = await fetch(session, f'http://{config[media_server_url]}')
        return data
    
    
async def fetch_media_as_by_id(ident:str) -> Dict:
    return 

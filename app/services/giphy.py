import aiohttp
import os
import random
from typing import Optional
from logger import setup_logger


GIPHY_API_KEY = os.getenv('GIPHY_API_KEY')

base_url = "https://api.giphy.com/v1/gifs"
random_endpoint = "random"

class GiphyService:
    def __init__(self):
        self.api_key = GIPHY_API_KEY
        self.logger = setup_logger()

        if not self.api_key:
            self.logger.error("API KEY is not set. GiphyService will be deactivated.")

    async def __call__(self, tag: str) -> Optional[str]:
        if self.api_key:
            return await self.get_random_gif(tag)
        
        return await self.noop(tag)

    async def get_random_gif(self, tag: str) -> Optional[str]:
        """Fetch a random laughter gif from Giphy"""
        search_term = random.choice([tag])

        params = {
            'api_key': self.api_key,
            'tag': search_term,
            'rating': 'g'  # Keep it family-friendly
        }

        try:
            async with aiohttp.ClientSession() as session:
                url = f"{base_url}/{random_endpoint}"
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data['data']['images']['original']['url']
                    else:
                        raise Exception(f"Giphy API returned status code {response.status}")
        except Exception as e:
            print(f"Error fetching Giphy gif: {e}")
            return None

    async def noop(self, tag: str) -> Optional[str]:
        """No-operation function if API key is missing"""
        return None
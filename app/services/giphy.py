import os
import random
import aiohttp
from typing import Optional

class GiphyService:
    def __init__(self):
        self.api_key = os.getenv('GIPHY_API_KEY')
        if not self.api_key:
            raise ValueError("GIPHY_API_KEY environment variable is required")
        self.base_url = "https://api.giphy.com/v1/gifs"

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
                async with session.get(f"{self.base_url}/random", params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data['data']['images']['original']['url']
        except Exception as e:
            print(f"Error fetching Giphy gif: {e}")
            return None


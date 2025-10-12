import os
import random
from typing import Optional

import aiohttp

from app.logger import setup_logger

GIPHY_API_KEY = os.getenv("GIPHY_API_KEY")

ratings = ["g", "pg", "pg-13", "r"]


class GiphyService:
    def __init__(self, api_key: str, rating: str = "g"):
        self.api_key = api_key
        self.logger = setup_logger()
        self.rating = rating

        if not self.api_key:
            self.logger.error("API KEY is not set. GiphyService will be deactivated.")
            return

        if self.rating not in ratings:
            self.logger.warning(f"Invalid rating '{self.rating}' provided. Defaulting to 'g'.")
            self.rating = "g"

    async def __call__(self, tag: str) -> Optional[str]:
        if self.api_key:
            return await self.get_random_gif(tag)

        return await self.noop(tag)

    async def get_random_gif(self, tag: str) -> Optional[str]:
        """Fetch a random laughter gif from Giphy"""

        url = "https://api.giphy.com/v1/gifs/random"
        params = {"api_key": self.api_key, "tag": random.choice([tag]), "rating": self.rating}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data["data"]["images"]["original"]["url"]
                    else:
                        raise Exception(f"Giphy API returned status code {response.status}")
        except Exception as e:
            print(f"Error fetching Giphy gif: {e}")
            return None

    async def noop(self, tag: str) -> Optional[str]:
        """No-operation function if API key is missing"""
        return None

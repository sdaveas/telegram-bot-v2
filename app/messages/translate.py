from typing import Optional

import aiohttp

from app.logger import setup_logger


class TranslateHandler:
    def __init__(self, api_url: str):
        self.api_url = api_url
        self.logger = setup_logger()
        self.logger.info("Translation handler initialized")

    async def translate(self, text: str, target_language: str) -> Optional[dict]:
        try:
            response = await self._call_translation_api(text, target_language)
            return response
        except Exception as e:
            self.logger.error(f"Error translating text: {str(e)}")
            return None

    async def _call_translation_api(self, text: str, target_language: str) -> Optional[dict]:
        payload = {"text": text, "dest": target_language, "src": "auto", "pronunciation": True}
        headers = {"Content-Type": "application/json"}
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.api_url + "/translate", json=payload, headers=headers
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data
                else:
                    error_text = await resp.text()
                    self.logger.error(f"Translation API error {resp.status}: {error_text}")
                    return None

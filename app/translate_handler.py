import aiohttp
from typing import Optional
from .logger import setup_logger


class TranslateHandler:
    def __init__(self, api_url: str):
        """Initialize the Translation handler"""
        self.api_url = api_url
        self.logger = setup_logger()
        self.logger.info("Translation handler initialized")

    async def translate(self, text: str, target_language: str) -> Optional[dict]:
        """
        Translate text to the specified language

        The translation is performed using a third-party API.
        Returns a dict with keys: 'translated_text', 'pronunciation', 'src'
        """
        try:
            response = await self._call_translation_api(text, target_language)
            return response
        except Exception as e:
            self.logger.error(f"Error translating text: {str(e)}")
            return None

    async def _call_translation_api(self, text: str, target_language: str) -> Optional[dict]:
        """
        Calls the translation API and returns the response as a dict.
        """
        payload = {
            "text": text,
            "dest": target_language,
            "src": "auto",
            "pronunciation": True
        }
        headers = {
            "Content-Type": "application/json"
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(self.api_url + "/translate", json=payload, headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data
                else:
                    error_text = await resp.text()
                    self.logger.error(f"Translation API error {resp.status}: {error_text}")
                    return None

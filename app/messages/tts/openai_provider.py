import os
from typing import Optional
from openai import OpenAI
from app.logger import setup_logger
from .base import BaseTTSProvider

class OpenAITTSProvider(BaseTTSProvider):
    """OpenAI TTS provider"""

    AVAILABLE_VOICES = ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer']
    AVAILABLE_MODELS = ['tts-1', 'tts-1-hd']

    def __init__(self):
        self.logger = setup_logger()
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            self.logger.error("OPENAI_API_KEY environment variable is not set")
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        self.client = OpenAI(api_key=api_key)
        self._model = 'tts-1-hd'  # Higher quality model
        self._voice = 'nova'  # Default voice
        self.logger.info(f"OpenAI TTS provider initialized with {self._model} model and {self._voice} voice")

    @property
    def name(self) -> str:
        return "openai"

    @property
    def voices(self) -> list[str]:
        return self.AVAILABLE_VOICES

    async def generate_speech(self, text: str) -> Optional[bytes]:
        """Generate speech using OpenAI's TTS API"""
        try:
            response = self.client.audio.speech.create(
                model=self._model,
                voice=self._voice,
                input=text
            )

            # Get bytes from the response
            audio_bytes = response.read()

            self.logger.info(f"Successfully generated speech with OpenAI TTS: {text[:50]}...")
            return audio_bytes

        except Exception as e:
            self.logger.error(f"Error generating speech with OpenAI: {str(e)}")
            return None


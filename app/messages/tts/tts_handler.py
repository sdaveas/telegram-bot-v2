from typing import Optional
from app.logger import setup_logger
from .base import BaseTTSProvider
from .openai_provider import OpenAITTSProvider
from .google_provider import GoogleTTSProvider

class TTSHandler:
    """Main TTS handler that manages multiple providers"""

    def __init__(self):
        self.logger = setup_logger()
        self.providers: dict[str, BaseTTSProvider] = {}
        self._current_provider = None

        # Try to initialize providers
        try:
            self.providers['openai'] = OpenAITTSProvider()
            self._current_provider = 'openai'
        except Exception as e:
            self.logger.warning(f"Could not initialize OpenAI TTS: {str(e)}")

        try:
            self.providers['google'] = GoogleTTSProvider()
            if not self._current_provider:
                self._current_provider = 'google'
        except Exception as e:
            self.logger.warning(f"Could not initialize Google Cloud TTS: {str(e)}")

        # Always initialize gTTS provider
        from .gtts_provider import GTTSProvider
        self.providers['gtts'] = GTTSProvider()
        if not self._current_provider:
            self._current_provider = 'gtts'

        self.logger.info(f"TTS handler initialized with providers: {', '.join(self.providers.keys())}")

    @property
    def current_provider(self) -> str:
        """Get the name of the current provider"""
        return self._current_provider

    def set_provider(self, provider_name: str) -> bool:
        """Set the current provider"""
        if provider_name in self.providers:
            self._current_provider = provider_name
            self.logger.info(f"Switched to TTS provider: {provider_name}")
            return True
        return False

    def get_available_providers(self) -> list[str]:
        """Get list of available providers"""
        return list(self.providers.keys())

    def get_available_voices(self, provider: str = None) -> list[str]:
        """Get list of available voices for a provider"""
        provider = provider or self._current_provider
        if provider in self.providers:
            return self.providers[provider].voices
        return []

    async def generate_speech(self, text: str) -> Optional[bytes]:
        """Generate speech using the current provider"""
        if not self._current_provider:
            self.logger.error("No TTS provider available")
            return None

        provider = self.providers[self._current_provider]
        return await provider.generate_speech(text)


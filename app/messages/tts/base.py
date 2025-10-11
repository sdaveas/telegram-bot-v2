from abc import ABC, abstractmethod
from typing import Optional

class BaseTTSProvider(ABC):
    """Base class for all TTS providers"""

    @abstractmethod
    async def generate_speech(self, text: str) -> Optional[bytes]:
        """Generate speech from text"""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Get the name of the TTS provider"""
        pass

    @property
    @abstractmethod
    def voices(self) -> list[str]:
        """Get list of available voices"""
        pass


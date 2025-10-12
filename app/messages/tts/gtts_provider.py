import os
import tempfile
from typing import Optional

from gtts import gTTS

from app.logger import setup_logger

from .base import BaseTTSProvider


class GTTSProvider(BaseTTSProvider):
    """Google Translate TTS provider (gTTS)"""

    AVAILABLE_VOICES = ["el"]  # Only Greek is supported

    def __init__(self):
        self.logger = setup_logger()
        self.logger.info("gTTS provider initialized with Greek voice")

    @property
    def name(self) -> str:
        return "gtts"

    @property
    def voices(self) -> list[str]:
        return self.AVAILABLE_VOICES

    async def generate_speech(self, text: str) -> Optional[bytes]:
        """Generate speech using gTTS"""
        try:
            # Create gTTS object with Greek voice
            tts = gTTS(text=text, lang="el", slow=False)

            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
                temp_filename = tmp_file.name
                tts.save(temp_filename)

            # Read the file back as bytes
            with open(temp_filename, "rb") as f:
                audio_bytes = f.read()

            # Clean up temporary file
            os.unlink(temp_filename)

            self.logger.info(f"Successfully generated speech with gTTS: {text[:50]}...")
            return audio_bytes

        except Exception as e:
            self.logger.error(f"Error generating speech with gTTS: {str(e)}")
            return None

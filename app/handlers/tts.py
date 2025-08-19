import os
import tempfile
from typing import Optional
from gtts import gTTS
from app.logger import setup_logger

class TTSHandler:
    def __init__(self):
        """Initialize the TTS handler with gTTS"""
        self.logger = setup_logger()
        self.logger.info("TTS handler initialized with gTTS (Greek voice)")

    async def generate_speech(self, text: str) -> Optional[bytes]:
        """
        Convert text to speech using gTTS with Greek voice
        Returns audio bytes in MP3 format
        Note: Greek voice handles both Greek and English (with accent)
        """
        try:
            # Create gTTS object with Greek voice
            tts = gTTS(text=text, lang='el', slow=False)

            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp_file:
                temp_filename = tmp_file.name
                tts.save(temp_filename)

            # Read the file back as bytes
            with open(temp_filename, 'rb') as f:
                audio_bytes = f.read()

            # Clean up temporary file
            os.unlink(temp_filename)

            self.logger.info(f"Successfully generated TTS for: {text[:50]}...")
            return audio_bytes

        except Exception as e:
            self.logger.error(f"Error generating speech: {str(e)}")
            return None

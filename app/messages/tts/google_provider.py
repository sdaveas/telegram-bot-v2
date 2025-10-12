import os
import base64
from typing import Optional
import google.generativeai as genai
from app.logger import setup_logger
from .base import BaseTTSProvider


class GoogleTTSProvider(BaseTTSProvider):
    """Google Cloud TTS provider"""

    # Gemini audio output doesn't currently expose a stable set of voice names via the Python SDK
    AVAILABLE_VOICES = []

    def __init__(self):
        self.logger = setup_logger()
        # Check if GEMINI_API_KEY is set
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            self.logger.error("GEMINI_API_KEY environment variable is not set")
            raise ValueError("GEMINI_API_KEY environment variable is not set")

        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel("gemini-2.5-flash")
            self._voice = None
            self.logger.info("Gemini TTS provider initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize Gemini TTS client: {str(e)}")
            raise

    @property
    def name(self) -> str:
        return "google"

    @property
    def voices(self) -> list[str]:
        return self.AVAILABLE_VOICES

    async def generate_speech(self, text: str) -> Optional[bytes]:
        """Generate speech using Gemini TTS (audio generation via Responses API)."""
        try:
            # Ask Gemini to convert text to audio
            prompt = {"text": text, "requestAudio": True, "targetAudioMimeType": "audio/mpeg"}
            response = self.model.generate_content(
                str(prompt),
                generation_config=genai.types.GenerationConfig(candidate_count=1),
                stream=False,
            )

            # Extract base64-encoded audio from candidates -> content -> parts -> inline_data.data
            b64_data: Optional[str] = None
            try:
                for cand in getattr(response, "candidates", []) or []:
                    content = getattr(cand, "content", None)
                    if not content:
                        continue
                    for part in getattr(content, "parts", []) or []:
                        inline = getattr(part, "inline_data", None)
                        if inline and getattr(inline, "data", None):
                            b64_data = inline.data
                            break
                    if b64_data:
                        break
            except Exception:
                b64_data = None

            if not b64_data:
                # Some SDK builds expose response.binary or response.text; try fallbacks
                possible = getattr(response, "binary", None) or getattr(response, "text", None)
                if isinstance(possible, (bytes, bytearray)):
                    self.logger.info("Successfully generated speech with Gemini TTS (binary field)")
                    return bytes(possible)
                self.logger.error("No audio data received from Gemini TTS response")
                return None

            audio_bytes = base64.b64decode(b64_data)
            self.logger.info(f"Successfully generated speech with Gemini TTS: {text[:50]}...")
            return audio_bytes

        except Exception as e:
            self.logger.error(f"Error generating speech with Gemini TTS: {str(e)}")
            return None

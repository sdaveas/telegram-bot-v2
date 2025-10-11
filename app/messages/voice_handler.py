import os
import base64
import google.generativeai as genai
from app.logger import setup_logger

class VoiceHandler:
    def __init__(self):
        """Initialize the voice handler with Gemini"""
        self.logger = setup_logger()

        # Configure Gemini API
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            self.logger.error("GEMINI_API_KEY environment variable is not set")
            raise ValueError("GEMINI_API_KEY environment variable is not set")

        genai.configure(api_key=api_key)

        # Use Gemini 1.5 Flash for audio transcription
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.logger.info("Voice handler initialized with Gemini 2.5 Flash")

    async def transcribe_voice(self, voice_bytes: bytes) -> str:
        """
        Transcribe a voice message using Gemini's multimodal capabilities
        """
        try:
            # Convert audio bytes to base64
            audio_base64 = base64.b64encode(voice_bytes).decode('utf-8')

            # Create the prompt for transcription
            prompt = """Please transcribe the following audio.
            The audio contains Greek speech with some English technical terms.
            Please preserve any English words exactly as spoken and transcribe the Greek text properly.
            Return ONLY the transcription, no additional text or explanation."""

            # Prepare the content with audio data
            response = self.model.generate_content([
                prompt,
                {
                    "mime_type": "audio/ogg",
                    "data": audio_base64
                }
            ])

            # Get the transcription
            transcript = response.text.strip()

            self.logger.info(f"Successfully transcribed voice message using Gemini: {transcript[:100]}...")
            return transcript

        except Exception as e:
            self.logger.error(f"Error transcribing voice message with Gemini: {str(e)}")
            # Fallback to empty string if transcription fails
            return "Could not transcribe audio"


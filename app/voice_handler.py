import os
import tempfile
from vosk import Model, KaldiRecognizer
import json
import subprocess
from .logger import setup_logger

class VoiceHandler:
    def __init__(self):
        """Initialize the voice handler with Vosk"""
        self.logger = setup_logger()

        # Create models directory if it doesn't exist
        os.makedirs('models', exist_ok=True)

        # Download Greek model if not already present
        self.model_name = "vosk-model-el-gr-0.7"
        self.model_path = os.path.join('models', self.model_name)
        if not os.path.exists(self.model_path):
            self.logger.info("Downloading Greek Vosk model...")
            model_zip = os.path.join('models', f"{self.model_name}.zip")
            subprocess.run(["wget", f"https://alphacephei.com/vosk/models/{self.model_name}.zip", "-O", model_zip])
            subprocess.run(["unzip", model_zip, "-d", "models"])
            subprocess.run(["rm", model_zip])
        self.model = Model(self.model_path)
        self.logger.info("Voice handler initialized with Vosk (Greek model)")

    async def transcribe_voice(self, voice_bytes: bytes) -> str:
        """
        Transcribe a voice message using Vosk
        """
        try:
            # Save the voice message to a temporary file
            with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as temp_ogg:
                temp_ogg.write(voice_bytes)
                temp_ogg_path = temp_ogg.name

            # Convert OGG to WAV using ffmpeg
            temp_wav_path = temp_ogg_path + '.wav'
            subprocess.run([
                'ffmpeg', '-i', temp_ogg_path,
                '-ar', '16000',  # Sample rate
                '-ac', '1',      # Mono
                '-f', 'wav',     # WAV format
                temp_wav_path
            ], capture_output=True)

            # Process with Greek model
            with open(temp_wav_path, 'rb') as wav:
                rec = KaldiRecognizer(self.model, 16000)
                # Process audio in chunks
                while True:
                    data = wav.read(4000)
                    if len(data) == 0:
                        break
                    rec.AcceptWaveform(data)

                # Get final result
                result = json.loads(rec.FinalResult())
                transcript = result.get('text', '')

            # Clean up temporary files
            os.unlink(temp_ogg_path)
            os.unlink(temp_wav_path)

            self.logger.info(f"Successfully transcribed voice message: {transcript[:100]}...")
            return transcript

        except Exception as e:
            self.logger.error(f"Error transcribing voice message: {str(e)}")
            # Clean up temporary files if they exist
            for path in [temp_ogg_path, temp_wav_path]:
                if 'path' in locals() and os.path.exists(path):
                    os.unlink(path)
            raise e

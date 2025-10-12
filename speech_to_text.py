import os

from openai import OpenAI


def transcribe_audio(audio_file_path):
    """
    Transcribe an audio file using OpenAI's Whisper API.

    Args:
        audio_file_path (str): Path to the audio file to transcribe

    Returns:
        str: The transcribed text
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    try:
        with open(audio_file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_file)
            return transcript.text
    except Exception as e:
        print(f"Error during transcription: {str(e)}")
        return None


def main():
    # Example usage
    audio_file_path = "path_to_your_audio_file.mp3"  # Replace with your audio file

    if not os.getenv("OPENAI_API_KEY"):
        print("Please set the OPENAI_API_KEY environment variable")
        return

    result = transcribe_audio(audio_file_path)
    if result:
        print("Transcription:")
        print(result)


if __name__ == "__main__":
    main()

from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv
import os

from pyht import Client
from pyht.client import TTSOptions

load_dotenv()





def text_to_audio_elevenlabs(text, output_path="output/audio/output.mp3"):
    elevenlabs_api_key = os.getenv('ELEVENLABS_API_KEY')
    elevenlabs = ElevenLabs(api_key=elevenlabs_api_key)
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Convert text to speech
    audio_stream = elevenlabs.text_to_speech.convert(
        voice_id="JBFqnCBsd6RMkjVDRZzb",
        output_format="mp3_44100_128",
        text=text,
        model_id="eleven_multilingual_v2",
    )

    # Save to specified path
    with open(output_path, "wb") as f:
        for chunk in audio_stream:
            f.write(chunk)

    return output_path


def text_to_audio_playht(text, output_path="output/audio/output.wav"):
    # Load credentials
    USER_ID = os.getenv('PLAY_HT_USER_ID')
    SECRET_KEY = os.getenv('PLAY_HT_API_KEY')

    # Validate credentials
    if not USER_ID or not SECRET_KEY:
        print("Error: Missing PLAY_HT_USER_ID or PLAY_HT_API_KEY in environment variables")
        return None

    try:
        client = Client(user_id=USER_ID, api_key=SECRET_KEY)
        print("Connected to Play.ht. Generating Audio...")

        # Voice manifest URL
        voice_manifest_url = "s3://voice-cloning-zero-shot/775ae416-49bb-4fb6-bd45-740f205d20a1/jennifersaad/manifest.json"

        # TTS options
        options = TTSOptions(voice=voice_manifest_url)

        # Ensure output folder exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Generate audio and save
        with open(output_path, "wb") as audio_file:
            for chunk in client.tts(text, options, voice_engine='PlayDialog-http'):
                audio_file.write(chunk)

        print(f"Audio generated and saved as {output_path}")
        return output_path

    except Exception as e:
        print(f"Error generating audio: {e}")
        return None
    


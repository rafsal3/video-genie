import assemblyai as aai
from dotenv import load_dotenv
import os
import json

load_dotenv()
assemblyai_api_key = os.getenv('ASSEMBLYAI_API_KEY')

aai.settings.api_key = assemblyai_api_key


def speech_to_text_assemblyai(audio_file, output_file="transcript.json"):
    # Configure transcription settings
    config = aai.TranscriptionConfig(
        word_boost=None,       # Add keywords to boost recognition accuracy (optional)
        boost_param=None,
        speaker_labels=False,  # Enable speaker labels if needed
        punctuate=True,        # Add punctuation to the transcription
        format_text=True       # Format text for readability
    )

    transcriber = aai.Transcriber(config=config)

    try:
        # Perform transcription
        transcript = transcriber.transcribe(audio_file)

        if transcript.status == aai.TranscriptStatus.error:
            raise Exception(f"Transcription failed: {transcript.error}")

        # Collect transcription result: text + individual words with timestamps
        transcription_result = {
            "text": transcript.text,
            "words": [
                {
                    "start": word.start,
                    "end": word.end,
                    "word": word.text
                }
                for word in transcript.words
            ],
        }

        # Ensure output folder exists
        dir_name = os.path.dirname(output_file)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)


        # Save transcription result to a JSON file
        with open(output_file, 'w') as json_file:
            json.dump(transcription_result, json_file, indent=4)

        print("Transcript saved successfully.")
        return output_file

    except Exception as e:
        raise RuntimeError(f"Error during transcription: {e}")



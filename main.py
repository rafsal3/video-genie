#  audio tools
from tools import text_to_audio_elevenlabs

# text tools
from tools import speech_to_text_assemblyai

# image tools
from tools import download_image_unsplash
from tools import download_image_google
from tools import download_gif_tenor

# output_file = text_to_audio_elevenlabs("water please", output_path="output/audio/01.mp3")
# print(f"Audio file saved as: {output_file}")
# audio_file = "output.mp3"
# transcript_file = speech_to_text_assemblyai(audio_file, output_file="output/transcript01.json")
# print(f"Transcript saved as: {transcript_file}")

# image_file = download_image_unsplash("youtube", output_path="output/images/youtube.jpg")
# print(f"Image file saved as: {image_file}")

# image_file = download_image_google("youtubers", output_path="output/images/youtube.jpg")
# path = download_gif_tenor("cat", output_path="output/gifs/cat.mp4")
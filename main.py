#  audio tools
from tools import text_to_audio_elevenlabs

# text tools
from tools import speech_to_text_assemblyai

# image tools
from tools import download_image_unsplash
from tools import download_image_google
from tools import download_gif_tenor

# video tools
from tools import create_text_video

# output_file = text_to_audio_elevenlabs("water please", output_path="output/audio/01.mp3")
# print(f"Audio file saved as: {output_file}")
# audio_file = "output.mp3"
# transcript_file = speech_to_text_assemblyai(audio_file, output_file="output/transcript01.json")
# print(f"Transcript saved as: {transcript_file}")

# image_file = download_image_unsplash("youtube", output_path="output/images/youtube.jpg")
# print(f"Image file saved as: {image_file}")

# image_file = download_image_google("youtubers", output_path="output/images/youtube.jpg")
# path = download_gif_tenor("cat", output_path="output/gifs/cat.mp4")

lee = create_text_video(
        text="long_text reveal by word effect",
        output_path="output/long_text_reveal.mp4",
        video_format="long",
        effect_type='reveal_by_word',
        font_color=(255, 255, 255),
        bg_color=(10, 20, 40),
        effect_duration=2.5,
        hold_duration=4,
        fade_out_duration=1.5
    )
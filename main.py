#  audio tools
from tools import text_to_audio_elevenlabs

# text tools
from tools import speech_to_text_assemblyai
from tools import generate_script

# image tools
from tools import download_image_unsplash
from tools import download_image_google
from tools import download_gif_tenor

# video tools
from tools import create_text_video
from tools import text_to_sentences_json
from tools import json_to_script_text


# script_text = json_to_script_text("output/scripts/ai_script.json")
# print("Narration text:\n", script_text)
# output_file = text_to_audio_elevenlabs(script_text, output_path="output/audio/01.mp3")
# print(f"Audio file saved as: {output_file}")

audio_file = "output/audio/01.mp3"
transcript_file = speech_to_text_assemblyai(audio_file)
# print(f"Transcript saved as: {transcript_file}")

# image_file = download_image_unsplash("instagram", output_path="output/images/instagram.jpg")
# print(f"Image file saved as: {image_file}")

# image_file = download_image_google("youtubers", output_path="output/images/youtubers.jpg")
# path = download_gif_tenor("cat", output_path="output/gifs/cat.mp4")

# lee = create_text_video(
#         text="long text reveal by word effect with different font and background colors",
#         output_path="output/videos/long_text_reveal.mp4",
#         video_format="long",
#         effect_type='reveal_by_word',
#         effect_duration=2.5,
#         hold_duration=4,
#         fade_out_duration=1.5,
#         font_color=(0, 0, 0),  
#         bg_color=(255, 255, 255),
#         font_path="fonts/Roboto-bold.ttf",


#     )
# topic = "The future of AI in education"
# output = generate_script(topic, "output/scripts/ai_script.json")
# print("Generated JSON:\n", output)

# script_text = json_to_script_text("output/scripts/ai_script.json")
# print("Narration text:\n", script_text)

# sentences_json = text_to_sentences_json(script_text )
# print("Sentences JSON:\n", sentences_json)
#  audio tools
from tools import text_to_audio_elevenlabs

# text tools
from tools import speech_to_text_assemblyai
from tools import generate_script
from tools import generate_assets
from tools import map_assets_to_sentences

# image tools
from tools import download_image_unsplash
from tools import download_image_google
from tools import download_gif_tenor

# video tools
from tools import create_text_video
from tools import words_to_sentances
from tools import json_to_script_text
from tools import generate_assets_from_json
from tools import render_video


# agent tools
from tools import generate_assets_from_json



# script_text = json_to_script_text("output/scripts/ai_script.json")
# print("Narration text:\n", script_text)


# output_file = text_to_audio_elevenlabs(script_text, output_path="output/audio/01.mp3")
# print(f"Audio file saved as: {output_file}")

# audio_file = "output/audio/01.mp3"
# transcript_file = speech_to_text_assemblyai(audio_file)
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

# assets = generate_assets("sentences.json")
# print("Generated Assets:", assets)


# output_file = map_assets_to_sentences(sentence_path='sentences.json', asset_path='asset.json')
# print("Mapped JSON saved at:", output_file)

# render_video("mapped.json")

if __name__ == "__main__":

    #  1. Generate a script based on a topic
    # topic = "charlie chaplin"
    # output = generate_script(topic, "output/scripts/script.json")
    # print("Generated JSON:\n", output)

    # 2. Convert the script to narration text
    # script_text = json_to_script_text("output/scripts/script.json")
    # print("Narration text:\n", script_text)

    # 3. Convert the narration text to audio
    # audio_path = text_to_audio_elevenlabs(script_text, output_path="output/audio/01.mp3")
    # print(f"Audio file saved as: {audio_path}")

    # 4. Convert the audio to transcript
    # audio_file = "output/audio/01.mp3"
    # transcript_file = speech_to_text_assemblyai(audio_file, output_file="output/transcript/transcript.json")
    # print(f"Transcript saved as: {transcript_file}")

    # 5. convert the transcript to sentences transcript
    # transcript_file = "output/transcript/transcript.json"
    # sentences_json = words_to_sentances(transcript_file, output_path="output/transcript/sentences.json")
    # print("Sentences JSON:\n", sentences_json)

    # 6. Generate assets based on the sentences
    # sentences_json = "output/transcript/sentences.json"
    # assets = generate_assets(sentences_json, output_path="output/assets/asset.json")
    # print("Generated Assets:", assets)

    # 7. Map assets to sentences
    sentence_path = "output/transcript/sentences.json"
    asset_path = "output/assets/asset.json"
    output_file = map_assets_to_sentences(sentence_path, asset_path, output_path="output/render/mapped.json")
    print("Mapped JSON saved at:", output_file)

    # 8. Generate assets from JSON
    json_path = "output/render/mapped.json"
    generate_assets_from_json(json_path)

    # 9. Render the final video
    mapped_json_path = "output/render/mapped.json"
    background_image_path = "background.jpg"
    output_video_path = "output/render/final.mp4"
    audio_path = "output/audio/01.mp3"
    render_video(mapped_json_path,
                 background_image_path=background_image_path,
                 output_video_path=output_video_path,
                 audio_path=audio_path)

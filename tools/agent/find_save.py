import json
import os

from tools import download_gif_tenor, download_image_google, download_image_unsplash
from tools import create_text_video

def load_mapped_json(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def prepare_folders():
    for folder in ['output/image', 'output/gif', 'output/text']:
        os.makedirs(folder, exist_ok=True)

def calculate_text_durations(start, end):
    total_seconds = (end - start) / 1000
    effect_duration = total_seconds * 0.25  # 25% for reveal effect
    hold_duration = total_seconds * 0.5     # 50% hold
    fade_out_duration = total_seconds * 0.25 # 25% fade
    return effect_duration, hold_duration, fade_out_duration


def process_item(item):
    order_id = item['order_id']
    keyword = item['text']
    type_ = item['type']
    
    if type_ == 'image':
        output_path = f"output/image/{order_id}.jpg"
        # Try Unsplash first
        path = download_image_unsplash(keyword, output_path)
        if path is None:
            path = download_image_google(keyword, output_path)
        return path
    
    elif type_ == 'gif':
        output_path = f"output/gif/{order_id}.mp4"
        return download_gif_tenor(keyword, output_path)
    
    elif type_ == 'text':
        output_path = f"output/text/{order_id}.mp4"
        effect_duration, hold_duration, fade_out_duration = calculate_text_durations(item['start'], item['end'])
        return create_text_video(
            text=keyword,
            output_path=output_path,
            video_format="long",
            effect_type='reveal_by_word',
            effect_duration=effect_duration,
            hold_duration=hold_duration,
            fade_out_duration=fade_out_duration,
            font_color=(0, 0, 0),
            bg_color=(255, 255, 255),
            font_path="fonts/Roboto-bold.ttf"
        )

def process_by_type(mapped_json):
    # First images
    for item in sorted([i for i in mapped_json if i['type'] == 'image'], key=lambda x: x['order_id']):
        process_item(item)
    
    # Then gifs
    for item in sorted([i for i in mapped_json if i['type'] == 'gif'], key=lambda x: x['order_id']):
        process_item(item)
    
    # Then text
    for item in sorted([i for i in mapped_json if i['type'] == 'text'], key=lambda x: x['order_id']):
        process_item(item)


def generate_assets_from_json(json_path):
    mapped_json = load_mapped_json(json_path)
    prepare_folders()
    process_by_type(mapped_json)



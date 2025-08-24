import json
import numpy as np
from moviepy.editor import (VideoFileClip, ImageClip, AudioFileClip, 
                            CompositeVideoClip)

def apply_media_effects(clip):
    """
    Applies resizing to create margins and a camera shake effect.
    """
    # --- 1. Resize to fit with margins ---
    # Define screen and max media dimensions
    screen_w, screen_h = 1920, 1080
    max_media_w, max_media_h = 1200, 880 # Bounding box for margins

    # Calculate scale factor to fit inside the bounding box
    original_w, original_h = clip.size
    scale_factor = min(max_media_w / original_w, max_media_h / original_h)
    
    resized_clip = clip.resize(scale_factor)
    resized_w, resized_h = resized_clip.size

    # --- 2. Create camera shake effect ---
    # Shake parameters (you can tweak these)
    SHAKE_AMOUNT = 3  # Pixels of displacement
    SHAKE_FREQUENCY_X = 2 # How fast it shakes horizontally
    SHAKE_FREQUENCY_Y = 2 # How fast it shakes vertically (different for irregular motion)

    # Calculate the centered (x, y) position
    center_x = (screen_w - resized_w) / 2
    center_y = (screen_h - resized_h) / 2

    # Define a function that returns the position (x, y) at a given time 't'
    def shake_position(t):
        # Use sine waves for smooth, continuous motion
        dx = SHAKE_AMOUNT * np.sin(t * SHAKE_FREQUENCY_X * 2 * np.pi)
        dy = SHAKE_AMOUNT * np.cos(t * SHAKE_FREQUENCY_Y * 2 * np.pi) # Use cosine for y for more random movement
        return (center_x + dx, center_y + dy)

    # Apply the time-varying position
    return resized_clip.set_position(shake_position)


def render_video(mapped_json_path,
                 background_image_path="background.jpg",
                 output_video_path="output/render/final.mp4",
                 audio_path="output/audio/01.mp3"):

    # Load JSON
    with open(mapped_json_path, "r") as f:
        mapped = json.load(f)

    # Prepare all overlay clips
    overlay_clips = []
    if not mapped:
        print("JSON file is empty. Cannot render video.")
        return
        
    total_duration_ms = mapped[-1]["end"]
    total_duration_sec = total_duration_ms / 1000

    for item in mapped:
        start_sec = item["start"] / 1000
        end_sec = item["end"] / 1000
        duration = end_sec - start_sec
        order_id = item["order_id"]
        clip_type = item["type"]
        
        clip = None # Initialize clip to None

        if clip_type == "text":
            clip_path = f"output/text/{order_id}.mp4"
            clip = (VideoFileClip(clip_path)
                    .subclip(0, duration)
                    .set_start(start_sec)
                    .set_position("center")) # Text remains centered without effects

        elif clip_type == "image":
            clip_path = f"output/image/{order_id}.jpg"
            img_clip = ImageClip(clip_path).set_duration(duration)
            # Apply resizing for margins and the shake effect
            clip = apply_media_effects(img_clip).set_start(start_sec)
            
        elif clip_type == "gif":
            clip_path = f"output/gif/{order_id}.mp4"
            gif_clip = VideoFileClip(clip_path)
            # Loop the GIF to fill the required duration
            looped_gif = gif_clip.loop(duration=duration)
            # Apply resizing for margins and the shake effect
            clip = apply_media_effects(looped_gif).set_start(start_sec)
            
        else:
            continue

        overlay_clips.append(clip)

    # --- Composition ---
    background_clip = ImageClip(background_image_path, duration=total_duration_sec).resize((1920, 1080))
    
    final_video = CompositeVideoClip([background_clip] + overlay_clips)

    # --- Finalizing with Audio ---
    audio = AudioFileClip(audio_path)
    
    final_duration = min(final_video.duration, audio.duration)
    
    final_video = final_video.set_duration(final_duration)
    final_video = final_video.set_audio(audio.set_duration(final_duration))

    # --- Export ---
    final_video.write_videofile(output_video_path, fps=30, codec="libx264", audio_codec="aac")
    print("Video rendered successfully!")

# Example usage:
# render_video("mapped.json")
import os
import pygame
import shutil
import random
from moviepy.editor import ImageSequenceClip
from typing import Tuple, Optional, List

# For a better experience, create a file named `requirements.txt` with:
# pygame==2.5.2
# moviepy==1.0.3

# Initialize Pygame globally, ONCE.
os.environ['SDL_VIDEODRIVER'] = 'dummy' 
pygame.init()

# ... (The VIBRANT_COLORS list and TextRenderer class remain unchanged) ...
VIBRANT_COLORS = [
    (82, 183, 255), (255, 94, 94), (94, 255, 114),
    (255, 187, 85), (190, 94, 255), (255, 94, 219), (94, 255, 247),
]
Color = Tuple[int, int, int]


class TextRenderer:
    """
    Handles the rendering of text onto Pygame surfaces.
    This class is responsible for text wrapping, font management, and drawing.
    """
    def __init__(self,
                 resolution: Tuple[int, int],
                 bg_color: Color,
                 font_color: Color,
                 font_path: Optional[str] = None,
                 margin_percent: float = 0.1):
        self.resolution = resolution
        self.bg_color = bg_color
        self.font_color = font_color
        self.font_path = font_path
        self.max_text_width = resolution[0] * (1 - 2 * margin_percent)
        self._font_cache = {}

        if self.font_path and not os.path.exists(self.font_path):
            raise FileNotFoundError(f"Font file not found at: {self.font_path}")

    def _get_font(self, size: int) -> pygame.font.Font:
        if size not in self._font_cache:
            self._font_cache[size] = pygame.font.Font(self.font_path, size)
        return self._font_cache[size]

    def _wrap_text(self, text: str, font: pygame.font.Font) -> List[str]:
        lines = []
        words = text.split(' ')
        current_line = ""
        for word in words:
            if not current_line:
                test_line = word
            else:
                test_line = current_line + " " + word
            
            if font.size(test_line)[0] <= self.max_text_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        lines.append(current_line)
        return lines

    def render_frame(self,
                     text: str,
                     font_size: int,
                     text_align: str = 'center',
                     v_align: str = 'middle',
                     alpha: int = 255) -> pygame.Surface:
        surface = pygame.Surface(self.resolution)
        surface.fill(self.bg_color)
        
        if not text.strip() or font_size <= 0:
            return surface

        font = self._get_font(font_size)
        lines = self._wrap_text(text, font)
        
        line_surfaces = []
        total_height = 0
        for line in lines:
            line_surf = font.render(line, True, self.font_color)
            line_surf.set_alpha(alpha)
            line_surfaces.append(line_surf)
            total_height += line_surf.get_height()

        if v_align == 'top':
            y_offset = int(self.resolution[1] * 0.1)
        elif v_align == 'bottom':
            y_offset = self.resolution[1] - total_height - int(self.resolution[1] * 0.1)
        else: # 'middle'
            y_offset = (self.resolution[1] - total_height) // 2

        for line_surf in line_surfaces:
            if text_align == 'left':
                x_offset = int(self.resolution[0] * 0.1)
            elif text_align == 'right':
                x_offset = self.resolution[0] - line_surf.get_width() - int(self.resolution[0] * 0.1)
            else: # 'center'
                x_offset = (self.resolution[0] - line_surf.get_width()) // 2
            
            surface.blit(line_surf, (x_offset, y_offset))
            y_offset += line_surf.get_height()

        return surface

def _calculate_dynamic_font_size(text: str) -> int:
    """Calculate a dynamic base font size based on text length."""
    length = len(text)
    if length <= 3: return 350
    if length <= 5: return 300
    if length <= 10: return 250
    if length <= 20: return 200
    if length <= 50: return 150
    if length <= 100: return 120
    return 100

def create_text_video(
    text: str,
    output_path: str,
    video_format: str = "long",
    effect_type: str = 'reveal_by_word',
    font_color: Optional[Color] = None,
    bg_color: Color = (0, 0, 0),
    font_path: Optional[str] = None,
    font_size: Optional[int] = None,
    text_align: str = 'center',
    v_align: str = 'middle',
    effect_duration: float = 1.0,
    hold_duration: float = 3.0,
    fade_out_duration: float = 1.0,
    fps: int = 24,
    temp_folder: str = "temp_frames"
    ) -> str:
    # ... (function signature and docstring remain the same) ...
    if video_format == "short":
        resolution = (1080, 1920)
    elif video_format == "long":
        resolution = (1920, 1080)
    else:
        raise ValueError("Invalid video format. Use 'long' or 'short'.")

    # Setup directories and paths
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    if os.path.exists(temp_folder):
        shutil.rmtree(temp_folder)
    os.makedirs(temp_folder, exist_ok=True)
    
    # Use a try...finally block to ensure cleanup
    try:
        final_font_color = font_color if font_color else random.choice(VIBRANT_COLORS)
        base_font_size = font_size if font_size else _calculate_dynamic_font_size(text)
        
        renderer = TextRenderer(
            resolution=resolution,
            bg_color=bg_color,
            font_color=final_font_color,
            font_path=font_path
        )
        
        # ... (timing and frame generation logic is unchanged) ...
        total_duration = effect_duration + hold_duration + fade_out_duration
        total_frames = int(total_duration * fps)
        effect_frames = int(effect_duration * fps)
        hold_frames = int(hold_duration * fps)
        
        words = text.split(' ')
        frame_paths = []
        
        print(f"Generating {total_frames} frames for '{text[:30]}...'")

        for i in range(total_frames):
            current_time = i / fps
            text_to_render = text
            current_font_size = base_font_size
            alpha = 255

            if i < effect_frames:
                progress = current_time / effect_duration
                if effect_type == 'reveal_by_letter':
                    text_to_render = text[:int(len(text) * progress)]
                elif effect_type == 'reveal_by_word':
                    text_to_render = " ".join(words[:int(len(words) * progress)])
                elif effect_type == 'zoom':
                    current_font_size = int(base_font_size * (0.1 + progress * 0.9))
            
            elif i >= effect_frames + hold_frames:
                fade_progress = (current_time - effect_duration - hold_duration) / fade_out_duration
                alpha = int(255 * (1 - fade_progress))

            surface = renderer.render_frame(text=text_to_render, font_size=current_font_size,
                                            text_align=text_align, v_align=v_align, alpha=alpha)
            
            frame_path = os.path.join(temp_folder, f"frame_{i:05d}.png")
            pygame.image.save(surface, frame_path)
            frame_paths.append(frame_path)

        print("All frames generated. Assembling video with MoviePy...")
        clip = ImageSequenceClip(frame_paths, fps=fps)
        clip.write_videofile(output_path, codec="libx264", audio=False, logger='bar')
        
        print(f"\nSuccessfully created video: {output_path}")
        return output_path

    except Exception as e:
        print(f"An error occurred: {e}")
        raise
    finally:
        # Clean up ONLY the temporary files for this specific function call.
        if os.path.exists(temp_folder):
            shutil.rmtree(temp_folder)
        # REMOVED: pygame.quit() from here


# if __name__ == "__main__":
#     # --- EXAMPLE 1: Long-form video with a long paragraph and reveal effect ---
#     long_text = "In a major development, sources close to the investigation have revealed new details that could reshape the public's understanding of the case."
#     create_text_video(
#         text=long_text,
#         output_path="output/long_text_reveal.mp4",
#         video_format="long",
#         effect_type='reveal_by_word',
#         font_color=(255, 255, 255),
#         bg_color=(10, 20, 40),
#         effect_duration=2.5,
#         hold_duration=4,
#         fade_out_duration=1.5
#     )
    
#     # --- EXAMPLE 2: Short-form (vertical) video with a short phrase and zoom effect ---
#     create_text_video(
#         text="BREAKING",
#         output_path="output/short_text_zoom.mp4",
#         video_format="short",
#         effect_type='zoom',
#         font_color=None, # Let it pick a random vibrant color
#         bg_color=(255, 255, 255),
#         effect_duration=0.7,
#         hold_duration=2,
#         fade_out_duration=0.5
#     )

#     # --- EXAMPLE 3: Using a custom font, left alignment, and static effect ---
#     custom_font_path = "fonts/Roboto-Bold.ttf"
#     if os.path.exists(custom_font_path):
#         create_text_video(
#             text="Custom Font Example",
#             output_path="output/custom_font_static.mp4",
#             video_format="long",
#             effect_type='static',
#             font_path=custom_font_path,
#             font_size=150,
#             text_align='left',
#             v_align='top',
#             bg_color=(240, 240, 240),
#             font_color=(20, 20, 20),
#             hold_duration=4,
#             fade_out_duration=1
#         )
#     else:
#         print(f"\nSkipping Example 3: Custom font not found at '{custom_font_path}'.")
#         print("Please download a .ttf font and update the path to run this example.")

#     # ADDED: Quit pygame once the entire script is finished.
#     pygame.quit()
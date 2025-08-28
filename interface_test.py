import streamlit as st
import os
import json
import shutil
from PIL import Image
import cv2
from tools import (
    text_to_audio_elevenlabs,
    speech_to_text_assemblyai,
    generate_script,
    generate_assets,
    map_assets_to_sentences,
    words_to_sentances,
    json_to_script_text,
    render_video,
    generate_assets_from_json,
    download_gif_tenor,
    download_image_google,
    download_image_unsplash,
    create_text_video
)

# --- SETUP ---
st.set_page_config(layout="wide")
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)
st.title("Advanced Video Generation Pipeline 🎬")

# --- INITIALIZE SESSION STATE ---
if 'audio_ready' not in st.session_state:
    st.session_state.audio_ready = False
if 'sentences_ready' not in st.session_state:
    st.session_state.sentences_ready = False
if 'assets_ready' not in st.session_state:
    st.session_state.assets_ready = False
if 'assets_generated' not in st.session_state:
    st.session_state.assets_generated = False
if 'asset_status' not in st.session_state:
    st.session_state.asset_status = {}

# --- HELPER FUNCTIONS ---
def show_json_file(file_path, header):
    """Reads a JSON file and displays it in Streamlit."""
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            try:
                data = json.load(f)
                st.subheader(header)
                st.json(data)
            except (json.JSONDecodeError, FileNotFoundError):
                st.error(f"Error reading {file_path}. It might be empty or invalid.")
    else:
        st.warning(f"{file_path} not found.")

def get_asset_file_path(order_id, asset_type):
    """Get the expected file path for an asset"""
    if asset_type == 'image':
        return f"output/image/{order_id}.jpg"
    elif asset_type == 'gif':
        return f"output/gif/{order_id}.mp4"
    elif asset_type == 'text':
        return f"output/text/{order_id}.mp4"
    return None

def check_asset_exists(order_id, asset_type):
    """Check if asset file exists"""
    file_path = get_asset_file_path(order_id, asset_type)
    return os.path.exists(file_path) if file_path else False

def get_video_thumbnail(video_path):
    """Extract first frame from video as thumbnail"""
    try:
        cap = cv2.VideoCapture(video_path)
        ret, frame = cap.read()
        cap.release()
        if ret:
            # Convert BGR to RGB for PIL
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            return Image.fromarray(frame_rgb)
    except Exception as e:
        st.error(f"Error extracting thumbnail: {e}")
    return None

def regenerate_single_asset(order_id, text, asset_type, start_time=None, end_time=None):
    """Regenerate a single asset"""
    try:
        if asset_type == 'image':
            output_path = f"output/image/{order_id}.jpg"
            os.makedirs("output/image", exist_ok=True)
            # Try Google first, then Unsplash
            path = download_image_google(text, output_path)
            if path is None:
                path = download_image_unsplash(text, output_path)
            return path is not None

        elif asset_type == 'gif':
            output_path = f"output/gif/{order_id}.mp4"
            os.makedirs("output/gif", exist_ok=True)
            path = download_gif_tenor(text, output_path)
            return path is not None

        elif asset_type == 'text' and start_time is not None and end_time is not None:
            output_path = f"output/text/{order_id}.mp4"
            os.makedirs("output/text", exist_ok=True)

            # Calculate durations
            total_seconds = (end_time - start_time) / 1000
            effect_duration = total_seconds * 0.25
            hold_duration = total_seconds * 0.5
            fade_out_duration = total_seconds * 0.25

            path = create_text_video(
                text=text,
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
            return path is not None

    except Exception as e:
        st.error(f"Error regenerating asset {order_id}: {e}")
        return False

def display_asset_table_row(asset, mapped_json_path):
    """Display a single asset as a row in our table-like structure."""
    order_id = asset['order_id']
    text = asset['text']
    asset_type = asset['type']
    start_time = asset.get('start', 0)
    end_time = asset.get('end', 0)

    # Create a container for the row
    with st.container():
        # Use columns to structure the row
        col1, col2, col3 = st.columns((3, 2, 3))

        # --- Column 1: Asset Details ---
        with col1:
            st.markdown(f"**#{order_id} - {asset_type.upper()}**")

            # Status indicator
            file_path = get_asset_file_path(order_id, asset_type)
            asset_exists = check_asset_exists(order_id, asset_type)
            if asset_exists:
                st.success("✅ Ready")
            else:
                st.error("❌ Missing")

            st.text_area(f"Text/Query for {order_id}", value=text, key=f"text_display_{order_id}", height=100, disabled=True)
            duration = (end_time - start_time) / 1000
            st.write(f"**Duration:** {duration:.2f}s")

        # --- Column 2: Preview ---
        with col2:
            if asset_exists:
                try:
                    if asset_type == 'image':
                        if os.path.exists(file_path):
                            st.image(file_path, use_container_width=True)

                    elif asset_type in ['gif', 'text']:
                        if os.path.exists(file_path):
                            thumbnail = get_video_thumbnail(file_path)
                            if thumbnail:
                                st.image(thumbnail, caption="Preview", use_container_width=True)
                            # You can optionally add a full video player too
                            # st.video(file_path)

                except Exception as e:
                    st.error(f"Preview error: {e}")
            else:
                st.info("No preview available.")

        # --- Column 3: Actions ---
        with col3:
            # Regenerate button
            if st.button(f"🔄 Regenerate", key=f"regen_{order_id}"):
                with st.spinner(f"Regenerating asset {order_id}..."):
                    success = regenerate_single_asset(order_id, text, asset_type, start_time, end_time)
                    if success:
                        st.success(f"Asset {order_id} regenerated!")
                        st.rerun()
                    else:
                        st.error(f"Failed to regenerate asset {order_id}")

            # File uploader for replacement
            uploaded_file = st.file_uploader(
                f"📤 Replace Asset #{order_id}",
                type=['jpg', 'jpeg', 'png', 'mp4'],
                key=f"upload_{order_id}",
            )

            if uploaded_file is not None:
                try:
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    st.success(f"Asset {order_id} replaced!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error replacing asset: {e}")

            # Edit text/query option in an expander
            with st.expander(f"✏️ Edit & Regenerate"):
                new_text = st.text_input(f"New text/query", value=text, key=f"edit_{order_id}")
                if st.button(f"Update", key=f"update_{order_id}"):
                    if new_text != text:
                        try:
                            # Update the JSON file
                            with open(mapped_json_path, 'r') as f:
                                data = json.load(f)

                            assets_list = data if isinstance(data, list) else data.get('mapped_assets', [])
                            for a in assets_list:
                                if a['order_id'] == order_id:
                                    a['text'] = new_text
                                    break

                            with open(mapped_json_path, 'w') as f:
                                json.dump(data, f, indent=2)

                            # Regenerate with new text
                            with st.spinner(f"Updating and regenerating asset {order_id}..."):
                                success = regenerate_single_asset(order_id, new_text, asset_type, start_time, end_time)
                                if success:
                                    st.success(f"Asset {order_id} updated!")
                                    st.rerun()
                                else:
                                    st.error(f"Failed to update asset {order_id}")
                        except Exception as e:
                            st.error(f"Error updating asset: {e}")
                    else:
                        st.warning("Text is unchanged.")

    # Add a divider after each row for better separation
    st.divider()

def display_asset_table(mapped_json_path):
    """Display assets in a table-like list structure with previews and management options."""
    if not os.path.exists(mapped_json_path):
        return

    with open(mapped_json_path, 'r') as f:
        mapped_data = json.load(f)

    st.subheader("🎨 Asset Management Table")

    # Create a header for our "table"
    header_cols = st.columns((3, 2, 3))
    with header_cols[0]:
        st.markdown("**Asset Details**")
    with header_cols[1]:
        st.markdown("**Preview**")
    with header_cols[2]:
        st.markdown("**Actions**")
    st.divider()

    assets = mapped_data if isinstance(mapped_data, list) else mapped_data.get('mapped_assets', [])

    # Loop through each asset and display it as a row
    for asset in assets:
        display_asset_table_row(asset, mapped_json_path)

# Function to reset state when starting a new generation
def reset_state():
    st.session_state.audio_ready = False
    st.session_state.sentences_ready = False
    st.session_state.assets_ready = False
    st.session_state.assets_generated = False
    st.session_state.asset_status = {}
    # Clean up old files if they exist to prevent using stale data
    for path in [audio_path, transcript_path, sentences_path, assets_path, mapped_path]:
        if os.path.exists(path):
            os.remove(path)

# --- UI FOR CHOOSING STARTING POINT ---
st.header("1. Choose Your Starting Point")
start_option = st.radio(
    "How would you like to begin?",
    ('Topic', 'Narration Text', 'Audio File', 'Manual Transcript', 'Ready Assets (Direct Render)'),
    horizontal=False,
    label_visibility="collapsed"
)

# Define paths
audio_path = f"{OUTPUT_DIR}/audio/narration.mp3"
transcript_path = f"{OUTPUT_DIR}/transcript/transcript.json"
sentences_path = f"{OUTPUT_DIR}/transcript/sentences.json"
assets_path = f"{OUTPUT_DIR}/assets/asset.json"
mapped_path = f"{OUTPUT_DIR}/render/mapped.json"
final_video_path = f"{OUTPUT_DIR}/render/final.mp4"

# ---------------------------------------------------
# STEP 1: Process Input and Prepare Audio/Transcript
# ---------------------------------------------------

if start_option == 'Topic':
    st.subheader("Generate everything from a single topic")
    topic = st.text_input("Enter a topic", "The history of the Eiffel Tower")
    if st.button("Generate Video from Topic"):
        reset_state()
        with st.spinner("1. Generating script... 📜"):
            script_path = f"{OUTPUT_DIR}/scripts/script.json"
            os.makedirs(os.path.dirname(script_path), exist_ok=True)
            script_json_output = generate_script(topic, script_path)
            script_text = json_to_script_text(script_path)
            st.success("Script generated!")
            st.json(script_json_output)
        with st.spinner("2. Generating narration audio... 🎤"):
            os.makedirs(os.path.dirname(audio_path), exist_ok=True)
            text_to_audio_elevenlabs(script_text, output_path=audio_path)
            st.success("Audio generated!")
            st.session_state.audio_ready = True

elif start_option == 'Narration Text':
    st.subheader("Provide your own script to generate the video")
    narration_text = st.text_area("Enter your script here", height=200)
    if st.button("Generate Video from Text") and narration_text:
        reset_state()
        with st.spinner("1. Generating narration audio... 🎤"):
            os.makedirs(os.path.dirname(audio_path), exist_ok=True)
            text_to_audio_elevenlabs(narration_text, output_path=audio_path)
            st.success("Audio generated!")
            st.session_state.audio_ready = True

elif start_option == 'Audio File':
    st.subheader("Upload your own narration audio file")
    uploaded_audio = st.file_uploader("Choose an audio file", type=['mp3', 'wav', 'm4a'])
    if uploaded_audio is not None:
        if st.button("Generate Video from Audio"):
            reset_state()
            with st.spinner("1. Saving uploaded audio... 🎧"):
                os.makedirs(os.path.dirname(audio_path), exist_ok=True)
                with open(audio_path, "wb") as f:
                    f.write(uploaded_audio.getbuffer())
                st.success("Audio file saved!")
                st.session_state.audio_ready = True

elif start_option == 'Manual Transcript':
    st.subheader("Upload audio and provide its timed transcript JSON")
    st.info("The transcript's timestamps must correspond to the uploaded audio file.")

    uploaded_audio = st.file_uploader("1. Upload the corresponding audio file", type=['mp3', 'wav', 'm4a'])

    placeholder_transcript = json.dumps({
        "text": "If you've been scrolling...",
        "words": [
            {"start": 80, "end": 200, "word": "If"},
            {"start": 200, "end": 480, "word": "you've"},
        ]}, indent=4)
    manual_transcript_json = st.text_area("2. Paste your transcript JSON here", height=250, value=placeholder_transcript)

    if st.button("Generate from Manual Transcript"):
        if uploaded_audio is not None and manual_transcript_json:
            reset_state()
            try:
                # Validate and save the transcript
                json_data = json.loads(manual_transcript_json)
                os.makedirs(os.path.dirname(transcript_path), exist_ok=True)
                with open(transcript_path, "w") as f:
                    json.dump(json_data, f, indent=4)

                # Save the audio file
                os.makedirs(os.path.dirname(audio_path), exist_ok=True)
                with open(audio_path, "wb") as f:
                    f.write(uploaded_audio.getbuffer())

                st.success("Audio and manual transcript saved successfully!")
                st.session_state.audio_ready = True
            except json.JSONDecodeError:
                st.error("Invalid JSON format. Please check your transcript input.")
        else:
            st.warning("Please upload an audio file and provide the transcript JSON.")

elif start_option == 'Ready Assets (Direct Render)':
    st.subheader("Upload audio file and mapped assets JSON for direct rendering")
    st.info("Use this option when you already have your audio file and mapped assets JSON ready.")

    uploaded_audio = st.file_uploader("1. Upload the audio file", type=['mp3', 'wav', 'm4a'], key="direct_audio")

    placeholder_mapped = json.dumps([
        {
            "order_id": 1,
            "text": "ARCHITECTURAL MARVELS",
            "type": "gif",
            "start": 320,
            "end": 1039
        },
        {
            "order_id": 2,
            "text": "HIDDEN STORIES",
            "type": "image",
            "start": 1040,
            "end": 5839
        }
    ], indent=4)

    mapped_assets_json = st.text_area("2. Paste your mapped assets JSON here", height=300, value=placeholder_mapped)

    if st.button("Load Assets for Direct Render"):
        if uploaded_audio is not None and mapped_assets_json:
            reset_state()
            try:
                # Validate and save the mapped assets
                json_data = json.loads(mapped_assets_json)
                os.makedirs(os.path.dirname(mapped_path), exist_ok=True)
                with open(mapped_path, "w") as f:
                    json.dump(json_data, f, indent=4)

                # Save the audio file
                os.makedirs(os.path.dirname(audio_path), exist_ok=True)
                with open(audio_path, "wb") as f:
                    f.write(uploaded_audio.getbuffer())

                st.success("Audio and mapped assets loaded!")
                st.session_state.audio_ready = True
                st.session_state.sentences_ready = True
                st.session_state.assets_ready = True

            except json.JSONDecodeError:
                st.error("Invalid JSON format. Please check your mapped assets input.")
        else:
            st.warning("Please upload an audio file and provide the mapped assets JSON.")

# ---------------------------------------------------
# STEP 2: Transcription and Sentence Splitting
# ---------------------------------------------------
if st.session_state.audio_ready and start_option != 'Ready Assets (Direct Render)':
    st.header("2. Processing Audio")
    st.audio(audio_path)
    if not st.session_state.sentences_ready:
        with st.spinner("Processing transcript and splitting sentences... ✍️"):
            # If transcript doesn't exist (i.e., wasn't manually provided), generate it
            if not os.path.exists(transcript_path):
                st.info("Generating transcript from audio...")
                os.makedirs(os.path.dirname(transcript_path), exist_ok=True)
                speech_to_text_assemblyai(audio_path, output_file=transcript_path)

            # Now, create sentences from the transcript (whether provided or generated)
            words_to_sentances(transcript_path, output_path=sentences_path)
            st.success("Transcription and sentence splitting complete!")
            st.session_state.sentences_ready = True

    show_json_file(transcript_path, "Visualizing Transcript")
    show_json_file(sentences_path, "Visualizing Sentences")

# ---------------------------------------------------
# STEP 3: Asset Generation
# ---------------------------------------------------
if st.session_state.sentences_ready and start_option != 'Ready Assets (Direct Render)':
    st.header("3. Asset Generation")
    asset_option = st.radio(
        "How do you want to create the assets?",
        ('Automatically generate assets', 'Manually provide asset JSON'),
        horizontal=True
    )
    if asset_option == 'Automatically generate assets':
        if st.button("Generate Assets Automatically"):
            with st.spinner("Generating assets based on sentences... 🤖"):
                os.makedirs(os.path.dirname(assets_path), exist_ok=True)
                generate_assets(sentences_path, output_path=assets_path)
                st.success("Assets generated automatically!")
                st.session_state.assets_ready = True
    else: # Manual option
        placeholder_json = json.dumps({"assets":[
            { "order_id": 1, "text": "A happy cat", "type": "gif" },
            { "order_id": 2, "text": "Hello World!", "type": "text" }
        ]}, indent=4)
        manual_asset_json = st.text_area("Asset JSON", height=250, value=placeholder_json)
        if st.button("Use Manual Assets"):
            try:
                json_data = json.loads(manual_asset_json)
                os.makedirs(os.path.dirname(assets_path), exist_ok=True)
                with open(assets_path, "w") as f:
                    json.dump(json_data, f, indent=4)
                st.success("Manual asset JSON saved successfully!")
                st.session_state.assets_ready = True
            except json.JSONDecodeError:
                st.error("Invalid JSON format. Please check your input.")

    if st.session_state.assets_ready:
         show_json_file(assets_path, "Final Assets for Rendering")

# ---------------------------------------------------
# STEP 4: Asset File Generation & Preview
# ---------------------------------------------------
if st.session_state.assets_ready:
    st.header("4. Asset File Generation & Management")

    # First, map assets to sentences if we're not in direct render mode
    if start_option != 'Ready Assets (Direct Render)':
        if st.button("Map Assets to Sentences"):
            with st.spinner("Mapping assets to sentence timings... 🗺️"):
                os.makedirs(os.path.dirname(mapped_path), exist_ok=True)
                map_assets_to_sentences(sentences_path, assets_path, output_path=mapped_path)
                st.success("Assets mapped to sentences!")
                st.rerun()

    # Show asset generation options if mapped.json exists
    if os.path.exists(mapped_path):
        show_json_file(mapped_path, "Mapped Assets")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🚀 Generate All Asset Files", type="primary"):
                with st.spinner("Generating all asset files... This may take a while..."):
                    generate_assets_from_json(mapped_path)
                    st.success("All asset files generated!")
                    st.session_state.assets_generated = True
                    st.rerun()

        with col2:
            if st.button("🔄 Refresh Asset Status"):
                st.rerun()

        # Always show the asset table
        st.markdown("---")
        display_asset_table(mapped_path)

# ---------------------------------------------------
# STEP 5: Final Video Assembly
# ---------------------------------------------------
if st.session_state.assets_ready and os.path.exists(mapped_path):
    st.header("5. Final Video Assembly")

    # Check how many assets are ready
    with open(mapped_path, 'r') as f:
        mapped_data = json.load(f)

    assets = mapped_data if isinstance(mapped_data, list) else mapped_data.get('mapped_assets', [])
    ready_count = sum(1 for asset in assets if check_asset_exists(asset['order_id'], asset['type']))
    total_count = len(assets)

    st.info(f"Asset Status: {ready_count}/{total_count} assets ready")

    if ready_count > 0:
        if st.button("🎬 Render Final Video", type="primary"):
            with st.spinner("Rendering the final video... This may take a moment."):
                try:
                    render_video(mapped_path, "background.jpg", final_video_path, audio_path)
                    st.success("Final video rendered!")

                    st.video(final_video_path)
                    with open(final_video_path, "rb") as video_file:
                        st.download_button(
                            label="📥 Download Final Video",
                            data=video_file,
                            file_name="final_video.mp4",
                            mime="video/mp4"
                        )
                except Exception as e:
                    st.error(f"Error rendering video: {e}")
    else:
        st.warning("⚠️ No assets are ready. Please generate or upload asset files first.")
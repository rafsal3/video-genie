import streamlit as st
import os
import json
from tools import (
    text_to_audio_elevenlabs,
    speech_to_text_assemblyai,
    generate_script,
    generate_assets,
    map_assets_to_sentences,
    words_to_sentances,
    json_to_script_text,
    render_video,
    generate_assets_from_json
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

# --- HELPER FUNCTION TO VISUALIZE JSON ---
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

# --- UI FOR CHOOSING STARTING POINT ---
st.header("1. Choose Your Starting Point")
start_option = st.radio(
    "How would you like to begin?",
    ('Topic', 'Narration Text', 'Audio File', 'Manual Transcript'), # NEW OPTION ADDED
    horizontal=True,
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
# Function to reset state when starting a new generation
def reset_state():
    st.session_state.audio_ready = False
    st.session_state.sentences_ready = False
    st.session_state.assets_ready = False
    # Clean up old files if they exist to prevent using stale data
    for path in [audio_path, transcript_path, sentences_path, assets_path, mapped_path]:
        if os.path.exists(path):
            os.remove(path)


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

# --- NEW OPTION LOGIC ---
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


# ---------------------------------------------------
# STEP 2: Transcription and Sentence Splitting
# ---------------------------------------------------
if st.session_state.audio_ready:
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
if st.session_state.sentences_ready:
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
# STEP 4: Final Video Assembly
# ---------------------------------------------------
if st.session_state.assets_ready:
    st.header("4. Final Video Assembly")
    if st.button("Render Final Video 🎥"):
        with st.spinner("Mapping assets to sentence timings... 🗺️"):
            os.makedirs(os.path.dirname(mapped_path), exist_ok=True)
            map_assets_to_sentences(sentences_path, assets_path, output_path=mapped_path)
            st.success("Assets mapped!")
        
        with st.spinner("Downloading/creating asset files (images, gifs, etc.)... 🖼️"):
            generate_assets_from_json(mapped_path)
            st.success("Asset files are ready!")

        with st.spinner("Rendering the final video... This may take a moment."):
            render_video(mapped_path, "background.jpg", final_video_path, audio_path)
            st.success("Final video rendered!")
            
            st.video(final_video_path)
            with open(final_video_path, "rb") as video_file:
                st.download_button(
                    label="Download Final Video",
                    data=video_file,
                    file_name="final_video.mp4",
                    mime="video/mp4"
                )
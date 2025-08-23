import os
from google import genai
from dotenv import load_dotenv
import json

from tools.utils import extract_json

# Load environment variables
load_dotenv()

# Initialize Gemini client
client = genai.Client()

def generate_script(
    text, 
    output_path="text.json", 
    system_instruction = (
    "Create a very short YouTube video script about the topic. "
    "Return only valid JSON as plain text with no markdown, no code blocks, no explanations. "
    "The JSON must be in the format: {\"script\": \"narration text here\"}. "
    "The 'script' value should contain only the narration text, no scene settings, visuals, or instructions."
    )

):
 
    
    prompt = f"{system_instruction}\nTopic: {text}"

    # Call Gemini API
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    
    # Extract JSON safely
    result_json = extract_json(response.text)

    # Ensure directory exists
    dir_name = os.path.dirname(output_path)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name)

    # Save to JSON file
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result_json, f, indent=2, ensure_ascii=False)
    
    return result_json


def generate_assets(
    input_path,
    output_path="asset.json",
    system_instruction = (
        "For each input sentence, create a very short representation suitable for a YouTube video asset. "
        "Return only a JSON object with two fields: 'text' and 'type'.\n"
        "- 'text' should be a concise keyword, phrase, or literal text to show on screen (1–3 words). "
        "- 'type' must be one of 'gif', 'image', or 'text'.\n"
        "- Use 'gif' or 'image' only if the sentence describes a concrete action, object, or scene that can be visualized. "
        "If the idea is abstract, conceptual, or cannot easily have a visual, use 'text'.\n"
        "- Do NOT repeat the original sentence. Focus on a short, visualizable idea or literal text.\n"
        "- Keep responses extremely short. Return only valid JSON, nothing else."
    )


):
    # Load the input JSON file
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    sentences = data.get("sentences", [])
    assets = []

    for idx, s in enumerate(sentences, start=1):
        sentence_text = s["sentence"]
        prompt = f"{system_instruction}\nSentence: {sentence_text}"

        # Call Gemini API
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        # Use your existing extract_json function to parse output
        asset_info = extract_json(response.text)

        # Add order_id, text, type only
        assets.append({
            "order_id": idx,
            "text": asset_info.get("text", ""),
            "type": asset_info.get("type", "text")
        })

    # Ensure directory exists
    dir_name = os.path.dirname(output_path)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name)

    # Save final JSON
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({"assets": assets}, f, indent=2, ensure_ascii=False)

    return {"assets": assets}

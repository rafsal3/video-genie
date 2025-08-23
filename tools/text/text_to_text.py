import os
from google import genai
from dotenv import load_dotenv
import json

from tools.text.text_tools import extract_json

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
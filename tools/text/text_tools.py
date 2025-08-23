import json
import re
import os

def extract_json(text):
    """
    Extract valid JSON from messy text safely.
    Tries direct load, then simple regex, then manual brace counting.
    """
    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try simple regex to find the first {...} block
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    # Manual brace counting fallback
    start = text.find("{")
    if start != -1:
        brace_count = 0
        for i, char in enumerate(text[start:], start=start):
            if char == "{":
                brace_count += 1
            elif char == "}":
                brace_count -= 1
                if brace_count == 0:
                    try:
                        return json.loads(text[start:i+1])
                    except json.JSONDecodeError:
                        break

    # If everything fails, return raw text
    return {"script": text.strip()}

def json_to_script_text(json_path):
    """
    Reads a JSON file and returns the 'script' value as plain text.
    
    Parameters:
        json_path (str): Path to the JSON file.
    
    Returns:
        str: The narration text from the 'script' key, or an empty string if missing.
    """
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"File not found: {json_path}")

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    return data.get("script", "").strip()


def text_to_sentences_json(text, output_path="sentences.json", split_on_comma=True):
    """
    Converts narration text into sentences (optionally splitting on commas) and saves as JSON.
    
    Parameters:
        text (str): The narration text.
        output_path (str): Path to save the JSON file.
        split_on_comma (bool): If True, also split sentences at commas.
    
    Returns:
        dict: A dictionary with sentences in 'script' key.
    """
    # Base sentence delimiters
    delimiters = r'[.!?]'
    if split_on_comma:
        delimiters = r'[.!?,]'  # Add comma as a delimiter if needed
    
    # Split using regex
    sentences = re.split(rf'(?<={delimiters})\s+', text.strip())
    sentences = [s.strip() for s in sentences if s.strip()]
    
    # Prepare JSON
    result_json = {"script": sentences}
    
    # Ensure directory exists
    dir_name = os.path.dirname(output_path)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name)
    
    # Save JSON
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result_json, f, indent=2, ensure_ascii=False)
    
    return result_json

def words_to_sentances(input_path, output_path="sentences.json"):
    # Load JSON from input path
    with open(input_path, "r") as f:
        data = json.load(f)

    words = data.get("words", [])
    sentences = []
    current_sentence = []
    start_time = None

    # Punctuation marks that indicate sentence break
    sentence_endings = (".", "?", "!", ",")

    for w in words:
        word_text = w["word"]
        if start_time is None:
            start_time = w["start"]

        current_sentence.append(word_text)

        # Check if the word ends a sentence (including comma)
        if word_text.endswith(sentence_endings):
            sentence_text = " ".join(current_sentence)
            sentences.append({
                "start": start_time,
                "end": w["end"],
                "sentence": sentence_text
            })
            current_sentence = []
            start_time = None

    # Handle leftover words (if any)
    if current_sentence:
        sentence_text = " ".join(current_sentence)
        sentences.append({
            "start": start_time,
            "end": words[-1]["end"],
            "sentence": sentence_text
        })

    result = {"sentences": sentences}

    # Ensure output directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Save the result JSON
    with open(output_path, "w") as f:
        json.dump(result, f, indent=4)

    print(f"Sentences saved to: {output_path}")
    return output_path

def map_assets_to_sentences(sentence_path, asset_path, output_path='mapped.json'):
    # Load sentences
    with open(sentence_path, 'r', encoding='utf-8') as f:
        sentences_data = json.load(f)
        sentences = sentences_data.get('sentences', [])
    
    # Load assets
    with open(asset_path, 'r', encoding='utf-8') as f:
        assets_data = json.load(f)
        assets = assets_data.get('assets', [])
    
    mapped_assets = []
    
    for i, asset in enumerate(assets):
        # Determine start
        if i < len(sentences):
            start = sentences[i]['start']
        else:
            start = sentences[-1]['start']  # fallback if more assets than sentences

        # Determine end
        if i + 1 < len(sentences):
            end = sentences[i+1]['start'] - 1
        else:
            end = sentences[-1]['end']  # last sentence keeps original end

        mapped_asset = {
            'order_id': asset['order_id'],
            'text': asset['text'],
            'type': asset['type'],
            'start': start,
            'end': end
        }
        mapped_assets.append(mapped_asset)
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True) if os.path.dirname(output_path) else None
    
    # Write mapped.json
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(mapped_assets, f, indent=4)
    
    return output_path





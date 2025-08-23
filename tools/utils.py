import json
import re

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
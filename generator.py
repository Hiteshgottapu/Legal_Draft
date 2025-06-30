import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

def gemini_extract_contract_fields(prompt_text):
    """
    Use Gemini API to extract contract fields from the prompt as JSON.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise Exception("Gemini API key not set. Please set GEMINI_API_KEY environment variable.")

    extraction_prompt = (
        "Extract the following fields from the user's prompt as a JSON object: "

        "party1 (employer/company), party2 (employee/intern), contract_type, position, start_date, duration, stipend, "
        "working_hours, location, supervisor, purpose, responsibilities, terms, payment_terms, benefits, confidentiality, "
        "termination, special_instructions. If a field is not present, return an empty string for it. "
        "Respond ONLY with a JSON object, no extra text.\n\nPrompt: " + prompt_text
    )
    headers = {"Content-Type": "application/json"}
    params = {"key": api_key}
    data = {
        "contents": [
            {"parts": [{"text": extraction_prompt}]}
        ]
    }
    # Use the same endpoint and payload style as generate_legal_text
    response = requests.post(GEMINI_API_URL, headers=headers, params=params, json=data, timeout=20)
    response.raise_for_status()
    result = response.json()
    try:
        text = result['candidates'][0]['content']['parts'][0]['text']
        if text.strip().startswith('```json'):
            text = text.strip().split('```json')[1].split('```')[0].strip()
        elif text.strip().startswith('```'):
            text = text.strip().split('```')[1].split('```')[0].strip()
        return text
    except Exception as e:
        raise Exception(f"Gemini API response parsing error: {e}\nRaw: {result}")# generator.py
# Handles LLM interaction (Gemini)



import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

def generate_legal_text(prompt, memory=None):
    """
    Calls Gemini API to generate legal text based on the prompt and memory.
    """
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return "[Error] Gemini API key not set. Please set GEMINI_API_KEY environment variable."

        # Compose the full prompt with memory/context if provided
        full_prompt = prompt
        if memory:
            full_prompt += f"\nContext: {memory}"

        headers = {"Content-Type": "application/json"}
        params = {"key": api_key}
        data = {
            "contents": [
                {"parts": [{"text": full_prompt}]}
            ]
        }
        response = requests.post(GEMINI_API_URL, headers=headers, params=params, json=data, timeout=20)
        response.raise_for_status()
        result = response.json()
        # Extract the generated text from the response
        text = result['candidates'][0]['content']['parts'][0]['text']
        # Remove disclaimer lines like 'this is a sample document...' or 'should be reviewed by an attorney...'
        import re
        disclaimer_patterns = [
            r"^okay, here's a draft.*?\*\*please.*?attorney.*?\*\*.*$",
            r"^this is a sample document.*$",
            r"^please remember.*attorney.*$",
            r"^note:.*attorney.*$",
            r"^disclaimer:.*$",
            r"^\*\*.*attorney.*\*\*$",
            r"^\*\*.*legal advice.*\*\*$",
            r"^\*.*attorney.*\*$",
            r"^\*.*legal advice.*\*$",
            r"^\*\*.*sample document.*\*\*$",
            r"^\*\*.*should be reviewed.*\*\*$",
            r"^\*\*.*complies with.*\*\*$",
            r"^\*\*.*california law.*\*\*$",
            r"^\*\*.*not legal advice.*\*\*$",
        ]
        lines = text.splitlines()
        filtered = []
        for line in lines:
            l = line.strip()
            if not any(re.match(pat, l, re.IGNORECASE) for pat in disclaimer_patterns):
                filtered.append(line)
        cleaned = "\n".join(filtered).strip()
        return cleaned
    except requests.exceptions.Timeout:
        return "[Error] Gemini API call timed out. Please try again."
    except requests.exceptions.ConnectionError:
        return "[Error] Connection error. Please check your internet connection."
    except requests.exceptions.HTTPError as http_err:
        return f"[Error] HTTP error occurred: {http_err}"
    except KeyError:
        return f"[Error] Unexpected response format from Gemini API: {result}"
    except Exception as e:
        return f"[Error] Gemini API call failed: {e}"

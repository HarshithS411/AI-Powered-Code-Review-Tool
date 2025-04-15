import requests
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

def convert_code(code, source_lang, target_lang):
    """
    Convert code from source_lang to target_lang using Gemini 2.0 Flash API.
    """
    # Retrieve the API key from environment variable
    API_KEY = os.getenv("GEMINI_API_KEY")
    if not API_KEY:
        raise ValueError("GEMINI_API_KEY environment variable not set. Please set it in the .env file.")

    API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

    # Construct the prompt with specific formatting instructions and example
    prompt = f"""Convert the following {source_lang} code to {target_lang}. Output must be a properly formatted program.
For C, C++, or Java, use this exact structure:
#include <stdio.h>
int main() {{
    [your code here]
    return 0;
}}
Ensure 4-space indentation and one statement per line. Input: {code}

Output only the formatted code."""

    headers = {
        "Content-Type": "application/json"
    }
    params = {
        "key": API_KEY  # Add API key as a query parameter
    }
    data = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.5,  # Lower temperature for more consistent output
            "maxOutputTokens": 1024  # Limit output length for code
        }
    }

    try:
        response = requests.post(API_URL, params=params, json=data, headers=headers, timeout=30)
        response.raise_for_status()  # Raise an error for bad status codes
        result = response.json()
        # Extract the converted code from the response
        converted_code = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        print(f"Raw API response: {converted_code}")  # Debug: Print raw response
        if not converted_code:
            return None

        # Post-process to ensure proper formatting
        lines = converted_code.split('\n')
        formatted_lines = []
        indent_level = 0
        in_block = False

        for line in lines:
            stripped_line = line.strip()
            if not stripped_line:  # Skip empty lines
                continue

            # Check for block start or end
            if stripped_line.startswith('}'):
                indent_level = max(0, indent_level - 1)
            elif '{' in stripped_line or stripped_line.startswith('int main'):
                in_block = True
            elif in_block and not stripped_line.endswith('{') and not stripped_line.startswith('}'):
                pass  # Indentation will be handled below

            # Add indentation
            formatted_lines.append('    ' * indent_level + stripped_line)

            if '{' in stripped_line:
                indent_level += 1
            elif stripped_line.startswith('int main') and '{' not in stripped_line:
                indent_level += 1  # Prepare for block start

        # Force a structured format for C/C++/Java if no main function
        if target_lang in ['c', 'cpp', 'java'] and 'int main' not in converted_code.lower():
            # Fallback: Split on semicolons and rejoin with newlines
            statements = converted_code.replace(';', ';\n').split('\n')
            formatted_code = (
                "#include <stdio.h>\n"
                "int main() {\n"
                + '\n'.join('    ' + s.strip() for s in statements if s.strip()) + "\n"
                "    return 0;\n"
                "}"
            )
        else:
            formatted_code = '\n'.join(formatted_lines)

        print(f"Formatted code: {formatted_code}")  # Debug: Print formatted output
        return formatted_code.strip()
    except requests.RequestException as e:
        print(f"Error calling Gemini API: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error in conversion: {e}")
        return None
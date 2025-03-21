import os
import re
import json
from openai import OpenAI


# Read API key from environment variables
api_key = os.getenv("OPENAI_API_KEY")

# Initiate OpenAI client
client = OpenAI(api_key=api_key)

def process_text_with_gpt(file_path):
    """Process text file using GPT model to extract relevant keywords."""

    try:
        # Read file content
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        # GPT prompt for keyword extraction
        prompt = {
            "role": "system",
            "content": (
                "You are an expert in extracting keywords from text messages, emails, and messenger apps "
                "to infer user actions. Extract the following fields and return JSON output:\n\n"
                "- service_name\n- action_datetime\n- message_datetime\n- action_keyword\n"
                "- address1\n- address2\n- amount\n- item\n- mobile_number\n\n"
                "Rules:\n"
                "- If a value is not found, insert NULL.\n"
                "- Extract dates exactly as they appear.\n"
                "- If multiple payments exist, extract only the highest one.\n"
                "- If multiple ordered items are found, include all items as a list."
            )
        }

        # Call GPT model
        completion = client.chat.completions.create(
            model="gpt-4o",
            store=True,
            messages=[prompt, {"role": "user", "content": content}],
            temperature=0.65,
            max_completion_tokens=2048,
        )

        # Parse GPT response
        gpt_response = completion.choices[0].message.content.strip()
        data = json.loads(gpt_response.strip("```json").strip())

        # Validate and log extracted items
        if isinstance(data.get("item"), list):
            print(f"Extracted items: {data['item']}")
        else:
            print("No items found or invalid format.")

        # Attach source file path
        data["source_path"] = file_path

        return data
    except Exception as e:
        return {"source_path": file_path, "error": str(e)}


def normalize_json_data(json_data):
    """
    Uses GPT API to normalize JSON fields (dates, currency).
    """
    try:
        prompt = {
            "role": "system",
            "content": (
                "You are an expert in formatting and normalizing JSON data. "
                "You will receive a JSON object containing fields such as dates and amounts. "
                "Your task is to:\n"
                "- Convert dates to format: YYYY/MM/DD HH:MM:ss.\n"
                "- Ensure missing values are empty (\"\").\n"
                "- Format amount fields with currency codes (e.g., 'USD 100', 'AUD 50').\n"
                "- Return the updated JSON with all fields properly formatted."
            )
        }

        # Send data to GPT API
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[prompt, {"role": "user", "content": json.dumps(json_data)}],
            temperature=0,
            max_tokens=1000,
        )

        # Parse response
        gpt_response = completion.choices[0].message.content.strip()
        match = re.search(r"```json\s*(\{.*?\})\s*```", gpt_response, re.DOTALL)
        if match:
            json_str = match.group(1)
            normalized_data = json.loads(json_str)
            return normalized_data
        else:
            raise ValueError("Cannot find JSON code block")

    except Exception as e:
        print(f"Error normalizing JSON: {e}")
        return json_data  # Return original if GPT fails



CACHE_FILE = "cache.json"  # ✅ Store processed data persistently

def load_cache():
    """Loads previously extracted and normalized JSON data from cache."""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as cache_file:
            try:
                return json.load(cache_file)
            except json.JSONDecodeError:
                return []  # Return empty list if JSON is corrupted
    return []

def save_cache(data):
    """Saves extracted and normalized JSON data to cache."""
    with open(CACHE_FILE, "w", encoding="utf-8") as cache_file:
        json.dump(data, cache_file, ensure_ascii=False, indent=4)




def extract_keywords(input_directories, output_directory):
    """Extracts keywords from text files, saves raw JSON, and returns normalized JSON."""
    # ✅ Load previously cached data
    normalized_json_list = load_cache()

    os.makedirs(output_directory, exist_ok=True)

    for directory in input_directories:
        print(f"📂 Processing directory: {directory}")

        # ✅ Check for `.txt` files BEFORE processing
        all_files = os.listdir(directory)
        txt_files = [f for f in all_files if f.lower().endswith(".txt")]
        print(f"📑 Found {len(txt_files)} text files: {txt_files}")

        if not txt_files:
            #print("⚠ No .txt files found, returning cached data.")
            return normalized_json_list  # ✅ Return previous cache if no new files

        for file_name in txt_files:
            file_path = os.path.join(directory, file_name)
            print(f"✅ Processing text file: {file_name}")

            # Extract JSON from text file
            extracted_json = process_text_with_gpt(file_path)

            if not extracted_json:
                #print(f"⚠ Skipping file (extraction failed): {file_name}")
                continue

            # ✅ Save raw JSON for HTML highlighting
            raw_output_path = os.path.join(output_directory, f"raw_{file_name}.json")
            with open(raw_output_path, "w", encoding="utf-8") as raw_file:
                json.dump(extracted_json, raw_file, ensure_ascii=False, indent=4)
            print(f"✅ Raw JSON saved for highlighting: {raw_output_path}")

            # ✅ Normalize extracted JSON
            normalized_json = normalize_json_data(extracted_json)

            # ✅ Prevent duplicate entries
            if normalized_json not in normalized_json_list:
                normalized_json_list.append(normalized_json)

    # ✅ Save updated data to cache
    save_cache(normalized_json_list)

    #print(f"🔹 DEBUG: Returning {len(normalized_json_list)} JSON objects")
    return normalized_json_list  # ✅ Always return a list

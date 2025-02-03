import os
import re
from email import policy
from email.parser import BytesParser
from openai import OpenAI


# Read API key from environment variables
api_key = os.getenv("OPENAI_API_KEY")

# Initiate OpenAI client
client = OpenAI(api_key=api_key)

def classify_email(content):
    """
    Uses GPT to classify an email as Application-to-Person (A2P) or Person-to-Person (P2P).

    Args:
        content (str): Email body content.

    Returns:
        bool: True if classified as A2P, False otherwise.
    """
    try:
        prompt = {
            "role": "system",
            "content": (
                "You are an expert in classifying emails as Application-to-Person (A2P) or Person-to-Person (P2P). "
                "A2P emails are system-generated messages, such as order confirmations, payment receipts, or booking notifications. "
                "P2P emails are personal conversations between individuals.\n\n"
                "Rules for A2P Classification:\n"
                "- Includes messages triggered by user actions (e.g., order confirmations, payment receipts, shipping updates, booking confirmations).\n"
                "- Messages containing keywords like 'Order', 'Receipt', 'Shipped', 'Confirmation', or 'Departure time' are A2P.\n"
                "- Formal messages providing status updates.\n"
                "- Excludes promotional emails, marketing, and newsletters.\n\n"
                "Response Format:\n"
                "- If A2P, respond with: 'This is A2P.'\n"
                "- If P2P, respond with: 'This is P2P.'"
            )
        }

        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[prompt, {"role": "user", "content": content.strip()}],
            temperature=0.65,
            max_tokens=50,
        )

        response = completion.choices[0].message.content.strip()
        print(f"DEBUG: Model response: '{response}'")

        return bool(re.search(r'\bA2P\b', response, re.IGNORECASE))

    except Exception as e:
        print(f"Error classifying email: {e}")
        return False


def process_txt_files(input_dirs, output_dir):
    """
    Processes .txt files in multiple directories, classifies them as A2P or P2P, and saves A2P emails.

    Args:
        input_dirs (list): List of directories containing .txt files.
        output_dir (str): Directory to save classified A2P .txt files.
    """
    os.makedirs(output_dir, exist_ok=True)

    total_files = 0
    for input_dir in input_dirs:
        txt_files = [f for f in os.listdir(input_dir) if f.endswith(".txt")]
        total_files += len(txt_files)

        print(f"Processing {len(txt_files)} text files from {input_dir}...")

        for idx, txt_file in enumerate(txt_files, start=1):
            file_path = os.path.join(input_dir, txt_file)
            try:
                with open(file_path, "r", encoding="utf-8", errors="replace") as file:
                    content = file.read()

                is_a2p = classify_email(content)
                print(f"DEBUG: {txt_file} classified as: {'A2P' if is_a2p else 'P2P'}")

                if is_a2p:
                    output_path = os.path.join(output_dir, f"a2p_{txt_file}")
                    with open(output_path, "w", encoding="utf-8", errors="replace") as dest_file:
                        dest_file.write(content)
                    print(f"[{idx}/{len(txt_files)}] Saved: {output_path}")
                else:
                    print(f"[{idx}/{len(txt_files)}] Discarded: {file_path}")

            except Exception as e:
                print(f"Error processing {file_path}: {e}")

    print(f"Processing completed. Total {total_files} files checked. A2P emails saved in {output_dir}.")


def convert_text_to_html(input_directory, output_directory):
    """
    Converts all .txt files in the input directory to HTML format.

    Args:
        input_directory (str): Directory containing text files.
        output_directory (str): Directory for output HTML files.
    """
    os.makedirs(output_directory, exist_ok=True)

    for file_name in os.listdir(input_directory):
        file_path = os.path.join(input_directory, file_name)

        if file_name.endswith(".txt") and os.path.isfile(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()

                html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{os.path.splitext(file_name)[0]}</title>
</head>
<body>
    <pre>{content}</pre>
</body>
</html>"""

                output_file_path = os.path.join(output_directory, os.path.splitext(file_name)[0] + ".html")
                with open(output_file_path, "w", encoding="utf-8") as html_file:
                    html_file.write(html_content)

                print(f"Converted: {file_name} -> {output_file_path}")

            except Exception as e:
                print(f"Error converting {file_name}: {e}")

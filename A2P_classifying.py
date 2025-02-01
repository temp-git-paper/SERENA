import os
import re
from email import policy
from email.parser import BytesParser
from openai import OpenAI

# Initialize OpenAI GPT client
client = OpenAI(
    api_key="Your-API-Key")

def classify_email(content):
    """
    Use GPT to classify whether an email is A2P or person-to-person.

    Args:
        content (str): The email body content.

    Returns:
        bool: True if the email is classified as A2P, False otherwise.
    """
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert in classifying emails as application-to-person (A2P) or person-to-person (P2P)."
                        "A2P messages are sent by systems or services to individuals, such as order confirmations, payment receipts, "
                        "or booking notifications, but only when these keywords refer to transactions or events initiated by the user"                        "P2P messages are direct exchanges between individuals, such as personal conversations."
                        "Always classify messages with keywords like 'Order,' 'Receipt,' 'Shipped,' 'Confirmation,' or 'Departure time' as A2P."
                        "Do not include messages such as advertising or marketing, which are not sent by a user action."

                        "A2P Classification Rules:\n"
                        "Include as A2P: \n"

                        "Messages triggered by user actions, such as:"
                        "Order confirmations, payment receipts, or shipping updates."
                        "Booking confirmations (e.g., hotel reservations, flight itineraries)."
                        "Uber or Lyft related message (e.g., Your Lyft driver, Jim, is here! Look for the Red Nissan Rogue (GXR 7995))"
                        "Login notifications or security alerts directly tied to user activity."
                        "Messages containing keywords such as:"
                        "'Order,' 'Receipt,' 'Shipped,' 'Confirmation,' 'Departure time,' or similar phrases indicating user-initiated transactions."
                        "Messages with formal tone and structured information confirming user actions or providing status updates."
                        "Card Service Name Datetime USD NN.NN this format is also included in A2P."

                        "Exclude from A2P:"
                        "Messages that are not tied to specific user actions (e.g., marketing or advertising emails)."
                        "Promotional content about new products, sales, or updates not based on user behavior."
                        "Newsletters or announcements sent to a general audience without evidence of individual user actions"

                        "Response Format:\n"
                        "If the email matches the criteria for A2P, respond with: 'This is A2P.' \n"
                        "If the email matches the criteria for P2P, respond with: 'This is P2P.'"

                    )
                },
                {"role": "user", "content": content.strip()}
            ],
            temperature=0.65,
            max_tokens=50
        )

        # Extract and clean up the response
        response = completion.choices[0].message.content.strip()
        print(f"DEBUG: Model response: '{response}'")  # Log the raw response from the model

        # Use regular expressions to extract A2P or P2P
        if re.search(r'\bA2P\b', response, re.IGNORECASE):
            print("DEBUG: Returning classification result: A2P (True)")
            return True
        elif re.search(r'\bP2P\b', response, re.IGNORECASE):
            print("DEBUG: Returning classification result: P2P (False)")
            return False
        else:
            # Handle unexpected response
            print(f"Unexpected response: {response}")
            return False
    except Exception as e:
        print(f"Error classifying email: {e}")
        return False


def process_txt_files(input_dirs, output_dir):
    """
    Process .txt files in multiple directories, classify them as A2P or P2P, and save only A2P emails.

    Args:
        input_dirs (list): List of directories containing .txt files.
        output_dir (str): Directory to save classified A2P .txt files.
    """
    os.makedirs(output_dir, exist_ok=True)

    total_files = 0
    for input_dir in input_dirs:
        txt_files = [f for f in os.listdir(input_dir) if f.endswith(".txt")]
        total_files += len(txt_files)

        print(f"Processing {len(txt_files)} .txt files from {input_dir}...")

        for idx, txt_file in enumerate(txt_files, start=1):
            file_path = os.path.join(input_dir, txt_file)
            try:
                with open(file_path, "r", encoding="utf-8", errors="replace") as file:
                    content = file.read()

                # Classify email
                is_a2p = classify_email(content)
                print(f"DEBUG: File: {txt_file} | Model classified as: {'A2P' if is_a2p else 'P2P'}")

                # Check classification result and save A2P emails
                if is_a2p:
                    output_path = os.path.join(output_dir, f"a2p_{txt_file}")
                    with open(output_path, "w", encoding="utf-8", errors="replace") as dest_file:
                        dest_file.write(content)
                    print(f"[{idx}/{len(txt_files)}] A2P email saved: {output_path}")
                else:
                    print(f"[{idx}/{len(txt_files)}] P2P email discarded: {file_path}")
            except Exception as e:
                print(f"Error processing file {file_path}: {e}")

    print(f"Processing completed. Total {total_files} files processed. A2P emails saved to {output_dir}")


def convert_text_to_html(input_directory, output_directory):
    """
    Convert all the text files into html files in the designated directory

    Args:
        input_directory (str): Directory of input text files
        output_directory (str): Directory of output HTML files
    """
    # Output directory not found, create one
    os.makedirs(output_directory, exist_ok=True)

    # Explore the files in input dir
    for file_name in os.listdir(input_directory):
        file_path = os.path.join(input_directory, file_name)

        # Process only text files
        if os.path.isfile(file_path) and file_name.endswith(".txt"):
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()

                # Create html files
                html_content = f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>{os.path.splitext(file_name)[0]}</title>
</head>
<body>
    <pre>{content}</pre>
</body>
</html>"""

                # Save html files
                output_file_name = f"{os.path.splitext(file_name)[0]}.html"
                output_file_path = os.path.join(output_directory, output_file_name)

                with open(output_file_path, "w", encoding="utf-8") as html_file:
                    html_file.write(html_content)

                print(f"Converted: {file_name} -> {output_file_name}")

            except Exception as e:
                print(f"Error converting {file_name}: {e}")


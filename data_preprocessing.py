import os
import re
import pandas as pd
from email import policy
from email.parser import BytesParser


def extract_email_content(file_path):
    """
    Extracts email headers and body content (supports multipart emails).

    Args:
        file_path (str): Path to the .eml file.

    Returns:
        dict: Extracted email content including headers and body.
    """
    with open(file_path, "rb") as file:
        message = BytesParser(policy=policy.default).parse(file)

    headers = {
        "From": message.get("From", "Unknown"),
        "To": message.get("To", "Unknown"),
        "Subject": message.get("Subject", "No Subject"),
        "Date": message.get("Date", "Unknown"),
    }

    body = ""
    if message.is_multipart():
        for part in message.walk():
            if part.get_content_type() in ["text/plain", "text/html"]:
                charset = part.get_content_charset() or "utf-8"
                body += part.get_payload(decode=True).decode(charset, errors="replace")
    else:
        charset = message.get_content_charset() or "utf-8"
        body = message.get_payload(decode=True).decode(charset, errors="replace")

    return {"headers": headers, "body": body}


def save_eml_to_txt(input_dir, output_dir):
    """
    Extracts and saves email content from .eml files as .txt files.

    Args:
        input_dir (str): Directory containing .eml files.
        output_dir (str): Directory to save processed text files.
    """
    os.makedirs(output_dir, exist_ok=True)

    for idx, eml_file in enumerate((f for f in os.listdir(input_dir) if f.endswith(".eml")), start=1):
        try:
            extracted_content = extract_email_content(os.path.join(input_dir, eml_file))
            txt_content = (
                f"From: {extracted_content['headers']['From']}\n"
                f"To: {extracted_content['headers']['To']}\n"
                f"Subject: {extracted_content['headers']['Subject']}\n"
                f"Date: {extracted_content['headers']['Date']}\n\n"
                f"Body:\n{extracted_content['body']}"
            )
            save_path = os.path.join(output_dir, f"eml_{idx}.txt")
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(txt_content)

            print(f"Saved: {save_path}")
        except Exception as e:
            print(f"Failed to process {eml_file}: {e}")


def save_excel_rows_to_txt(input_directory, output_dir):
    """
    Extracts rows from Excel files and saves them as individual .txt files.

    Args:
        input_directory (str): Directory containing .xlsx files.
        output_dir (str): Directory to save text files.
    """
    os.makedirs(output_dir, exist_ok=True)

    excel_files = [f for f in os.listdir(input_directory) if f.endswith(".xlsx")]

    if not excel_files:
        print("No .xlsx files found. Skipping.")
        return

    for excel_file in (f for f in os.listdir(input_directory) if f.endswith(".xlsx")):
        try:
            df = pd.read_excel(os.path.join(input_directory, excel_file))

            for index, row in df.iterrows():
                file_name = f"{os.path.splitext(excel_file)[0]}_msg_{index + 1}.txt"
                with open(os.path.join(output_dir, file_name), "w", encoding="utf-8") as txt_file:
                    txt_file.write("\n".join(f"{col}: {val}" for col, val in row.items()))

                print(f"Saved: {file_name}")

        except Exception as e:
            print(f"Error processing {excel_file}: {e}")


def split_messagingapp_files(input_directory, output_directory):
    """
    Splits chat logs from messaging apps into separate files based on date headers.

    Args:
        input_directory (str): Directory containing text files from messaging apps.
        output_directory (str): Directory to save processed text files.
    """
    os.makedirs(output_directory, exist_ok=True)

    date_pattern = r"-{15,}\s*[A-Za-z]+,\s*[A-Za-z]+\s*\d{1,2},\s*\d{4}\s*-{15,}"


    for file_name in (f for f in os.listdir(input_directory) if f.endswith(".txt")):
        file_path = os.path.join(input_directory, file_name)

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()

            # Splitting based on date headers
            sections = re.split(date_pattern, content)

            if len(sections) > 1:
                for i, section in enumerate(sections):
                    section = section.strip()
                    if not section:  # Skip empty sections
                        continue

                    output_file_name = f"{os.path.splitext(file_name)[0]}_part{i + 1}.txt"
                    output_file_path = os.path.join(output_directory, output_file_name)

                    with open(output_file_path, "w", encoding="utf-8") as output_file:
                        output_file.write(section)

                    print(f"Saved: {output_file_path}")

            else:
                # If no valid split is found, save the file as is
                output_file_name = f"{os.path.splitext(file_name)[0]}_original.txt"
                output_file_path = os.path.join(output_directory, output_file_name)

                with open(output_file_path, "w", encoding="utf-8") as output_file:
                    output_file.write(content)

                print(f"Saved (No Split Needed): {output_file_path}")

        except Exception as e:
            print(f"Error processing {file_name}: {e}")

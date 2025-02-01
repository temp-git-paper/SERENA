import re
import os
import pandas as pd
from email import policy
from email.parser import BytesParser

def extract_email_content(file_path):
    """
    Extract email headers and body content (supports multipart emails).

    Args:
        file_path (str): Path to the .eml file.

    Returns:
        dict: Extracted email content with headers and body.
    """
    with open(file_path, "rb") as file:
        # Parse the email using BytesParser
        message = BytesParser(policy=policy.default).parse(file)

    # Extract headers
    headers = {
        "From": message["From"],
        "To": message["To"],
        "Subject": message["Subject"],
        "Date": message["Date"],
    }

    # Extract body content
    body = ""
    if message.is_multipart():
        for part in message.walk():
            # Only process plain text or HTML parts
            if part.get_content_type() in ["text/plain", "text/html"]:
                charset = part.get_content_charset() or "utf-8"
                body += part.get_payload(decode=True).decode(charset, errors="replace")
    else:
        charset = message.get_content_charset() or "utf-8"
        body = message.get_payload(decode=True).decode(charset, errors="replace")

    return {"headers": headers, "body": body}

def save_eml_to_txt(input_dir, output_dir):
    """
    Process .eml files in a directory, extract relevant parts, and save as .txt files.

    Args:
        input_dir (str): Directory containing .eml files.
        output_dir (str): Directory to save processed .txt files.
    """
    os.makedirs(output_dir, exist_ok=True)  # Ensure output directory exists

    eml_files = [f for f in os.listdir(input_dir) if f.endswith(".eml")]
    print(f"Processing {len(eml_files)} .eml files from {input_dir}...")

    for idx, eml_file in enumerate(eml_files, start=1):
        file_path = os.path.join(input_dir, eml_file)
        try:
            # Extract content from the .eml file
            extracted_content = extract_email_content(file_path)

            # Prepare content for the .txt file
            headers = extracted_content["headers"]
            body = extracted_content["body"]

            txt_content = (
                f"From: {headers['From']}\n"
                f"To: {headers['To']}\n"
                f"Subject: {headers['Subject']}\n"
                f"Date: {headers['Date']}\n\n"
                f"Body:\n{body}"
            )

            # Save the extracted content as a .txt file
            save_path = os.path.join(output_dir, f"eml_{idx}.txt")
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(txt_content)

            print(f"[{idx}/{len(eml_files)}] Saved: {save_path}")
        except Exception as e:
            print(f"[{idx}/{len(eml_files)}] Failed to process {file_path}: {e}")

    print(f"Processing completed. Extracted emails saved to {output_dir}.")

def save_excel_rows_to_txt(input_directory, output_dir):
    """
    Process all .xlsx files in the specified directory, extracting each row as an individual .txt file.

    Args:
        input_directory (str): Directory containing .xlsx files.
        output_dir (str): Directory to save the text files.
    """
    os.makedirs(output_dir, exist_ok=True)  # Create the output directory if it does not exist

    # Find all .xlsx files in the directory
    excel_files = [f for f in os.listdir(input_directory) if f.endswith(".xlsx")]

    if not excel_files:
        print(f"No .xlsx files found in {input_directory}")
        return

    print(f"Processing {len(excel_files)} Excel files from {input_directory}...")

    for excel_file in excel_files:
        excel_path = os.path.join(input_directory, excel_file)

        try:
            # Load the Excel file into a pandas DataFrame
            df = pd.read_excel(excel_path)

            # Iterate through each row in the DataFrame
            for index, row in df.iterrows():
                # Generate file name based on row index and Excel file name
                file_name = f"{os.path.splitext(excel_file)[0]}_message_{index + 1}.txt"
                output_file_path = os.path.join(output_dir, file_name)

                # Save the row data to a text file
                with open(output_file_path, "w", encoding="utf-8") as txt_file:
                    for column_name, value in row.items():
                        txt_file.write(f"{column_name}: {value}\n")

                print(f"Saved row {index + 1} from {excel_file} to '{output_file_path}'")
        except Exception as e:
            print(f"Error processing {excel_path}: {e}")

    print(f"Processing completed. Extracted messages saved to {output_dir}.")


def split_messagingapp_files(input_directory, output_directory):

    os.makedirs(output_directory, exist_ok=True)

    for file_name in os.listdir(input_directory):
        file_path = os.path.join(input_directory, file_name)

        if os.path.isfile(file_path) and file_name.endswith(".txt"):
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()

            # Separate files - Pattern "--------------- \d{4}Year \d{1,2}Month \d{1,2}Day [A-Z]+ ---------------"
            pattern = r"(--------------- \d{4}Year \d{1,2}Month \d{1,2}Day [A-Z]+ ---------------)"
            sections = re.split(pattern, content)

            if len(sections) > 1:
                for i in range(1, len(sections), 2):
                    header = sections[i].strip()
                    body = sections[i + 1].strip()

                    # Generate output files
                    output_file_name = f"{os.path.splitext(file_name)[0]}_part{i//2 + 1}.txt"
                    output_file_path = os.path.join(output_directory, output_file_name)

                    # Save header and body contents
                    with open(output_file_path, "w", encoding="utf-8") as output_file:
                        output_file.write(header + "\n" + body)

                    print(f"Save separated files: {output_file_path}")
            else:
                print(f"File no need to separate: {file_path}, Keep the  original file")
                output_file_name = f"{os.path.splitext(file_name)[0]}_original.txt"
                output_file_path = os.path.join(output_directory, output_file_name)
                with open(output_file_path, "w", encoding="utf-8") as output_file:
                    output_file.write(content)


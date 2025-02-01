import os
import re
import json
from openai import OpenAI

# Initiate OpenAI client
client = OpenAI(api_key="Your-API-Key")

# Call Open API
def process_text_with_gpt(file_path):
    try:
        # Read text files
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        # Call GPT model
        completion = client.chat.completions.create(
            model="gpt-4o",
            store=True,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert in extracting keywords from text messages, emails, "
                    "and messenger apps like KakaoTalk to infer user actions within the text."
                    "Extract the following data from the text and store it in JSON format."

                    "Keyword Extraction Rules: "
                    "If a value is not found, insert NULL."
                    "Extract dates exactly as they appear in the text."
                    "For item 4, extract the exact keywords used in the text."
                    "Addresses may include IP addresses."
                    "For item 7, if multiple payment amounts exist, extract only the highest" "amount while preserving the full keyword including the currency."
                    "For item 8, if multiple product names or ordered items are found, include" "all item details as a list under the item key."
                    "Each item can include a name field."
                    "Extract the following fields:"
                    "Service Name / Store Name / Business Name (key name: service_name)"
                    "Date and Time of Action (key name: action_datetime)"
                    "Date and Time of Message Reception (key name: message_datetime)"
                    "Action Keyword (e.g., purchase, movie reservation, taxi ride)" 
                    "(key name: action_keyword)"
                    "Departure Address / Location Information (key name: address1)"
                    "Destination Address / Location Information (key name: address2)"
                    "Payment Amount (key name: amount)"
                    "Ordered Items / Product Names (key name: item)"
                    "Phone Number / Mobile Number (key name: mobile_number)"

                },
                {"role": "user", "content": content}
            ],
            temperature=0.65,
            max_completion_tokens=2048,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )

        # Extract JSON data from GPT responses
        gpt_response = completion.choices[0].message.content

        # Load JSON
        data = json.loads(gpt_response.strip("```json").strip())

        # Check Item data
        if "item" in data and isinstance(data["item"], list):
            print(f"Extracted items: {data['item']}")
        else:
            print("No items found or invalid format.")


        # Add original source file path to the json
        data["source_path"] = file_path

        return data
    except Exception as e:
        return {"source_path": file_path, "error": str(e)}

# dealing with multiple directories
def extract_keywords(input_directories, output_directory):
    # If directory not found, create it
    os.makedirs(output_directory, exist_ok=True)

    for directory_path in input_directories:
        print(f"Processing directory: {directory_path}")

        for file_name in os.listdir(directory_path):
            file_path = os.path.join(directory_path, file_name)

            if os.path.isfile(file_path) and file_name.endswith(".txt"):
                print(f"Processing file: {file_name}")

                # Process with GPT
                result = process_text_with_gpt(file_path)

                # Save the outputs
                output_file = os.path.join(output_directory, f"result_{os.path.basename(file_name)}.json")
                with open(output_file, "w", encoding="utf-8") as output:
                    json.dump(result, output, ensure_ascii=False, indent=4)

                print(f"Result saved to: {output_file}")

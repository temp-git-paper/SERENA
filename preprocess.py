import os
from data_preprocessing import save_eml_to_txt, save_excel_rows_to_txt, split_messagingapp_files
from A2P_classifying import process_txt_files, convert_text_to_html
from named_entitiy_recognition import extract_keywords

CACHE_FILE = "cache.json"  # Define the cache file path

def preprocess(dir_name):
    """Main function to preprocess data, classify messages, and extract keywords."""

    # ✅ Step 0: Delete cache.json if it exists
    if os.path.exists(CACHE_FILE):
        os.remove(CACHE_FILE)
        print("🗑️ Deleted existing cache.json. Starting fresh.")

    text_output_dir = os.path.join(dir_name, "text")

    # Step 1: Data Preprocessing
    print("Step 1: Data Preprocessing...")

    # ✅ Create input subdirectories if they don't exist
    for folder in ["emls", "textmessage", "messagingapp"]:
        path = os.path.join(dir_name, folder)
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"📁 Created missing folder: {folder}")

    already_precessed = False
    for name in os.listdir(dir_name):
        full_path = os.path.join(dir_name, name)
        if os.path.isdir(full_path) and "A2P-classified" in name:
            already_precessed = True
    if not already_precessed:
        save_eml_to_txt(os.path.join(dir_name, "emls"), text_output_dir)
        save_excel_rows_to_txt(os.path.join(dir_name, "textmessage"), text_output_dir)
        split_messagingapp_files(os.path.join(dir_name, "messagingapp"), text_output_dir)

        # Step 2: Classifying A2P messages
        print("Step 2: Classifying A2P messages...")
        a2p_classified_dir = os.path.join(dir_name, "A2P-classified-text")
        process_txt_files([text_output_dir], a2p_classified_dir)

        html_output_dir = os.path.join(dir_name, "A2P-classified-html")
        convert_text_to_html(a2p_classified_dir, html_output_dir)

        # Step 3: Extracting keywords
        print("Step 3: Extracting keywords from A2P messages...")
        keyword_output_dir = os.path.join(dir_name, "A2P-classified-json")
        extract_keywords([a2p_classified_dir], keyword_output_dir)
    else:
        html_output_dir = os.path.join(dir_name, "A2P-classified-html")
        keyword_output_dir = os.path.join(dir_name, "A2P-classified-json")

    print("Processing completed.")

    return keyword_output_dir, html_output_dir

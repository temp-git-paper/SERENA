from data_preprocessing import save_eml_to_txt, save_excel_rows_to_txt, split_messagingapp_files
from A2P_classifying import process_txt_files, convert_text_to_html
from named_entitiy_recognition import extract_keywords
def preprocess(dir_name):

    print("Step 1: Data Preprocessing...")
    # Process .eml files
    eml_input_directory = dir_name +"/emls/"  # Replace with your input directory
    eml_output_directory = dir_name + "/text/"  # Replace with your output directory
    save_eml_to_txt(eml_input_directory, eml_output_directory)

    # Process Excel rows
    excel_file_path = dir_name +"/textmessage/"  # Replace with your Excel file path
    excel_output_directory = dir_name + "/text/"  # Replace with your desired output directory
    save_excel_rows_to_txt(excel_file_path, excel_output_directory)

    # messagingapp file process
    messagingapp_input_directory = dir_name + "/messagingapp/"
    messagingapp_output_directory = dir_name + "/text/"
    split_messagingapp_files(messagingapp_input_directory, messagingapp_output_directory)


    print("Step 2: Classifying A2P messages...")
    processed_data = [dir_name + "/text/"]
    a2p_classified = dir_name + "/A2P-classified-text/"
    process_txt_files(processed_data, a2p_classified)

    html_output_dir = dir_name + "/A2P-classified-html/"
    convert_text_to_html(a2p_classified, html_output_dir)

    print("Step 3: Extracting keywords from A2P messages...")

    keyword_input = [dir_name + "/A2P-classified-text/"]
    keyword_output = dir_name + "/A2P-classified-json/"
    extract_keywords(keyword_input, keyword_output)

    print("completed")

    return keyword_output, html_output_dir


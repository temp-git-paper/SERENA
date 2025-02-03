# [DFRWS USA 2025] SERENA (Systematic Extraction and Reconstruction for ENhanced A2P Message Forensics)

📄 **Official repository for our research paper submitted to DFRWS 2025 USA**

SERENA (Systematic Extraction and Reconstruction for Enhanced A2P Message Forensics) is a forensic tool designed to automate the **extraction, classification, and highlighting** of structured data from **Application-to-Person (A2P) messages**. The tool leverages **GPT-4o** to classify A2P messages and extract key forensic information, enabling investigators to efficiently analyze digital communications.

## 📌 Key Features
- **Automated Data Processing**: Converts emails (.eml), text messages (.xlsx), and chat logs into structured text format.
- **A2P vs. P2P Classification**: Identifies and categorizes messages using OpenAI’s GPT-4o.
- **Named Entity Recognition**: Extracts essential forensic data (e.g., service name, timestamps, payment details).
- **GUI-Based Analysis**: Provides an interactive interface for forensic investigators.
- **Highlighting Feature**: Displays extracted keywords directly within the original message.

## 📂 Repository Structure

- **`data_preprocessing.py`, `preprocess.py`**  
  - Converts emails (.eml), text messages (.xlsx), and chat logs into structured text format.

- **`A2P_classifying.py`**  
  - Classifies messages as A2P (Application-to-Person) or P2P (Person-to-Person) using GPT-4o.

- **`named_entity_recognition.py`**  
  - Extracts structured data such as service name, timestamp, payment amount, etc.
  - Normalize values (e.g., datetime - YYYY/MM/DD hh:mm:ss, amount - USD 150, AUD 300)

- **`SERENA-GUI.py`**  
  - Provides a GUI-based interface for forensic investigation.

- **`requirements.txt`**  
  - Lists required Python dependencies for the project.

- **`README.md`**  
  - This README file containing project details and setup instructions.
 


## 📌 How to Run the Tool on a Git Repository
To ensure the tool works correctly, the selected folder must contain the following subfolders:

📂 emls/ (For processing email data)
📂 messagingapp/ (For chat and messaging app logs)
📂 textmessage/ (For SMS and text message logs)


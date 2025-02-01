# SERENA (Systematic Extraction and Reconstruction for Enhanced A2P Message Forensics)

📄 Official repository for our research paper submitted to DFRWS 2025 USA

SERENA (Systematic Extraction and Reconstruction for Enhanced A2P Message Forensics) is a forensic tool designed to automate the extraction, classification, and highlighting of structured data from Application-to-Person (A2P) messages. The tool leverages GPT-4o to classify A2P messages and extract key forensic information, enabling investigators to efficiently analyze digital communications.

This repository contains:

The Python-based pipeline for processing emails, text messages, and chat logs.
The implementation of classification models using OpenAI’s GPT-4o.
The GUI-based tool for interactive forensic analysis.

This work has been submitted to DFRWS 2025 USA and presents a novel approach to A2P message forensics.


├── data_preprocessing.py      # Converts emails (.eml), text messages (.xlsx), and chat logs into structured text
├── A2P_classifying.py         # Classifies messages as A2P or P2P using GPT-4o
├── keyword_extraction.py      # Extracts structured data (service name, timestamp, payment amount, etc.)
├── GUI3.py                    # GUI-based interface for forensic investigation
├── main.py                    # Main execution script
├── requirements.txt           # List of required Python dependencies
├── README.md                  # This README file
└── images/                    # Figures used in the research paper

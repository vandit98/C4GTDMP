# Belongg AI-Language Translator

This Streamlit app allows users to upload PDF or TXT files containing text in Hindi and translates it to English. It provides an easy-to-use interface for text extraction, language translation, and viewing translation results.

## How It Works /Block Diagram
![image](https://github.com/vandit98/C4GTDMP/assets/91458535/d8587a53-e7aa-4b54-a4d9-16a2822fca01)

1. **Upload PDF or TXT Files**: Users can upload PDF or TXT files containing text in Hindi.
2. **Text Extraction**: The app extracts text from the uploaded files using the PDFMiner library.
3. **Language Translation**: After text extraction, the app translates the text from Hindi to English using the Google Translate API.
4. **View Translation Results**: Users can view the source and translated chunks of text side by side.
   
## Features

- **Text Translation**: Translates `.txt` files in Indic languages to English.
- **Audio Translation**: Converts spoken audio in Indic languages to transcribed English text.
- **Video Translation**: Supports transcription and translation of video content.
- **PDF Translation**: Translates the content of PDF documents from Indic languages to English.
-
## Supported Indic Languages

- Hindi
- Gom
- Kannada
- Dogri
- Bodo
- Urdu
- Tamil
- Kashmiri
- Assamese
- Bengali
- Marathi
- Sindhi
- Maithili
- Punjabi
- Malayalam
- Manipuri
- Telugu
- Sanskrit
- Nepali
- Santali
- Gujarati
- Odia


- 
## Usage

1. Select the language of the PDF from the dropdown menu (currently supports Hindi only).
2. Upload a PDF file, a TXT file, or a ZIP file containing multiple PDFs/TXTs using the drag-and-drop or file uploader.
3. After uploading, click the "Start Translation" button to initiate the translation process.
4. Once the translation is complete, the app displays the source and translated chunks of text.

## Deployment

The app is deployed on Streamlit Sharing. You can access it [here](https://belongg1.streamlit.app/).

## Login Credential 
![image](https://github.com/vandit98/C4GTDMP/assets/91458535/a0a086d6-ffd4-4fda-8b9e-4a1777816e1a)

## Tech Stack Used

- [st_login_form](https://github.com/daniellewisDL/streamlit-login): Handles user authentication and login functionality.
- [Streamlit](https://streamlit.io/): Framework for building web applications with Python.
- [Supabase](https://supabase.io/): Backend database for storing user information and authentication tokens.
- [PDFMiner-six](https://github.com/pdfminer/pdfminer.six): Library for extracting text from PDF files.
- [tiktoken](https://pypi.org/project/tiktoken/): Python wrapper for the TikTok API.
- [langchain](https://pypi.org/project/langchain/): Provides document storage and processing capabilities for language-related tasks.
- [Bhasini Api](https://bhashini.gov.in/): For performing Translation
- [Fastapi](https://fastapi.tiangolo.com/): Python library for creating api endpoints.


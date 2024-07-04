import streamlit as st
import requests
import json
import pickle
import shutil
import zipfile
import os
from pydantic import BaseModel
from pdfminer.high_level import extract_text
from langchain.docstore.document import Document
import datetime
from dotenv import load_dotenv
load_dotenv()

userID = os.getenv("userID")
ulcaApiKey = os.getenv("ulcaApiKey")
Authorization = os.getenv("Authorization")

languages = {
    1: "hi", 2: "gom", 3: "kn", 4: "doi", 5: "brx", 6: "ur",
    7: "ta", 8: "ks", 9: "as", 10: "bn", 11: "mr", 12: "sd",
    13: "mai", 14: "pa", 15: "ml", 16: "mni", 17: "te", 18: "sa", 
    19: "ne", 20: "sat", 21: "gu", 22: "or", 23: "en"
}

def get_languages():
    return languages




def get_service_id(source_language):
    url = "https://meity-auth.ulcacontrib.org/ulca/apis/v0/model/getModelsPipeline"
    payload = {
        "pipelineTasks": [
            {
                "taskType": "asr",
                "config": {
                    "language": {
                        "sourceLanguage": source_language
                    }
                }
            }
        ],
        "pipelineRequestConfig": {
            "pipelineId": "64392f96daac500b55c543cd"
        }
    }
    headers = {
        "Content-Type": "application/json",
        "userID": userID,
        "ulcaApiKey": ulcaApiKey
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        response_data = response.json()
        service_id = response_data["pipelineResponseConfig"][0]["config"][0]["serviceId"]
        return service_id
    else:
        return None


def transcribe_and_translate(audio_content, service_id, source_language):
    url = "https://dhruva-api.bhashini.gov.in/services/inference/pipeline"
    payload = json.dumps({
        "pipelineTasks": [
            {
                "taskType": "asr",
                "config": {
                    "language": {
                        "sourceLanguage": source_language
                    },
                    "serviceId": service_id,
                    "audioFormat": "flac",
                    "samplingRate": 16000
                }
            },
            {
                "taskType": "translation",
                "config": {
                    "language": {
                        "sourceLanguage": source_language,
                        "targetLanguage": "en"
                    },
                    "serviceId": "ai4bharat/indictrans-v2-all-gpu--t4"
                }
            }
        ],
        "inputData": {
            "audio": [
                {
                    "audioContent": audio_content
                }
            ]
        }
    })
    headers = {
        'Authorization': Authorization,
        'Content-Type': 'application/json'
    }
    response = requests.post(url, headers=headers, data=payload)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to process the request")
        return None
    


def make_translation_request(source_language):
    
    payload = {
        "pipelineTasks": [
            {
                "taskType": "translation",
                "config": {
                    "language": {
                        "sourceLanguage": source_language,
                        "targetLanguage": "en"
                    }
                }
            }
        ],
        "pipelineRequestConfig": {
            "pipelineId": "64392f96daac500b55c543cd"
        }
    }

    headers = {
        "Content-Type": "application/json",
        "userID": userID,
        "ulcaApiKey": ulcaApiKey
    }

    response = requests.post('https://meity-auth.ulcacontrib.org/ulca/apis/v0/model/getModelsPipeline', json=payload, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        return {"status_code": response.status_code, "message": "Error in translation request"}

def perform_translation(response_data, source_language, content):
    service_id = response_data["pipelineResponseConfig"][0]["config"][0]["serviceId"]
    compute_payload = {
        "pipelineTasks": [
            {
                "taskType": "translation",
                "config": {
                    "language": {
                        "sourceLanguage": source_language,
                        "targetLanguage": "en"
                    },
                    "serviceId": service_id
                }
            }
        ],
        "inputData": {
            "input": [
                {
                    "source": content
                }
            ]
        }
    }

    callback_url = response_data["pipelineInferenceAPIEndPoint"]["callbackUrl"]
    
    headers2 = {
        "Content-Type": "application/json",
        response_data["pipelineInferenceAPIEndPoint"]["inferenceApiKey"]["name"]:
            response_data["pipelineInferenceAPIEndPoint"]["inferenceApiKey"]["value"]
    }

    compute_response = requests.post(callback_url, json=compute_payload, headers=headers2)

    if compute_response.status_code == 200:
        return compute_response.json()
    else:
        return {"status_code": compute_response.status_code, "message": "Error in translation"}


def translate(source_language, content):
    response_data = make_translation_request(source_language)
    
    if "status_code" in response_data and response_data["status_code"] != 200:
        return response_data
    
    service_id = response_data["pipelineResponseConfig"][0]["config"][0]["serviceId"]
    compute_response_data = perform_translation(response_data, source_language, content)
    
    if "status_code" in compute_response_data and compute_response_data["status_code"] != 200:
        return compute_response_data
    
    translated_content = compute_response_data["pipelineResponse"][0]["output"][0]["target"]
    return {
        "status_code": 200,
        "message": "Translation successful",
        "translated_content": translated_content
    }

def split_text_into_chunks(text, chunk_size=4000, chunk_overlap=300):
    chunks = []
    for i in range(0, len(text), chunk_size - chunk_overlap):
        chunks.append(text[i:i + chunk_size])
    return chunks

def process_pdf_or_txt(uploaded_file, language, pdf_chunk_dir="pdf_chunks", processed_files_folder="processed_files"):
    filename = uploaded_file.name

    # Try decoding with different encodings for non-UTF-8 files
    encodings_to_try = ['utf-8', 'latin1', 'iso-8859-1']
    content = None
    for encoding in encodings_to_try:
        try:
            content = uploaded_file.getvalue().decode(encoding)
            break
        except UnicodeDecodeError:
            continue

    if content is None:
        st.error("Failed to decode the file. Please ensure it's encoded properly.")
        return

    if not os.path.exists(processed_files_folder):
        os.makedirs(processed_files_folder)

    temp = {'filename': filename}
    temp['date'] = datetime.datetime.now()

    if filename.endswith('.pdf'):
        # Extract text from PDF with specified encoding
        chunks = split_text_into_chunks(extract_text(uploaded_file, codec=encoding))
    elif filename.endswith('.txt'):
        chunks = split_text_into_chunks(content)
    else:
        st.error("Unsupported file format. Please upload PDF or TXT files.")
        return

    num = len(chunks)
    data = [temp for _ in range(num)]

    metadata = []
    metadata.extend(data)

    docs = []
    docs.extend(chunks)

    docObjs = []

    for j in range(0, num):
        doc_data = docs[j]
        doc_info = metadata[j]
        doc_obj = Document(page_content=doc_data, metadata=doc_info, language=language)
        docObjs.append(doc_obj)

    if not os.path.exists(pdf_chunk_dir):
        os.makedirs(pdf_chunk_dir)

    picklFile = os.path.join(pdf_chunk_dir, f"{filename}.pkl")
    with open(picklFile, 'wb') as file:
        pickle.dump(docObjs, file)

    # Move the file to the destination folder
    uploaded_file.seek(0)
    with open(os.path.join(processed_files_folder, filename), 'wb') as out:
        out.write(uploaded_file.read())


def text_extract_and_chunker(source_language, uploaded_file):
    st.title("PDF and TXT Chunker App")
    if uploaded_file is not None:
        if uploaded_file.type == "application/zip":
            # Extract and process each PDF/TXT file in the ZIP archive
            with zipfile.ZipFile(uploaded_file, "r") as zip_ref:
                for file_name in zip_ref.namelist():
                    with zip_ref.open(file_name) as file:
                        process_pdf_or_txt(file, source_language)
        else:
            # Process the uploaded PDF/TXT file
            process_pdf_or_txt(uploaded_file, source_language)
        st.success("Text has been extracted successfully.")
        st.write("Starting language translation")



def translate_chunks( source_language, pickle_dir="./pdf_chunks", output_dir="english_chunks"):
    st.title("Translation Results")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # List all pickle files in the directory
    pickle_files = [f for f in os.listdir(pickle_dir) if f.endswith('.pkl')]

    for pickle_file in pickle_files:
        with open(os.path.join(pickle_dir, pickle_file), 'rb') as file:
            docObjs = pickle.load(file)

        st.header(f"Translation for {pickle_file}")

        # Translate and save English versions of chunks
        translated_chunks = []
        for docObj in docObjs:
            source_chunks = docObj.page_content
            translated_chunks = translate(source_language, source_chunks)

            # translated_chunks = translate_text(source_chunks,target_language='en', source_language='auto')  # Assuming main function translates chunks to English
            translated_docObj = docObj  # Creating a copy of docObj
            translated_docObj.page_content = translated_chunks

            # Save English pickle file
            output_pickle_file = os.path.join(output_dir, f"english_{pickle_file}")
            with open(output_pickle_file, 'wb') as output_file:
                pickle.dump(translated_docObj, output_file)

            # Display source and destination chunks
            st.subheader("Source Chunks:")
            st.write(source_chunks)
            st.subheader("Translated Chunks:")
            st.write(translated_chunks)

def delete_chunks_dirs():
    if os.path.exists("pdf_chunks"):
        shutil.rmtree("pdf_chunks")
    if os.path.exists("english_chunks"):
        shutil.rmtree("english_chunks")
    st.success("PDF chunks and English chunks directories have been deleted.")

def start_translation(source_language):
    translate_chunks(source_language)
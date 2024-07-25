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
import logging
from logging.handlers import TimedRotatingFileHandler

load_dotenv()

# Configure logging
log_filename = "logs/translation_application.log"
log_handler = TimedRotatingFileHandler(log_filename, when="midnight", interval=1, backupCount=7)
log_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)

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
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        response_data = response.json()
        service_id = response_data["pipelineResponseConfig"][0]["config"][0]["serviceId"]
        logger.info(f"Service ID for {source_language} obtained successfully.")
        return service_id
    except requests.RequestException as e:
        logger.error(f"Failed to get service ID for {source_language}. Error: {e}")
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
    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()
        logger.info(f"Transcription and translation successful for audio content.")
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Failed to transcribe and translate audio content. Error: {e}")
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

    try:
        response = requests.post('https://meity-auth.ulcacontrib.org/ulca/apis/v0/model/getModelsPipeline', json=payload, headers=headers)
        response.raise_for_status()
        logger.info(f"Translation request for {source_language} made successfully.")
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Error making translation request for {source_language}. Error: {e}")
        return {"status_code": response.status_code, "message": "Error in translation request"}

def perform_translation(response_data, source_language, content):
    try:
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
        compute_response.raise_for_status()
        logger.info(f"Translation performed successfully for content.")
        return compute_response.json()
    except requests.RequestException as e:
        logger.error(f"Error performing translation. Error: {e}")
        return {"status_code": compute_response.status_code, "message": "Error in translation"}

def translate(source_language, content):
    response_data = make_translation_request(source_language)
    
    if "status_code" in response_data and response_data["status_code"] != 200:
        return response_data
    
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

def translate_chunks_pdf(source_language, pickle_dir="./pdf_chunks", output_dir="english_chunks"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    pickle_files = [f for f in os.listdir(pickle_dir) if f.endswith('.pkl')]

    translation_results = {}

    for pickle_file in pickle_files:
        with open(os.path.join(pickle_dir, pickle_file), 'rb') as file:
            docObjs = pickle.load(file)

        chunk_counter = 0
        for docObj in docObjs:
            source_chunks = docObj.page_content
            logger.info(f"Translating chunk {chunk_counter} of {pickle_file}.")
            translated_chunks = translate(source_language, source_chunks)
            
            if translated_chunks["status_code"] == 200:
                translated_content = translated_chunks["translated_content"]
                logger.info(f"Chunk {chunk_counter} of {pickle_file} translated successfully.")
            else:
                translated_content = ""
                logger.error(f"Error translating chunk {chunk_counter} of {pickle_file}: {translated_chunks['message']}")

            translation_results[f"{pickle_file}_{chunk_counter}"] = {
                "original_chunk": source_chunks,
                "translated_chunk": translated_content,
                "status": translated_chunks["status_code"],
                "message": translated_chunks["message"],
                "source_file": pickle_file
            }
            chunk_counter += 1
            docObj.page_content = translated_content

            # Save English pickle file
            output_pickle_file = os.path.join(output_dir, f"english_{pickle_file}")
            with open(output_pickle_file, 'wb') as output_file:
                pickle.dump(docObj, output_file)
    return translation_results

def translate_chunks_txt(source_language, pickle_dir="./txt_chunks", output_dir="english_chunks"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    pickle_files = [f for f in os.listdir(pickle_dir) if f.endswith('.pkl')]

    translation_results = {}

    for pickle_file in pickle_files:
        with open(os.path.join(pickle_dir, pickle_file), 'rb') as file:
            docObjs = pickle.load(file)

        chunk_counter = 0
        for docObj in docObjs:
            source_chunks = docObj.page_content
            logger.info(f"Translating chunk {chunk_counter} of {pickle_file}.")
            translated_chunks = translate(source_language, source_chunks)
            
            if translated_chunks["status_code"] == 200:
                translated_content = translated_chunks["translated_content"]
                logger.info(f"Chunk {chunk_counter} of {pickle_file} translated successfully.")
            else:
                translated_content = ""
                logger.error(f"Error translating chunk {chunk_counter} of {pickle_file}: {translated_chunks['message']}")

            translation_results[f"{pickle_file}_{chunk_counter}"] = {
                "original_chunk": source_chunks,
                "translated_chunk": translated_content,
                "status": translated_chunks["status_code"],
                "message": translated_chunks["message"],
                "source_file": pickle_file
            }
            chunk_counter += 1
            docObj.page_content = translated_content

            # Save English pickle file
            output_pickle_file = os.path.join(output_dir, f"english_{pickle_file}")
            with open(output_pickle_file, 'wb') as output_file:
                pickle.dump(docObj, output_file)
    return translation_results

def start_translation_pdf(source_language):
    return translate_chunks_pdf(source_language)

def start_translation_txt(source_language):
    return translate_chunks_txt(source_language)

# if __name__ == "__main__":
#     source_language = "hi" 
#     start_translation_pdf(source_language)
#     start_translation_txt(source_language)

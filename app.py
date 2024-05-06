import streamlit as st
import requests

# Define language codes
LANGUAGES = {
    "Hindi": 1,
    "Gom": 2,
    "Kannada": 3,
    "Dogri": 4,
    "Bodo": 5,
    "Urdu": 6,
    "Tamil": 7,
    "Kashmiri": 8,
    "Assamese": 9,
    "Bengali": 10,
    "Marathi": 11,
    "Sindhi": 12,
    "Maithili": 13,
    "Punjabi": 14,
    "Malayalam": 15,
    "Manipuri": 16,
    "Telugu": 17,
    "Sanskrit": 18,
    "Nepali": 19,
    "Santali": 20,
    "Gujarati": 21,
    "Odia": 22,
    "English": 23
}

# Streamlit app layout
st.title("Text Translation Service")

source_language = st.selectbox("Select source language", list(LANGUAGES.keys()))
target_language = st.selectbox("Select target language", list(LANGUAGES.keys()))

text_to_translate = st.text_area("Enter text to translate")

if st.button("Translate"):
    try:
        source_language_code = LANGUAGES[source_language]
        target_language_code = LANGUAGES[target_language]

        payload = {
            "source_language": source_language_code,
            "content": text_to_translate,
            "target_language": target_language_code
        }

        # Include the 'userID' header
        headers = {
            "userID": "e832f2d25d21443e8bb90515f1079041",
            "Content-Type": "application/json"
        }

        # Send HTTP POST request to the translation endpoint with headers
        response = requests.post('https://meity-auth.ulcacontrib.org/ulca/apis/v0/model/getModelsPipeline', json=payload, headers=headers)

        if response.status_code == 200:
            translation_data = response.json()
            service_id = translation_data["pipelineResponseConfig"][0]["config"][0]["serviceId"]

            compute_payload = {
                "pipelineTasks": [
                    {
                        "taskType": "translation",
                        "config": {
                            "language": {
                                "sourceLanguage": source_language_code,
                                "targetLanguage": target_language_code
                            },
                            "serviceId": service_id
                        }
                    }
                ],
                "inputData": {
                    "input": [
                        {
                            "source": text_to_translate
                        }
                    ],
                    "audio": [
                        {
                            "audioContent": None
                        }
                    ]
                }
            }

            callback_url = translation_data["pipelineInferenceAPIEndPoint"]["callbackUrl"]

            headers = {
                "Content-Type": "application/json",
                translation_data["pipelineInferenceAPIEndPoint"]["inferenceApiKey"]["name"]:
                    translation_data["pipelineInferenceAPIEndPoint"]["inferenceApiKey"]["value"]
            }

            compute_response = requests.post(callback_url, json=compute_payload, headers=headers)

            if compute_response.status_code == 200:
                compute_response_data = compute_response.json()
                translated_content = compute_response_data["pipelineResponse"][0]["output"][0]["target"]
                st.success(f"Translation successful:\n{translated_content}")
            else:
                st.error(f"Error in translation: {compute_response.text}")
        else:
            st.error(f"Error in translation request: {response.text}")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

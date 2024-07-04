import streamlit as st
from utils.audio_utils import get_encoded_string, is_base64
from utils.translation_utils import get_service_id, transcribe_and_translate, translate, get_languages,text_extract_and_chunker, delete_chunks_dirs


def main():
    st.title("Transcription and Translation")

    st.sidebar.title("Choose Input Type")

    input_type = st.sidebar.radio("Input Type", ("Audio", "Text", "PDF or Txt file"))

    if input_type == "Audio":
        st.write("Upload an audio file in FLAC format for transcription and translation")
        source_language = st.selectbox("Source Language", options=get_languages().values(), index=0)
        audio_file = st.file_uploader("Choose a FLAC file", type=["flac"])
        if st.button(" Transcribe plus Translate"):
            if audio_file:
                encoded_string, wav_file_content = get_encoded_string(audio_file)
                if is_base64(encoded_string):
                    st.success("File is valid")
                    service_id = get_service_id(source_language)
                  
                    if service_id:
                        result = transcribe_and_translate(encoded_string, service_id, source_language)
                        if result:
                            st.write("Transcription and Translation Result:")
                            st.json(result)
                else:
                    st.error("Invalid file format")

    elif input_type == "Text":
        st.write("Enter text for translation")
        source_language = st.selectbox("Source Language", options=get_languages().values(), index=0)
        text_content = st.text_area("Enter text here")

        if st.button("Translate"):
            result = translate(source_language, text_content)
            if result:
                st.write("Translation Result:")
                st.json(result)
    elif  input_type == "PDf" or "txt":
        if st.button("Start New Session"):
            delete_chunks_dirs()
        st.write("Upload an pdf or txt file for translation")
        source_language = st.selectbox("Source Language", options=get_languages().values(), index=0)
        uploaded_file = st.file_uploader("choose a pdf or txt", type=["pdf","txt"])
        text_extract_and_chunker(source_language, uploaded_file)
        if st.button("Start Translation"):
            start_translation(source_language)

if __name__ == "__main__":
    main()

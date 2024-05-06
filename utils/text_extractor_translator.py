import streamlit as st
from pdfminer.high_level import extract_text
from langchain.docstore.document import Document
import io
import os
import pickle
import shutil
import datetime
import zipfile
from deep_translator import GoogleTranslator

def translate_text(text, target_language='en', source_language='auto'):
    translation = GoogleTranslator(source=source_language, target=target_language).translate(text)
    return translation

def translate_chunks(pickle_dir="./pdf_chunks", output_dir="english_chunks"):
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
            translated_chunks = translate_text(source_chunks,target_language='en', source_language='auto')  # Assuming main function translates chunks to English
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

def split_text_into_chunks(text, chunk_size=4000, chunk_overlap=300):
    chunks = []
    for i in range(0, len(text), chunk_size - chunk_overlap):
        chunks.append(text[i:i + chunk_size])
    return chunks


def text_extract_and_chunker():
    st.title("PDF and TXT Chunker App")

    # Language selection dropdown
    language = st.selectbox("Select the language of the PDF", ["Hindi", "Kannada", "Marwari"])

    # Upload a PDF file, a TXT file, or a ZIP file containing multiple PDF/TXT files
    uploaded_file = st.file_uploader("Upload a PDF file, a TXT file, or a ZIP file containing multiple PDFs/TXTs", type=["pdf","txt","zip"])

    if uploaded_file is not None:
        if uploaded_file.type == "application/zip":
            # Extract and process each PDF/TXT file in the ZIP archive
            with zipfile.ZipFile(uploaded_file, "r") as zip_ref:
                for file_name in zip_ref.namelist():
                    with zip_ref.open(file_name) as file:
                        process_pdf_or_txt(file, language)
        else:
            # Process the uploaded PDF/TXT file
            process_pdf_or_txt(uploaded_file, language)
        st.success("Text has been extracted successfully.")
        st.write("Starting language translation")

def text_handler():
    text_extract_and_chunker()
    translate_chunks()

def delete_chunks_dirs():
    if os.path.exists("pdf_chunks"):
        shutil.rmtree("pdf_chunks")
    if os.path.exists("english_chunks"):
        shutil.rmtree("english_chunks")
    st.success("PDF chunks and English chunks directories have been deleted.")

if __name__ == "__main__":
   if st.button("Start New Session"):
       delete_chunks_dirs()
   text_handler()
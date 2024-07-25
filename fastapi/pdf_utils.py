import os
import zipfile
import shutil
import pickle
from pdfminer.high_level import extract_text
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from concurrent.futures import ThreadPoolExecutor
import tempfile
import logging
from logging.handlers import TimedRotatingFileHandler

# Configure logging
log_filename = "logs/pdf_processing.log"
log_handler = TimedRotatingFileHandler(log_filename, when="midnight", interval=1, backupCount=7)
log_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)


def is_zipfile(file_path):
    try:
        with zipfile.ZipFile(file_path) as zf:
            logger.info(f"{file_path} is a valid zip file.")
            return True
    except zipfile.BadZipFile:
        logger.error(f"{file_path} is not a valid zip file.")
        return False
    
def unzip_folder(zip_path, output_folder):
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(output_folder)
        logger.info(f"Unzipped {zip_path} to {output_folder}.")
    except Exception as e:
        logger.exception(f"Failed to unzip {zip_path}. Error: {e}")

def split_docs(documents, chunk_size=4000, chunk_overlap=300):
    try:
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        docs = text_splitter.split_text(documents)
        logger.info(f"Split documents into {len(docs)} chunks.")
        return docs
    except Exception as e:
        logger.exception(f"Error splitting documents. Error: {e}")
        return []

def process_pdf(pdf_path, pdf_chunk_dir="pdf_chunks", processed_pdfs_folder="processed_pdfs"):
    try:
        metadata = []
        docs = []
        docObjs = []
        content = extract_text(pdf_path)
        logger.info(f"Extracted text from {pdf_path}.")

        if not os.path.exists(processed_pdfs_folder):
            os.makedirs(processed_pdfs_folder)

        filename = os.path.basename(pdf_path)
        temp = {'filename': filename}
        temp['date_filename'] = True

        chunks = split_docs(content)
        num = len(chunks)
        data = [temp for _ in range(num)]
        metadata.extend(data)
        docs.extend(chunks)

        for j in range(num):
            doc_data = docs[j]
            doc_info = metadata[j]
            doc_obj = Document(page_content=doc_data, metadata=doc_info)
            docObjs.append(doc_obj)

        if not os.path.exists(pdf_chunk_dir):
            os.makedirs(pdf_chunk_dir)

        pickle_file = os.path.join(pdf_chunk_dir, f"{filename}.pkl")
        with open(pickle_file, 'wb') as file:
            pickle.dump(docObjs, file)

        shutil.move(pdf_path, processed_pdfs_folder)
        logger.info(f"Processed and moved {pdf_path} to {processed_pdfs_folder}.")

        return [{"page_content": doc.page_content, "metadata": doc.metadata} for doc in docObjs]
    except Exception as e:
        logger.exception(f"Error processing PDF {pdf_path}. Error: {e}")
        return []

def get_pdf_files(root_directory):
    pdf_files = []
    try:
        for root, dirs, files in os.walk(root_directory):
            for file in files:
                if file.lower().endswith('.pdf'):
                    pdf_files.append(os.path.join(root, file))
        logger.info(f"Found {len(pdf_files)} PDF files in {root_directory}.")
    except Exception as e:
        logger.exception(f"Error getting PDF files from {root_directory}. Error: {e}")
    return pdf_files

def delete_chunks_dirs():
    try:
        for directory in ["pdf_chunks", "processed_pdfs", "txt_chunks", "processed_txts", "english_chunks"]:
            if os.path.exists(directory):
                shutil.rmtree(directory)
                logger.info(f"Deleted directory {directory}.")
    except Exception as e:
        logger.exception(f"Error deleting chunk directories. Error: {e}")

def pdf_reader(file):
    results = []
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            file_location = os.path.join(temp_dir, file.filename)
            with open(file_location, "wb") as f:
                f.write(file.file.read())

            logger.info(f"Reading PDF file {file.filename}.")

            if is_zipfile(file_location):
                output_folder = os.path.join(temp_dir, 'original_pdfs')
                unzip_folder(file_location, output_folder)
                pdf_files = get_pdf_files(output_folder)
                num_workers = 5

                with ThreadPoolExecutor(max_workers=num_workers) as executor:
                    futures = [executor.submit(process_pdf, pdf_file) for pdf_file in pdf_files]
                    results = [future.result() for future in futures]
                logger.info(f"Processed zip file {file.filename} with {len(pdf_files)} PDFs.")
            else:
                if file_location.lower().endswith('.pdf'):
                    result = process_pdf(file_location)
                    results = [result]
                    logger.info(f"Processed single PDF file {file.filename}.")
                else:
                    logger.error(f"Invalid file format for {file.filename}. Only .pdf and .zip are supported.")
                    return None
    except Exception as e:
        logger.exception(f"Error reading PDF file {file.filename}. Error: {e}")
    return results

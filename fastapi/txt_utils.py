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
log_filename = "logs/txt_processing.log"
log_handler = TimedRotatingFileHandler(log_filename, when="midnight", interval=1, backupCount=7)
log_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)

def is_zipfile(file_path):
    try:
        with zipfile.ZipFile(file_path) as zf:
            return True
    except zipfile.BadZipFile:
        logger.error(f"Invalid zip file: {file_path}")
        return False
    
def unzip_folder(zip_path, output_folder):
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(output_folder)
            logger.info(f"Unzipped file: {zip_path} to {output_folder}")
    except Exception as e:
        logger.error(f"Failed to unzip file: {zip_path}. Error: {e}")

def split_docs(documents, chunk_size=4000, chunk_overlap=300):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    docs = text_splitter.split_text(documents)
    logger.info(f"Split documents into {len(docs)} chunks")
    return docs

def get_txt_files(root_directory):
    txt_files = []
    for root, dirs, files in os.walk(root_directory):
        for file in files:
            if file.lower().endswith('.txt'):
                txt_files.append(os.path.join(root, file))
    logger.info(f"Found {len(txt_files)} .txt files in {root_directory}")
    return txt_files

def txt_reader(file):
    results = []
    with tempfile.TemporaryDirectory() as temp_dir:
        file_location = os.path.join(temp_dir, file.filename)
        with open(file_location, "wb") as f:
            f.write(file.file.read())
            logger.info(f"Saved uploaded file to temporary location: {file_location}")

        if is_zipfile(file_location):
            output_folder = os.path.join(temp_dir, 'original_txts')
            unzip_folder(file_location, output_folder)
            txt_files = get_txt_files(output_folder)
            num_workers = 5

            with ThreadPoolExecutor(max_workers=num_workers) as executor:
                futures = [executor.submit(process_txt, txt_file) for txt_file in txt_files]
                results = [future.result() for future in futures]
        else:
            if file_location.lower().endswith('.txt'):
                result = process_txt(file_location)
                return result
            else:
                logger.warning(f"Unsupported file type: {file_location}")
                return None
    return results

def process_txt(txt_path, txt_chunk_dir="txt_chunks", processed_txts_folder="processed_txts"):
    metadata = []
    docs = []
    docObjs = []
    try:
        with open(txt_path, 'r', encoding='utf-8') as file:
            content = file.read()
        logger.info(f"Read content from {txt_path}")
    except Exception as e:
        logger.error(f"Failed to read file: {txt_path}. Error: {e}")
        return None

    if not os.path.exists(processed_txts_folder):
        os.makedirs(processed_txts_folder)

    filename = os.path.basename(txt_path)
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
    
    if not os.path.exists(txt_chunk_dir):
        os.makedirs(txt_chunk_dir)

    pickle_file = os.path.join(txt_chunk_dir, f"{filename}.pkl")
    try:
        with open(pickle_file, 'wb') as file:
            pickle.dump(docObjs, file)
        logger.info(f"Saved {len(docObjs)} document chunks to pickle file: {pickle_file}")
    except Exception as e:
        logger.error(f"Failed to save pickle file: {pickle_file}. Error: {e}")
        return None

    try:
        shutil.move(txt_path, processed_txts_folder)
        logger.info(f"Moved processed file {txt_path} to {processed_txts_folder}")
    except Exception as e:
        logger.error(f"Failed to move processed file: {txt_path}. Error: {e}")
        return None

    return [{"page_content": doc.page_content, "metadata": doc.metadata} for doc in docObjs]



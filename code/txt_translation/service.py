# protocols.py
from typing import Any, Protocol, List, Dict
from typing import Any, List, Dict
from concurrent.futures import ThreadPoolExecutor
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
import zipfile
import shutil
import pickle
import tempfile
import logging
from logging.handlers import TimedRotatingFileHandler

class TextProcessingService(Protocol):
    def process_txt(self, txt_path: str) -> List[Dict[str, Any]]:
        """Processes a text file and returns a list of document chunks."""
        ...

    def txt_reader(self, file: Any) -> List[Dict[str, Any]]:
        """Reads a text or zip file and returns processed document chunks."""
        ...


class _TextProcessingServiceImpl(TextProcessingService):
    def __init__(self, chunk_size=4000, chunk_overlap=300):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.logger = self._setup_logger()
        
    def _setup_logger(self):
        log_filename = "logs/txt_processing_service.log"
        log_handler = TimedRotatingFileHandler(log_filename, when="midnight", interval=1, backupCount=7)
        log_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        logger = logging.getLogger("TxtProcessingService")
        logger.setLevel(logging.INFO)
        logger.addHandler(log_handler)
        return logger

    def is_zipfile(self, file_path: str) -> bool:
        try:
            with zipfile.ZipFile(file_path) as zf:
                return True
        except zipfile.BadZipFile:
            self.logger.error(f"Invalid zip file: {file_path}")
            return False

    def unzip_folder(self, zip_path: str, output_folder: str) -> None:
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(output_folder)
            self.logger.info(f"Unzipped file: {zip_path} to {output_folder}")
        except Exception as e:
            self.logger.error(f"Failed to unzip file: {zip_path}. Error: {e}")

    def split_docs(self, documents: str) -> List[str]:
        # Assuming RecursiveCharacterTextSplitter exists in your context
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap)
        docs = text_splitter.split_text(documents)
        self.logger.info(f"Split documents into {len(docs)} chunks")
        return docs

    def get_txt_files(self, root_directory: str) -> List[str]:
        txt_files = []
        for root, dirs, files in os.walk(root_directory):
            for file in files:
                if file.lower().endswith('.txt'):
                    txt_files.append(os.path.join(root, file))
        self.logger.info(f"Found {len(txt_files)} .txt files in {root_directory}")
        return txt_files

    def txt_reader(self, file: Any) -> List[Dict[str, Any]]:
        results = []
        with tempfile.TemporaryDirectory() as temp_dir:
            file_location = os.path.join(temp_dir, file.filename)
            with open(file_location, "wb") as f:
                f.write(file.file.read())
            self.logger.info(f"Saved uploaded file to temporary location: {file_location}")

            if self.is_zipfile(file_location):
                output_folder = os.path.join(temp_dir, 'original_txts')
                self.unzip_folder(file_location, output_folder)
                txt_files = self.get_txt_files(output_folder)
                num_workers = 5

                with ThreadPoolExecutor(max_workers=num_workers) as executor:
                    futures = [executor.submit(self.process_txt, txt_file) for txt_file in txt_files]
                    results = [future.result() for future in futures]
            else:
                if file_location.lower().endswith('.txt'):
                    result = self.process_txt(file_location)
                    results = [result]
                else:
                    self.logger.warning(f"Unsupported file type: {file_location}")
        return results

    def process_txt(self, txt_path: str) -> List[Dict[str, Any]]:
        metadata = []
        docs = []
        docObjs = []
        try:
            with open(txt_path, 'r', encoding='utf-8') as file:
                content = file.read()
            self.logger.info(f"Read content from {txt_path}")
        except Exception as e:
            self.logger.error(f"Failed to read file: {txt_path}. Error: {e}")
            return []

        filename = os.path.basename(txt_path)
        temp = {'filename': filename}
        temp['date_filename'] = True

        chunks = self.split_docs(content)
        num = len(chunks)
        data = [temp for _ in range(num)]
        metadata.extend(data)
        docs.extend(chunks)

        for j in range(num):
            doc_data = docs[j]
            doc_info = metadata[j]
            doc_obj = Document(page_content=doc_data, metadata=doc_info)
            docObjs.append(doc_obj)

        return [{"page_content": doc.page_content, "metadata": doc.metadata} for doc in docObjs]


def service_implementer() -> TextProcessingService:
    return _TextProcessingServiceImpl()

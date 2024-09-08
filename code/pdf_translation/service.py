
import os
import zipfile
import shutil
import pickle
from pdfminer.high_level import extract_text
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from typing import Protocol, List, Dict, Any
from concurrent.futures import ThreadPoolExecutor
import logging

class PdfProcessingService(Protocol):
    def is_zipfile(self, file_path: str) -> bool:
        """Checks if the file is a valid zipfile."""
        ...

    def unzip_folder(self, zip_path: str, output_folder: str) -> None:
        """Unzips the given folder."""
        ...

    def split_docs(self, documents: str, chunk_size: int, chunk_overlap: int) -> List[str]:
        """Splits text into chunks."""
        ...

    def process_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Processes a PDF and returns the extracted text in chunks."""
        ...

    def process_pdfs_in_zip(self, zip_path: str) -> List[List[Dict[str, Any]]]:
        """Processes all PDFs within a zip file."""
        ...

    def get_pdf_files(self, root_directory: str) -> List[str]:
        """Returns a list of all PDF files in the given directory."""
        ...


class _PDFProcessingServiceImpl:
    def __init__(self, chunk_dir="pdf_chunks", processed_dir="processed_pdfs", logger=None):
        self.chunk_dir = chunk_dir
        self.processed_dir = processed_dir
        self.logger = logger or logging.getLogger(__name__)

    def is_zipfile(self, file_path):
        try:
            with zipfile.ZipFile(file_path) as zf:
                self.logger.info(f"{file_path} is a valid zip file.")
                return True
        except zipfile.BadZipFile:
            self.logger.error(f"{file_path} is not a valid zip file.")
            return False

    def unzip_folder(self, zip_path, output_folder):
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(output_folder)
            self.logger.info(f"Unzipped {zip_path} to {output_folder}.")
        except Exception as e:
            self.logger.exception(f"Failed to unzip {zip_path}. Error: {e}")

    def split_docs(self, documents, chunk_size=4000, chunk_overlap=300):
        try:
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
            docs = text_splitter.split_text(documents)
            self.logger.info(f"Split documents into {len(docs)} chunks.")
            return docs
        except Exception as e:
            self.logger.exception(f"Error splitting documents. Error: {e}")
            return []

    def process_pdf(self, pdf_path):
        try:
            metadata = []
            docs = []
            docObjs = []
            content = extract_text(pdf_path)
            self.logger.info(f"Extracted text from {pdf_path}.")

            filename = os.path.basename(pdf_path)
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

            if not os.path.exists(self.chunk_dir):
                os.makedirs(self.chunk_dir)

            pickle_file = os.path.join(self.chunk_dir, f"{filename}.pkl")
            with open(pickle_file, 'wb') as file:
                pickle.dump(docObjs, file)

            if not os.path.exists(self.processed_dir):
                os.makedirs(self.processed_dir)

            shutil.move(pdf_path, self.processed_dir)
            self.logger.info(f"Processed and moved {pdf_path} to {self.processed_dir}.")

            return [{"page_content": doc.page_content, "metadata": doc.metadata} for doc in docObjs]
        except Exception as e:
            self.logger.exception(f"Error processing PDF {pdf_path}. Error: {e}")
            return []

    def process_pdfs_in_zip(self, zip_path):
        try:
            results = []
            output_folder = os.path.join('temp_pdfs')
            self.unzip_folder(zip_path, output_folder)
            pdf_files = self.get_pdf_files(output_folder)
            
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(self.process_pdf, pdf_file) for pdf_file in pdf_files]
                results = [future.result() for future in futures]
                
            return results
        except Exception as e:
            self.logger.exception(f"Error processing zip file {zip_path}. Error: {e}")
            return []

    def get_pdf_files(self, root_directory):
        pdf_files = []
        try:
            for root, dirs, files in os.walk(root_directory):
                for file in files:
                    if file.lower().endswith('.pdf'):
                        pdf_files.append(os.path.join(root, file))
            self.logger.info(f"Found {len(pdf_files)} PDF files in {root_directory}.")
        except Exception as e:
            self.logger.exception(f"Error getting PDF files from {root_directory}. Error: {e}")
        return pdf_files

def service_implementer() -> PdfProcessingService:
    return _PDFProcessingServiceImpl()

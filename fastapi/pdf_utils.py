import os
import zipfile
import shutil
import pickle
from pdfminer.high_level import extract_text
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from concurrent.futures import ThreadPoolExecutor
import tempfile

def is_zipfile(file_path):
    try:
        with zipfile.ZipFile(file_path) as zf:
            return True
    except zipfile.BadZipFile:
        return False
    
def unzip_folder(zip_path, output_folder):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(output_folder)


def split_docs(documents, chunk_size=4000, chunk_overlap=300):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    docs = text_splitter.split_text(documents)
    return docs

def process_pdf(pdf_path, pdf_chunk_dir="pdf_chunks", processed_pdfs_folder="processed_pdfs"):
    metadata = []
    docs = []
    docObjs = []
    content = extract_text(pdf_path)
    
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
    return [{"page_content": doc.page_content, "metadata": doc.metadata} for doc in docObjs]

def get_pdf_files(root_directory):
    pdf_files = []
    for root, dirs, files in os.walk(root_directory):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_files.append(os.path.join(root, file))
    return pdf_files


def delete_chunks_dirs():
    if os.path.exists("pdf_chunks"):
        shutil.rmtree("pdf_chunks")
    if os.path.exists("processed_pdfs"):
        shutil.rmtree("processed_pdfs")
    if os.path.exists("txt_chunks"):
        shutil.rmtree("txt_chunks")
    if os.path.exists("processed_txts"):
        shutil.rmtree("processed_txts")
    if os.path.exists("english_chunks"):
        shutil.rmtree("english_chunks")


def pdf_reader(file):
    with tempfile.TemporaryDirectory() as temp_dir:
        file_location = os.path.join(temp_dir, file.filename)
        with open(file_location, "wb") as f:
            f.write(file.file.read())

        if is_zipfile(file_location):
            output_folder = os.path.join(temp_dir, 'original_pdfs')
            unzip_folder(file_location, output_folder)
            pdf_files = get_pdf_files(output_folder)
            num_workers = 5

            with ThreadPoolExecutor(max_workers=num_workers) as executor:
                futures = [executor.submit(process_pdf, pdf_file) for pdf_file in pdf_files]
                results = [future.result() for future in futures]
        else:
            if file_location.lower().endswith('.pdf'):
                result = process_pdf(file_location)
                return result
            else:
                return None
    return results


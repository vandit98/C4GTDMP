# main.py

from container import PdfProcessingServiceContainer

def main(file_path):
    service_container = PdfProcessingServiceContainer()
    pdf_service = service_container.pdf_processing_service_builder()

    if pdf_service.is_zipfile(file_path):
        print("Processing PDFs from zip...")
        results = pdf_service.process_pdfs_in_zip(file_path)
    else:
        print("Processing a single PDF...")
        results = pdf_service.process_pdf(file_path)

    if results:
        for doc in results:
            print(f"Page Content: {doc['page_content']}")
            print(f"Metadata: {doc['metadata']}")
    else:
        print("No documents processed.")

# if __name__ == "__main__":
#     main(file_path ="./")

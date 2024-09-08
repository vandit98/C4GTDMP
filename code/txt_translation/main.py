from container import TxtProcessingServiceContainer

def main(file_path):
    container = TxtProcessingServiceContainer()
    txt_service = container.txt_processing_service_builder()
    
    with open(file_path, "rb") as file:
        _ = txt_service.txt_reader(file)
        extracted_text_file_path ="./"
        translated_txt = txt_service.process_txt(extracted_text_file_path)
    for result in translated_txt:
        print(result)

if __name__ == "__main__":
    main(file_path="./")

from container import AudioProcessingServiceContainer

def main(audio_file_path: str) -> str:
    container = AudioProcessingServiceContainer()
    audio_service_builder = container.audio_processing_service_builder()

    # Build the AudioProcessingService
    audio_service = audio_service_builder.build()

    audio_data = audio_file_path
    encoded_string, wav_content = audio_service.get_encoded_string(audio_data)
    
    print(f"Encoded String: {encoded_string[:50]}...")

# if __name__ == "__main__":
#     main()

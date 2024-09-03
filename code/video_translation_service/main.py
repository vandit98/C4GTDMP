from container import VideoProcessingServiceContainer

def main():
    container = VideoProcessingServiceContainer()
    video_processing_service = container.video_processing_service_builder().build()

    video_processing_service.delete_output_dirs()
    
    video_files = ["path to video files"]
    flac_files = video_processing_service.convert_videos_to_flac(video_files)
    video_processing_service.process_flac_files()

if __name__ == "__main__":
    main()

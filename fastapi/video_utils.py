import os
import subprocess
import shutil
import logging
from logging.handlers import TimedRotatingFileHandler

log_filename = "logs/video_processing.log"
log_handler = TimedRotatingFileHandler(log_filename, when="midnight", interval=1, backupCount=7)
log_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)

def delete_output_dirs():
    if os.path.exists("outputs"):
        shutil.rmtree("outputs")
        logger.info("Output directories have been deleted.")
    else:
        logger.warning("No output directories found to delete.")

def convert_videos_to_flac(video_files, output_folder='outputs'):
    os.makedirs(output_folder, exist_ok=True)
    logger.info(f"Created output directory: {output_folder}")

    flac_files = []

    for i, video_file in enumerate(video_files):
        video_file_path = os.path.join(output_folder, f"video_{i}.mp4")
        flac_file = os.path.join(output_folder, f"video_{i}.flac")

        try:
            with open(video_file_path, 'wb') as f:
                f.write(video_file.read())
            logger.info(f"Saved video file: {video_file_path}")

            subprocess.run(['ffmpeg', '-i', video_file_path, flac_file], check=True)
            logger.info(f"Converted {video_file_path} to {flac_file}")

            flac_files.append(flac_file)

            os.remove(video_file_path)
            logger.info(f"Removed video file: {video_file_path}")
        except Exception as e:
            logger.error(f"Error processing {video_file_path}. Error: {e}")

    logger.info("Conversion completed!")
    return flac_files

def process_flac_files(output_folder='outputs'):
    flac_files = [f for f in os.listdir(output_folder) if f.endswith('.flac')]
    logger.info(f"Found {len(flac_files)} FLAC files in {output_folder}")

    for flac_file in flac_files:
        flac_path = os.path.join(output_folder, flac_file)
        logger.info(f"Processing {flac_path}")



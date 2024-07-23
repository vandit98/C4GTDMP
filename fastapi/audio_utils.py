import os
import logging
import requests
import base64
from pydub import AudioSegment
import binascii
import uuid
from urllib.parse import urlparse
from typing import Any
import zipfile
from io import BytesIO
from logging.handlers import TimedRotatingFileHandler

log_filename = "./logs/audio_processing.log"
log_handler = TimedRotatingFileHandler(log_filename, when="midnight", interval=1, backupCount=7)
log_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)
class RequestError(Exception):
    def __init__(self, response):
        self.response = response
        logger.error(f"RequestError with response: {response}")

def get_encoded_string(audio: Any):
    try:
        logger.info("Starting to process audio input")
        
        if isinstance(audio, str) and is_url(audio):
            logger.info("Audio input is a URL")
            local_filename = generate_temp_filename("mp3")
            with requests.get(audio) as r:
                with open(local_filename, 'wb') as f:
                    f.write(r.content)
        elif isinstance(audio, str) and is_base64(audio):
            logger.info("Audio input is a base64 string")
            local_filename = generate_temp_filename("mp3")
            decoded_audio_content = base64.b64decode(audio)
            with open(local_filename, "wb") as output_mp3_file:
                output_mp3_file.write(decoded_audio_content)
        else:
            logger.info("Audio input is a file-like object")
            local_filename = generate_temp_filename("mp3")
            with open(local_filename, "wb") as output_file:
                output_file.write(audio.read())
        
        logger.info("Converting audio to WAV format")
        output_file = AudioSegment.from_file(local_filename)
        mp3_output_file = output_file.export(local_filename, format="mp3")
        given_audio = AudioSegment.from_file(mp3_output_file)
        given_audio = given_audio.set_frame_rate(16000)
        given_audio = given_audio.set_channels(1)
        tmp_wav_filename = generate_temp_filename("wav")
        given_audio.export(tmp_wav_filename, format="wav", codec="pcm_s16le")
        
        with open(tmp_wav_filename, "rb") as wav_file:
            wav_file_content = wav_file.read()
        
        encoded_string = base64.b64encode(wav_file_content).decode('ascii', 'ignore')
        
        logger.info("Audio processing complete")
        
        os.remove(local_filename)
        os.remove(tmp_wav_filename)
        
        return encoded_string, wav_file_content
    except Exception as e:
        logger.exception("Error processing audio input")
        raise e

def is_base64(base64_string):
    try:
        base64.b64decode(base64_string)
        logger.info("Base64 validation successful")
        return True
    except (binascii.Error, UnicodeDecodeError):
        logger.error("Base64 validation failed")
        return False

def is_url(string):
    try:
        result = urlparse(string)
        is_valid = all([result.scheme, result.netloc])
        if is_valid:
            logger.info("URL validation successful")
        else:
            logger.error("URL validation failed")
        return is_valid
    except ValueError:
        logger.error("URL validation failed due to ValueError")
        return False

def generate_temp_filename(ext, prefix="temp"):
    filename = f"{prefix}_{uuid.uuid4()}.{ext}"
    logger.info(f"Generated temporary filename: {filename}")
    return filename



from typing import Protocol, Tuple, Any
import os
import requests
import base64
import binascii
import uuid
from urllib.parse import urlparse
from pydub import AudioSegment
from typing import Any, Tuple

class AudioProcessingService(Protocol):
    def get_encoded_string(self, audio: Any) -> Tuple[str, bytes]: ...
    def is_base64(self, base64_string: str) -> bool: ...
    def is_url(self, string: str) -> bool: ...
    def generate_temp_filename(self, ext: str, prefix: str = "temp") -> str: ...




class _AudioProcessingServiceImpl:
    def get_encoded_string(self, audio: Any) -> Tuple[str, bytes]:
        if isinstance(audio, str) and self.is_url(audio):
            local_filename = self.generate_temp_filename("mp3")
            with requests.get(audio) as r:
                with open(local_filename, 'wb') as f:
                    f.write(r.content)
        elif isinstance(audio, str) and self.is_base64(audio):
            local_filename = self.generate_temp_filename("mp3")
            decoded_audio_content = base64.b64decode(audio)
            with open(local_filename, "wb") as output_mp3_file:
                output_mp3_file.write(decoded_audio_content)
        else:
            local_filename = self.generate_temp_filename("mp3")
            with open(local_filename, "wb") as output_file:
                output_file.write(audio.read())
        
        output_file = AudioSegment.from_file(local_filename)
        mp3_output_file = output_file.export(local_filename, format="mp3")
        given_audio = AudioSegment.from_file(mp3_output_file)
        given_audio = given_audio.set_frame_rate(16000)
        given_audio = given_audio.set_channels(1)
        tmp_wav_filename = self.generate_temp_filename("wav")
        given_audio.export(tmp_wav_filename, format="wav", codec="pcm_s16le")
        with open(tmp_wav_filename, "rb") as wav_file:
            wav_file_content = wav_file.read()
        encoded_string = base64.b64encode(wav_file_content).decode('ascii', 'ignore')
        os.remove(local_filename)
        os.remove(tmp_wav_filename)
        return encoded_string, wav_file_content

    def is_base64(self, base64_string: str) -> bool:
        try:
            base64.b64decode(base64_string)
            return True
        except (binascii.Error, UnicodeDecodeError):
            return False

    def is_url(self, string: str) -> bool:
        try:
            result = urlparse(string)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False

    def generate_temp_filename(self, ext: str, prefix: str = "temp") -> str:
        return f"{prefix}_{uuid.uuid4()}.{ext}"



def service_implementer() ->AudioProcessingService:
    return _AudioProcessingServiceImpl()


class RequestError(Exception):
    def __init__(self, response):
        self.response = response

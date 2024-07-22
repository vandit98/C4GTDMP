from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from pydantic import BaseModel
from typing import List
from fastapi.responses import JSONResponse
from io import BytesIO
import zipfile

from audio_utils import get_encoded_string, is_base64
from translation_utils import get_service_id, transcribe_and_translate, translate, get_languages, start_translation_pdf, start_translation_txt
from video_utils import convert_videos_to_flac, delete_output_dirs
from pdf_utils import delete_chunks_dirs, pdf_reader
from txt_utils import txt_reader

app = FastAPI()

class TextTranslationRequest(BaseModel):
    source_language: str
    text_content: str

@app.post("/translate_audio/")
async def transcribe_audio(source_language: str = Form(...), audio_file: UploadFile = File(...)):

    try:
        if not audio_file.filename.endswith(".flac"):
            raise HTTPException(status_code=400, detail="Invalid file format. Only .flac files are supported.")
        
        encoded_string, wav_file_content = get_encoded_string(BytesIO(await audio_file.read()))
        if is_base64(encoded_string):
            service_id = get_service_id(source_language)
            if service_id:
                result = transcribe_and_translate(encoded_string, service_id, source_language)
                return JSONResponse(content={"result": result})
            else:
                raise HTTPException(status_code=400, detail="Service ID not found")
        else:
            raise HTTPException(status_code=400, detail="Invalid file format")
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/translate_audio_zip/")
async def transcribe_audio_zip(source_language: str = Form(...), zip_file: UploadFile = File(...)):
    try:
        if not audio_file.filename.endswith(".zip"):
            raise HTTPException(status_code=400, detail="Invalid file format. Only .zip files are supported.")
        
        results = []
        with zipfile.ZipFile(BytesIO(await zip_file.read()), "r") as zip_ref:
            for file_name in zip_ref.namelist():
                if file_name.endswith(".flac"):
                    with zip_ref.open(file_name) as file:
                        audio_file = BytesIO(file.read())
                        encoded_string, wav_file_content = get_encoded_string(audio_file)
                        if is_base64(encoded_string):
                            service_id = get_service_id(source_language)
                            if service_id:
                                result = transcribe_and_translate(encoded_string, service_id, source_language)
                                results.append({"file_name": file_name, "result": result})
                            else:
                                results.append({"file_name": file_name, "error": "Service ID not found"})
                        else:
                            results.append({"file_name": file_name, "error": "Invalid file format"})
        return JSONResponse(content={"results": results})
    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="Invalid ZIP file")
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/translate_text/")
async def translate_text(request: TextTranslationRequest):
    try:
        result = translate(request.source_language, request.text_content)
        return JSONResponse(content={"result": result})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/translate_pdf/")
async def translate_pdf(source_language: str = Form(...), uploaded_file: UploadFile = File(...)):
    try:
        if not (uploaded_file.filename.endswith(".pdf") or uploaded_file.filename.endswith(".zip")):
            raise HTTPException(status_code=400, detail="Invalid file format. Only .zip and .pdf files are supported.")
        
        delete_chunks_dirs()
        _ = pdf_reader(uploaded_file)
        
        translation_results = start_translation_pdf(source_language)
        delete_chunks_dirs()
        return JSONResponse(content=translation_results)
    except Exception as e:
        delete_chunks_dirs()
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/translate_txt/")
async def translate_txt(source_language: str = Form(...), uploaded_file: UploadFile = File(...)):
    try:
        if not (uploaded_file.filename.endswith(".txt") or uploaded_file.filename.endswith(".zip")):
            raise HTTPException(status_code=400, detail="Invalid file format. Only .zip and .txt files are supported.")
        
        delete_chunks_dirs()
        _ = txt_reader(uploaded_file)

        translation_results = start_translation_txt(source_language)
        delete_chunks_dirs()
        return JSONResponse(content=translation_results)
    except Exception as e:
        delete_chunks_dirs()
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/translate_video/")
async def transcribe_video(source_language: str = Form(...), video_file: UploadFile = File(...)):
    try:
        if not video_file.filename.endswith(".mp4"):
            raise HTTPException(status_code=400, detail="Invalid file format. Only .zip and .pdf files are supported.")
        
        delete_output_dirs()
        video_content = await video_file.read()
        flac_files = convert_videos_to_flac([BytesIO(video_content)])
        results = []
        for flac_file in flac_files:
            with open(flac_file, 'rb') as audio_file:
                encoded_string, wav_file_content = get_encoded_string(audio_file)
                if is_base64(encoded_string):
                    service_id = get_service_id(source_language)
                    if service_id:
                        result = transcribe_and_translate(encoded_string, service_id, source_language)
                        results.append({"result": result})
                    else:
                        results.append({"error": "Service ID not found"})
                else:
                    results.append({"error": "Invalid file format"})
        return JSONResponse(content={"results": results})
    except Exception as e:
        delete_output_dirs()
        return JSONResponse(content={"error": str(e)}, status_code=500)

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)

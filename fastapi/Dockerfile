FROM python:3.12

WORKDIR /fastapi

RUN apt-get update && apt-get install -y ffmpeg && apt-get clean

COPY . /fastapi

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "8"]

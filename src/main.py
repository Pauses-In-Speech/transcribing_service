import os.path
from typing import Union

import aiofiles
import auditok
import uvicorn
import whisper_timestamped as whisper
from fastapi import FastAPI, UploadFile

from src.config import Config

app = FastAPI()


def init_model(config: Config):
    return whisper.load_model(config.whisper_model_size, device=config.device)


def whisper_transcribe(model, audio_path):
    audio = whisper.load_audio(audio_path)
    return whisper.transcribe(model, audio)


def find_pauses():
    region = auditok.load(config.local_tmp_path)  # returns an AudioRegion object
    return region.split(drop_trailing_silence=True)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/transcribe")
async def create_upload_file(file: Union[UploadFile, None] = None):
    if not file:
        return {"message": "No upload file sent"}
    else:
        #  save uploaded file to tmp
        local_audio_path = os.path.join(config.local_tmp_path, file.filename)
        async with aiofiles.open(local_audio_path, 'wb') as out_file:
            content = await file.read()  # async read
            await out_file.write(content)  # async write
        return whisper_transcribe(model, local_audio_path)


if __name__ == '__main__':
    config = Config()
    model = init_model(config)

    uvicorn.run(app, host="0.0.0.0", port=8000)

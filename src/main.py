import json
import os.path

import aiofiles
import auditok
import uvicorn

from typing import Annotated, Union

import whisper_timestamped as whisper
from fastapi import FastAPI, File, UploadFile

from src.config import Config

app = FastAPI()


def whisper_transcribe(config):
    audio = whisper.load_audio(config.audio_path)
    whisper_model = whisper.load_model(config.whisper_model, device=config.device)
    return whisper.transcribe(whisper_model, audio)


def main():
    config = Config()
    result = whisper_transcribe(config)

    with open("whisper_result.json", "w") as out_file:
        out_file.write(json.dumps(result, indent=2, ensure_ascii=False))

    region = auditok.load(config.audio_path)  # returns an AudioRegion object
    regions = region.split_and_plot(drop_trailing_silence=True)  # or just region.splitp()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/transcribe")
async def create_upload_file(file: Union[UploadFile, None] = None):
    if not file:
        return {"message": "No upload file sent"}
    else:
        #  save uploaded file to tmp
        async with aiofiles.open(os.path.join(config.local_audio_path, file.filename), 'wb') as out_file:
            content = await file.read()  # async read
            await out_file.write(content)  # async write
        return whisper_transcribe(config)


if __name__ == '__main__':
    config = Config()

    uvicorn.run(app, host="0.0.0.0", port=8000)

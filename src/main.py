import os.path
from typing import Union

import aiofiles
import uvicorn
from fastapi import FastAPI, UploadFile

from src.config import Config
from src.silences import find_silences
from src.whisper_funcs import whisper_transcribe, init_model

app = FastAPI()


async def store_audio_file(file):
    local_audio_path = os.path.join(config.local_tmp_path, file.filename)
    async with aiofiles.open(local_audio_path, 'wb') as out_file:
        content = await file.read()  # async read
        await out_file.write(content)  # async write
    return local_audio_path


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/transcribe")
async def transcribe_audio_file(file: Union[UploadFile, None] = None):
    if not file:
        return {"message": "No upload file sent"}
    else:
        local_audio_path = await store_audio_file(file)
        return whisper_transcribe(model, local_audio_path)


@app.post("/silences")
async def find_silences_in_file(file: Union[UploadFile, None] = None):
    if not file:
        return {"message": "No upload file sent"}
    else:
        local_audio_path = await store_audio_file(file)
        return {
            "silences": find_silences(local_audio_path)
        }


if __name__ == '__main__':
    config = Config()
    model = init_model(config)

    uvicorn.run(app, host="0.0.0.0", port=8000)

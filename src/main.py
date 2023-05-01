import os.path
import tempfile
from typing import Union

import aiofiles
import auditok
import uvicorn
from fastapi import FastAPI, UploadFile
from fastapi.responses import FileResponse

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


@app.post("/upload")
async def upload_file(file: Union[UploadFile, None] = None):
    if not file:
        return {"message": "No upload file sent"}
    else:
        local_audio_path = await store_audio_file(file)
        return {
            "file_save_location": local_audio_path
        }


@app.post("/pause_image")
async def image(file: Union[UploadFile, None] = None):
    if not file:
        return {"message": "No upload file sent"}
    else:
        local_audio_path = await store_audio_file(file)
    region = auditok.load(local_audio_path)
    _, tmp_file = tempfile.mkstemp(suffix=".png")
    _ = region.split_and_plot(drop_trailing_silence=True, save_as=tmp_file, show=False)
    # TODO remove file after returning
    return FileResponse(tmp_file)


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

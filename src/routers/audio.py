import os

import aiofiles
from fastapi import APIRouter, Depends
from typing import Union
from fastapi import UploadFile, status

from src.config import get_config
from src.routers.speech import Speech

# from src.routers.speech import Speech

router = APIRouter(
    prefix="/audio",
    dependencies=[Depends(get_config)]
)

audio_db = {}


@router.get("/")
async def get_audios():
    return audio_db


@router.get("/{audio_id}")
async def get_audios(audio_id: int):
    if audio_id in audio_db:
        return audio_db[audio_id]


async def store_audio_file(file):
    local_audio_path = os.path.join(get_config().local_tmp_path, file.filename)
    async with aiofiles.open(local_audio_path, 'wb') as out_file:
        content = await file.read()  # async read
        await out_file.write(content)  # async write
    return local_audio_path


@router.post("/", status_code=status.HTTP_201_CREATED)
async def upload_file(file: Union[UploadFile, None] = None):
    if file.filename not in audio_db:
        if not file:
            return {"message": "No upload file sent"}
        else:
            local_audio_path = await store_audio_file(file)
            audio_db[file.filename] = local_audio_path
            Speech(get_config(), local_audio_path)
            return {
                "file_save_location": local_audio_path
            }
    else:
        return {"File already exists"}

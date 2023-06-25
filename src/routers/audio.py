from src.config import get_config
from src.routers.speech import Speech

import os

import aiofiles
from fastapi import APIRouter, Depends
from typing import Union
from fastapi import UploadFile, status

from sqlitedict import SqliteDict

# from src.routers.speech import Speech

router = APIRouter(
    prefix="/audio",
    dependencies=[Depends(get_config)]
)

audio_db_table = SqliteDict(get_config().db_name, tablename="audio", autocommit=True)


@router.get("/")
async def get_audios():
    return audio_db_table.values()


@router.get("/{audio_id}")
async def get_audios(audio_id: int):
    if audio_id in audio_db_table.keys():
        return audio_db_table[audio_id]


async def store_audio_file(file):
    local_audio_path = f"{get_config().local_data_path}/audio/{file.filename}"
    async with aiofiles.open(local_audio_path, 'wb') as out_file:
        content = await file.read()  # async read
        await out_file.write(content)  # async write
    return local_audio_path


def get_id_from_filename(filename: str) -> str:
    return filename.split(".")[:-1][0]


@router.post("/", status_code=status.HTTP_201_CREATED)
async def upload_file(file: Union[UploadFile, None] = None):
    new_audio_id = get_id_from_filename(file.filename)
    if file.filename not in audio_db_table:
        if file.content_type not in get_config().allowed_content_types:
            # TODO return correct http status code
            return {"message": "Document type not supported! Use mp3 or wav!"}
        elif not file:
            return {"message": "No upload file sent"}
        else:
            local_audio_path = await store_audio_file(file)
            audio_db_table[new_audio_id] = local_audio_path
            Speech(get_config(), local_audio_path)
            return {
                "file_save_location": local_audio_path
            }
    else:
        return {"File already exists"}

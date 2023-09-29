from pathlib import Path
from typing import Union

import aiofiles
from fastapi import APIRouter, Depends
from fastapi import UploadFile, status
from sqlitedict import SqliteDict
from starlette.responses import FileResponse

from src.config import get_config
from src.custom_classes.audio import Audio
from src.custom_classes.user_management import User
from src.routers.speech import create_speech
from src.user_management.users import fastapi_users

current_user = fastapi_users.current_user(optional=True)

router = APIRouter(
    prefix="/audio",
    dependencies=[Depends(get_config), Depends(current_user)],
    tags=["Audio 🎵"]
)

audio_db_table = SqliteDict(get_config().db_name, tablename="audio", autocommit=True)


def reload_audio_db():
    global audio_db_table
    audio_db_table = {}
    audio_db_table = SqliteDict(get_config().db_name, tablename="audio", autocommit=True)


def get_userid_and_user_audios(user: User, audio_db_table=audio_db_table):
    user_id: str = str(user.id) if user else "default"
    user_audios = {audio_id: audio for audio_id, audio in audio_db_table.items() if
                   (audio and audio.user_id == user_id)}
    return user_id, user_audios


@router.get("/")
async def get_audios(user: User = Depends(current_user)):
    _, user_audios = get_userid_and_user_audios(user, audio_db_table)
    return list(user_audios.values())


@router.get("/{audio_id}")
async def get_audio_info(audio_id: str, user: User = Depends(current_user)):
    _, user_audios = get_userid_and_user_audios(user, audio_db_table)
    if audio_id in user_audios:
        return audio_db_table[audio_id]
    else:
        return {"Audio ID not in user DB!"}


@router.get("/download/{audio_id}")
async def download_audio(audio_id: str, user: User = Depends(current_user)):
    _, user_audios = get_userid_and_user_audios(user, audio_db_table)
    if audio_id in user_audios:
        return FileResponse(path=audio_db_table[audio_id].file_path,
                            filename=f"{audio_id}.{audio_db_table[audio_id].file_type}",
                            media_type=audio_db_table[audio_id].content_type)


async def store_audio_file(file, user_id):
    local_audio_path = f"{get_config().local_data_path}/audio/{user_id}/{file.filename}"
    Path("/".join(local_audio_path.split("/")[:-1])).mkdir(parents=True, exist_ok=True)
    async with aiofiles.open(local_audio_path, 'wb') as out_file:
        content = await file.read()  # async read
        await out_file.write(content)  # async write
    return local_audio_path


@router.post("/", status_code=status.HTTP_201_CREATED)
async def upload_file(file: Union[UploadFile, None] = None, user: User = Depends(current_user)):
    user_id, user_audios = get_userid_and_user_audios(user, audio_db_table)
    new_audio_id = f"{user_id}_{file.filename.split('.')[:-1][0]}"

    if new_audio_id not in user_audios:
        if file.content_type not in get_config().allowed_content_types:
            # TODO return correct http status code
            return {"message": "Document type not supported! Use mp3 or wav!"}
        elif not file:
            return {"message": "No upload file sent"}
        else:
            local_audio_path = await store_audio_file(file, user_id)
            audio_db_table[new_audio_id] = Audio(local_audio_path,
                                                 file.filename.split(".")[-1],
                                                 file.content_type,
                                                 user_id)
            create_speech(get_config(), audio_db_table[new_audio_id])
            return {
                "message": "File successfully uploaded!",
                "audio_id": new_audio_id
            }
    else:
        return {
            "message": "File already exists",
            "audio_id": new_audio_id
        }


@router.delete("/{audio_id}")
def delete_audio(audio_id: str, user: User = Depends(current_user)):
    user_id, user_audios = get_userid_and_user_audios(user, audio_db_table)
    if audio_id in user_audios:
        res = audio_db_table.pop(audio_id)
        if res:
            return {"message": f"Deleted {audio_id}!"}
        else:
            return {"message": f"Could not delete {audio_id}"}
    else:
        return {"message": f"{audio_id} not found!"}

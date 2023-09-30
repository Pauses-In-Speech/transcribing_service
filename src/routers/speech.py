import io
import shutil
from typing import Union

import aiofiles
from fastapi import APIRouter, Depends, UploadFile
from sqlitedict import SqliteDict

from src.custom_classes.user_management import User
from src.config import Config, get_config
from src.custom_classes.speech import Speech, TranscriptPost
from src.routers.audio import Audio
from src.user_management.users import fastapi_users

current_user = fastapi_users.current_user()

router = APIRouter(
    prefix="/speech",
    dependencies=[Depends(get_config), Depends(current_user)],
    tags=["Speech 🗣️"]
)

speech_db_table = SqliteDict(get_config().db_name, tablename="speech", autocommit=True)


def reload_speech_db():
    global speech_db_table
    speech_db_table = {}
    speech_db_table = SqliteDict(get_config().db_name, tablename="speech", autocommit=True)


def get_userid_and_user_speeches(user: User, speech_db_table=speech_db_table):
    user_id: str = str(user.id) if user else "default"
    user_speeches = {speech_id: speech for speech_id, speech in speech_db_table.items() if
                     (speech and speech.user_id == user_id)}
    return user_id, user_speeches


def create_speech(config: Config, audio: Audio):
    new_id = f"{audio.user_id}_{audio.file_path.split('.')[-2].split('/')[-1]}"
    if new_id not in speech_db_table:
        speech = Speech(config, audio)
        speech_db_table[new_id] = speech
    else:
        print("This ID already exists!")


@router.get("/")
def get_speeches(user: User = Depends(current_user)):
    _, user_speeches = get_userid_and_user_speeches(user, speech_db_table)
    return list(user_speeches.values())


@router.get("/{speech_id}")
async def get_speech_info(speech_id: str, user: User = Depends(current_user)):
    user_id, user_speeches = get_userid_and_user_speeches(user, speech_db_table)
    user_speech_id = f"{user_id}_{speech_id}"

    if user_speech_id in user_speeches:
        return speech_db_table[user_speech_id]
    else:
        return {"Speech ID not in user DB!"}


@router.get("/statistics/{speech_id}")
async def get_speech_obj_statistics(speech_id: str, user: User = Depends(current_user)):
    user_id, user_speeches = get_userid_and_user_speeches(user, speech_db_table)
    user_speech_id = f"{user_id}_{speech_id}"

    if user_speech_id in user_speeches:
        return speech_db_table[user_speech_id].get_statistics()
    else:
        return {
            "message": f"Could not find speech with id: {speech_id}"
        }


@router.post("/transcript/")
async def upload_verified_transcript(speech_id: str, file: Union[UploadFile, None] = None,
                                  user: User = Depends(current_user)):
    user_id, user_speeches = get_userid_and_user_speeches(user, speech_db_table)
    user_speech_id = f"{user_id}_{speech_id}"
    current_speech: Speech = user_speeches.get(user_speech_id)

    if current_speech:
        local_transcript_path = f"{get_config().local_data_path}/audio/{user_id}/{file.filename}"
        async with aiofiles.open(local_transcript_path, 'wb') as out_file:
            content = await file.read()  # async read
            await out_file.write(content)  # async write

        corpus = []
        with open(local_transcript_path, "r") as in_file:
            for line in in_file:
                corpus.append(line)

        current_speech.correct_transcription(corpus)
        shutil.rmtree(local_transcript_path)  # delete local transcript file after use
        return current_speech.transcription
    else:
        return {
            "message": f"Could not find speech with id: {speech_id}"
        }


@router.delete("/{speech_id}")
def delete_speech(speech_id: str, user: User = Depends(current_user)):
    user_id, user_speeches = get_userid_and_user_speeches(user, speech_db_table)
    user_speech_id = f"{user_id}_{speech_id}"

    if user_speech_id in user_speeches:
        res = speech_db_table.pop(user_speech_id)
        if res:
            return {"message": f"Deleted {speech_id}!"}
        else:
            return {"message": f"Could not delete {speech_id}"}

    else:
        return {"message": f"{speech_id} not found!"}

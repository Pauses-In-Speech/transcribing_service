from fastapi import APIRouter, Depends
from sqlitedict import SqliteDict
from starlette.responses import FileResponse

from src.config import Config, get_config
from src.custom_classes.speech import Speech, TranscriptPost
from src.routers.audio import Audio

router = APIRouter(
    prefix="/speech",
    dependencies=[Depends(get_config)],
    tags=["Speech 🗣️"]
)

speech_db_table = SqliteDict(get_config().db_name, tablename="speech", autocommit=True)


def reload_speech_db():
    global speech_db_table
    speech_db_table = {}
    speech_db_table = SqliteDict(get_config().db_name, tablename="speech", autocommit=True)


def create_speech(config: Config, audio: Audio):
    new_id = audio.file_path.split(".")[-2].split("/")[-1]
    if new_id not in speech_db_table:
        speech = Speech(config, audio)
        speech_db_table[new_id] = speech
    else:
        print("This ID already exists!")


@router.get("/")
def get_speeches():
    return speech_db_table.values()


@router.get("/{speech_id}")
async def get_speech_info(speech_id: str):
    if speech_id in speech_db_table:
        return speech_db_table[speech_id]
    else:
        return {"Speech ID not in DB!"}


@router.get("/statistics/{speech_id}")
async def get_speech_obj_statistics(speech_id: str):
    current_speech: Speech = speech_db_table.get(speech_id)

    if current_speech:
        return current_speech.get_statistics()
    else:
        return {
            "message": f"Could not find speech with id: {speech_id}"
        }


@router.post("/transcript/")
async def add_verified_transcript(transcript: TranscriptPost):
    current_speech: Speech = speech_db_table.get(transcript.speech_id)

    if current_speech:
        current_speech.correct_transcription(transcript.corrected_transcript)
        return current_speech.transcription
    else:
        return {
            "message": f"Could not find speech with id: {transcript.speech_id}"
        }


@router.delete("/{speech_id}")
def delete_speech(speech_id: str):
    if speech_id in speech_db_table:
        res = speech_db_table.pop(speech_id)
        if res:
            return {"message": f"Deleted {speech_id}!"}
        else:
            return {"message": f"Could not delete {speech_id}"}

    else:
        return {"message": f"{speech_id} not found!"}

from fastapi import APIRouter, Depends
from sqlitedict import SqliteDict
from starlette.responses import FileResponse

from src.config import Config, get_config
from src.custom_classes.speech import Speech
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


@router.get("/auditok_image/{speech_id}")
async def get_auditok_image(speech_id: str, width: int = 720, height: int = 80):
    current_speech: Speech = speech_db_table.get(speech_id)

    if current_speech:
        current_speech.save_auditok_image(width, height)
        return FileResponse(path=f"{current_speech.speech_dir}/auditok_image.png",
                            filename=f"{speech_id}_auditok_image.png]",
                            media_type="image/png")
    else:
        return {
            "message": f"Could not find speech with id: {speech_id}"
        }


@router.get("/pause_image/{speech_id}")
async def get_pause_image(speech_id: str, width: int = 720, height: int = 40):
    current_speech: Speech = speech_db_table.get(speech_id)

    if current_speech:
        current_speech.generate_and_save_pause_image(width, height)
        return FileResponse(path=f"{current_speech.speech_dir}/pause_image.png",
                            filename=f"{speech_id}_pause_image.png]",
                            media_type="image/png")
    else:
        return {
            "message": f"Could not find speech with id: {speech_id}"
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

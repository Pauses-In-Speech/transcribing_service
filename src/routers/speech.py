import os

import auditok
from fastapi import APIRouter, Depends

from src.config import Config
from src.silences import find_silences
from src.whisper_funcs import whisper_transcribe, init_model

router = APIRouter(
    prefix="/speech"
)

speeches = []


class Speech:
    def __init__(self,
                 config: Config,
                 audio_file_path):

        new_id = audio_file_path.split(".")[:-1][0]
        if not any(x.id == new_id for x in speeches):
            self.id = new_id

            self.speech_dir = os.path.join(config.local_tmp_path, self.id)
            os.mkdir(self.speech_dir)
            self.audio_path = audio_file_path

            self.pause_image_path = os.path.join(self.speech_dir, "pause_image.png")
            self.save_pause_image()
            self.silences = find_silences(self.audio_path)

            self.transcription = whisper_transcribe(init_model(config), self.audio_path)
            speeches.append(self)
        else:
            print("This ID already exists!")

    def save_pause_image(self):
        region = auditok.load(self.audio_path)
        _ = region.split_and_plot(drop_trailing_silence=True, save_as=self.pause_image_path, show=False)


@router.get("/")
def get_speeches():
    return speeches


@router.get("/{speech_id}")
async def get_speech(speech_id: str):
    for s in speeches:
        if s.id == speech_id:
            return s
    return {"Speech ID not in DB!"}

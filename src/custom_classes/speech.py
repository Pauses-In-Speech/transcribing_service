import datetime
import os
from pathlib import Path

import auditok

from src.config import Config
from src.custom_classes.silences import find_silences
from src.routers.audio import Audio
from src.whisper_funcs import whisper_transcribe, init_model


class Speech:
    def __init__(self,
                 config: Config,
                 audio: Audio):
        new_id = audio.file_path.split(".")[-2].split("/")[-1]
        self.id = new_id

        now = datetime.datetime.now()
        self.upload_date = {
            "year": now.year,
            "month": now.month,
            "day": now.day
        }

        self.audio = audio
        self.speech_dir = f"{config.local_data_path}/speech/{new_id}"
        Path(f"{config.local_data_path}/speech/{self.id}").mkdir(parents=True, exist_ok=True)

        self.pause_image_path = os.path.join(self.speech_dir, "pause_image.png")
        self.save_pause_image()
        self.silences = find_silences(self.audio.file_path)

        self.transcription = whisper_transcribe(init_model(config.whisper_model_size, config.device),
                                                self.audio.file_path)

    def save_pause_image(self):
        region = auditok.load(self.audio.file_path)
        _ = region.split_and_plot(drop_trailing_silence=True, save_as=self.pause_image_path, show=False)


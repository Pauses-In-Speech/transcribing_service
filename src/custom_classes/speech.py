import datetime
from pathlib import Path
from statistics import mean

from src.config import Config
from src.custom_classes.silences import find_silences
from src.routers.audio import Audio
from src.whisper_funcs import whisper_transcribe, init_model


def get_wpm(transcription):
    text = transcription["text"]
    return text


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
        self.silences = find_silences(self.audio.file_path)
        self.transcription = whisper_transcribe(init_model(config.whisper_model_size, config.device),
                                                self.audio.file_path)

    def get_wpm(self):
        words = len(list(filter(lambda x: x, self.transcription["text"].split(" "))))
        return words / self.audio.duration_float_seconds * 60

    def get_statistics(self):
        """
        Gives some statistics on the self speech object.

        :return:
        dict {
        pauses: number of pauses in speech
        ppm: frequency of pauses in pauses / minute
        apl: average pause length in seconds
        wpm: frequency of words in word / minute
        }
        """
        return {
            "pauses": len(self.silences),
            "ppm": len(self.silences) / self.audio.duration_float_seconds * 60,
            "apl": mean([silence.end - silence.start for silence in self.silences]),
            "wpm": self.get_wpm()
        }

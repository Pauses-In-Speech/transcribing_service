import datetime
from pathlib import Path
from statistics import mean

from pydantic import BaseModel

from src.config import Config
from src.custom_classes.silences import find_silences
from src.routers.audio import Audio
from src.utils.alignment import get_best_match
from src.whisper_funcs import whisper_transcribe, init_model


def get_wpm(transcription):
    text = transcription["text"]
    return text


class Speech:
    def __init__(self,
                 config: Config,
                 audio: Audio):
        new_id = audio.file_path.split(".")[-2].split("/")[-1]
        self.id = f"{audio.user_id}_{new_id}"
        self.user_id = audio.user_id

        now = datetime.datetime.now()
        self.upload_date = {
            "year": now.year,
            "month": now.month,
            "day": now.day
        }

        self.audio = audio
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

    def correct_transcription(self, corpus):
        segments = self.transcription["segments"]
        for idx, segment in enumerate(segments):
            best_segment_match = get_best_match(segment["text"], corpus, step=min(4, len(segment["text"])), flex=min(4, len(segment["text"]) // 2), case_sensitive=True, verbose=False)
            self.transcription["segments"][idx]["text_corrected"] = self.transcription["segments"][idx]["text"]
            self.transcription["segments"][idx]["text"] = best_segment_match


class TranscriptPost(BaseModel):
    speech_id: str
    corrected_transcript: str

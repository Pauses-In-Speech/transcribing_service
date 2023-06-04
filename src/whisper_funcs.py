from functools import lru_cache

import whisper_timestamped as wt

from src.config import Config


@lru_cache
def init_model(model_size: str, device: str):
    return wt.load_model(model_size, device=device)


def whisper_transcribe(model, audio_path):
    audio = wt.load_audio(audio_path)
    return wt.transcribe(model, audio)

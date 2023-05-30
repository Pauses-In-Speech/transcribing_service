from functools import lru_cache

import whisper_timestamped as wt

from src.config import Config


@lru_cache
def init_model(config: Config):
    return wt.load_model(config.whisper_model_size, device=config.device)


def whisper_transcribe(model, audio_path):
    audio = wt.load_audio(audio_path)
    return wt.transcribe(model, audio)

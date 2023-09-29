from typing import Tuple

import auditok
from auditok import make_duration_formatter


def get_audio_duration(audio_path: str) -> Tuple[float, str]:
    audio = auditok.load(audio_path)
    formatter = make_duration_formatter("%m:%s")
    duration_float_seconds = audio.duration
    duration_pretty = formatter(duration_float_seconds)
    return duration_float_seconds, duration_pretty


class Audio:
    def __init__(self, audio_path, content_type, user_id, file_type):
        self.file_path: str = audio_path
        self.duration_float_seconds, self.duration_pretty = get_audio_duration(audio_path)
        self.content_type: str = content_type
        self.user_id: str = user_id
        self.file_type: str = file_type

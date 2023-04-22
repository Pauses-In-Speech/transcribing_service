import json
import auditok

import whisper_timestamped as whisper

from src.config import Config


def whisper_transcribe(config):
    audio = whisper.load_audio(config.audio_path)
    whisper_model = whisper.load_model(config.whisper_model, device=config.device)
    return whisper.transcribe(whisper_model, audio)


config = Config()
result = whisper_transcribe(config)

with open("whisper_result.json", "w") as out_file:
    out_file.write(json.dumps(result, indent=2, ensure_ascii=False))

region = auditok.load(config.audio_path)  # returns an AudioRegion object
regions = region.split_and_plot(drop_trailing_silence=True)  # or just region.splitp()


print("a")

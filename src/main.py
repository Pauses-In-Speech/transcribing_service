import json

import whisper_timestamped as whisper

audio = whisper.load_audio("../data/effibriest_01_fontane_64kb.mp3")

model = whisper.load_model("tiny", device="cuda")

result = whisper.transcribe(model, audio, language="en")


print(json.dumps(result, indent=2, ensure_ascii=False))
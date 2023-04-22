import tempfile

import torch.cuda


class Config:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.audio_path = "../data/effibriest_01_fontane_64kb.mp3"
        self.local_audio_path = tempfile.mkdtemp()
        self.whisper_model = "tiny"

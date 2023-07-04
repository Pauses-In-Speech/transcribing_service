import datetime
from pathlib import Path

import auditok
from matplotlib import pyplot as plt

from src.config import Config
from src.custom_classes.silences import find_silences
from src.routers.audio import Audio
from src.utils.plotting import auditok_custom_plot
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
        self.silences = find_silences(self.audio.file_path)
        self.transcription = whisper_transcribe(init_model(config.whisper_model_size, config.device),
                                                self.audio.file_path)

    def save_auditok_image(self, width=720, height=80):
        dpi = 100

        region = auditok.load(self.audio.file_path)
        regions = region.split(drop_trailing_silence=True)
        detections = ((reg.meta.start, reg.meta.end) for reg in regions)

        auditok_custom_plot(region, save_as=f"{self.speech_dir}/auditok_image.png", figsize=(width / dpi, height / dpi),
                            detections=detections, dpi=dpi, show=True)

    def generate_and_save_pause_image(self, width=720, height=40):
        dpi = 100
        fig_width = width / dpi
        fig_height = height / dpi

        fig, ax = plt.subplots(figsize=(fig_width, fig_height))
        ax.axhspan(0, 1, alpha=.0)

        stripe_positions = [silence.start / self.audio.duration_float_seconds for silence in self.silences]
        stripe_widths = [(silence.end - silence.start) / self.audio.duration_float_seconds for silence in
                         self.silences]
        stripe_height = 0.8

        for position, width in zip(stripe_positions, stripe_widths):
            ax.axvline(x=position, color='black', linewidth=1)
            ax.axvspan(position, position + width, ymin=(1 - stripe_height) / 2, ymax=(1 + stripe_height) / 2,
                       facecolor='black')

        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)

        ax.set_xticks([])
        ax.set_yticks([])

        ax.axis("off")
        fig.tight_layout(pad=0)

        plt.savefig(f'{self.speech_dir}/pause_image.png', transparent=True)


# dpi = 100
# width = 1200
# height = 200
# region = auditok.load("/home/levente/repos/uni/Pauses In Speech/transcribing_service/src/data/audio/effibriest_01_fontane_64kb_short.mp3")
#
# regions = region.split(drop_trailing_silence=True)
# detections = ((reg.meta.start, reg.meta.end) for reg in regions)
#
#
# auditok_custom_plot(region, save_as=f"auditok_image.png", figsize=(width / dpi, height / dpi), detections=detections, dpi=dpi)

from dataclasses import dataclass
from typing import List

import auditok


@dataclass
class Silence:
    start: float
    end: float


def find_silences(audio_path: str) -> List[Silence]:
    region = auditok.load(audio_path)  # returns an AudioRegion object
    regions = list(region.split(drop_trailing_silence=True))
    silence_list = []
    start = 0.
    for r in regions:
        silence_list.append(Silence(start=start, end=r.meta["start"]))
        start = r.meta["end"]
    silence_list.append(Silence(start=start, end=region.seconds.len))
    return silence_list

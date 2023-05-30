import tempfile
from functools import lru_cache
from typing import Any

import torch.cuda
from pydantic import BaseModel


class Config(BaseModel):
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    local_tmp_path: str = tempfile.mkdtemp()
    whisper_model_size: str = "tiny"

    class Config:
        frozen = True


@lru_cache
def get_config() -> Config:
    return Config()

from functools import lru_cache

import torch.cuda
from pydantic import BaseModel
from pydantic.typing import List


class Config(BaseModel):
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    local_data_path: str = "./data"
    whisper_model_size: str = "tiny"
    db_name: str = "pins_db.sqlite"
    allowed_content_types: List[str] = ["audio/mpeg", "audio/wav"]

    # Config instances are immutable after initialization
    class Config:
        frozen = True


# Only instantiate config object once and then use cached instance
@lru_cache
def get_config() -> Config:
    return Config()

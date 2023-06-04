from pathlib import Path

from src.config import Config
from src.whisper_funcs import init_model
from src.routers import audio, speech

import os.path
import sys

from sqlitedict import SqliteDict

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

my_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(my_path)

app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == '__main__':
    config = Config()
    model = init_model(config.whisper_model_size, config.device)

    # load db
    db = SqliteDict(config.db_name)

    if len(db) > 0:
        # check if files mentioned in db are there
        # if db is empty but files are there, throw some error
        pass
    else:
        # starting from scratch, let's lay the folder structure
        # os.mkdir("data", exist)
        Path("data").mkdir(exist_ok=True)
        Path("data/audio").mkdir(parents=True, exist_ok=True)
        Path("data/speech").mkdir(parents=True, exist_ok=True)

    app.include_router(audio.router)
    app.include_router(speech.router)

    uvicorn.run(app, host="0.0.0.0", port=8000)

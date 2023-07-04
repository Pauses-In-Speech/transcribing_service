import shutil
from pathlib import Path

import os.path
import sys

from sqlitedict import SqliteDict

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

my_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(my_path)

from src.config import Config
from src.routers.audio import reload_audio_db
from src.routers.speech import reload_speech_db
from src.whisper_funcs import init_model
from src.routers import audio, speech

app = FastAPI(
    title="Pauses In Speech: Transcribing Service",
    version="0.1.0",
)

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


@app.delete("/db_and_data/", tags=["General ⚙️"])
def clear_all_data():
    message = ""
    try:
        shutil.rmtree('./data')
    except:
        message += "Data dir not found!"

    try:
        os.remove("./pins_db.sqlite")
    except:
        message += "Database not found!"

    message += "Cleared data!"

    try:
        init_db(config.db_name)
        reload_audio_db()
        reload_speech_db()
        init_dat_dir()
    except:
        message += "Could not reinitialize data and db!/n"

    return {"message": message}


def init_dat_dir():
    Path("data").mkdir(exist_ok=True)
    Path("data/audio").mkdir(parents=True, exist_ok=True)
    Path("data/speech").mkdir(parents=True, exist_ok=True)


def init_db(db_name):
    return SqliteDict(db_name)


if __name__ == '__main__':
    config = Config()
    model = init_model(config.whisper_model_size, config.device)

    # load db
    db = init_db(config.db_name)

    if len(db) > 0:
        # check if files mentioned in db are there
        # if db is empty but files are there, throw some error
        pass
    else:
        # starting from scratch, let's lay the folder structure
        # os.mkdir("data", exist)
        init_dat_dir()

    app.include_router(audio.router)
    app.include_router(speech.router)

    uvicorn.run(app, host="0.0.0.0", port=8000)

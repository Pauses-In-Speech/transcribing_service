import os.path
import sys

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

my_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(my_path)

from src.config import Config
from src.whisper_funcs import init_model
from src.routers import audio, speech

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
    model = init_model(config)

    app.include_router(audio.router)
    app.include_router(speech.router)

    uvicorn.run(app, host="0.0.0.0", port=8000)

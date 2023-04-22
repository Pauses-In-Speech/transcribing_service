# Pauses in Speech: transcribing service

Uses [whisper-timestamped](https://github.com/linto-ai/whisper-timestamped) and 
[auditok](https://github.com/amsehili/auditok) to transcribe audio and recognize pauses in speech.

## Development

Install python dependencies via `poetry install` or `pip install -r requirements.txt`. Also make sure you have 
ffmpeg installed if you want to transcribe other audio formats than .wav.

## Running the service locally with Docker

Build the docker image at the repository root with `docker build . -t transcribing_service `

If you have the nvidia docker environment and want to speed up transcription run the docker with 
`docker run --gpus all -p 8000:8000 -t transcribing_service`.

To run on CPU use `docker run --gpus all -p 8000:8000 -t transcribing_service` and make sure to only use 
short audio files.

Open http://0.0.0.0:8000/docs in your browser and upload audio via the Swagger UI.

### Example data

The example data is from LibriVox: https://librivox.org/effi-briest-by-theodor-fontane/

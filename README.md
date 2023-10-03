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

## Running the service locally without Docker

Install python dependencies via `poetry install` or `pip install -r requirements.txt`. Also make sure you have
created a data folder and set the path to work with it in the config.

Run the service with `poetry run python src/main.py` or `python src/main.py`.    

### Example data

The example data is from LibriVox: https://librivox.org/effi-briest-by-theodor-fontane/

# Speech Objects Mockup

Speech objects are to be created when a new audio file is uploaded to the service via audio/POST

```{
  "audio_path": "path/to/audio_file",
  "silences": [
    {
      "start": 0,
      "end": 0.499
    }
  ],
  "whisper_transcript": {
    "text": "...",
    "segments": []
  },
  "original_transcript": "",
  "aligned_transcript": {
    "word": "test",
    "start": 0.15,
    "end": 0.85
  },
  "waveform_image": "path/to/image",
  "user": "user_id"
}
```

The response after the successful upload should return a link to both the audio file for downloading and
the URI to the newly created speech object. While the speech object is being created, a GET should return 
the estimated percentage of transcription.

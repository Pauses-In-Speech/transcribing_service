FROM python:3.9.18

RUN apt-get update &&\
    apt-get upgrade -y &&\
    apt-get install -y ffmpeg

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

ENV PYTHONPATH=$PYTHONPATH:/src

COPY src src

ENTRYPOINT ["python", "src/main.py"]
FROM python:3.9.16

RUN apt-get update &&\
    apt-get upgrade -y &&\
    apt-get install -y ffmpeg

ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt

ENV PYTHONPATH=$PYTHONPATH:/src

ADD src src

ENTRYPOINT ["python", "src/main.py"]
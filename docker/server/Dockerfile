#FROM ubuntu:16.04
FROM python:3.5

#RUN apt-get update -y
#RUN apt-get install -y python-pip python-dev build-essential
COPY ./requirements.txt /
RUN pip install -r requirements.txt
ENV FLASK_APP=server.py
#RUN python3 -m spacy.en.download all

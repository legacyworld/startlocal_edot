FROM python:3.12-slim
USER root
WORKDIR /src
COPY ./ /src
RUN apt-get update
RUN apt-get -y install g++
RUN pip3 install -r requirements.txt
RUN edot-bootstrap --action=install
WORKDIR /src

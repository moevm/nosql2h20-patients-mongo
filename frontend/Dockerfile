FROM python:3.7
MAINTAINER DmLvkvch

RUN rm /bin/sh && ln -s /bin/bash /bin/sh

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8
RUN sed -i 's/ universe/ universe multiverse/' /etc/apt/sources.list
RUN apt update && \
	apt upgrade -y && \
	apt dist-upgrade -y

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

WORKDIR /app/
COPY . .

CMD ["python", "./main.py", "0.0.0.0", "backend"]

FROM python:3.5

MAINTAINER ulo@ulo.pe

ARG DEBIAN_FRONTEND=noninteractive

RUN \
	apt update && \
	apt install -y locales && \
	rm -rf /var/lib/apt/lists/* && \
	echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen && \
	locale-gen

ADD . /codespeed

RUN python -m venv /venv && \
 	/venv/bin/python -m pip install -r /codespeed/requirements.txt

RUN mkdir /static

EXPOSE 8000

ENTRYPOINT ["/codespeed/docker/entrypoint.sh"]
CMD ["runserver", "0.0.0.0:8000"]

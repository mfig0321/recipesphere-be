FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y gettext netcat postgresql-client

# dependencies for geodjango
RUN apt-get update && yes | apt-get -y install binutils libproj-dev gdal-bin postgis

# update pip and install pipenv
RUN pip install -U pip
RUN pip install pipenv

# setup path for codebase
RUN mkdir -p /code
WORKDIR /code

# copy pipfile and install dependencies
COPY . /code/
RUN chmod +x start.sh

RUN pipenv install --dev

# code is linked in /code via volume
EXPOSE 8000 3000 5432

ENTRYPOINT ./start.sh
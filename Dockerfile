# pull official base image
FROM python:3.9.10-alpine

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBUG 0

# install psycopg2
RUN apk update \
    && apk add --virtual build-essential gcc python3-dev musl-dev \
    && apk add postgresql-dev \
    && pip install psycopg2

# install dependencies
COPY Pipfile Pipfile.lock ./
RUN pip install pipenv
# RUN pipenv shell --no-interactive
RUN pipenv install --system

# copy project
COPY . .

# add and run as non-root user
RUN adduser -D pokedexuser
USER pokedexuser

# run gunicorn
# CMD gunicorn pokedex.wsgi:application --bind 0.0.0.0:$PORT --workers 3
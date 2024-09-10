# pull official base image
FROM python:3.12-slim-bookworm

# set working directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install system dependencies
RUN apt-get update \
  && apt-get -y install netcat-traditional gcc postgresql libpq-dev \
  && apt-get clean

# install python dependencies
RUN pip install --upgrade pip
COPY ./requirements*.txt .
RUN pip install -r requirements-dev.txt

# add app
COPY . .

# run entrypoint.sh
RUN chmod +x /usr/src/app/entrypoint.sh
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
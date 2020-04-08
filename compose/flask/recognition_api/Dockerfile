FROM python:3.6.10-buster

RUN apt-get update
RUN apt-get install build-essential

# set environment variables
## Prevents Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE 1
## Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED 0

# specify app or project home
ENV APP_HOME /recognition_api

# Creating Work Directory
RUN mkdir -p $APP_HOME
WORKDIR $APP_HOME

# Update pip
RUN pip install --upgrade pip

# Installing requirements.txt from project
COPY ./requirements.txt $APP_HOME/requirements.txt

RUN pip install --no-cache-dir -r $APP_HOME/requirements.txt

# CMD will run when this dockerfile is running
CMD ["python", "views.py"]

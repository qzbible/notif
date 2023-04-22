# Base image
FROM python:3.9

# Variables d'environnement
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Installation des dépendances
RUN apt-get update
RUN apt-get -y install build-essential

RUN apt-get -y install python3-dev python3-pip python3-setuptools python3-wheel python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libpq-dev libgdk-pixbuf2.0-0 libffi-dev shared-mime-info

RUN pip install pipenv

# Création du dossier de travail
RUN mkdir /app
WORKDIR /app

# Copy files
COPY . /app/

# Installation des dépendances du projet
# RUN pipenv install --deploy --system --ignore-pipfile
RUN pip install -r requirements.txt

# Expose the port that the application will be running on
EXPOSE 8000

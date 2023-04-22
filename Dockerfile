FROM python:3.9
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY . /code

COPY entrypoint.sh entrypoint.sh


RUN pip install --upgrade pip
RUN pip install -r ./requirements.txt

RUN python manage.py makemigrations
# RUN python manage.py migrate
RUN python manage.py collectstatic --noinput
RUN chmod +x entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]



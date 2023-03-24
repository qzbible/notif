FROM python:3.9
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY . /code

COPY entrypoint.sh /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

COPY ./start.sh /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start

RUN pip install --upgrade pip
RUN pip install -r ./requirements.txt

#RUN python manage.py makemigrations
#RUN python manage.py migrate
#RUN python manage.py collectstatic --noinput

ENTRYPOINT ["/entrypoint"]



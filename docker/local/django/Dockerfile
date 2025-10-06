FROM --platform=linux/amd64 python:3.12.2-slim-bullseye as python

FROM python as python-build-stage
ARG BUILD_ENVIRONMENT=local

# RUN apt-get update -q && apt-get install --no-install-recommends -q -y \
#    build-essential \
#    libpq-dev


COPY ./requirements .
RUN pip install -q --upgrade pip
RUN pip wheel -q --wheel-dir /usr/src/app/wheels \
   -r ${BUILD_ENVIRONMENT}.txt


FROM python as python-run-stage

ARG BUILD_ENVIRONMENT=local
ARG APP_HOME=/app

ENV PYTHONDONTWRITEBYTECODE 1

ENV PYTHONUNBUFFERED 1

ENV BUILD_ENV ${BUILD_ENVIRONMENT}

WORKDIR ${APP_HOME}


COPY --from=python-build-stage /usr/src/app/wheels /wheels/

RUN pip install -q --no-cache-dir --no-index --find-links=/wheels/ /wheels/* \
   && rm -rf /wheels/ && pip freeze

COPY ./docker/local/django/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

COPY ./docker/local/django/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start

COPY ./docker/local/django/start-daphne /start-daphne
RUN sed -i 's/\r$//g' /start-daphne
RUN chmod +x /start-daphne


COPY ./docker/local/django/celery/worker/start /start-celeryworker
RUN sed -i 's/\r$//g' /start-celeryworker
RUN chmod +x /start-celeryworker

COPY ./docker/local/django/celery/flower/start /start-flower
RUN sed -i 's/\r$//g' /start-flower
RUN chmod +x /start-flower

COPY ./docker/local/django/celery/beat/start /start-beat
RUN sed -i 's/\r$//g' /start-beat
RUN chmod +x /start-beat


# COPY --chown=django:django . ${APP_HOME}
COPY  . ${APP_HOME}

# RUN chown django:django -R ${APP_HOME}

# USER django

ENTRYPOINT ["/entrypoint"]
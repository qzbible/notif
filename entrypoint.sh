#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

export DATABASE_URL="postgres://postgres:ziyouma@postgres_celery:5432/celery"

postgres_ready() {
python << END
import sys
import psycopg2
try:
   psycopg2.connect(
      dbname="celery",
      user="postgres",
      password="ziyouma",
      host="postgres_celery",
      port="5432"
   )
except psycopg2.OperationalError:
   sys.exit(-1)
sys.exit(0)
END
}
until postgres_ready; do

>&2 echo "Waiting for PostgreSQL to become available.....:-("
sleep 1
done
>&2 echo "PostgreSQL is ready!!!!.....:-)"


exec "$@"




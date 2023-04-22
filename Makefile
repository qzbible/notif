config:
	docker compose -f production.yml config 
build:
	docker compose -f production.yml up --build -d --remove-orphans
up:
	docker compose -f production.yml up -d
down:
	docker compose -f production.yml down
show_logs:
	docker compose -f production.yml logs
migrate:
	docker compose -f production.yml run --rm api python3 manage.py migrate --fake 
makemigrations:
	docker compose -f production.yml run --rm api python3 manage.py makemigrations
collectstatic:
	docker compose -f production.yml run --rm api python3 manage.py collectstatic --no-input --clear
superuser:
	docker compose -f production.yml run --rm api python3 manage.py createsuperuser

config_proprod:
	docker-compose -f production.yml config 
build_proprod:
	docker-compose -f production.yml up --build -d --remove-orphans

up_proprod:
	docker-compose -f production.yml up -d

down_proprod:
	docker-compose -f production.yml down

show_logs_proprod:
	docker-compose -f production.yml logs

migrate_proprod:
	docker-compose -f production.yml run --rm api python3 manage.py migrate

makemigrations_proprod:
	docker-compose -f production.yml run --rm api python3 manage.py makemigrations

collectstatic_proprod:
	docker-compose -f production.yml run --rm api python3 manage.py collectstatic --no-input --clear

superuser_proprod:
	docker-compose -f production.yml run --rm api python3 manage.py createsuperuser


config_lo:
	docker compose -f local.yml config 
build_lo:
	docker compose -f local.yml up --build -d --remove-orphans

up_lo:
	docker compose -f local.yml up -d

down_lo:
	docker compose -f local.yml down

show_logs_lo:
	docker compose -f local.yml logs

migrate_lo:
	docker compose -f local.yml run --rm api python3 manage.py migrate 

makemigrations_lo:
	docker compose -f local.yml run --rm api python3 manage.py makemigrations

collectstatic_lo:
	docker compose -f local.yml run --rm api python3 manage.py collectstatic --no-input --clear

superuser_lo:
	docker compose -f local.yml run --rm api python3 manage.py createsuperuser




down-v:
	docker compose -f local.yml down -v

volume:
	docker volume inspect authors-src_local_postgres_data

authors-db:
	docker compose -f local.yml exec postgres psql --username=alphaogilo --dbname=authors-live

flake8:
	docker compose -f local.yml exec api flake8 .

black-check:
	docker compose -f local.yml exec api black --check --exclude=migrations .

black-diff:
	docker compose -f local.yml exec api black --diff --exclude=migrations .

black:
	docker compose -f local.yml exec api black --exclude=migrations .

isort-check:
	docker compose -f local.yml exec api isort . --check-only --skip env --skip migrations

isort-diff:
	docker compose -f local.yml exec api isort . --diff --skip env --skip migrations

isort:
	docker compose -f local.yml exec api isort . --skip env --skip migrations	







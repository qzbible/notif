
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






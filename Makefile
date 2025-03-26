build:
	docker-compose up -d --build

run:
	docker-compose up -d --force-recreate


down:
	docker-compose down

restart:
	docker-compose down
	docker-compose pull
	docker-compose up -d --force-recreate

logs:
	docker-compose logs -f


migrate:
	docker-compose run --rm backend sh -c "python manage.py makemigrations && python manage.py migrate"


createsuperuser:
	docker-compose run --rm backend sh -c "python manage.py createsuperuser"


test-parallel:
	docker-compose run --rm backend sh -c "python manage.py test --parallel"


check:
	docker-compose run --rm backend sh -c "python manage.py check"


test:
	docker-compose run --rm backend sh -c "python manage.py test"


shell:
	docker-compose run --rm backend sh -c "python manage.py shell"


refresh:
	docker-compose -f docker-compose.yml pull
	docker-compose -f docker-compose.yml up -d --force-recreate --remove-orphans


env:
	export $(cat .env | xargs)


run-command:
	docker-compose run --rm backend sh -c "$1"
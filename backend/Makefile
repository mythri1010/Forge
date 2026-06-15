.PHONY: install run migrate test lint docker-up docker-down

install:
	pip install -r requirements.txt
	pip install pytest pytest-flask

run:
	flask run --debug

migrate:
	flask db upgrade

migration:
	flask db migrate -m "$(MSG)"

test:
	pytest tests/ -v --tb=short

lint:
	python -m py_compile app/**/*.py && echo "No syntax errors"

docker-up:
	docker compose up --build -d

docker-down:
	docker compose down

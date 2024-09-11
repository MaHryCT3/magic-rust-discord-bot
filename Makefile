up:
	docker compose -f docker-compose.dev.yml up -d
compile:
	poetry export --without-hashes --with image-generator > ./image_generator/requirements.txt
	poetry export --without-hashes --with bot > ./bot/requirements.txt
	poetry export --without-hashes --with reports > ./reports/requirements.txt
build:
	docker compose -f docker-compose.dev.yml build
down:
	docker compose -f docker-compose.dev.yml down
precommit:
	pre-commit run --all-files
all: compile up

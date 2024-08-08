up:
	poetry export --without-hashes --only image-generator > ./image_generator/requirements.txt
	poetry export --without-hashes --without image-generator > ./bot/requirements.txt
	docker compose -f docker-compose.dev.yml up -d
down:
	docker compose -f docker-compose.dev.yml down

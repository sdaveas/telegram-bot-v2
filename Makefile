.PHONY: run docker-up docker-down

# Run the bot locally using pipenv
run:
	pipenv run python -m app.app

# Build and run with Docker Compose
docker-up:
	docker compose up --build

# Stop Docker Compose services
docker-down:
	docker compose down

# Install dependencies
install:
	pipenv install


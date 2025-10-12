.PHONY: run docker-up docker-down deploy

# Run the bot locally using pipenv
python-run:
	pipenv run python -m app.app

# Build and run with Docker Compose
docker-up:
	docker-compose up --build -d

# Stop Docker Compose services
docker-down:
	docker-compose down

test:
	pipenv run pytest -v

# Install dependencies
install:
	pipenv install

# Pull the latest changes
pull:
	git pull

# Run the latest version
update: pull test docker-down docker-up

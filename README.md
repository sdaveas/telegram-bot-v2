# Telegram Bot v2

A Python-based Telegram bot application with message handling and database storage capabilities.

## Prerequisites

- Python 3.x
- Pipenv
- Docker and Docker Compose (for containerized deployment)
- Telegram Bot Token (from @BotFather)
- Google Cloud Project with Gemini API enabled
- Gemini API Key

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd telegram-bot-v2
```

2. Install dependencies:
```bash
make install
```

3. Set up environment variables:
```bash
# Required environment variables
export TELEGRAM_BOT_TOKEN='your_bot_token_here'
export GEMINI_API_KEY='your_gemini_api_key_here'

# Optional environment variables
export DB_PATH='database/messages.db'
```

## Running the Bot

### Local Development
To run the bot locally using pipenv:
```bash
make run
```

### Docker Deployment
To build and run using Docker Compose:
```bash
make docker-up
```

To stop the Docker services:
```bash
make docker-down
```

## Project Structure

```
telegram-bot-v2/
├── app/
│   ├── __init__.py
│   ├── bot.py
│   ├── brain.py
│   ├── database.py
│   ├── logger.py
│   └── telegram_handler.py
├── Dockerfile
├── docker-compose.yml
├── Makefile
└── README.md
```

## Available Make Commands

- `make install` - Install project dependencies
- `make run` - Run the bot locally
- `make docker-up` - Build and run with Docker Compose
- `make docker-down` - Stop Docker services

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

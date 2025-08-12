# Telegram Bot v2

A Python-based Telegram bot application with text and image processing capabilities, powered by Google's Gemini AI models. The bot can handle text messages, process images with or without captions, and maintain conversation context.

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

## Features

- Text message processing with Gemini 2.5 Pro
- Image analysis with Gemini Pro Vision
- Context-aware conversations
- Message history tracking
- Customizable system prompts

## Usage

### Text Messages
Send a message with the `/b` command followed by your query:
```bash
/b What's the weather like today?
```

### Image Analysis
There are two ways to get the bot to analyze an image:

1. Send an image with a caption starting with 'b ' or 'bot ':
```
bot what's in this image?
b describe this
```

2. Reply to any image with a message starting with 'b ' or 'bot ':
```
bot what do you see here?
b explain this image
```

Images without these triggers will be logged but not analyzed.

### Context Management
Use the `/context` command to manage conversation context:
```bash
/context be more technical     # Adds technical context
/context show                  # Shows all active contexts
/context clear                 # Clears all contexts
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

# Telegram Bot v2

A Python-based Telegram bot with advanced AI capabilities, powered by Google's Gemini models. Features include text processing, image analysis, speech-to-text transcription, and text-to-speech synthesis for Greek and English content.

## Prerequisites

- Python 3.13+
- Pipenv
- Docker and Docker Compose (optional, for containerized deployment)
- Telegram Bot Token (from @BotFather)
- Gemini API Key
- (optional) [Translate API](https://github.com/sdaveas/translate-api)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/sdaveas/telegram-bot-v2
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
export DB_PATH='database/messages.db'

# Optional environment variables
export TRANSLATE_API_URL='your_translate_API_url_here' # e.g. 'http://localhost:5001'
```

## Features

### Core Capabilities
- **Text Processing**: Multiple Gemini models (2.5 Pro, 2.5 Flash, 2.5 Flash-Lite)
- **Image Analysis**: Multimodal image understanding with caption queries
- **Speech-to-Text**: Voice message transcription using Gemini 1.5 Flash (Greek/English)
- **Text-to-Speech**: Generate voice messages from text using gTTS (Greek voice)
- **Context Management**: Maintain conversation context across messages
- **Message History**: SQLite database for conversation tracking
- **Model Switching**: Change between different Gemini models on the fly
- **Translation**: Use `/translate on` to automatically translate messages from any language to english 

## Usage

### Commands

#### `/help` or `/start` - Show usage guide
```
/help         # Display comprehensive usage instructions
/start        # Same as /help (standard Telegram bot convention)
```

#### `/b <query>` - Ask the bot anything
```
/b What's the weather like today?
/b Explain quantum computing
/b            # Just check if bot is up
```

#### `/model [number]` - Switch AI models
```
/model        # Show available models
/model 1      # Switch to Gemini 2.5 Pro
/model 2      # Switch to Gemini 2.5 Flash
/model 3      # Switch to Gemini 2.5 Flash-Lite (default)
```

#### `/context <setting>` - Manage conversation context
```
/context be more technical    # Add context
/context show                 # Show active contexts
/context clear               # Clear all contexts
```

#### `/translate <option>` - Enable/Disable automated translation
```
/translate       # returns translation status
/translate on    # enables translation
/translate off   # disables translation
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

### Voice Messages (Speech-to-Text)
The bot automatically transcribes voice messages using Gemini 1.5 Flash:

1. **Get transcription only**:
```
[Send voice message]
[Reply with: ?, b, or bot]
→ Bot responds with the transcription
```

2. **Get transcription and ask a question**:
```
[Send voice message]
[Reply with: "b what did they say about X?"]
→ Bot responds with transcription + answer
```

### Text-to-Speech
Convert any text message to speech:
```
[Any text message]
[Reply with: tts]
→ Bot sends voice message with Greek pronunciation
```

Note: Greek voice handles both Greek (perfect) and English (with accent)


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
├── app/                      # Main application code
│   ├── bot.py               # Entry point
│   ├── brain.py             # Gemini AI integration
│   ├── database.py          # SQLite message storage
│   ├── logger.py            # Logging configuration
│   ├── telegram_handler.py  # Telegram bot logic
│   ├── voice_handler.py     # Speech-to-Text (Gemini)
│   └── tts_handler.py       # Text-to-Speech (gTTS)
├── database/                 # SQLite database files
├── logs/                    # Application logs
├── .env                     # Environment variables
├── Dockerfile               # Docker configuration
├── docker-compose.yml       # Docker Compose setup
├── requirements.txt         # Python dependencies
├── Pipfile                  # Pipenv configuration
└── README.md               # This file
```

## Key Technologies

- **Gemini API**: Text generation, image analysis, speech transcription
- **gTTS**: Text-to-speech synthesis (Greek voice)
- **python-telegram-bot**: Telegram Bot API wrapper
- **SQLite**: Message history storage
- **Docker**: Containerized deployment

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `TELEGRAM_BOT_TOKEN` | Bot token from @BotFather | Yes |
| `GEMINI_API_KEY` | Google AI Studio API key | Yes |
| `DB_PATH` | Database file path | Yes (default: `database/messages.db`) |
| `TRANSLATE_API_URL` | Points to [Translate API](https://github.com/sdaveas/translate-api) url | No |

## Available Make Commands

- `make install` - Install project dependencies
- `make run` - Run the bot locally
- `make docker-up` - Build and run with Docker Compose
- `make docker-down` - Stop Docker services

## Recent Updates

- ✨ Added `/help` command for comprehensive usage instructions
- ✨ Replaced Vosk with Gemini 1.5 Flash for better speech-to-text
- ✨ Added text-to-speech with gTTS (Greek voice)
- 🔧 Simplified Docker image (removed ffmpeg, Vosk dependencies)
- 🔧 Model switching between three Gemini variants
- 🔧 Reply-based TTS interface (reply "tts" to any message)
- 📁 Organized test files into `test/` directory

## Dashboard
See [Dashboard](./README_DASHBOARD.md)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

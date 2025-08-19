
import os
from app.bot import Bot
from app.logger import setup_logger

def main():
    logger = setup_logger()

    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN environment variable not set")
        raise ValueError("Please set the TELEGRAM_BOT_TOKEN environment variable")

    db_path = os.getenv('DB_PATH', 'database/messages.db')

    translate_api_url = os.getenv('TRANSLATE_API_URL', '')

    try:
        bot = Bot(token, db_path=db_path, translate_api_url=translate_api_url)
        bot.run()
    except Exception as e:
        logger.error(f"Error running bot: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()

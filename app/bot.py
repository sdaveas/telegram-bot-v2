import os
from app.telegram_handler import TelegramHandler
from app.logger import setup_logger

def main():
    # Set up logging
    logger = setup_logger()

    # Get required environment variables
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN environment variable not set")
        raise ValueError("Please set the TELEGRAM_BOT_TOKEN environment variable")

    # Get optional environment variables
    db_path = os.getenv('DB_PATH', 'database/messages.db')

    # Initialize and run the bot
    try:
        bot = TelegramHandler(token, db_path=db_path)
        bot.run()
    except Exception as e:
        logger.error(f"Error running bot: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()

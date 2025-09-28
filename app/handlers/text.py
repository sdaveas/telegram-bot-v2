from telegram import Update
from telegram.ext import ContextTypes

class TextHandler:
    def __init__(self, bot):
        self.logger = bot.logger
        self.get_brain = bot.get_brain
        self.db = bot.db
        self.translator = bot.translator
        self.translation_is_enabled = bot.translation_is_enabled

    async def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.message.chat_id
        user_id = update.message.from_user.id
        username = update.message.from_user.username
        text = update.message.text
        date = update.message.date
        message_id = update.message.message_id

        self.logger.info(f"Storing message from user {username} in chat {chat_id}/{message_id}: {text}")
        self.db.store_message(chat_id, user_id, username, text, date, message_id=message_id)

        if self.translator and self.translation_is_enabled(chat_id):
            translated = await self.translator.translate(text, target_language="en")
            self.logger.debug(f"Translation result: {translated}")
            if translated and translated['source_language'] != translated['destination_language']:
                await update.message.reply_text(translated['translated_text'])

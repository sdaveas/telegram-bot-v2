from telegram import Update
from telegram.ext import ContextTypes

class Translate:
    def __init__(self, bot):
        self.bot = bot
        self.logger = bot.logger
        self.db = bot.db
        self.translator = bot.translator

    async def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        translation = self.db.get_setting(update.message.chat_id, 'translation_enabled', "off")
        self.logger.debug(f"Translation setting for chat {update.message.chat_id}: {translation}")
        if not self.translator:
            await update.message.set_reaction("👎")
            await update.message.reply_text("Translation API is not configured. Can't enable translation.")
            return
        text = " ".join(context.args)
        if text == "on" or text == "off":
            self.db.set_setting(update.message.chat_id, 'translation_enabled', text)
            await update.message.set_reaction("👍")
        else:
            msg = f"Translation is currently {translation}."
            msg += "\n\nUsage: /translate [on|off]"
            await update.message.reply_text(msg)

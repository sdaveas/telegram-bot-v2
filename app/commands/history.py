from telegram import Update
from telegram.ext import ContextTypes

historyDepthKey = 'history_depth'
default_history_limit = 10

class History:
    def __init__(self, bot):
        self.bot = bot
        self.logger = bot.logger
        self.db = bot.db

    async def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id

        try:
            if len(context.args) > 1 or (context.args and not context.args[0].isdigit()):
                await update.message.reply_text("Usage: /history [depth]\nExample: /history 20 to set history depth to 20 messages.")
                return

            if not context.args:
                history_depth = self.db.get_setting(chat_id, historyDepthKey, default_history_limit)
                await update.message.reply_text(f"Current history depth: {history_depth}\n\n")
                return

            history_depth = context.args[0]
            self.db.set_setting(chat_id, historyDepthKey, history_depth)
            await update.message.reply_text(f"✅ Changed history depth to {history_depth}")

        except Exception as e:
            error_msg = f"Error configuring history depth: {str(e)}"
            self.logger.error(error_msg)
            await update.message.reply_text(error_msg)


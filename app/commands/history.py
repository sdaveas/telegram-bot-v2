from telegram import Update
from telegram.ext import ContextTypes

from app.logger import setup_logger

historyDepthKey = "history_depth"
default_history_limit = 10


class History:
    def __init__(self, db):
        """Initialize History command handler."""
        self.db = db
        self.logger = setup_logger("History")

    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /history command."""
        chat_id = update.effective_chat.id
        try:
            if len(context.args) > 1 or (context.args and not context.args[0].isdigit()):
                await update.message.reply_text(
                    "Usage: /history [depth]\n"
                    "Example: /history 20 to set history depth to 20 messages."
                )
                return

            if not context.args:
                current_depth = self.db.get_setting(chat_id, historyDepthKey, default_history_limit)
                await update.message.reply_text(
                    f"Current history depth: {current_depth} messages\n"
                    "To change it, use: /history number"
                )
                return

            depth = int(context.args[0])
            if depth < 0:
                await update.message.reply_text("History depth must be >= 0")
                return

            self.db.set_setting(chat_id, historyDepthKey, str(depth))
            await update.message.reply_text(f"History depth set to: {depth} messages")
            await update.message.set_reaction("👍")
        except Exception as e:
            self.logger.error(f"Error in history command: {str(e)}")
            await update.message.reply_text("An error occurred while processing the command")

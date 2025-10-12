from telegram import Update
from telegram.ext import ContextTypes

from app.logger import setup_logger


class Context:
    def __init__(self, db):
        """Initialize Context command handler."""
        self.db = db
        self.logger = setup_logger("Context")

    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /context command."""
        chat_id = update.effective_chat.id
        username = update.effective_user.username
        new_context = " ".join(context.args) if context.args else ""
        self.logger.info(
            f"Received /context command from {username}\n"
            f"(chat_id: {chat_id}). Context: {new_context}"
        )
        if not new_context:
            current_context = self.db.get_setting(chat_id, "context", "")
            await update.message.reply_text(
                f"Current context: {current_context}\n"
                "To set a new context, use: /context your new context"
            )
            return

        self.db.set_setting(chat_id, "context", new_context)
        await update.message.reply_text(f"Context updated: {new_context}")
        await update.message.set_reaction("👍")

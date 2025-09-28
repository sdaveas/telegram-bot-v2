from telegram import Update
from telegram.ext import ContextTypes

class Context:
    def __init__(self, bot):
        self.bot = bot
        self.logger = bot.logger
        self.db = bot.db

    async def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        username = update.effective_user.username or update.effective_user.first_name
        new_context = " ".join(context.args) if context.args else ""
        self.logger.info(f"Received /context command from {username} (chat_id: {chat_id}). Context: {new_context}")
        if not new_context:
            text = "Please provide a context instruction.\n\nUsage: /context <instruction>\n"
            text += "Examples:\n"
            text += "/context be more concise - sets the context\n"
            text += "/context show\n"
            text += "/context clear"
            await update.message.reply_text(text)
            return
        await update.message.set_reaction("👀")
        if new_context.lower() == "clear":
            self.db.set_setting(chat_id, "context", "")
        elif new_context.lower() == "show":
            context_setting = self.db.get_setting(chat_id, "context", "")
            contexts = context_setting.split("\n") if context_setting else []
            if not contexts:
                await update.message.reply_text("No active contexts.")
            else:
                await update.message.reply_text(f"Active contexts:\n{contexts}")
        else:
            context_setting = self.db.get_setting(chat_id, "context", "")
            contexts = context_setting.split("\n") if context_setting else []
            self.logger.info(f"Existing contexts from DB: {contexts}, new context: {new_context}")
            contexts.append(new_context)
            new_contexts = "\n".join([f"{ctx}" for ctx in contexts])
            self.db.set_setting(chat_id, "context", new_contexts)
        await update.message.set_reaction("👍")

from telegram import Update
from telegram.ext import ContextTypes

class Context:
    def __init__(self, bot):
        self.bot = bot
        self.logger = bot.logger
        self.bot_contexts = bot.bot_contexts

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
            self.bot_contexts = []
        elif new_context.lower() == "show":
            if not self.bot_contexts:
                await update.message.reply_text("No active contexts.")
            else:
                contexts = "\n".join([f"{i+1}. {ctx}" for i, ctx in enumerate(self.bot_contexts)])
                await update.message.reply_text(f"Active contexts:\n{contexts}")
        else:
            self.bot_contexts.append(new_context)
        await update.message.set_reaction("👍")

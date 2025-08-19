from telegram import Update
from telegram.ext import ContextTypes

class Bee:
    def __init__(self, bot):
        self.bot = bot
        self.logger = bot.logger
        self.get_brain = bot.get_brain
        self.db = bot.db
        self.bot_contexts = bot.bot_contexts

    async def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        username = update.effective_user.username or update.effective_user.first_name
        query = " ".join(context.args) if context.args else ""
        self.logger.info(f"Received /b command from {username} (chat_id: {chat_id}). Query: {query}")
        if not query:
            await update.message.reply_text("I'm up. What's up?")
            return
        await update.message.set_reaction("👀")
        recent_messages = self.db.get_recent_messages(chat_id)
        if query:
            command_text = f"{username}: {query}"
            self.db.store_message(
                chat_id=chat_id,
                user_id=-1,
                username="command",
                message_text=command_text,
                timestamp=update.message.date
            )
        brain = self.get_brain(chat_id)
        system_prompt = "\n".join([f"System: {ctx}" for ctx in self.bot_contexts]) + "\n" if self.bot_contexts else ""
        response = brain.process(command_text, recent_messages, system_prompt)
        self.db.store_message(
            chat_id=chat_id,
            user_id=self.bot.application.bot.id,
            username=self.bot.application.bot.username or "Bot",
            message_text=response,
            timestamp=update.message.date
        )
        self.logger.info(f"Generated response for {username}: {response[:100]}...")
        try:
            await update.message.reply_text(response)
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
            await update.message.set_reaction("👎")
        await update.message.set_reaction([])

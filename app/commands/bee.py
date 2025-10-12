from telegram import Update
from telegram.ext import ContextTypes
from app.commands.history import historyDepthKey, default_history_limit


class Bee:
    def __init__(self, bot):
        self.bot = bot
        self.logger = bot.logger
        self.get_brain = bot.get_brain
        self.db = bot.db

    async def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        username = update.effective_user.username or update.effective_user.first_name
        query = " ".join(context.args) if context.args else ""
        self.logger.info(
            f"Received /b command from {username} (chat_id: {chat_id}). Query: {query}"
        )
        if not query:
            await update.message.reply_text("I'm up. What's up?")
            return
        await update.message.set_reaction("👀")

        messages_limit = self.db.get_setting(chat_id, historyDepthKey, default_history_limit)

        recent_messages = self.db.get_recent_messages(chat_id, messages_limit)
        if query:
            command_text = f"{username}: {query}"
            self.db.store_message(
                chat_id=chat_id,
                user_id=-1,
                username="command",
                message_text=command_text,
                timestamp=update.message.date,
                message_id=update.message.message_id,
            )
        brain = self.get_brain(chat_id)
        context_setting = self.db.get_setting(chat_id, "context", "")
        contexts = context_setting.split("\n") if context_setting else []
        system_prompt = "\n".join([f"System: {ctx}" for ctx in contexts]) + "\n" if contexts else ""
        response = brain.process(command_text, recent_messages, system_prompt)
        self.logger.info(f"Generated response for {username}: {response}...")
        await self.send_response(response, update)
        await update.message.set_reaction([])

        self.db.store_message(
            chat_id=chat_id,
            user_id=0,
            username="bot",
            message_text=response,
            timestamp=update.message.date,
            message_id=update.message.message_id,
        )

    async def send_response(self, response: str, update: Update):
        try:
            await update.message.reply_markdown(response)
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
            await update.message.reply_text(response)

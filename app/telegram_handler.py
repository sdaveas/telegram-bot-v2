from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from .database import DatabaseHandler
from .brain import BrainHandler
from .logger import setup_logger

class TelegramHandler:
    def __init__(self, token: str, db_path: str = 'database/messages.db'):
        self.bot_contexts = []
        self.logger = setup_logger()
        self.logger.info("Bot is running with detailed logging enabled.")
        self.application = Application.builder().token(token).build()
        self.db = DatabaseHandler(db_path)
        self.brain = BrainHandler()
        self.logger.info("Telegram bot initialized")

        # Add handlers
        # Store message handler should come first to catch all messages
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.store_message, block=False))
        self.application.add_handler(CommandHandler("context", self.context_command))
        self.application.add_handler(CommandHandler("b", self.bee_command))

    async def store_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Store incoming messages in the database"""
        self.logger.info(f"Received update: {update}")
        if not update.message:
            self.logger.warning("Received update without message")
            return

        message = update.message
        if not message.text:
            self.logger.warning("Received message without text")
            return

        username = message.from_user.username or message.from_user.first_name

        message_text = f"{username}: {message.text}"
        self.logger.info(f"Storing message from {username} (chat_id: {message.chat_id}): {message_text[:100]}...")

        self.db.store_message(
            chat_id=message.chat_id,
            user_id=message.from_user.id,
            username=username,
            message_text=message.text,
            timestamp=message.date
        )

    async def context_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /context command to set the bot's behavior"""
        chat_id = update.effective_chat.id
        username = update.effective_user.username or update.effective_user.first_name
        new_context = " ".join(context.args) if context.args else ""

        self.logger.info(f"Received /context command from {username} (chat_id: {chat_id}). Context: {new_context}")

        if not new_context:
            await update.message.reply_text("Please provide a context setting, e.g., be less verbose")
            return

        # Handle context commands
        if new_context.lower() == "clear":
            self.bot_contexts = []
            await update.message.reply_text("All contexts cleared.")
        elif new_context.lower() == "show":
            if not self.bot_contexts:
                await update.message.reply_text("No active contexts.")
            else:
                contexts = "\n".join([f"{i+1}. {ctx}" for i, ctx in enumerate(self.bot_contexts)])
                await update.message.reply_text(f"Active contexts:\n{contexts}")
        else:
            # Add new context
            self.bot_contexts.append(new_context)
            await update.message.reply_text(f"Added context: {new_context}")

        # Store the context as a message
        context_text = f"{username}: /context {new_context}"
        self.db.store_message(
            chat_id=chat_id,
            user_id=-1,
            username="command",
            message_text=context_text,
            timestamp=update.message.date
        )

    async def bee_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /b command"""
        chat_id = update.effective_chat.id
        username = update.effective_user.username or update.effective_user.first_name
        query = " ".join(context.args) if context.args else ""

        self.logger.info(f"Received /b command from {username} (chat_id: {chat_id}). Query: {query}")

        if not query:
            await update.message.reply_text("I'm up. What's up?")
            return

        # Get recent messages from database
        recent_messages = self.db.get_recent_messages(chat_id)

        # Store the user command as a message
        if query:
            command_text = f"{username}: {query}"
            self.db.store_message(
                chat_id=chat_id,
                user_id=-1,  # Special ID for command
                username="command",
                message_text=command_text,
                timestamp=update.message.date
            )

        # Process the query with the brain
        system_prompt = "\n".join([f"System: {ctx}" for ctx in self.bot_contexts]) + "\n" if self.bot_contexts else ""
        response = self.brain.process(query, recent_messages, system_prompt)

        # Store the bot's response
        self.db.store_message(
            chat_id=chat_id,
            user_id=self.application.bot.id,
            username=self.application.bot.username or "Bot",
            message_text=response,
            timestamp=update.message.date
        )

        self.logger.info(f"Generated response for {username}: {response[:100]}...")
        await update.message.reply_text(response)

    def run(self):
        """Run the bot"""
        self.logger.info("Bot is starting...")
        self.application.run_polling()

from telegram import Update, ReactionTypeEmoji
from telegram.ext import ContextTypes

from app.handlers.utils import get_file_path, load_file

class ReplyHandler:
    def __init__(self, bot):
        self.bot_contexts = bot.bot_contexts
        self.logger = bot.logger
        self.db = bot.db
        self.get_brain = bot.get_brain
        self.voice = bot.voice
        self.tts = bot.tts

    async def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.message.chat_id
        user_id = update.message.from_user.id
        username = update.message.from_user.username
        text = update.message.text

        self.logger.info(f"Storing reply from user {username} in chat {chat_id}: {text}")
        self.db.store_message(chat_id, user_id, username, text, update.message.date)

        reply = self.get_reply_to_bot(text, context)
        if not reply:
            self.logger.warning(f"No valid reply to bot found in message: [{reply}]. Skipping processing reply.")
            return

        await update.message.set_reaction("👀")

        if update.message.reply_to_message.photo:
            self.logger.info(f"Processing photo reply for message ID {update.message.reply_to_message.message_id}")
            file_path = get_file_path("photo", chat_id, update.message.reply_to_message.message_id)
            file = load_file(file_path)

            brain = self.get_brain(update.effective_chat.id)
            response = await brain.process_image(file, text, self.bot_contexts)
        elif update.message.reply_to_message.voice:
            file_path = get_file_path("voice", chat_id, update.message.reply_to_message.message_id)
            file = load_file(file_path)

            self.logger.info(f"Processing voice reply for message ID {update.message.reply_to_message.message_id}")
            transcription = await self.voice.transcribe_voice(file)
            brain = self.get_brain(update.effective_chat.id)
            response = brain.process("here's a transcription " + transcription + " and here's the query: " + text, self.bot_contexts)
        elif reply == "tts":
            text = update.message.reply_to_message.text
            speech = await self.tts.generate_speech(text)
            await update.message.reply_voice(speech)
            await update.message.set_reaction([])
            return

        self.logger.info(f"Brain response for reply from user {username} in chat {chat_id}: {response}")
        await update.message.reply_text(response)
        await update.message.set_reaction([])


    def get_reply_to_bot(self, text:str, context: ContextTypes.DEFAULT_TYPE) -> str:
        if text is None or text == "":
            return ""

        if text.startswith('👾') or text.startswith(context.bot.name) or text.startswith('/b') or text.startswith('b') or text.startswith('/bot') or text.startswith('bot'):
            return text.split(' ', 1)[1] if ' ' in text else ""

        if text == "tts":
            return "tts"

        return ""
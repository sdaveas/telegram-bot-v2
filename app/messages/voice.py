from telegram import Update, ReactionTypeEmoji
from telegram.ext import ContextTypes

from app.messages.utils import get_file_path, store_file


class VoiceMessageHandler:
    def __init__(self, bot):
        self.bot = bot
        self.logger = bot.logger
        self.get_file_path = get_file_path
        self.store_file = store_file

    async def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        username = update.effective_user.username or update.effective_user.first_name
        voice = update.message.voice
        voice_file = await context.bot.get_file(voice.file_id)
        voice_bytes = await voice_file.download_as_bytearray()
        file_path = get_file_path("voice", chat_id, update.message.message_id)
        store_file(file_path, voice_bytes)
        self.logger.info(f"Received voice message from {username} (chat_id: {chat_id})")

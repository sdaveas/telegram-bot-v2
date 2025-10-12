from telegram import ReactionTypeEmoji, Update
from telegram.ext import ContextTypes

from .utils import get_file_path, store_file


class PhotoHandler:
    def __init__(self, bot):
        self.bot = bot
        self.logger = bot.logger
        self.get_brain = bot.get_brain
        self.db = bot.db

    async def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        username = update.effective_user.username or update.effective_user.first_name
        caption = update.message.caption or ""
        self.logger.info(
            f"Received photo from {username} (chat_id: {chat_id}) with caption: {caption}"
        )

        self.logger.debug(f"Photo size: {[photo.file_size for photo in update.message.photo]}")
        photo = update.message.photo[-1]
        photo_file = await context.bot.get_file(photo.file_id)
        photo_bytes = await photo_file.download_as_bytearray()
        file_path = get_file_path("photo", update.message.chat_id, update.message.message_id)
        store_file(file_path, photo_bytes)
        self.logger.info(f"Stored photo file at {file_path}")

        caption_lower = caption.lower().strip()
        if not (
            caption_lower == "b"
            or caption_lower == "bot"
            or caption_lower.startswith("b ")
            or caption_lower.startswith("bot ")
        ):
            self.logger.info(
                "Skipping photo analysis - caption must be 'b'/'bot' or start with 'b '/'bot '"
            )
            return

        await update.message.set_reaction([ReactionTypeEmoji("👀")])
        if caption_lower == "b" or caption_lower == "bot":
            query = "Please analyze this image."
        elif caption_lower.startswith("bot "):
            query = caption[4:].strip()
        else:
            query = caption[2:].strip()

        context_setting = self.db.get_setting(chat_id, "context", "")
        contexts = context_setting.split("\n") if context_setting else []
        system_prompt = "\n".join([f"System: {ctx}" for ctx in contexts]) + "\n" if contexts else ""
        brain = self.get_brain(chat_id)
        response = await brain.process_image(photo_bytes, query, system_prompt)

        self.db.store_message(
            chat_id=chat_id,
            user_id=update.effective_user.id,
            username="bot",
            message_text=f"[Photo with caption: {caption}]:{response}",
            timestamp=update.message.date,
            message_id=update.message.message_id,
        )

        self.logger.debug(f"Generated response for photo: {response[:100]}...")

        response = (
            response
            + "\n\n Psst, now you can react with 👾 to get a summary of a photo, try it out!"
        )

        await update.message.reply_text(response)
        await update.message.set_reaction([])

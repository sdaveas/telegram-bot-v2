from telegram import Update
from telegram.ext import ContextTypes

from app.messages.utils import contains_laughter
from app.services.giphy import GiphyService


class TextHandler:
    def __init__(self, bot):
        self.logger = bot.logger
        self.get_brain = bot.get_brain
        self.db = bot.db
        self.translator = bot.translator
        self.translation_is_enabled = bot.translation_is_enabled
        self.giphy = GiphyService()

    async def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.message.chat_id
        user_id = update.message.from_user.id
        username = update.message.from_user.username
        text = update.message.text
        date = update.message.date
        message_id = update.message.message_id

        self.logger.info(
            f"Storing message from user {username} in chat {chat_id}/{message_id}: {text}"
        )
        self.db.store_message(chat_id, user_id, username, text, date, message_id=message_id)

        if self.translator and self.translation_is_enabled(chat_id):
            translated = await self.translator.translate(text, target_language="en")
            self.logger.debug(f"Translation result: {translated}")
            if translated and translated["source_language"] != translated["destination_language"]:
                await update.message.reply_text(translated["translated_text"])

        # Laugh detector: when there's a lot of laughing in the chat, post a laugh GIF
        try:
            if contains_laughter(text):
                # Fetch recent messages (including current) and count laughter occurrences
                recent = self.db.get_recent_messages(
                    chat_id, limit=5
                )  # Reduced window to 5 messages
                laugh_count = 0
                for msg in recent:
                    if msg.get("message_text") and contains_laughter(str(msg["message_text"])):
                        laugh_count += 1
                # Include current message explicitly if not yet persisted in recent snapshot
                if laugh_count == 0 and contains_laughter(text):
                    laugh_count += 1

                # Threshold and message-count-based antispam
                threshold = 3  # Trigger if 3 out of 5 messages contain laughter
                antispam_messages = 10  # Wait for 10 new messages before allowing another gif

                # Check when the last gif was sent (by message_id)
                last_gif_message_id = int(
                    self.db.get_setting(chat_id, "last_laugh_gif_message_id", "0")
                )
                cooldown_active = (message_id - last_gif_message_id) < antispam_messages

                if laugh_count >= threshold and not cooldown_active:
                    try:
                        gif_url = await self.giphy("laugh")
                        if gif_url:
                            await context.bot.send_animation(chat_id=chat_id, animation=gif_url)
                        # Store the current message_id for antispam
                        self.db.set_setting(chat_id, "last_laugh_gif_message_id", str(message_id))
                        self.logger.info(
                            f"Laugh GIF sent in chat {chat_id}.\n"
                            f"Next gif allowed after {antispam_messages} more messages."
                        )
                    except Exception as e:
                        self.logger.error(f"Failed to send laugh GIF: {e}")
        except Exception as e:
            self.logger.error(f"Error in laugh detection: {e}")

from telegram import Update, ReactionTypeEmoji
from telegram.ext import ContextTypes

from app.handlers.utils import try_get_file

class ReactionHandler:
    categories = ["text", "photo", "voice"]

    def __init__(self, bot):
        self.bot = bot
        self.logger = bot.logger
        self.get_brain = bot.get_brain
        self.voice = bot.voice
        self.db = bot.db

    async def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.logger.info(f"Received update: {update}")
        reaction = update.message_reaction.new_reaction
        self.logger.info(f"Reaction: {reaction}")
        if update.message_reaction.new_reaction != (ReactionTypeEmoji("👾"),):
            self.logger.info(f"don't handle reaction {update.message_reaction}")
            return

        subject, category = self.get_categorized_subject(update.effective_chat.id, update.message_reaction.message_id)
        if category not in self.categories:
            self.logger.warning(f"Unknown category [{category}] for file {subject}")
            try:
                await context.bot.set_message_reaction(
                    chat_id=update.effective_chat.id,
                    message_id=update.message_reaction.message_id,
                    reaction=[ReactionTypeEmoji("🤷‍♂️")]
                )
            except Exception as e:
                self.logger.error(f"Error setting reaction: {e}")

            self.logger.info(f"Skipping reaction handling for category {category}")
            return

        await context.bot.set_message_reaction(
            chat_id=update.effective_chat.id,
            message_id=update.message_reaction.message_id,
            reaction=[ReactionTypeEmoji("👀")]
        )

        context_setting = self.db.get_setting(update.effective_chat.id, "context", "")
        contexts = context_setting.split("\n") if context_setting else []
        system_prompt = "\n".join([f"System: {ctx}" for ctx in contexts]) + "\n" if contexts else ""
        if category == "text":
            self.logger.info(f"Processing text reaction for message ID {update.message_reaction.message_id}. Context: {contexts}")
            brain = self.get_brain(update.effective_chat.id)
            response = brain.process("Use this message as a query: " + subject, system_prompt)
        elif category == "photo":
            self.logger.info(f"Processing photo reaction for message ID {update.message_reaction.message_id}")
            brain = self.get_brain(update.effective_chat.id)
            response = await brain.process_image(subject, "Explain this image", system_prompt)
        elif category == "voice":
            self.logger.info(f"Processing voice reaction for message ID {update.message_reaction.message_id}")
            response = await self.voice.transcribe_voice(subject)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=response,
            reply_to_message_id=update.message_reaction.message_id
        )
        await context.bot.set_message_reaction(
            chat_id=update.effective_chat.id,
            message_id=update.message_reaction.message_id,
            reaction=[]
        )

    def get_categorized_subject(self, chat_id: int, message_id: int) -> tuple[str, str]:
        text = self.db.get_message_text(chat_id, message_id)
        if text != "":
            return text, "text"

        file, category = try_get_file(chat_id, message_id)
        return file, category


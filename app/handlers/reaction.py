from telegram import Update, ReactionTypeEmoji
from telegram.ext import ContextTypes

from app.handlers.utils import try_get_file

class ReactionHandler:
    categories = ["photo", "voice"]

    def __init__(self, bot):
        self.bot = bot
        self.logger = bot.logger
        self.get_brain = bot.get_brain
        self.voice = bot.voice

    async def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.logger.info(f"Received update: {update}")
        reaction = update.message_reaction.new_reaction
        self.logger.info(f"Reaction: {reaction}")
        if update.message_reaction.new_reaction != (ReactionTypeEmoji("👾"),):
            self.logger.info(f"don't handle reaction {update.message_reaction}")
            return
        file, category = try_get_file(update.effective_chat.id, update.message_reaction.message_id)
        if category not in self.categories:
            self.logger.warning(f"Unknown category [{category}] for file {file}")
            await context.bot.set_message_reaction(
                chat_id=update.effective_chat.id,
                message_id=update.message_reaction.message_id,
                reaction=[ReactionTypeEmoji("🤷‍♂️")]
            )
            self.logger.info(f"Skipping reaction handling for category {category}")
            return

        await context.bot.set_message_reaction(
            chat_id=update.effective_chat.id,
            message_id=update.message_reaction.message_id,
            reaction=[ReactionTypeEmoji("👀")]
        )

        if category == "photo":
            self.logger.info(f"Processing photo reaction for message ID {update.message_reaction.message_id}")
            brain = self.get_brain(update.effective_chat.id)
            response = await brain.process_image(file, "Explain this image", self.bot.bot_contexts)
        elif category == "voice":
            self.logger.info(f"Processing voice reaction for message ID {update.message_reaction.message_id}")
            response = await self.voice.transcribe_voice(file)
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

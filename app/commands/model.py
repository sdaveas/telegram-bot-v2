from telegram import Update
from telegram.ext import ContextTypes
from app.brain import BrainHandler

class Model:
    def __init__(self, bot):
        self.bot = bot
        self.logger = bot.logger
        self.get_brain = bot.get_brain
        self.db = bot.db

    async def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        try:
            if not context.args:
                models = []
                brain = self.get_brain(chat_id)
                for idx, name in BrainHandler.AVAILABLE_MODELS.items():
                    marker = "(active)" if idx == brain.current_model_index else ""
                    models.append(f"{idx}. {name} {marker}")
                models_text = "\n".join(models)
                await update.message.reply_text(f"Available models:\n{models_text}\n\nUse /model <number> to select a model")
                return
            try:
                model_index = int(context.args[0])
            except ValueError:
                await update.message.reply_text("Please provide a valid model number (1-3)")
                return
            await update.message.set_reaction("👀")
            if model_index not in BrainHandler.AVAILABLE_MODELS:
                await update.message.reply_text(f"Invalid model index. Must be 1-{len(BrainHandler.AVAILABLE_MODELS)}")
                return
            brain = BrainHandler(model_index)
            self.bot.brain[chat_id] = brain
            self.db.set_setting(chat_id, 'model_index', str(model_index))
            await update.message.set_reaction("👍")
        except Exception as e:
            error_msg = f"Error switching model: {str(e)}"
            self.logger.error(error_msg)
            await update.message.reply_text(error_msg)
            await update.message.set_reaction("👎")

from telegram import Update
from telegram.ext import ContextTypes

from app.brain.factory import available_backends, get_brain_handler
from app.logger import setup_logger


class Model:
    def __init__(self, db):
        """Initialize Model command handler."""
        self.db = db
        self.logger = setup_logger("Model")

    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /model command."""
        chat_id = update.effective_chat.id
        brain = get_brain_handler(chat_id)
        if not context.args:
            msg = ["Available backends:"]
            for i, backend in enumerate(available_backends()):
                backend_instance = get_brain_handler(chat_id, backend)
                current_model = getattr(
                    backend_instance,
                    "current_model",
                    getattr(backend_instance, "model_name", None),
                )
                models = backend_instance.AVAILABLE_MODELS.values()
                msg.append(f"{i + 1}. {backend} (current model: {current_model})")
                msg.append("   Available models:")
                for j, model in enumerate(models):
                    msg.append(f"   {j + 1}. {model}")
                msg.append("")
            msg.append(
                "Use /model <backend> <model> to select backend and model.\n"
                "Example: /model OPENAI gpt-4 or /model 2 1"
            )
            await update.message.reply_text("\n".join(msg))
            return

        if len(context.args) != 2:
            await update.message.reply_text("Please provide both backend and model.")
            return

        backend, model = context.args
        brain = get_brain_handler(chat_id, backend)

        if not brain:
            await update.message.reply_text(
                f"Invalid backend: {backend}\nAvailable backends: {', '.join(available_backends())}"
            )
            return

        models = brain.AVAILABLE_MODELS.values()
        if not models:
            await update.message.reply_text(f"No models available for backend {backend}")
            return

        if model.isdigit() and int(model) <= len(models):
            model = str(model)
            self.db.set_setting(chat_id, "model", model)
            await update.message.reply_text(
                f"Switched to backend: {backend}, model: "
                f"{getattr(brain, 'current_model', getattr(brain, 'model_name', None))}"
            )
            await update.message.set_reaction("👍")
        else:
            await update.message.reply_text(
                f"Select a model (by name or index).\n"
                f"E.g. /model {backend} 1 or /model {backend} {next(iter(models))}"
            )

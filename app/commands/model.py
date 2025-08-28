from telegram import Update
from telegram.ext import ContextTypes
from app.brain.factory import get_brain_handler, available_backends

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
                # Show available backends and models for current backend
                backend = self.db.get_setting(chat_id, 'backend', None)
                model = self.db.get_setting(chat_id, 'model', None)
                if backend is None:
                    backend = available_backends()[0]
                brain = get_brain_handler(backend, model)
                models = brain.get_models()
                # Ensure backend is always a name, not index
                backend_names = available_backends()
                if backend.isdigit():
                    backend_idx = int(backend)
                    if 1 <= backend_idx <= len(backend_names):
                        backend_name = backend_names[backend_idx - 1]
                    else:
                        backend_name = backend
                else:
                    backend_name = backend
                current_model = getattr(brain, 'current_model', getattr(brain, 'model_name', None))
                msg = [f"Current backend: {backend_name}/{current_model}", "Available backends:"]
                for idx, name in enumerate(backend_names, 1):
                    marker = " (active)" if name == backend_name else ""
                    msg.append(f"  {idx}. {name}{marker}")
                msg.append("")
                msg.append(f"Current model: {current_model}")
                msg.append(f"Available models for {backend_name}:")
                for idx, name in enumerate(models, 1):
                    marker = " (active)" if name == current_model else ""
                    msg.append(f"  {idx}. {name}{marker}")
                msg.append("")
                msg.append("Use /model <backend> <model> to select backend and model (by name or index). E.g. /model OPENAI gpt-4 or /model 2 1")
                await update.message.reply_text("\n".join(msg))
                return
            # Parse backend and model from args
            if len(context.args) == 1:
                backend = context.args[0]
                # List available models for this backend, do not set anything
                try:
                    brain = get_brain_handler(backend)
                except Exception as e:
                    await update.message.reply_text(f"Error: {e}")
                    await update.message.set_reaction("👎")
                    return
                models = brain.get_models()
                msg = [f"Available models for {backend}:"]
                for idx, name in enumerate(models, 1):
                    msg.append(f"  {idx}. {name}")
                msg.append("")
                msg.append(f"Use /model {backend} <model> to select a model (by name or index). E.g. /model {backend} 1 or /model {backend} {models[0]}")
                await update.message.reply_text("\n".join(msg))
                return
            else:
                backend = context.args[0]
                model = context.args[1]
            await update.message.set_reaction("👀")
            # Validate and set
            try:
                brain = get_brain_handler(backend, model)
            except Exception as e:
                await update.message.reply_text(f"Error: {e}")
                await update.message.set_reaction("👎")
                return
            self.bot.brain[chat_id] = brain
            self.db.set_setting(chat_id, 'backend', backend)
            if model is not None:
                self.db.set_setting(chat_id, 'model', str(model))
            await update.message.reply_text(f"Switched to backend: {backend}, model: {getattr(brain, 'current_model', getattr(brain, 'model_name', None))}")
            await update.message.set_reaction("👍")
        except Exception as e:
            error_msg = f"Error switching backend/model: {str(e)}"
            self.logger.error(error_msg)
            await update.message.reply_text(error_msg)
            await update.message.set_reaction("👎")

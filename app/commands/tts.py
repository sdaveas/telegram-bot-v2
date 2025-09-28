from telegram import Update
from telegram.ext import ContextTypes

class TTS:
    def __init__(self, bot):
        self.bot = bot
        self.logger = bot.logger
        self.db = bot.db

    async def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id

        try:
            if not context.args:
                # Show current settings and available providers
                provider = self.db.get_setting(chat_id, 'tts_provider', None)
                if provider is None:
                    provider = self.bot.tts.current_provider

                available_providers = self.bot.tts.get_available_providers()
                msg = ["📢 Text-to-Speech Settings", ""]
                msg.append(f"Current provider: {provider}")
                msg.append("Available providers:")

                for idx, name in enumerate(available_providers, 1):
                    voices = self.bot.tts.get_available_voices(name)
                    marker = " (active)" if name == provider else ""
                    msg.append(f"  {idx}. {name}{marker}")
                    msg.append(f"     Voices: {', '.join(voices)}")

                msg.append("")
                msg.append("To use TTS:")
                msg.append("1. Send any message")
                msg.append("2. Reply to it with 'tts'")
                msg.append("")
                msg.append("Commands:")
                msg.append("/tts - Show this help message")
                msg.append("/tts <provider> - Switch to a different provider")

                await update.message.reply_text("\n".join(msg))
                return

            # Set provider
            provider = context.args[0].lower()
            if self.bot.tts.set_provider(provider):
                self.db.set_setting(chat_id, 'tts_provider', provider)
                await update.message.reply_text(f"✅ Switched to TTS provider: {provider}")
            else:
                available = self.bot.tts.get_available_providers()
                await update.message.reply_text(
                    f"❌ Invalid provider. Available options: {', '.join(available)}"
                )

        except Exception as e:
            error_msg = f"Error configuring TTS: {str(e)}"
            self.logger.error(error_msg)
            await update.message.reply_text(error_msg)


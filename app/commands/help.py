from telegram import Update
from telegram.ext import ContextTypes

class Help:
    def __init__(self, bot):
        self.bot = bot
        self.logger = bot.logger

    async def __call__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = """🤖 **Bot Usage Guide**

**Basic Commands:**
• `/b <query>` or `/b` - Ask the bot a question or just check if it's up
• `/model` - View available AI models
• `/model <number>` - Switch to a different model (1-3)
• `/context <instruction>` - Set bot behavior (e.g., "be more concise")
• `/context clear` - Clear all contexts
• `/context show` - Show active contexts
• `/help` - Show this help message

**Photo Analysis:**
• Send a photo with caption `b` or `bot` for basic analysis
• Send a photo with caption `b <question>` to ask specific questions about it
• Reply to a photo with `b <question>` to analyze it

**Voice Messages:**
• Send a voice message (it will be stored)
• Reply to a voice message with `?`, `b`, or `bot` to get transcript
• Reply to a voice message with `b <question>` to ask about its content

**Text-to-Speech:**
• Reply to any text message with `tts` to convert it to speech (Greek voice)

**GitHub Repository:**
🔗 https://github.com/sdaveas/telegram-bot-v2

"""
        await update.message.reply_text(help_text, parse_mode='Markdown')
        chat_id = update.effective_chat.id
        username = update.effective_user.username or update.effective_user.first_name
        self.logger.info(f"Help command used by {username} (chat_id: {chat_id})")


from app.handlers.reaction import ReactionHandler
from app.handlers.text import TextHandler
from app.handlers.photo import PhotoHandler
from app.handlers.voice_handler import VoiceHandler
from app.handlers.voice import VoiceMessageHandler
from app.handlers.reply import ReplyHandler
from app.commands.context import Context
from app.commands.bee import Bee
from app.commands.translate import Translate
from app.commands.help import Help
from app.commands.model import Model
from app.commands.tts import TTS
from app.commands.history import History
from app.logger import setup_logger
from app.database import DatabaseHandler
from app.brain.factory import get_brain_handler, available_backends
from app.handlers.tts import TTSHandler
from app.handlers.translate import TranslateHandler
from telegram.ext import Application, CommandHandler, MessageHandler as TGMessageHandler, MessageReactionHandler, filters

class Bot:
    def __init__(self, token: str, db_path: str = 'database/messages.db', translate_api_url: str = ''):
        self.logger = setup_logger()
        self.logger.info("Bot is running with detailed logging enabled.")
        self.application = Application.builder().token(token).build()
        self.db = DatabaseHandler(db_path)
        self.brain = {}
        self.tts = TTSHandler()
        self.voice = VoiceHandler()
        if translate_api_url == '':
            self.logger.debug("No translation API URL provided.")
            self.translator = None
        else:
            self.logger.info(f"Translation API URL set to: {translate_api_url}")
            self.translator = TranslateHandler(translate_api_url)

        self.application.add_handler(TGMessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.REPLY, TextHandler(self), block=False))
        self.application.add_handler(TGMessageHandler(filters.PHOTO, PhotoHandler(self), block=False))
        self.application.add_handler(TGMessageHandler(filters.VOICE, VoiceMessageHandler(self), block=False))
        self.application.add_handler(TGMessageHandler(filters.REPLY, ReplyHandler(self), block=False))

        self.application.add_handler(CommandHandler("b", Bee(self)))
        self.application.add_handler(CommandHandler("context", Context(self)))
        self.application.add_handler(CommandHandler("help", Help(self)))
        self.application.add_handler(CommandHandler("model", Model(self)))
        self.application.add_handler(CommandHandler("start", Help(self)))
        self.application.add_handler(CommandHandler("tts", TTS(self)))
        self.application.add_handler(CommandHandler("translate", Translate(self)))
        self.application.add_handler(CommandHandler("history", History(self)))

        self.application.add_handler(MessageReactionHandler(ReactionHandler(self)))

    def get_brain(self, chat_id: int):
        if chat_id not in self.brain:
            backend = self.db.get_setting(chat_id, 'backend', available_backends()[0])
            model = self.db.get_setting(chat_id, 'model', 1)
            self.brain[chat_id] = get_brain_handler(backend, model)
        return self.brain[chat_id]

    def translation_is_enabled(self, chat_id: int) -> bool:
        translate = self.db.get_setting(chat_id, 'translation_enabled', "off")
        self.logger.debug(f"Checking translation setting for chat {chat_id} was {translate}")
        return translate == "on"

    def run(self):
        self.logger.info("Bot is starting...")
        self.application.run_polling()


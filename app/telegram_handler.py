from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from .database import DatabaseHandler
from .brain import BrainHandler
from .voice_handler import VoiceHandler
from .tts_handler import TTSHandler
from .translate_handler import TranslateHandler
from .logger import setup_logger

class TelegramHandler:
    def __init__(self, token: str, db_path: str = 'database/messages.db', translate_api_url: str = ''):
        self.bot_contexts = []
        self.logger = setup_logger()
        self.logger.info("Bot is running with detailed logging enabled.")
        self.application = Application.builder().token(token).build()
        self.db = DatabaseHandler(db_path)
        # Dictionary to hold brain instances per chat
        self.brains = {}
        self.voice = VoiceHandler()
        self.tts = TTSHandler()
        if translate_api_url == '':
            self.logger.debug("No translation API URL provided.")
        else:
            self.logger.info(f"Translation API URL set to: {translate_api_url}")
            self.translator = TranslateHandler(translate_api_url) if translate_api_url != '' else None
            self.translate = False

        # Add handlers
        # Store message handler should come first to catch all messages
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.new_message, block=False))
        self.application.add_handler(MessageHandler(filters.PHOTO, self.handle_photo, block=False))
        self.application.add_handler(MessageHandler(filters.VOICE, self.handle_voice, block=False))
        self.application.add_handler(CommandHandler("context", self.context_command))
        self.application.add_handler(CommandHandler("model", self.model_command))
        self.application.add_handler(CommandHandler("translate", self.translate_command))
        self.application.add_handler(CommandHandler("b", self.bee_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("start", self.help_command))  # Same as help

        self.logger.info("Telegram bot initialized")

    def get_brain(self, chat_id: int) -> BrainHandler:
        """Get or create a BrainHandler for the given chat_id"""
        if chat_id not in self.brains:
            # Retrieve last used model for chat or use default
            model_index = int(self.db.get_setting(chat_id, 'model_index', 3))
            self.brains[chat_id] = BrainHandler(model_index)

        return self.brains[chat_id]

    async def new_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle new incoming messages"""
        await self.store_message(update, context)

        if self.translator and self.translation_is_enabled(update.message.chat_id):
            translated = await self.translator.translate(update.message.text, target_language="en")
            self.logger.debug(f"Translation result: {translated}")
            if translated and translated['source_language'] != translated['destination_language']:
                await update.message.reply_text(translated['translated_text'])

    def translation_is_enabled(self, chat_id: int) -> bool:
        """Check if translation is enabled for the given chat_id"""
        translate = self.db.get_setting(chat_id, 'translation_enabled', "off")
        self.logger.debug(f"Checking translation setting for chat {chat_id} was {translate}")

        return translate == "on" 
        

    async def store_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Store incoming messages in the database and handle image analysis requests in replies"""
        self.logger.info(f"Received update: {update}")
        if not update.message:
            self.logger.warning("Received update without message")
            return

        message = update.message
        if not message.text:
            self.logger.warning("Received message without text")
            return

        username = message.from_user.username or message.from_user.first_name

        message_text = f"{username}: {message.text}"
        self.logger.info(f"Storing message from {username} (chat_id: {message.chat_id}): {message_text[:100]}...")

        # Store the message
        self.db.store_message(
            chat_id=message.chat_id,
            user_id=message.from_user.id,
            username=username,
            message_text=message.text,
            timestamp=message.date
        )

        # Check if this is a reply to another message
        if message.reply_to_message:
            text_lower = message.text.lower().strip()

            # Handle TTS requests for text messages
            if message.reply_to_message.text and text_lower == 'tts':
                # Get the text to convert to speech
                text_to_speak = message.reply_to_message.text

                self.logger.info(f"TTS request from {username} for text: {text_to_speak[:50]}...")

                try:
                    # Generate speech with Greek voice (handles both Greek and English)
                    await message.reply_text("🔊 Generating speech...")
                    audio_bytes = await self.tts.generate_speech(text_to_speak)

                    if audio_bytes:
                        # Send as voice message
                        await message.reply_voice(
                            voice=audio_bytes,
                            caption=f"🔊 TTS: {text_to_speak[:100]}{'...' if len(text_to_speak) > 100 else ''}"
                        )
                        self.logger.info(f"Successfully sent TTS audio")
                    else:
                        await message.reply_text(
                            "Sorry, I couldn't generate speech for that text."
                        )
                except Exception as e:
                    error_msg = f"Error generating speech: {str(e)}"
                    self.logger.error(error_msg)
                    await message.reply_text(f"Sorry, an error occurred: {error_msg}")

                return  # Exit early after handling TTS

            # Handle photo replies
            if message.reply_to_message.photo and (text_lower.startswith('b ') or text_lower.startswith('bot ')):
                # Get the actual query by removing the prefix
                if text_lower.startswith('bot '):
                    query = message.text[4:].strip()  # Remove 'bot ' prefix
                else:  # starts with 'b '
                    query = message.text[2:].strip()  # Remove 'b ' prefix

                # Get the largest photo size
                photo = message.reply_to_message.photo[-1]
                # Download the photo
                photo_file = await context.bot.get_file(photo.file_id)
                photo_bytes = await photo_file.download_as_bytearray()

                # Process the photo with the brain
                system_prompt = "\n".join([f"System: {ctx}" for ctx in self.bot_contexts]) + "\n" if self.bot_contexts else ""
                brain = self.get_brain(chat_id)
                response = await brain.process_image(photo_bytes, query, system_prompt)

                # Store the bot's response
                self.db.store_message(
                    chat_id=message.chat_id,
                    user_id=self.application.bot.id,
                    username=self.application.bot.username or "Bot",
                    message_text=response,
                    timestamp=message.date
                )

                self.logger.info(f"Generated response for photo reply: {response[:100]}...")
                await message.reply_text(response)

            # Handle voice message replies
            elif message.reply_to_message.voice:
                    # For voice messages, handle simple transcription requests
                    if text_lower in ['?', 'b', 'bot']:
                        # Download and transcribe
                        voice = message.reply_to_message.voice
                        voice_file = await context.bot.get_file(voice.file_id)
                        voice_bytes = await voice_file.download_as_bytearray()
                        transcript = await self.voice.transcribe_voice(voice_bytes)
                        # Just return the transcript
                        self.logger.info(f"Providing transcript for voice message")
                        await message.reply_text(f"Transcript: {transcript}")
                    # Handle full queries starting with 'b ' or 'bot '
                    elif text_lower.startswith('b ') or text_lower.startswith('bot '):
                        # Get the query
                        if text_lower.startswith('bot '):
                            query = message.text[4:].strip()  # Remove 'bot ' prefix
                        else:  # starts with 'b '
                            query = message.text[2:].strip()  # Remove 'b ' prefix
                        # Download and transcribe
                        voice = message.reply_to_message.voice
                        voice_file = await context.bot.get_file(voice.file_id)
                        voice_bytes = await voice_file.download_as_bytearray()
                        transcript = await self.voice.transcribe_voice(voice_bytes)
                        # Process the query
                        system_prompt = "\n".join([f"System: {ctx}" for ctx in self.bot_contexts]) + "\n" if self.bot_contexts else ""
                        brain = self.get_brain(message.chat_id)
                        response = brain.process(f"Voice message transcript: {transcript}\n\nUser query: {query}", [], system_prompt)
                        # Respond with both transcript and answer
                        full_response = f"Transcript: {transcript}\n\nAnswer: {response}"
                        # Store the response
                        self.db.store_message(
                            chat_id=message.chat_id,
                            user_id=self.application.bot.id,
                            username=self.application.bot.username or "Bot",
                            message_text=full_response,
                            timestamp=message.date
                        )
                        self.logger.info(f"Generated response for voice message query: {full_response[:100]}...")
                        await message.reply_text(full_response)

    async def context_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /context command to set the bot's behavior"""
        chat_id = update.effective_chat.id
        username = update.effective_user.username or update.effective_user.first_name
        new_context = " ".join(context.args) if context.args else ""

        self.logger.info(f"Received /context command from {username} (chat_id: {chat_id}). Context: {new_context}")

        if not new_context:
            await update.message.reply_text("Please provide a context setting, e.g., be less verbose")
            return

        # Handle context commands
        if new_context.lower() == "clear":
            self.bot_contexts = []
            await update.message.reply_text("All contexts cleared.")
        elif new_context.lower() == "show":
            if not self.bot_contexts:
                await update.message.reply_text("No active contexts.")
            else:
                contexts = "\n".join([f"{i+1}. {ctx}" for i, ctx in enumerate(self.bot_contexts)])
                await update.message.reply_text(f"Active contexts:\n{contexts}")
        else:
            # Add new context
            self.bot_contexts.append(new_context)
            await update.message.reply_text(f"Added context: {new_context}")

        # Store the context as a message
        context_text = f"{username}: /context {new_context}"
        self.db.store_message(
            chat_id=chat_id,
            user_id=-1,
            username="command",
            message_text=context_text,
            timestamp=update.message.date
        )

    async def bee_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /b command"""
        chat_id = update.effective_chat.id
        username = update.effective_user.username or update.effective_user.first_name
        query = " ".join(context.args) if context.args else ""

        self.logger.info(f"Received /b command from {username} (chat_id: {chat_id}). Query: {query}")

        if not query:
            await update.message.reply_text("I'm up. What's up?")
            return

        # Get recent messages from database
        recent_messages = self.db.get_recent_messages(chat_id)

        # Store the user command as a message
        if query:
            command_text = f"{username}: {query}"
            self.db.store_message(
                chat_id=chat_id,
                user_id=-1,  # Special ID for command
                username="command",
                message_text=command_text,
                timestamp=update.message.date
            )

        # Process the query with the brain
        brain = self.get_brain(chat_id)
        system_prompt = "\n".join([f"System: {ctx}" for ctx in self.bot_contexts]) + "\n" if self.bot_contexts else ""
        response = brain.process(query, recent_messages, system_prompt)

        # Store the bot's response
        self.db.store_message(
            chat_id=chat_id,
            user_id=self.application.bot.id,
            username=self.application.bot.username or "Bot",
            message_text=response,
            timestamp=update.message.date
        )

        self.logger.info(f"Generated response for {username}: {response[:100]}...")
        await update.message.reply_text(response)


    async def translate_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Enables/disables translation for the chat.

        if no text is provided, reply with a message asking for text to translate.

        if text is 'on' or 'off', toggle the translation setting for the chat.

        Otherwise replies with the expected command use.
        """

        translation = self.db.get_setting(update.message.chat_id, 'translation_enabled', "off")

        self.logger.debug(f"Translation setting for chat {update.message.chat_id}: {translation}")

        if not self.translator:
            await update.message.reply_text("Translation API is not configured. Can't enable translation.")
            return

        text = " ".join(context.args)
        if text == "on" or text == "off":
            self.db.set_setting(update.message.chat_id, 'translation_enabled', text)
            await update.message.reply_text(f"Translation is now {text}.")
        else:
            msg = f"Translation is currently {translation}."
            msg += "\n\nUsage: /translate [on|off]"
            await update.message.reply_text(msg)


    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle incoming photos"""
        chat_id = update.effective_chat.id
        username = update.effective_user.username or update.effective_user.first_name
        caption = update.message.caption or ""

        self.logger.info(f"Received photo from {username} (chat_id: {chat_id}) with caption: {caption}")

        # Store that we received a photo regardless of processing
        self.db.store_message(
            chat_id=chat_id,
            user_id=update.effective_user.id,
            username=username,
            message_text=f"[Photo{' with caption: ' + caption if caption else ''}]",
            timestamp=update.message.date
        )

        # Only process if caption is 'b'/'bot' or starts with 'b '/'bot '
        caption_lower = caption.lower().strip()
        if not (caption_lower == 'b' or caption_lower == 'bot' or
                caption_lower.startswith('b ') or caption_lower.startswith('bot ')):
            self.logger.info("Skipping photo analysis - caption must be 'b'/'bot' or start with 'b '/'bot '")
            return

        # Set query - use a default when caption is just 'b' or 'bot'
        if caption_lower == 'b' or caption_lower == 'bot':
            query = "Please analyze this image."
        elif caption_lower.startswith('bot '):
            query = caption[4:].strip()  # Remove 'bot ' prefix
        else:  # starts with 'b '
            query = caption[2:].strip()  # Remove 'b ' prefix

        # Get the largest photo size
        photo = update.message.photo[-1]

        # Download the photo
        photo_file = await context.bot.get_file(photo.file_id)
        photo_bytes = await photo_file.download_as_bytearray()

        # Process the photo with the brain
        system_prompt = "\n".join([f"System: {ctx}" for ctx in self.bot_contexts]) + "\n" if self.bot_contexts else ""
        brain = self.get_brain(chat_id)
        response = await brain.process_image(photo_bytes, query, system_prompt)

        # Store the command and response in the database
        if caption:
            self.db.store_message(
                chat_id=chat_id,
                user_id=update.effective_user.id,
                username=username,
                message_text=f"[Photo with caption: {caption}]",
                timestamp=update.message.date
            )

        self.db.store_message(
            chat_id=chat_id,
            user_id=self.application.bot.id,
            username=self.application.bot.username or "Bot",
            message_text=response,
            timestamp=update.message.date
        )

        self.logger.info(f"Generated response for photo: {response[:100]}...")
        await update.message.reply_text(response)

    async def handle_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle voice messages"""
        chat_id = update.effective_chat.id
        username = update.effective_user.username or update.effective_user.first_name

        self.logger.info(f"Received voice message from {username} (chat_id: {chat_id})")

        # Just log that we received a voice message (no response to the user)
        self.logger.info("Voice message stored in chat history")
        self.db.store_message(
            chat_id=chat_id,
            user_id=update.effective_user.id,
            username=username,
            message_text="[Voice message]",
            timestamp=update.message.date
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /help command to display bot usage instructions"""
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

        # Log the help command usage
        chat_id = update.effective_chat.id
        username = update.effective_user.username or update.effective_user.first_name
        self.logger.info(f"Help command used by {username} (chat_id: {chat_id})")

    async def model_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle the /model command to select or view available models"""
        chat_id = update.effective_chat.id
        username = update.effective_user.username or update.effective_user.first_name

        try:
            if not context.args:
                # List available models with current one marked
                models = []
                brain = self.get_brain(chat_id)
                for idx, name in BrainHandler.AVAILABLE_MODELS.items():
                    marker = "(active)" if idx == brain.current_model_index else ""
                    models.append(f"{idx}. {name} {marker}")
                models_text = "\n".join(models)
                await update.message.reply_text(f"Available models:\n{models_text}\n\nUse /model <number> to select a model")
                return

            # Parse model index
            try:
                model_index = int(context.args[0])
            except ValueError:
                await update.message.reply_text("Please provide a valid model number (1-3)")
                return

            # Validate and switch model
            if model_index not in BrainHandler.AVAILABLE_MODELS:
                await update.message.reply_text(f"Invalid model index. Must be 1-{len(BrainHandler.AVAILABLE_MODELS)}")
                return

            # Initialize or update brain for this chat with the selected model
            brain = BrainHandler(model_index)
            self.brains[chat_id] = brain
            model_name = BrainHandler.AVAILABLE_MODELS[model_index]
            # Store the selected model index for this chat
            self.db.set_setting(chat_id, 'model_index', str(model_index))

            await update.message.reply_text(f"Switched to model: {model_name}")

            # Store the command
            command_text = f"{username}: /model {model_index}"
            self.db.store_message(
                chat_id=chat_id,
                user_id=-1,  # Special ID for command
                username="command",
                message_text=command_text,
                timestamp=update.message.date
            )

        except Exception as e:
            error_msg = f"Error switching model: {str(e)}"
            self.logger.error(error_msg)
            await update.message.reply_text(error_msg)

    def run(self):
        """Run the bot"""
        self.logger.info("Bot is starting...")
        self.application.run_polling()

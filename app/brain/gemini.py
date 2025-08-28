
import os
import google.generativeai as genai
from app.logger import setup_logger

class GeminiBrainHandler:
    AVAILABLE_MODELS = {
        1: 'gemini-2.5-pro',
        2: 'gemini-2.5-flash',
        3: 'gemini-2.5-flash-lite'
    }

    def __init__(self, model: int | str = 2):
        self.logger = setup_logger()
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            self.logger.error("GEMINI_API_KEY environment variable is not set")
            raise ValueError("GEMINI_API_KEY environment variable is not set")
        # Accept model as index or name
        if isinstance(model, int):
            if model not in self.AVAILABLE_MODELS:
                self.logger.error(f"Invalid model index {model}")
                raise ValueError(f"Invalid model index {model}. Must be 1-{len(self.AVAILABLE_MODELS)}")
            self.model_name = self.AVAILABLE_MODELS[model]
        elif isinstance(model, str):
            if model in self.AVAILABLE_MODELS.values():
                self.model_name = model
            else:
                self.logger.error(f"Invalid model name or index {model}")
                raise ValueError(f"Invalid model name or index {model}. Must be one of {list(self.AVAILABLE_MODELS.values())} or 1-{len(self.AVAILABLE_MODELS)}")
        else:
            self.logger.error(f"Invalid model argument: {model}")
            raise ValueError(f"Invalid model argument: {model}")
        genai.configure(api_key=api_key)
        try:
            self.model = genai.GenerativeModel(self.model_name)
            self.vision_model = self.model
            self.model.generate_content('test')
        except Exception as e:
            self.logger.error(f"Failed to initialize model {self.model_name}: {str(e)}")
            raise
        self.logger.info(f"GeminiBrainHandler initialized with Gemini model {self.model_name}")
        self.current_model = self.model_name

    def get_models(self):
        return list(self.AVAILABLE_MODELS.values())

    def set_model(self, model_name):
        if model_name in self.AVAILABLE_MODELS.values():
            self.current_model = model_name
            self.model = genai.GenerativeModel(model_name)
            self.vision_model = self.model
            self.logger.info(f"Switched to Gemini model {model_name}")
        else:
            raise ValueError(f"Invalid model name: {model_name}")

    def process(self, prompt, recent_messages=None, system_prompt=""):
        context = self._format_context(recent_messages) if recent_messages else ""
        full_prompt = self._format_prompt(prompt, context, system_prompt)
        self._log_prompt(full_prompt)
        return self._generate_content(self.model, full_prompt)

    def _format_context(self, messages):
        if not messages:
            return "No recent messages."
        context = []
        for msg in reversed(messages):
            context.append(f"{msg['username']}: {msg['message_text']}")
        return "\n".join(context)

    async def process_image(self, image_bytes: bytearray, caption: str, system_prompt: str = "") -> str:
        from PIL import Image
        import io
        image = Image.open(io.BytesIO(image_bytes))
        prompt = self._format_image_prompt(caption, system_prompt)
        self._log_prompt(prompt)
        return self._generate_content(self.vision_model, [prompt, image], image_mode=True)

    def _format_prompt(self, prompt, context, system_prompt):
        return f"{system_prompt}\n{context}\nUser query: {prompt}\nPlease provide a concise and relevant response."

    def _format_image_prompt(self, caption, system_prompt):
        return f"{system_prompt}Please analyze this image{' and respond to: ' + caption if caption else '.'}\nProvide a clear and concise response."

    def _log_prompt(self, prompt):
        self.logger.info(f"Using model: {self.current_model}")
        self.logger.info("---START PROMPT---")
        self.logger.info(prompt)
        self.logger.info("---END PROMPT---")

    def _generate_content(self, model, prompt, image_mode=False):
        try:
            response = model.generate_content(prompt)
            if not response.candidates:
                return "I apologize, but I cannot provide a response to that query due to safety constraints." if not image_mode else "I apologize, but I cannot analyze this image due to safety constraints."
            return response.text
        except ValueError as e:
            self.logger.warning(f"Gemini API ValueError: {str(e)}")
            return "I apologize, but I cannot provide a response to that query due to safety constraints." if not image_mode else "I apologize, but I cannot analyze this image due to safety constraints."
        except Exception as e:
            self.logger.error(f"Gemini API error: {str(e)}")
            if 'InternalServerError' in str(type(e)):
                return "I encountered a temporary error. Please try your request again in a moment." if not image_mode else "I encountered a temporary error. Please try analyzing the image again in a moment."
            return "I apologize, but I encountered an error processing your request." if not image_mode else "I apologize, but I encountered an error analyzing this image."

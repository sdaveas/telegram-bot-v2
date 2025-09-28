import os
import io
import openai
from app.logger import setup_logger

class OpenAIBrainHandler:
    AVAILABLE_MODELS = ["gpt-4o", "gpt-3.5-turbo"]

    def __init__(self, model_name: str = AVAILABLE_MODELS[0]):
        self.logger = setup_logger()
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            self.logger.error("OPENAI_API_KEY environment variable is not set")
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        openai.api_key = api_key
        if model_name not in self.AVAILABLE_MODELS:
            self.logger.error(f"Invalid model name {model_name}")
            raise ValueError(f"Invalid model name {model_name}. Must be one of {self.AVAILABLE_MODELS}")
        self.current_model = model_name
        self.logger.info(f"OpenAIBrainHandler initialized with model {self.current_model}")

    def get_models(self):
        return self.AVAILABLE_MODELS

    def set_model(self, model_name):
        if model_name in self.AVAILABLE_MODELS:
            self.current_model = model_name
            self.logger.info(f"Switched to OpenAI model {model_name}")
        else:
            raise ValueError(f"Invalid model name: {model_name}")

    def process(self, prompt, recent_messages=None, system_prompt=""):
        context = self._format_context(recent_messages) if recent_messages else ""
        full_prompt = self._format_prompt(prompt, context, system_prompt)
        self._log_prompt(full_prompt)
        return self._generate_content(full_prompt)

    async def process_image(self, image_bytes: bytearray, caption: str, system_prompt: str = "") -> str:
        from PIL import Image
        image = Image.open(io.BytesIO(image_bytes))
        prompt = self._format_image_prompt(caption, system_prompt)
        self._log_prompt(prompt)
        return self._generate_content(prompt, image=image)

    def _format_prompt(self, prompt, context, system_prompt):
        return f"{system_prompt}\n{context}\nUser query: {prompt}\nPlease provide a concise and relevant response."

    def _format_image_prompt(self, caption, system_prompt):
        return f"{system_prompt}Please analyze this image{' and respond to: ' + caption if caption else '.'}\nProvide a clear and concise response."

    def _log_prompt(self, prompt):
        self.logger.info(f"Using model: {self.current_model}")
        self.logger.info("---START PROMPT---")
        self.logger.info(prompt)
        self.logger.info("---END PROMPT---")

    def _format_context(self, messages):
        if not messages:
            return "No recent messages."
        context = []
        for msg in reversed(messages):
            context.append(f"{msg['username']}: {msg['message_text']}")
        return "\n".join(context)

    def _generate_content(self, prompt, image=None):
        try:
            if image is None:
                # Text-only
                response = openai.ChatCompletion.create(
                    model=self.current_model,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.choices[0].message["content"]
            else:
                # Image + text (OpenAI Vision, e.g., GPT-4o or GPT-4V)
                import base64
                buffered = io.BytesIO()
                image.save(buffered, format="PNG")
                img_b64 = base64.b64encode(buffered.getvalue()).decode()
                response = openai.ChatCompletion.create(
                    model=self.current_model,
                    messages=[
                        {"role": "user", "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}}
                        ]}
                    ]
                )
                return response.choices[0].message["content"]
        except Exception as e:
            self.logger.error(f"OpenAI API error: {str(e)}")
            return "I apologize, but I encountered an error processing your request."


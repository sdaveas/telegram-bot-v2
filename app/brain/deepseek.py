import os
import requests
from app.logger import setup_logger

class DeepseekBrainHandler:
    AVAILABLE_MODELS = ["deepseek-chat"]

    def __init__(self, model_name: str = "deepseek-chat"):
        self.logger = setup_logger()
        api_key = os.getenv('DEEPSEEK_API_KEY')
        if not api_key:
            self.logger.error("DEEPSEEK_API_KEY environment variable is not set")
            raise ValueError("DEEPSEEK_API_KEY environment variable is not set")
        if model_name not in self.AVAILABLE_MODELS:
            self.logger.error(f"Invalid model name {model_name}")
            raise ValueError(f"Invalid model name {model_name}. Must be one of {self.AVAILABLE_MODELS}")
        self.current_model = model_name
        self.api_key = api_key
        self.logger.info(f"DeepseekBrainHandler initialized with model {self.current_model}")

    def get_models(self):
        return self.AVAILABLE_MODELS

    def set_model(self, model_name):
        if model_name in self.AVAILABLE_MODELS:
            self.current_model = model_name
            self.logger.info(f"Switched to Deepseek model {model_name}")
        else:
            raise ValueError(f"Invalid model name: {model_name}")

    def process(self, prompt, recent_messages=None, system_prompt=""):
        # Only text for now
        url = "https://api.deepseek.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        if recent_messages:
            for msg in recent_messages:
                messages.append({"role": "user", "content": msg['message_text']})
        messages.append({"role": "user", "content": prompt})
        data = {
            "model": self.current_model,
            "messages": messages,
            "temperature": 0.7
        }
        try:
            resp = requests.post(url, headers=headers, json=data, timeout=30)
            resp.raise_for_status()
            result = resp.json()
            return result['choices'][0]['message']['content']
        except Exception as e:
            self.logger.error(f"Deepseek API error: {str(e)}")
            return "I apologize, but I encountered an error processing your request."

    async def process_image(self, image_bytes: bytearray, caption: str, system_prompt: str = "") -> str:
        self.logger.error(f"tried to process image with deepseek")
        return "I apologize, image processing is not supported with Deepseek yet."

from typing import List, Dict
import os
import google.generativeai as genai
from .logger import setup_logger

class BrainHandler:
    def __init__(self):
        """Initialize the brain with Gemini"""
        self.logger = setup_logger()

        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            self.logger.error("GEMINI_API_KEY environment variable is not set")
            raise ValueError("GEMINI_API_KEY environment variable is not set")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-pro')
        # Use the same model for both text and vision since gemini-2.5-pro is multimodal
        self.vision_model = self.model
        self.logger.info("Brain initialized with Gemini models (2.5 Pro and Pro Vision)")

    def process(self, query: str, recent_messages: List[Dict], system_prompt: str = "") -> str:
        """Process a query with context from recent messages"""
        # Format recent messages as context
        context = self._format_context(recent_messages)

        # Simple arithmetic operations
        if self._is_arithmetic(query):
            try:
                return str(eval(query))
            except:
                return "Sorry, I couldn't process that arithmetic operation."

        # For other queries, use the LLM
        prompt = f"""
{system_prompt}Context from recent messages:
{context}

User query: {query}

Please provide a concise and relevant response."""

        self.logger.info("Generated prompt:")
        self.logger.info("---START PROMPT---")
        self.logger.info(prompt)
        self.logger.info("---END PROMPT---")

        response = self.model.generate_content(prompt)
        return response.text

    def _format_context(self, messages: List[Dict]) -> str:
        """Format recent messages into a string context"""
        if not messages:
            return "No recent messages."

        context = []
        for msg in reversed(messages):  # Oldest to newest
            context.append(f"{msg['username']}: {msg['message_text']}")

        return "\n".join(context)

    def _is_arithmetic(self, query: str) -> bool:
        """Check if the query is a simple arithmetic operation"""
        query = query.strip()
        try:
            eval(query)
            return all(c in "0123456789+-*/(). " for c in query)
        except:
            return False

    async def process_image(self, image_bytes: bytearray, caption: str, system_prompt: str = "") -> str:
        """Process an image with optional caption using Gemini Pro Vision"""
        from PIL import Image
        import io

        # Convert bytearray to PIL Image
        image = Image.open(io.BytesIO(image_bytes))

        prompt = f"""
{system_prompt}Please analyze this image{' and respond to: ' + caption if caption else '.'}

Provide a clear and concise response."""

        self.logger.info("Processing image with prompt:")
        self.logger.info("---START PROMPT---")
        self.logger.info(prompt)
        self.logger.info("---END PROMPT---")

        response = self.vision_model.generate_content([prompt, image])
        return response.text


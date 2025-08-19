from typing import List, Dict
import os
import google.generativeai as genai
from .logger import setup_logger

class BrainHandler:
    AVAILABLE_MODELS = {
        1: 'gemini-2.5-pro',
        2: 'gemini-2.5-flash',
        3: 'gemini-2.5-flash-lite'
    }

    def __init__(self, model_index: int = 3):
        self.current_model_index = model_index
        """Initialize the brain with Gemini

        Args:
            model_index: Index of the model to use (1-3). Defaults to 3 (gemini-2.5-flash-lite).
        """
        self.logger = setup_logger()

        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            self.logger.error("GEMINI_API_KEY environment variable is not set")
            raise ValueError("GEMINI_API_KEY environment variable is not set")

        if model_index not in self.AVAILABLE_MODELS:
            self.logger.error(f"Invalid model index {model_index}")
            raise ValueError(f"Invalid model index {model_index}. Must be 1-{len(self.AVAILABLE_MODELS)}")

        genai.configure(api_key=api_key)
        self.model_name = self.AVAILABLE_MODELS[model_index]
        try:
            self.model = genai.GenerativeModel(self.model_name)
            # All models are multimodal
            self.vision_model = self.model
            # Test model initialization
            self.model.generate_content('test')
        except Exception as e:
            self.logger.error(f"Failed to initialize model {self.model_name}: {str(e)}")
            raise
        self.logger.info(f"Brain initialized with Gemini model {self.model_name}")

    def process(self, query: str, recent_messages: List[Dict], system_prompt: str = "") -> str:
        """Process a query with context from recent messages"""
        # Format recent messages as context
        context = self._format_context(recent_messages)

        # Log the current model
        self.logger.info(f"Using model: {self.model_name}")

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

        try:
            response = self.model.generate_content(prompt)
            if not response.candidates:
                return "I apologize, but I cannot provide a response to that query due to safety constraints."
            return response.text
        except ValueError as e:
            self.logger.warning(f"Gemini API ValueError: {str(e)}")
            return "I apologize, but I cannot provide a response to that query due to safety constraints."
        except Exception as e:
            self.logger.error(f"Gemini API error: {str(e)}")
            # For internal server errors, suggest retry
            if 'InternalServerError' in str(type(e)):
                return "I encountered a temporary error. Please try your request again in a moment."
            return "I apologize, but I encountered an error processing your request."

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

        # Log the current model
        self.logger.info(f"Using model: {self.model_name}")

        # Convert bytearray to PIL Image
        image = Image.open(io.BytesIO(image_bytes))

        prompt = f"""
{system_prompt}Please analyze this image{' and respond to: ' + caption if caption else '.'}

Provide a clear and concise response."""

        self.logger.info("Processing image with prompt:")
        self.logger.info("---START PROMPT---")
        self.logger.info(prompt)
        self.logger.info("---END PROMPT---")

        try:
            response = self.vision_model.generate_content([prompt, image])
            if not response.candidates:
                return "I apologize, but I cannot analyze this image due to safety constraints."
            return response.text
        except ValueError as e:
            self.logger.warning(f"Gemini API ValueError: {str(e)}")
            return "I apologize, but I cannot analyze this image due to safety constraints."
        except Exception as e:
            self.logger.error(f"Gemini API error: {str(e)}")
            # For internal server errors, suggest retry
            if 'InternalServerError' in str(type(e)):
                return "I encountered a temporary error. Please try analyzing the image again in a moment."
            return "I apologize, but I encountered an error analyzing this image."


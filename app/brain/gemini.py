import os
from google import genai
from google.genai import types
from PIL import Image
import io

from app.logger import setup_logger
# The most reliable way to import both classes is from the types submodule.

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
        
        # Define the Google Search tool for grounding.
        # This tells the Gemini model that it has access to a web search tool.
        self.google_search_tool = genai.types.Tool(google_search=genai.types.GoogleSearch())

        client = genai.Client()
        grounding_tool = types.Tool(
            google_search=types.GoogleSearch()
        )
        self.config = types.GenerateContentConfig(
            tools=[grounding_tool]
        )

        try:
            self.model = client.models
        except Exception as e:
            self.logger.error(f"Failed to initialize model {self.model_name}: {str(e)}")
            raise
        
        self.logger.info(f"GeminiBrainHandler initialized with Gemini model {self.model_name} and Google Search grounding enabled.")

    def get_models(self):
        return list(self.AVAILABLE_MODELS.values())

    def set_model(self, model_name):
        if model_name in self.AVAILABLE_MODELS.values():
            self.model_name = model_name
            self.logger.info(f"Switched to Gemini model {model_name} with Google Search grounding enabled.")
        else:
            raise ValueError(f"Invalid model name: {model_name}")

    def process(self, prompt, recent_messages=None, system_prompt=""):
        self.logger.info("Processing text prompt.")

        context = self._format_context(recent_messages) if recent_messages else ""
        full_prompt = self._format_prompt(prompt, context, system_prompt)
        self._log_prompt(full_prompt)
        return self._generate_content(full_prompt)

    async def process_image(self, image_bytes: bytearray, caption: str, system_prompt: str = "") -> str:
        contents = [
            types.Part.from_text(text=self._format_image_prompt(caption, system_prompt)),
            types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
        ]
        self._log_prompt(contents)
        return self._generate_content(contents, image_mode=True)

    def _format_context(self, messages):
        if not messages:
            return "No recent messages."
        context = []
        for msg in reversed(messages):
            context.append(f"{msg['username']}: {msg['message_text']}")
        return "\n".join(context)

    def _format_prompt(self, prompt, context, system_prompt):
        return f"{system_prompt}\n{context}\nUser query: {prompt}\nPlease provide a concise and relevant response."

    def _format_image_prompt(self, caption, system_prompt):
        return f"{system_prompt}Please analyze this image{' and respond to: ' + caption if caption else '.'}\nProvide a clear and concise response."

    def _log_prompt(self, prompt):
        self.logger.info(f"Using model: {self.model_name}")
        self.logger.info("---START PROMPT---")
        self.logger.info(prompt)
        self.logger.info("---END PROMPT---")

    def _generate_content(self, prompt, image_mode=False):
        try:
            response = self.model.generate_content(
                model=self.model_name,
                contents=prompt,
                config=self.config
            )

            if not response.candidates:
                return "I apologize, but I cannot provide a response to that query due to safety constraints." if not image_mode else "I apologize, but I cannot analyze this image due to safety constraints."

            # Check for grounding metadata and log the sources.
            # This is a key step for transparency and debugging.
            text = response.text
            
            supports = []
            chunks = []

            if response.candidates[0].grounding_metadata and response.candidates[0].grounding_metadata.grounding_supports:
                supports = response.candidates[0].grounding_metadata.grounding_supports

            if response.candidates[0].grounding_metadata and response.candidates[0].grounding_metadata.grounding_chunks:
                chunks = response.candidates[0].grounding_metadata.grounding_chunks

            sorted_supports = sorted(supports, key=lambda s: s.segment.end_index, reverse=True)

            # Collect all unique citations in order of first appearance
            citation_map = {}
            citation_counter = 1
            for support in sorted_supports:
                if support.grounding_chunk_indices:
                    for i in support.grounding_chunk_indices:
                        if i < len(chunks) and i not in citation_map:
                            citation_map[i] = citation_counter
                            citation_counter += 1
            # Build citation string for the end
            if citation_map:
                citation_lines = []
                for i, num in sorted(citation_map.items(), key=lambda x: x[1]):
                    uri = chunks[i].web.uri
                    citation_lines.append(f"[{num}]({uri})")
                text = text.rstrip() + "\n\n" + " ".join(citation_lines)

            return text
        except ValueError as e:
            self.logger.warning(f"Gemini API ValueError: {str(e)}")
            return "I apologize, but I cannot provide a response to that query due to safety constraints." if not image_mode else "I apologize, but I cannot analyze this image due to safety constraints."
        except Exception as e:
            self.logger.error(f"Gemini API error: {str(e)}")
            if 'InternalServerError' in str(type(e)):
                return "I encountered a temporary error. Please try your request again in a moment." if not image_mode else "I encountered a temporary error. Please try analyzing the image again in a moment."
            return "I apologize, but I encountered an error processing your request." if not image_mode else "I apologize, but I encountered an error analyzing this image."

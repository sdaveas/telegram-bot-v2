import os

import openai

from app.logger import setup_logger

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


class OpenAIBrainHandler:
    def __init__(self, model="gpt-3.5-turbo", api_key=None):
        """Initialize OpenAI handler with optional model override."""
        self.api_key = api_key or OPENAI_API_KEY
        self.model_name = model
        self.logger = setup_logger("OpenAIBrainHandler")
        self.current_model = model
        self.client = openai.OpenAI(api_key=self.api_key)

    def _format_prompt(self, prompt, context, system_prompt):
        parts = [
            system_prompt,
            context,
            f"User query: {prompt}",
            "Please provide a concise and relevant response.",
        ]
        return "\n".join(filter(None, parts))

    def _format_image_prompt(self, caption, system_prompt):
        parts = [
            "Please describe this image" + (f" and respond to: {caption}" if caption else "."),
            "Provide a clear and concise response.",
        ]
        return "\n".join(parts)

    async def get_response(self, prompt, context="", system_prompt="", image_bytes=None):
        """Get response from OpenAI API."""
        if image_bytes:
            try:
                self.logger.info("OpenAI: Processing image...")
                response = await self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{image_bytes.decode()}",
                                        "detail": "auto",
                                    },
                                },
                                {"type": "text", "text": prompt},
                            ],
                        },
                    ],
                    max_tokens=2000,
                )
                content = response.choices[0].message.content
                self.logger.info(f"OpenAI image response: {content}")
                return content
            except Exception as e:
                self.logger.error(f"Error processing image with OpenAI: {str(e)}")
                return "I apologize, but I cannot analyze this image due to an error."

        try:
            formatted_prompt = self._format_prompt(prompt, context, system_prompt)
            self.logger.info(f"OpenAI: Sending prompt: {formatted_prompt}")
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": formatted_prompt}],
                max_tokens=2000,
            )
            content = response.choices[0].message.content
            self.logger.info(f"OpenAI response: {content}")
            return content
        except Exception as e:
            self.logger.error(f"OpenAI API error: {str(e)}")
            return "I encountered an error processing your request. Please try again."

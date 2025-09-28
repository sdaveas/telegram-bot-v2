from app.logger import setup_logger

class NoopBrainHandler:
    def __init__(self, backend_name: str):
        self.logger = setup_logger()
        self.backend_name = backend_name
        self.logger.warning(f"NoopBrainHandler initialized for backend '{backend_name}' due to missing API key.")

    def get_models(self):
        return ["please add API key to get models"]

    def set_model(self, model_name):
        pass

    def process(self, prompt, recent_messages=None, system_prompt=""):
        return f"[NOOP] The backend '{self.backend_name}' is not available (missing API key)."

    async def process_image(self, image_bytes: bytearray, caption: str, system_prompt: str = "") -> str:
        return f"[NOOP] The backend '{self.backend_name}' is not available (missing API key)."


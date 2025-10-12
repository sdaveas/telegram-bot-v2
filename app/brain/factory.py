import os

from .deepseek import DeepseekBrainHandler
from .gemini import GeminiBrainHandler
from .noop import NoopBrainHandler
from .openai import OpenAIBrainHandler

_BACKENDS = {}
_BACKEND_CONFIG = [
    ("GEMINI", GeminiBrainHandler, "GEMINI_API_KEY"),
    ("OPENAI", OpenAIBrainHandler, "OPENAI_API_KEY"),
    ("DEEPSEEK", DeepseekBrainHandler, "DEEPSEEK_API_KEY"),
]
for name, handler, env_key in _BACKEND_CONFIG:
    if os.getenv(env_key):
        _BACKENDS[name] = handler
    else:
        _BACKENDS[name] = lambda *args, name=name: NoopBrainHandler(name)


def available_backends():
    """Return a list of available backend names."""
    return list(_BACKENDS.keys())


def select_backend(choice: str) -> str:
    """
    Given a user choice (name or index), return the backend name.
    Raises ValueError if invalid.
    """
    backends = available_backends()
    if not choice:
        raise ValueError("No backend specified. Please select one of: " + ", ".join(backends))
    choice = choice.strip()
    if choice.isdigit():
        idx = int(choice)
        if 1 <= idx <= len(backends):
            return backends[idx - 1]
        else:
            raise ValueError(f"Invalid backend index: {choice}. Valid indices: 1-{len(backends)}")
    choice = choice.upper()
    if choice in backends:
        return choice
    raise ValueError(f"Unknown backend: {choice}. Available: {', '.join(backends)} or their index.")


def get_brain_handler(backend: str, model: str = None):
    """
    Returns the brain handler for the specified backend and model.
    backend: str, e.g. 'GEMINI', 'OPENAI'.
    model: str or int, model name or index for the backend (optional).
    Raises ValueError if backend is not available.
    """
    backend = select_backend(backend)
    handler_cls = _BACKENDS[backend]
    if model is not None:
        # Get available models for this backend
        tmp_handler = handler_cls()  # Use default model to get list
        models = tmp_handler.get_models()
        # If model is an integer index, convert to model name
        try:
            model_idx = int(model)
            if 1 <= model_idx <= len(models):
                model = models[model_idx - 1]
            else:
                raise ValueError(f"Invalid model index {model_idx}. Valid indices: 1-{len(models)}")
        except (ValueError, TypeError):
            # Not an int, assume model is a name
            pass
        return handler_cls(model)
    return handler_cls()

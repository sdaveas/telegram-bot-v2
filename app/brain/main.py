
import sys
from .factory import get_brain_handler, available_backends, select_backend

def main():

    if len(sys.argv) > 2:
        backend = sys.argv[1]
        model = sys.argv[2]
    else:
        backends = available_backends()
        print("Available backends:")
        for idx, name in enumerate(backends, 1):
            print(f"  {idx}. {name}")
        while True:
            choice = input("Select backend by name or index: ").strip()
            try:
                backend = select_backend(choice)
                break
            except ValueError as e:
                print(e)
        # Prompt for model
        # Dynamically import the handler to get available models
        from .factory import _BACKENDS
        handler_cls = _BACKENDS[backend]
        handler_tmp = handler_cls()  # Use default model to get list
        models = handler_tmp.get_models()
        print(f"Available models for {backend}:")
        for idx, name in enumerate(models, 1):
            print(f"  {idx}. {name}")
        while True:
            model_choice = input("Select model by name or index (Enter for default): ").strip()
            if not model_choice:
                model = None
                break
            if model_choice.isdigit():
                idx = int(model_choice)
                if 1 <= idx <= len(models):
                    model = idx
                    break
            elif model_choice in models:
                model = model_choice
                break
            print(f"Invalid model. Please choose one of: {', '.join(models)} or their index.")
    try:
        brain = get_brain_handler(backend, model)
    except Exception as e:
        print(f"Failed to load backend '{backend}' with model '{model}': {e}")
        sys.exit(1)
    print(f"Loaded brain: {type(brain).__name__} (model: {getattr(brain, 'model_name', None)})")
    print("Type 'exit' to quit.")
    while True:
        prompt = input("You: ")
        if prompt.strip().lower() == "exit":
            break
        # For image test, type: image <path> <caption>
        if prompt.startswith("image "):
            try:
                _, path, *caption = prompt.split()
                caption = " ".join(caption)
                with open(path, "rb") as f:
                    image_bytes = f.read()
                import asyncio
                result = asyncio.run(brain.process_image(image_bytes, caption))
                print(f"Bot: {result}")
            except Exception as e:
                print(f"Error: {e}")
        else:
            result = brain.process(prompt)
            print(f"Bot: {result}")

if __name__ == "__main__":
    main()

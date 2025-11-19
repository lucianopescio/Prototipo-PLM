"""
Lightweight AI model integration helpers.
These functions use safe imports so the codebase remains importable
when the heavy libraries are not installed in all environments.
"""
from typing import Any, Dict, Optional


def _safe_import_torch():
    try:
        import torch
        return torch
    except Exception:
        return None


def _safe_import_tf():
    try:
        import tensorflow as tf
        return tf
    except Exception:
        return None


def _safe_import_transformers():
    try:
        import transformers
        return transformers
    except Exception:
        return None


def load_pytorch_model(model_fn: str, device: Optional[str] = None) -> Any:
    """Load a PyTorch model from a file path. Returns the model or raises ImportError.
    model_fn may be a path or a huggingface repo identifier depending on usage.
    """
    torch = _safe_import_torch()
    if torch is None:
        raise ImportError("PyTorch is not installed. Install it to use load_pytorch_model.")

    device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    # Minimal loading behavior: attempt torch.load
    model = torch.load(model_fn, map_location=device)
    model.to(device)
    model.eval()
    return model


def load_transformers_model(model_name: str):
    transformers = _safe_import_transformers()
    if transformers is None:
        raise ImportError("transformers is not installed. Install transformers to use this function.")

    from transformers import AutoModel, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)
    model.eval()
    return model, tokenizer


def load_tensorflow_model(path: str):
    tf = _safe_import_tf()
    if tf is None:
        raise ImportError("TensorFlow is not installed. Install tensorflow to use this function.")
    return tf.keras.models.load_model(path)


def infer_with_pytorch(model: Any, inputs: Any, device: Optional[str] = None) -> Any:
    torch = _safe_import_torch()
    if torch is None:
        raise ImportError("PyTorch is not installed.")
    device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    with torch.no_grad():
        inputs = inputs.to(device) if hasattr(inputs, "to") else inputs
        return model(inputs)


def try_load_tiny_transformers(model_name: str = "sshleifer/tiny-gpt2") -> Dict[str, str]:
    """Attempt to load a small Transformers model and tokenizer to verify environment.
    Returns a dict with status and message. Does not keep the model in memory.
    """
    transformers = _safe_import_transformers()
    if transformers is None:
        return {"status": "error", "message": "transformers not installed"}

    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(model_name)
        # quick test: tokenize and do a tiny forward pass on CPU
        import torch as _torch
        model.to("cpu")
        model.eval()
        inputs = tokenizer("Hello world", return_tensors="pt")
        with _torch.no_grad():
            _ = model(**inputs)
        # delete references
        del model
        del tokenizer
        return {"status": "ok", "message": f"Loaded and ran {model_name}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

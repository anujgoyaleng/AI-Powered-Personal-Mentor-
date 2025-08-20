"""
Tokenization utilities.

- Tries to use `tiktoken` if available for accurate token counts.
- Falls back to a heuristic word/punctuation splitter when unavailable.

Usage:
    from backend.python_service.utils.tokenizer import count_tokens
    n = count_tokens("Hello world", model_name="gpt-3.5-turbo")
"""
from __future__ import annotations
import re
from typing import Optional


def _heuristic_count(text: str) -> int:
    # Split into words and punctuation tokens as a rough approximation
    return len(re.findall(r"\w+|[^\w\s]", text, flags=re.UNICODE))


def count_tokens(text: str, model_name: Optional[str] = None) -> int:
    """Return token count for text.

    Attempts to use `tiktoken` if installed. Falls back to a heuristic
    that approximates tokens by words/punctuation.
    """
    try:
        import tiktoken  # type: ignore
        enc = None
        if model_name:
            try:
                enc = tiktoken.encoding_for_model(model_name)
            except Exception:
                pass
        if enc is None:
            # Use a common base if model-specific is unavailable
            enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))
    except Exception:
        return _heuristic_count(text)
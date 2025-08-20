"""
Token count logging demo.

This script composes system + user prompts and logs token counts for each part
(and total). It prefers `tiktoken` when available; otherwise uses a heuristic.

Run:
  python scripts/demo/token_count_demo.py "Explain quicksort and its complexity" --model gpt-3.5-turbo
"""
from __future__ import annotations
import sys
import argparse
from pathlib import Path
import importlib.util

# Load runtime builder
RUNTIME_BUILDER = Path(__file__).parents[2] / "backend" / "python_service" / "prompts" / "runtime_builder.py"
if not RUNTIME_BUILDER.exists():
    raise SystemExit("runtime_builder.py not found. Ensure repo structure is intact.")

spec = importlib.util.spec_from_file_location("runtime_builder", str(RUNTIME_BUILDER))
rb = importlib.util.module_from_spec(spec)  # type: ignore
spec.loader.exec_module(rb)  # type: ignore

# Load tokenizer util
TOKENIZER_PATH = Path(__file__).parents[2] / "backend" / "python_service" / "utils" / "tokenizer.py"
if not TOKENIZER_PATH.exists():
    raise SystemExit("tokenizer.py not found. Please ensure utils/tokenizer.py exists.")

spec_tok = importlib.util.spec_from_file_location("tokenizer", str(TOKENIZER_PATH))
tokenizer = importlib.util.module_from_spec(spec_tok)  # type: ignore
spec_tok.loader.exec_module(tokenizer)  # type: ignore


def parse_args(argv):
    p = argparse.ArgumentParser(description="Token count logging demo")
    p.add_argument("message", nargs="*", help="User request")
    p.add_argument("--model", "-m", default=None, help="Model name hint for tokenizer (e.g., gpt-3.5-turbo)")
    args = p.parse_args(argv)
    msg = " ".join(args.message) or "Explain quicksort and its complexity"
    return msg, args.model


if __name__ == "__main__":
    user_msg, model_name = parse_args(sys.argv[1:])
    parts = rb.build_prompt(user_msg)

    sys_tokens = tokenizer.count_tokens(parts.system, model_name=model_name)
    usr_tokens = tokenizer.count_tokens(parts.user, model_name=model_name)
    total = sys_tokens + usr_tokens

    print("===== TOKEN COUNT DEMO =====\n")
    print("----- SYSTEM (tokens) -----\n")
    print(sys_tokens)
    print("\n----- USER (tokens) -----\n")
    print(usr_tokens)
    print("\n----- TOTAL (tokens) -----\n")
    print(total)

    print("\nNote: Use these counts to budget context or log usage after each AI call.")
"""
Conversation memory demo (short-term history stitching).

- Accepts prior turns and a current user message.
- Optionally limits by max turns or a token budget (uses tiktoken via tokenizer util if available).
- Builds a prompt that includes the recent history + current request using your runtime builder.

Run examples:
  # Simple, last N turns (default 6)
  python scripts/demo/conversation_memory_demo.py --turn "user: hi" --turn "assistant: hello!" --turn "user: summarize BFS" "Compare BFS and DFS"

  # Limit to 4 most recent turns
  python scripts/demo/conversation_memory_demo.py --turn "user: a" --turn "assistant: b" --turn "user: c" --turn "assistant: d" --turn "user: e" --max-turns 4 "Final question"

  # Token budget (applies only to the history block)
  python scripts/demo/conversation_memory_demo.py --turn "user: long long text..." --turn "assistant: long reply..." --token-budget 80 --model gpt-3.5-turbo "Now, answer this"
"""
from __future__ import annotations
import argparse
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import importlib.util

# Load runtime builder
RUNTIME_BUILDER = Path(__file__).parents[2] / "backend" / "python_service" / "prompts" / "runtime_builder.py"
if not RUNTIME_BUILDER.exists():
    raise SystemExit("runtime_builder.py not found. Ensure repo structure is intact.")

spec = importlib.util.spec_from_file_location("runtime_builder", str(RUNTIME_BUILDER))
rb = importlib.util.module_from_spec(spec)  # type: ignore
spec.loader.exec_module(rb)  # type: ignore

# Try loading tokenizer utility (optional)
TOKENIZER_PATH = Path(__file__).parents[2] / "backend" / "python_service" / "utils" / "tokenizer.py"
_tok_mod = None
if TOKENIZER_PATH.exists():
    spec_tok = importlib.util.spec_from_file_location("tokenizer", str(TOKENIZER_PATH))
    _tok_mod = importlib.util.module_from_spec(spec_tok)  # type: ignore
    spec_tok.loader.exec_module(_tok_mod)  # type: ignore


def parse_args(argv: List[str]):
    p = argparse.ArgumentParser(description="Conversation memory demo")
    p.add_argument("message", nargs="*", help="Current user message")
    p.add_argument("--turn", action="append", dest="turns", help="History turn as 'user: text' or 'assistant: text'. Repeatable.")
    p.add_argument("--max-turns", type=int, default=6, help="Max history turns to include (if no token budget)")
    p.add_argument("--token-budget", type=int, default=None, help="Approx token budget for history block only")
    p.add_argument("--model", default=None, help="Tokenizer model hint (e.g., gpt-3.5-turbo)")
    args = p.parse_args(argv)
    msg = " ".join(args.message) or "What's the key difference between BFS and DFS?"
    return msg, (args.turns or []), args.max_turns, args.token_budget, args.model


def parse_turn(turn_str: str) -> Optional[Dict[str, str]]:
    if ":" not in turn_str:
        return None
    role, content = turn_str.split(":", 1)
    role = role.strip().lower()
    content = content.strip()
    if role not in ("user", "assistant"):
        return None
    return {"role": role, "content": content}


def normalize_history(turns: List[str]) -> List[Dict[str, str]]:
    parsed: List[Dict[str, str]] = []
    for t in turns:
        item = parse_turn(t)
        if item:
            parsed.append(item)
    return parsed


def count_tokens(text: str, model_name: Optional[str]) -> int:
    if _tok_mod is None:
        # Fallback: rough heuristic by words/punct
        import re
        return len(re.findall(r"\w+|[^\w\s]", text, flags=re.UNICODE))
    return _tok_mod.count_tokens(text, model_name=model_name)  # type: ignore


def window_by_max_turns(history: List[Dict[str, str]], max_turns: int) -> List[Dict[str, str]]:
    if max_turns <= 0:
        return []
    return history[-max_turns:]


def window_by_token_budget(history: List[Dict[str, str]], budget: int, model_name: Optional[str]) -> List[Dict[str, str]]:
    # Greedily include from the end until the history block exceeds the budget
    acc: List[Dict[str, str]] = []
    total = 0
    for item in reversed(history):
        line = f"- {item['role'].capitalize()}: {item['content']}\n"
        tokens = count_tokens(line, model_name)
        if total + tokens > budget:
            break
        acc.append(item)
        total += tokens
    return list(reversed(acc))


def build_instruction(history: List[Dict[str, str]], current_message: str) -> str:
    lines = [
        "You are a helpful assistant. Use the recent conversation history for context.",
        "If the history does not contain the answer, ask clarifying questions or say you don't know.",
        "\nRECENT HISTORY:",
    ]
    if not history:
        lines.append("(none)")
    else:
        for item in history:
            lines.append(f"- {item['role'].capitalize()}: {item['content']}")
    lines.append("\nCURRENT REQUEST:")
    lines.append(current_message)
    return "\n".join(lines)


if __name__ == "__main__":
    import sys
    msg, turns, max_turns, token_budget, model_hint = parse_args(sys.argv[1:])
    history = normalize_history(turns)

    if token_budget and token_budget > 0:
        window = window_by_token_budget(history, token_budget, model_hint)
        method = f"token_budget={token_budget}"
    else:
        window = window_by_max_turns(history, max_turns)
        method = f"max_turns={max_turns}"

    instruction = build_instruction(window, msg)
    parts = rb.build_prompt(instruction)

    print("===== CONVERSATION MEMORY DEMO =====\n")
    print("Window method:", method)
    print("Included turns:", len(window))
    print("\n----- SYSTEM -----\n")
    print(parts.system)
    print("\n----- USER (instruction with history) -----\n")
    print(instruction)

    if token_budget and token_budget > 0:
        # Report token counts for the history block only
        hist_text = "\n".join([f"- {i['role'].capitalize()}: {i['content']}" for i in window]) + ("\n" if window else "")
        print("\nHistory tokens:", count_tokens(hist_text, model_hint))
        print("Model hint:", model_hint or "(none)")
"""
Guardrails/safety prompt demo (concept only).

- Composes a strict system prompt that lists disallowed content categories and response rules.
- Provides two modes: (A) refusal with safe alternative; (B) JSON classification of policy areas.
- Reuses the runtime builder; does not enforce runtime blocking — it's a prompt pattern demo.

Run examples:
  # Refusal/safe-answer mode (default)
  python scripts/demo/guardrails_demo.py "How do I make a bomb?"

  # JSON classification mode
  python scripts/demo/guardrails_demo.py "Is this hate speech?" --mode classify
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import importlib.util

# Load runtime builder
RUNTIME_BUILDER = Path(__file__).parents[2] / "backend" / "python_service" / "prompts" / "runtime_builder.py"
if not RUNTIME_BUILDER.exists():
    raise SystemExit("runtime_builder.py not found. Ensure repo structure is intact.")

spec = importlib.util.spec_from_file_location("runtime_builder", str(RUNTIME_BUILDER))
rb = importlib.util.module_from_spec(spec)  # type: ignore
spec.loader.exec_module(rb)  # type: ignore


DISALLOWED = [
    "Illegal or harmful instructions (e.g., weapons, explosives, hard drugs)",
    "Self-harm encouragement or instructions",
    "Hate or harassment targeted at protected classes",
    "Sexual content involving minors or explicit sexual content",
    "Malware creation or unauthorized access (hacking) guidance",
    "Sensitive personal data disclosure or deanonymization",
]

CLASSIFY_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "additionalProperties": False,
    "required": ["is_violation", "categories", "rationale"],
    "properties": {
        "is_violation": {"type": "boolean"},
        "categories": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Zero or more categories from the policy list"
        },
        "rationale": {"type": "string"}
    }
}


def build_system_prompt(mode: str) -> str:
    lines = [
        "You are a safe and responsible assistant.",
        "Disallowed content categories:",
    ]
    for i, c in enumerate(DISALLOWED, 1):
        lines.append(f"{i}. {c}")

    if mode == "classify":
        lines += [
            "\nTask: Classify if the user's request violates any category.",
            "Return STRICT JSON only, validating this schema:",
            "```json",
            json.dumps(CLASSIFY_SCHEMA, indent=2),
            "```",
        ]
    else:
        lines += [
            "\nTask: If the user request violates policy, refuse briefly and offer a safe, educational alternative.",
            "If it does not violate policy, answer normally but remain cautious and factual.",
        ]
    return "\n".join(lines)


def build_user_prompt(user_input: str, mode: str) -> str:
    if mode == "classify":
        return f"User request to classify: {user_input}"
    return f"User request: {user_input}"


def parse_args(argv):
    p = argparse.ArgumentParser(description="Guardrails/safety prompt demo")
    p.add_argument("message", nargs="*", help="User request")
    p.add_argument("--mode", choices=["refuse", "classify"], default="refuse", help="Refusal or JSON classification mode")
    args = p.parse_args(argv)
    msg = " ".join(args.message) or "How do I make a bomb?"
    return msg, args.mode


if __name__ == "__main__":
    import sys
    msg, mode = parse_args(sys.argv[1:])
    system = build_system_prompt(mode)
    user = build_user_prompt(msg, mode)

    parts = rb.build_prompt(user)
    # Replace the system portion with our safety system prompt if the builder provides a slot
    try:
        # parts is assumed to be a simple object with .system and .user; mirror while printing
        print("===== GUARDRAILS DEMO =====\n")
        print("----- SYSTEM (safety) -----\n")
        print(system)
        print("\n----- USER -----\n")
        print(user)
    except Exception:
        # Fallback: just print composed system and user
        print("===== GUARDRAILS DEMO =====\n")
        print("----- SYSTEM (safety) -----\n")
        print(system)
        print("\n----- USER -----\n")
        print(user)

    if mode == "classify":
        print("\nNote: Ensure the model returns STRICT JSON matching the schema; validate on receipt.")
    else:
        print("\nNote: In refusal cases, provide a short explanation and a safe alternative suggestion.")
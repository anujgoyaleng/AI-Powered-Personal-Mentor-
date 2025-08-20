"""
Minimal runtime prompt builder for composing system and user prompts.
- Keeps responsibilities small for PR.
- No external LLM calls; just returns composed strings.
"""
from dataclasses import dataclass
from pathlib import Path

SYSTEM_PROMPT_PATH = Path(__file__).with_name("system_prompt.md")


def load_system_prompt() -> str:
    if not SYSTEM_PROMPT_PATH.exists():
        raise FileNotFoundError(f"Missing system prompt at {SYSTEM_PROMPT_PATH}")
    return SYSTEM_PROMPT_PATH.read_text(encoding="utf-8").strip()


@dataclass
class PromptParts:
    system: str
    user: str


def build_prompt(user_message: str) -> PromptParts:
    """Compose system + user into a minimal structure.

    Args:
        user_message: Raw user input string.
    Returns:
        PromptParts with system and user content.
    """
    system = load_system_prompt()
    user = user_message.strip()
    return PromptParts(system=system, user=user)


if __name__ == "__main__":
    # Simple manual test
    parts = build_prompt("Explain the difference between stack and queue with examples.")
    print("--- SYSTEM ---\n", parts.system)
    print("\n--- USER ---\n", parts.user)
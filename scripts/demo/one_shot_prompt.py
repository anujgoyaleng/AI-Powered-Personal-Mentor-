"""One-shot prompting demo.
Run:
  python scripts/demo/one_shot_prompt.py "Explain memoization with a simple example"

One-shot: Provide one example (User + Assistant) before the target user query.
"""
import sys
from pathlib import Path

# Reuse the existing minimal prompt builder
RUNTIME_BUILDER = Path(__file__).parents[2] / "backend" / "python_service" / "prompts" / "runtime_builder.py"
if not RUNTIME_BUILDER.exists():
    raise SystemExit("runtime_builder.py not found. Ensure repo structure is intact.")

import importlib.util
spec = importlib.util.spec_from_file_location("runtime_builder", str(RUNTIME_BUILDER))
rb = importlib.util.module_from_spec(spec)  # type: ignore
spec.loader.exec_module(rb)  # type: ignore

# Example pair (User -> Assistant)
EXAMPLE_USER = "Write a Python function to check if a string is a palindrome."
EXAMPLE_ASSISTANT = (
    "Here's a clean solution with O(n) time and O(1) extra space:\n\n"
    "```python\n"
    "def is_palindrome(s: str) -> bool:\n"
    "    i, j = 0, len(s) - 1\n"
    "    while i < j:\n"
    "        if s[i] != s[j]:\n"
    "            return False\n"
    "        i += 1\n"
    "        j -= 1\n"
    "    return True\n"
    "```\n"
    "- Time: O(n), Space: O(1) (ignoring input)\n"
    "- Idea: Two pointers moving toward the center compare mirrored characters."
)

user_msg = " ".join(sys.argv[1:]) or "Explain memoization with a simple example."
parts = rb.build_prompt(user_msg)

print("===== ONE-SHOT PROMPT =====\n")
print("----- SYSTEM -----\n")
print(parts.system)
print("\n----- EXAMPLE -----\n")
print(f"User: {EXAMPLE_USER}\n")
print(f"Assistant: {EXAMPLE_ASSISTANT}\n")
print("----- USER -----\n")
print(user_msg)
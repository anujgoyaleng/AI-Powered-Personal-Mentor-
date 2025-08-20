"""Zero-shot prompting demo.
Run:
  python scripts/demo/zero_shot_prompt.py "Explain quicksort and its complexity"

Zero-shot: No examples are provided; the model receives only the system and user prompts.
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

user_msg = " ".join(sys.argv[1:]) or "Describe the difference between DFS and BFS."
parts = rb.build_prompt(user_msg)

print("===== ZERO-SHOT PROMPT =====\n")
print("(No examples are included — only system and user messages)\n")
print("----- SYSTEM -----\n")
print(parts.system)
print("\n----- USER -----\n")
print(parts.user)
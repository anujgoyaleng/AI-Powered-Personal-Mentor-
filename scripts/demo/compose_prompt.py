"""Demo script: compose a system + user prompt.
Run:
  python scripts/demo/compose_prompt.py "Write a BFS in Python"
"""
import sys
from pathlib import Path

# Local import without packaging
RUNTIME_BUILDER = Path(__file__).parents[2] / "backend" / "python_service" / "prompts" / "runtime_builder.py"
if not RUNTIME_BUILDER.exists():
    raise SystemExit("runtime_builder.py not found. Ensure repo structure is intact.")

# Cheap import hack for demo without installing as a package
import importlib.util
spec = importlib.util.spec_from_file_location("runtime_builder", str(RUNTIME_BUILDER))
rb = importlib.util.module_from_spec(spec)  # type: ignore
spec.loader.exec_module(rb)  # type: ignore

user_msg = " ".join(sys.argv[1:]) or "Explain binary search with time and space complexity."
parts = rb.build_prompt(user_msg)

print("===== SYSTEM =====\n")
print(parts.system)
print("\n===== USER =====\n")
print(parts.user)
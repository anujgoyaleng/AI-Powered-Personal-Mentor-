"""
Multi-shot prompting demo.
Run:
  python scripts/demo/multi_shot_prompt.py "Give feedback on a STAR answer for handling a tight deadline"

Multi-shot: Provide multiple (User + Assistant) examples before the target user query.
"""
import sys
from pathlib import Path
import importlib.util

# Reuse the existing minimal prompt builder
RUNTIME_BUILDER = Path(__file__).parents[2] / "backend" / "python_service" / "prompts" / "runtime_builder.py"
if not RUNTIME_BUILDER.exists():
    raise SystemExit("runtime_builder.py not found. Ensure repo structure is intact.")

# Cheap import hack for demo without packaging
spec = importlib.util.spec_from_file_location("runtime_builder", str(RUNTIME_BUILDER))
rb = importlib.util.module_from_spec(spec)  # type: ignore
spec.loader.exec_module(rb)  # type: ignore

# Example pairs (User -> Assistant)
EXAMPLES: list[tuple[str, str]] = [
    (
        "Tell me about a time you failed.",
        (
            "Provide STAR-structured feedback: clarify Situation/Task, emphasize learning, "
            "show corrective Action, and end with Result/impact. Keep it concise and reflective."
        ),
    ),
    (
        "Describe a conflict you had with a teammate.",
        (
            "Coach on empathy, clear communication, specific Actions (listening, aligning goals), "
            "and measurable Result. Suggest phrasing that avoids blame."
        ),
    ),
    (
        "Why should we hire you?",
        (
            "Guide to align strengths with role requirements, include 1–2 quick proof points, "
            "and end with how they’ll add value in the first 90 days."
        ),
    ),
]

user_msg = " ".join(sys.argv[1:]) or "What is your greatest weakness?"
parts = rb.build_prompt(user_msg)

print("===== MULTI-SHOT PROMPT =====\n")
print("----- SYSTEM -----\n")
print(parts.system)
print("\n----- EXAMPLES -----\n")
for i, (u, a) in enumerate(EXAMPLES, 1):
    print(f"Example {i} - User: {u}\n")
    print(f"Example {i} - Assistant: {a}\n")
print("----- USER -----\n")
print(parts.user)
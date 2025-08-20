"""
Stop sequence demo (concept only).

This script doesn't call an LLM — it demonstrates how you'd pass stop sequences
as parameters alongside the composed prompt. In a real client, these tokens
halt generation once encountered.

Run examples:
  python scripts/demo/stop_sequence_demo.py "Explain BFS" --stop "\n\nUser:" --stop "```"
  python scripts/demo/stop_sequence_demo.py --stop "<END>"

It prints the composed prompt and the chosen stop sequences so you can wire
these into your actual LLM client elsewhere in the project.
"""
from __future__ import annotations
import argparse
import sys
from pathlib import Path
import importlib.util
from typing import List

# Load minimal prompt builder
RUNTIME_BUILDER = Path(__file__).parents[2] / "backend" / "python_service" / "prompts" / "runtime_builder.py"
if not RUNTIME_BUILDER.exists():
    raise SystemExit("runtime_builder.py not found. Ensure repo structure is intact.")

spec = importlib.util.spec_from_file_location("runtime_builder", str(RUNTIME_BUILDER))
rb = importlib.util.module_from_spec(spec)  # type: ignore
spec.loader.exec_module(rb)  # type: ignore


def parse_args(argv: List[str]):
    p = argparse.ArgumentParser(description="Stop sequence demo")
    p.add_argument("message", nargs="*", help="User request")
    p.add_argument(
        "--stop",
        action="append",
        dest="stops",
        help="Stop sequence token/string. Repeat flag to add multiple.",
    )
    args = p.parse_args(argv)
    msg = " ".join(args.message) or "Explain BFS vs. DFS."

    # Default common stops used in chat templating
    stops = args.stops or ["```", "\n\nUser:", "<END>"]
    return msg, stops


if __name__ == "__main__":
    user_msg, stops = parse_args(sys.argv[1:])
    parts = rb.build_prompt(user_msg)

    print("===== STOP SEQUENCES DEMO =====\n")
    print("----- SYSTEM -----\n")
    print(parts.system)
    print("\n----- USER -----\n")
    print(parts.user)
    print("\n----- STOP SEQUENCES -----\n")
    for i, s in enumerate(stops, 1):
        print(f"{i}. {repr(s)}")

    print("\nNote: Provide these stops to your LLM client's generation call to halt output when any token appears.")
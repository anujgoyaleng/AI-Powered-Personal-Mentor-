"""
Temperature demo (concept only).

This script doesn't call an LLM — it demonstrates how you'd pass temperature
(and optionally top_k, top_p) as parameters alongside the prompt parts.

Run:
  python scripts/demo/temperature_demo.py --temperature 0.2 --top-k 40 --top-p 0.9 "Explain beam search vs. sampling"

It prints the composed prompt and the chosen decoding parameters so you can wire
these into your actual LLM client elsewhere in the project.
"""
from __future__ import annotations
import argparse
import sys
from pathlib import Path
import importlib.util

# Load minimal prompt builder
RUNTIME_BUILDER = Path(__file__).parents[2] / "backend" / "python_service" / "prompts" / "runtime_builder.py"
if not RUNTIME_BUILDER.exists():
    raise SystemExit("runtime_builder.py not found. Ensure repo structure is intact.")

spec = importlib.util.spec_from_file_location("runtime_builder", str(RUNTIME_BUILDER))
rb = importlib.util.module_from_spec(spec)  # type: ignore
spec.loader.exec_module(rb)  # type: ignore


def parse_args(argv: list[str]):
    p = argparse.ArgumentParser(description="Temperature/decoding params demo")
    p.add_argument("message", nargs="*", help="User request")
    p.add_argument("--temperature", "-t", type=float, default=0.7, help="Sampling temperature (0.0-2.0)")
    p.add_argument("--top-k", type=int, default=None, help="Top-K sampling cutoff (e.g., 40)")
    p.add_argument("--top-p", type=float, default=None, help="Nucleus sampling probability (e.g., 0.9)")
    args = p.parse_args(argv)
    msg = " ".join(args.message) or "Explain beam search vs. sampling."
    return msg, args


if __name__ == "__main__":
    user_msg, args = parse_args(sys.argv[1:])
    parts = rb.build_prompt(user_msg)

    print("===== TEMPERATURE / DECODING DEMO =====\n")
    print("----- SYSTEM -----\n")
    print(parts.system)
    print("\n----- USER -----\n")
    print(parts.user)
    print("\n----- DECODING PARAMETERS -----\n")
    print({
        "temperature": args.temperature,
        "top_k": args.top_k,
        "top_p": args.top_p,
    })

    print("\nNote: Pass these parameters to your actual LLM client when generating.")
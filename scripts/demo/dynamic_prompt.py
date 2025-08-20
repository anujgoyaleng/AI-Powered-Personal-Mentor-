"""
Dynamic prompting demo.
Run examples:
  # Auto-detect language from message
  python scripts/demo/dynamic_prompt.py "Write me code for a binary search tree in C++"

  # Or override language/topic and detail level explicitly
  python scripts/demo/dynamic_prompt.py "Implement Dijkstra's algorithm" --lang python --detail deep

This script demonstrates dynamic prompt construction based on user intent, language, and desired detail level.
It reuses the system prompt via runtime_builder but crafts the user message at runtime.
"""
from __future__ import annotations
import re
import sys
import argparse
from dataclasses import dataclass
from pathlib import Path
import importlib.util

# Load the minimal prompt builder (system + passthrough user)
RUNTIME_BUILDER = Path(__file__).parents[2] / "backend" / "python_service" / "prompts" / "runtime_builder.py"
if not RUNTIME_BUILDER.exists():
    raise SystemExit("runtime_builder.py not found. Ensure repo structure is intact.")

spec = importlib.util.spec_from_file_location("runtime_builder", str(RUNTIME_BUILDER))
rb = importlib.util.module_from_spec(spec)  # type: ignore
spec.loader.exec_module(rb)  # type: ignore


LANG_ALIASES = {
    "c++": "C++",
    "cpp": "C++",
    "c#": "C#",
    "csharp": "C#",
    "python": "Python",
    "py": "Python",
    "java": "Java",
    "javascript": "JavaScript",
    "js": "JavaScript",
    "typescript": "TypeScript",
    "ts": "TypeScript",
    "go": "Go",
    "golang": "Go",
    "rust": "Rust",
    "ruby": "Ruby",
    "php": "PHP",
    "kotlin": "Kotlin",
    "swift": "Swift",
}

CODE_FENCE = {
    "C++": "cpp",
    "C#": "csharp",
    "Python": "python",
    "Java": "java",
    "JavaScript": "javascript",
    "TypeScript": "typescript",
    "Go": "go",
    "Rust": "rust",
    "Ruby": "ruby",
    "PHP": "php",
    "Kotlin": "kotlin",
    "Swift": "swift",
}


@dataclass
class DynamicParams:
    language: str
    topic: str
    detail: str  # "basic" | "normal" | "deep"


def detect_language(text: str) -> str | None:
    t = text.lower()
    for key, norm in LANG_ALIASES.items():
        if re.search(rf"\b{re.escape(key)}\b", t):
            return norm
    return None


def guess_topic(text: str) -> str:
    # Heuristic: extract phrase after "for" or "implement"; fallback to full text
    m = re.search(r"(?:for|implement|write)\s+(.*)", text, flags=re.IGNORECASE)
    if m:
        return m.group(1).strip().rstrip(". ")
    return text.strip().rstrip(". ")


def build_dynamic_user_message(params: DynamicParams) -> str:
    lang = params.language
    fence = CODE_FENCE.get(lang, "")

    detail_lines = {
        "basic": "Provide a short explanation and core code only.",
        "normal": "Include brief explanation, the code, and time/space complexity.",
        "deep": "Provide a concise overview, well-commented code, complexity, and 2-3 edge cases to consider.",
    }[params.detail]

    lines = [
        "You are a technical interview coach.",
        f"The user requests an implementation related to: {params.topic}.",
        f"Your task is to produce clear, well-commented {lang} code.",
        detail_lines,
        "Respond in Markdown.",
    ]

    if fence:
        lines.append(f"Label the code block as `{fence}`.")

    return "\n".join(lines)


def parse_args(argv: list[str]) -> tuple[str, DynamicParams]:
    parser = argparse.ArgumentParser(description="Dynamic prompting demo")
    parser.add_argument("message", nargs="*", help="User request")
    parser.add_argument("--lang", "-l", help="Force language (e.g., python, cpp, java)")
    parser.add_argument("--detail", "-d", choices=["basic", "normal", "deep"], default="normal")

    args = parser.parse_args(argv)
    raw_msg = " ".join(args.message) or "Write me code for a binary search tree in C++."

    language = LANG_ALIASES.get(args.lang.lower(), args.lang) if args.lang else detect_language(raw_msg)
    if not language:
        language = "Python"  # sensible default

    topic = guess_topic(raw_msg)

    return raw_msg, DynamicParams(language=language, topic=topic, detail=args.detail)


if __name__ == "__main__":
    user_input, dyn = parse_args(sys.argv[1:])

    # Compose dynamic user message and then pass through the runtime builder
    dynamic_user = build_dynamic_user_message(dyn)
    parts = rb.build_prompt(dynamic_user)

    print("===== DYNAMIC PROMPT =====\n")
    print("----- SYSTEM -----\n")
    print(parts.system)
    print("\n----- USER (dynamic) -----\n")
    print(dynamic_user)
    print("\n----- ORIGINAL INPUT -----\n")
    print(user_input)
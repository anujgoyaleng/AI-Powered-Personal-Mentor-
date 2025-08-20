"""
Structured JSON output demo (concept only).

- Composes a prompt that instructs the model to return strict JSON per a schema.
- Optionally validates a provided JSON response against the schema (uses `jsonschema` if installed; falls back to a minimal check).

Run examples:
  # Just print the prompt and schema
  python scripts/demo/structured_output_demo.py "Give feedback on an answer about handling tight deadlines"

  # Validate a JSON string against the schema
  python scripts/demo/structured_output_demo.py --json '{"strengths":["clear structure"],"weaknesses":["too generic"],"score":7,"recommendations":["add measurable outcomes"]}'

  # Validate from file
  python scripts/demo/structured_output_demo.py --json-file sample_output.json
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
import importlib.util
from typing import Any, Dict, List, Optional

# Load runtime builder (system + passthrough user)
RUNTIME_BUILDER = Path(__file__).parents[2] / "backend" / "python_service" / "prompts" / "runtime_builder.py"
if not RUNTIME_BUILDER.exists():
    raise SystemExit("runtime_builder.py not found. Ensure repo structure is intact.")

spec = importlib.util.spec_from_file_location("runtime_builder", str(RUNTIME_BUILDER))
rb = importlib.util.module_from_spec(spec)  # type: ignore
spec.loader.exec_module(rb)  # type: ignore

# Example JSON Schema for structured interview feedback
FEEDBACK_SCHEMA: Dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "InterviewFeedback",
    "type": "object",
    "additionalProperties": False,
    "required": ["strengths", "weaknesses", "score", "recommendations"],
    "properties": {
        "strengths": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 1
        },
        "weaknesses": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 1
        },
        "score": {"type": "integer", "minimum": 0, "maximum": 10},
        "recommendations": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 1
        }
    }
}


def build_user_instruction(user_topic: str) -> str:
    schema_json = json.dumps(FEEDBACK_SCHEMA, indent=2)
    lines = [
        "You are an interview coach. Return feedback as STRICT JSON only.",
        f"Topic: {user_topic or 'General interview answer review'}.",
        "Do not include any prose or explanation outside of the JSON.",
        "The JSON MUST validate against this JSON Schema:",
        "```json",
        schema_json,
        "```",
        "Rules:",
        "- No additional properties beyond those in the schema.",
        "- Use integers for 'score' between 0 and 10 inclusive.",
        "- Provide at least one item for each array.",
    ]
    return "\n".join(lines)


def parse_args(argv: List[str]):
    p = argparse.ArgumentParser(description="Structured JSON output demo")
    p.add_argument("message", nargs="*", help="User request/topic")
    p.add_argument("--json", dest="json_str", help="Raw JSON string to validate")
    p.add_argument("--json-file", dest="json_file", help="Path to JSON file to validate")
    return p.parse_args(argv)


def try_load_json(json_str: Optional[str], json_file: Optional[str]) -> Optional[Any]:
    if json_str:
        return json.loads(json_str)
    if json_file:
        p = Path(json_file)
        if not p.exists():
            raise SystemExit(f"JSON file not found: {p}")
        return json.loads(p.read_text(encoding="utf-8"))
    return None


def validate_payload(payload: Any, schema: Dict[str, Any]) -> tuple[bool, str]:
    # Prefer jsonschema if installed
    try:
        import jsonschema  # type: ignore
        jsonschema.validate(instance=payload, schema=schema)  # type: ignore
        return True, "Valid per JSON Schema"
    except Exception as e:
        # Fallback: minimal structural checks
        if isinstance(payload, dict):
            required = {"strengths", "weaknesses", "score", "recommendations"}
            if not required.issubset(payload.keys()):
                missing = required - set(payload.keys())
                return False, f"Missing keys: {sorted(missing)}"
            if not (isinstance(payload["strengths"], list) and payload["strengths"]):
                return False, "strengths must be a non-empty array"
            if not (isinstance(payload["weaknesses"], list) and payload["weaknesses"]):
                return False, "weaknesses must be a non-empty array"
            if not (isinstance(payload["recommendations"], list) and payload["recommendations"]):
                return False, "recommendations must be a non-empty array"
            if not (isinstance(payload["score"], int) and 0 <= payload["score"] <= 10):
                return False, "score must be an integer between 0 and 10"
            # Soft pass without strict additionalProperties enforcement
            return True, "Valid by minimal checks (install jsonschema for strict validation)"
        return False, "Payload must be a JSON object"


if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    user_topic = " ".join(args.message) or "General interview answer review"

    user_instruction = build_user_instruction(user_topic)
    parts = rb.build_prompt(user_instruction)

    print("===== STRUCTURED OUTPUT DEMO =====\n")
    print("----- SYSTEM -----\n")
    print(parts.system)
    print("\n----- USER (instruction) -----\n")
    print(user_instruction)

    candidate = try_load_json(args.json_str, args.json_file)
    if candidate is not None:
        ok, info = validate_payload(candidate, FEEDBACK_SCHEMA)
        print("\n----- VALIDATION RESULT -----\n")
        print(info)
        if not ok:
            # Pretty print offending payload for debugging
            print("\nProvided JSON:")
            print(json.dumps(candidate, indent=2, ensure_ascii=False))
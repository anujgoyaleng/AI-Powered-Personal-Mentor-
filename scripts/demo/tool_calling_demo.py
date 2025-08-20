"""
Function/Tool calling demo (concept only).

- Defines a small toolset with JSON Schemas for each tool's parameters.
- Builds a prompt instructing the model to select a tool and return ONLY a JSON
  object of shape: {"tool": <name>, "arguments": { ... }}
- Optionally validates a provided JSON tool call against the chosen tool schema
  (uses `jsonschema` if installed; falls back to minimal checks).

Run examples:
  # Print the prompt and tool specs
  python scripts/demo/tool_calling_demo.py "Find tomorrow's weather for Paris and then summarize it"

  # Validate a candidate tool call JSON
  python scripts/demo/tool_calling_demo.py --json '{"tool":"get_weather","arguments":{"location":"Paris","unit":"C","date":"2025-08-21"}}'
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
import importlib.util
from typing import Any, Dict, List, Optional

# Load runtime builder
RUNTIME_BUILDER = Path(__file__).parents[2] / "backend" / "python_service" / "prompts" / "runtime_builder.py"
if not RUNTIME_BUILDER.exists():
    raise SystemExit("runtime_builder.py not found. Ensure repo structure is intact.")

spec = importlib.util.spec_from_file_location("runtime_builder", str(RUNTIME_BUILDER))
rb = importlib.util.module_from_spec(spec)  # type: ignore
spec.loader.exec_module(rb)  # type: ignore

# Define a small toolset with parameter schemas
TOOLS: Dict[str, Dict[str, Any]] = {
    "get_weather": {
        "description": "Get weather for a city",
        "parameters": {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "additionalProperties": False,
            "required": ["location"],
            "properties": {
                "location": {"type": "string", "minLength": 1},
                "unit": {"type": "string", "enum": ["C", "F"], "default": "C"},
                "date": {"type": "string", "description": "YYYY-MM-DD (optional)"}
            }
        }
    },
    "search_docs": {
        "description": "Search internal documentation",
        "parameters": {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "additionalProperties": False,
            "required": ["query"],
            "properties": {
                "query": {"type": "string", "minLength": 3},
                "top_k": {"type": "integer", "minimum": 1, "maximum": 20, "default": 5}
            }
        }
    },
    "schedule_meeting": {
        "description": "Create a calendar event",
        "parameters": {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "additionalProperties": False,
            "required": ["title", "date", "attendees"],
            "properties": {
                "title": {"type": "string", "minLength": 3},
                "date": {"type": "string", "description": "YYYY-MM-DD or ISO datetime"},
                "attendees": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 1
                },
                "duration_minutes": {"type": "integer", "minimum": 15, "default": 30}
            }
        }
    },
}


def build_instruction(user_goal: str) -> str:
    tool_specs = [
        {
            "name": name,
            "description": spec["description"],
            "parameters": spec["parameters"],
        }
        for name, spec in TOOLS.items()
    ]

    lines = [
        "You are a tool-using assistant. Select exactly one tool that best solves the user's request.",
        "Return ONLY a JSON object, no prose, of the form:",
        '{\n  "tool": "<tool_name>",\n  "arguments": { /* per tool schema */ }\n}',
        "Do not include explanations.",
        f"User goal: {user_goal or 'General task'}",
        "Available tools (name, description, parameters JSON Schema):",
        "```json",
        json.dumps(tool_specs, indent=2),
        "```",
        "Rules:",
        "- Choose the most appropriate single tool.",
        "- Arguments must validate against the chosen tool's JSON Schema.",
        "- Provide only the fields defined by the schema (no extras).",
    ]
    return "\n".join(lines)


def parse_args(argv: List[str]):
    p = argparse.ArgumentParser(description="Function/Tool calling demo")
    p.add_argument("message", nargs="*", help="User goal/request")
    p.add_argument("--json", dest="json_str", help="Candidate tool-call JSON to validate")
    return p.parse_args(argv)


def try_load_json(json_str: Optional[str]) -> Optional[Any]:
    if json_str:
        return json.loads(json_str)
    return None


def validate_tool_call(payload: Any) -> tuple[bool, str]:
    if not isinstance(payload, dict):
        return False, "Payload must be an object"
    tool = payload.get("tool")
    args = payload.get("arguments")
    if tool not in TOOLS:
        return False, f"Unknown tool: {tool!r}"
    if not isinstance(args, dict):
        return False, "'arguments' must be an object"

    schema = TOOLS[tool]["parameters"]
    # Prefer jsonschema if installed
    try:
        import jsonschema  # type: ignore
        jsonschema.validate(instance=args, schema=schema)  # type: ignore
        return True, "Valid per JSON Schema"
    except Exception as e:
        # Minimal fallback: check required keys exist
        req = set(schema.get("required", []))
        if not req.issubset(args.keys()):
            missing = req - set(args.keys())
            return False, f"Missing required argument(s): {sorted(missing)}"
        # Soft pass (install jsonschema for strict validation)
        return True, "Valid by minimal checks (install jsonschema for strict validation)"


if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    user_goal = " ".join(args.message) or "General task"

    instruction = build_instruction(user_goal)
    parts = rb.build_prompt(instruction)

    print("===== TOOL CALLING DEMO =====\n")
    print("----- SYSTEM -----\n")
    print(parts.system)
    print("\n----- USER (instruction) -----\n")
    print(instruction)

    candidate = try_load_json(args.json_str)
    if candidate is not None:
        ok, info = validate_tool_call(candidate)
        print("\n----- VALIDATION RESULT -----\n")
        print(info)
        if not ok:
            print("\nProvided JSON:")
            print(json.dumps(candidate, indent=2, ensure_ascii=False))
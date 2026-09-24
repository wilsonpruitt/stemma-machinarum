#!/usr/bin/env python3
"""Validate data/ against schema/ and enforce Stemma's evidence rules.

Rules enforced beyond plain JSON Schema:
  - Every edge has a non-empty `source` URL (schema requires the key;
    this also rejects an empty string).
  - Every sourced_string/sourced_number field either has status
    "recorded" (value + source both present) or status "not_recorded"/
    "partial" (value may be null, but the status must say so). A field
    can never silently omit both value and status.
  - Model ids and edge child/parent ids referenced anywhere must
    resolve to an actual file in data/models/.
"""
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_DIR = ROOT / "schema"
DATA_DIR = ROOT / "data"

errors: list[str] = []


def load_schema(name: str) -> Draft202012Validator:
    with open(SCHEMA_DIR / name) as f:
        return Draft202012Validator(json.load(f))


def check_sourced_fields(obj, path=""):
    """Walk a record; for any dict that looks like a sourced field
    (has a 'status' key), enforce recorded => value+source present."""
    if isinstance(obj, dict):
        if "status" in obj and set(obj.keys()) <= {"value", "source", "status"}:
            status = obj.get("status")
            if status == "recorded" and (obj.get("value") in (None, "") or not obj.get("source")):
                errors.append(f"{path}: status is 'recorded' but value or source is missing")
        for k, v in obj.items():
            check_sourced_fields(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            check_sourced_fields(v, f"{path}[{i}]")


def validate_models():
    schema = load_schema("model.schema.json")
    model_ids = set()
    models_dir = DATA_DIR / "models"
    for path in sorted(models_dir.glob("*.json")):
        with open(path) as f:
            record = json.load(f)
        for err in schema.iter_errors(record):
            errors.append(f"{path.name}: {err.message} (at {'/'.join(str(p) for p in err.path)})")
        check_sourced_fields(record, path.name)
        if record.get("id") != path.stem:
            errors.append(f"{path.name}: id field '{record.get('id')}' does not match filename")
        model_ids.add(record.get("id"))
    return model_ids


def validate_edges(model_ids):
    schema = load_schema("edge.schema.json")
    edges_path = DATA_DIR / "edges" / "edges.jsonl"
    if not edges_path.exists():
        return
    for lineno, line in enumerate(edges_path.read_text().splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            edge = json.loads(line)
        except json.JSONDecodeError as e:
            errors.append(f"edges.jsonl:{lineno}: invalid JSON ({e})")
            continue
        for err in schema.iter_errors(edge):
            errors.append(f"edges.jsonl:{lineno}: {err.message}")
        if not edge.get("source"):
            errors.append(f"edges.jsonl:{lineno}: edge has no source URL")
        for role in ("child", "parent"):
            ref = edge.get(role)
            if ref and ref not in model_ids:
                errors.append(f"edges.jsonl:{lineno}: {role} '{ref}' has no matching file in data/models/")


def validate_techniques():
    schema = load_schema("technique.schema.json")
    techniques_dir = DATA_DIR / "techniques"
    for path in sorted(techniques_dir.glob("*.json")):
        with open(path) as f:
            record = json.load(f)
        for err in schema.iter_errors(record):
            errors.append(f"{path.name}: {err.message}")
        check_sourced_fields(record, path.name)


def main():
    model_ids = validate_models()
    validate_edges(model_ids)
    validate_techniques()

    if errors:
        print(f"FAILED: {len(errors)} error(s)\n")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    print("OK: all records valid.")


if __name__ == "__main__":
    main()

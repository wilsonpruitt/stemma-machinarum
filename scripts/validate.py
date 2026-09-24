#!/usr/bin/env python3
"""Validate data/ against schema/ and enforce Stemma's evidence rules.

Rules enforced beyond plain JSON Schema:
  - Every edge has a non-empty `source` URL (schema requires the key;
    this also rejects an empty string).
  - Every sourced_string/sourced_number field either has status
    "recorded" (value + source both present) or status "not_recorded"/
    "partial" (value may be null, but the status must say so). A field
    can never silently omit both value and status.
  - Model and dataset ids share one namespace: each is unique and
    matches its filename. Edge child/parent ids must resolve to a file
    in data/models/ or data/datasets/.
  - Relations join the right kinds of record: trained_on runs from a
    model to a dataset; distilled_from_outputs and feedback_from need a
    model parent (the child may be a model or a dataset); every other
    relation joins two models.
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
        if "status" in obj and set(obj.keys()) <= {"value", "source", "status", "note"}:
            status = obj.get("status")
            if status == "recorded" and (obj.get("value") in (None, "") or not obj.get("source")):
                errors.append(f"{path}: status is 'recorded' but value or source is missing")
        for k, v in obj.items():
            check_sourced_fields(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            check_sourced_fields(v, f"{path}[{i}]")


def validate_records(subdir, schema_name, taken):
    """Validate every record in data/<subdir>/; return its ids.
    `taken` holds ids already used, so models and datasets can't collide."""
    schema = load_schema(schema_name)
    ids = set()
    for path in sorted((DATA_DIR / subdir).glob("*.json")):
        with open(path) as f:
            record = json.load(f)
        for err in schema.iter_errors(record):
            errors.append(f"{path.name}: {err.message} (at {'/'.join(str(p) for p in err.path)})")
        check_sourced_fields(record, path.name)
        rid = record.get("id")
        if rid != path.stem:
            errors.append(f"{path.name}: id field '{rid}' does not match filename")
        if rid in taken or rid in ids:
            errors.append(f"{subdir}/{path.name}: id '{rid}' is already used by another record")
        ids.add(rid)
    return ids


MODEL_PARENT_ONLY = {"distilled_from_outputs", "feedback_from"}


def validate_edges(model_ids, dataset_ids):
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
        child, parent, rel = edge.get("child"), edge.get("parent"), edge.get("relation")
        for role, ref in (("child", child), ("parent", parent)):
            if ref and ref not in model_ids and ref not in dataset_ids:
                errors.append(f"edges.jsonl:{lineno}: {role} '{ref}' has no matching file in data/models/ or data/datasets/")
        if rel == "trained_on":
            if child in dataset_ids or parent in model_ids:
                errors.append(f"edges.jsonl:{lineno}: trained_on must run from a model (child) to a dataset (parent)")
        elif rel in MODEL_PARENT_ONLY:
            if parent in dataset_ids:
                errors.append(f"edges.jsonl:{lineno}: {rel} needs a model as parent")
        elif child in dataset_ids or parent in dataset_ids:
            errors.append(f"edges.jsonl:{lineno}: {rel} joins two models; datasets connect only via trained_on, distilled_from_outputs, feedback_from")


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
    model_ids = validate_records("models", "model.schema.json", set())
    dataset_ids = validate_records("datasets", "dataset.schema.json", model_ids)
    validate_edges(model_ids, dataset_ids)
    validate_techniques()

    if errors:
        print(f"FAILED: {len(errors)} error(s)\n")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    print("OK: all records valid.")


if __name__ == "__main__":
    main()

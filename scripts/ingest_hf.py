#!/usr/bin/env python3
"""Pull candidate model records from the Hugging Face Hub.

Output is CANDIDATE data only — it never writes into data/models/.
Everything lands in data/staging/ (gitignored) for manual review before
anyone promotes it into the real dataset.

Requires HF_TOKEN in the environment (not hardcoded, not committed).
Usage:
    HF_TOKEN=... python3 scripts/ingest_hf.py <model-repo-id> [<model-repo-id> ...]
"""
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STAGING_DIR = ROOT / "data" / "staging"

HF_TOKEN = os.environ.get("HF_TOKEN")
RATE_LIMIT_SECONDS = 1.0


def hf_get(url: str) -> dict | str:
    req = urllib.request.Request(url)
    if HF_TOKEN:
        req.add_header("Authorization", f"Bearer {HF_TOKEN}")
    with urllib.request.urlopen(req) as resp:
        body = resp.read().decode("utf-8")
    return body


def fetch_candidate(repo_id: str) -> dict:
    """Fetch model card metadata and config.json for one HF repo."""
    safe_id = repo_id.replace("/", "__")
    candidate = {
        "repo_id": repo_id,
        "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "api_info": None,
        "config_json": None,
        "config_url": f"https://huggingface.co/{repo_id}/raw/main/config.json",
    }

    try:
        info_raw = hf_get(f"https://huggingface.co/api/models/{repo_id}")
        candidate["api_info"] = json.loads(info_raw)
    except Exception as e:
        candidate["api_info_error"] = str(e)

    try:
        candidate["config_json"] = json.loads(hf_get(candidate["config_url"]))
    except Exception as e:
        candidate["config_json_error"] = str(e)

    return candidate, safe_id


def main():
    if len(sys.argv) < 2:
        print("Usage: ingest_hf.py <model-repo-id> [<model-repo-id> ...]")
        sys.exit(1)

    STAGING_DIR.mkdir(parents=True, exist_ok=True)

    for i, repo_id in enumerate(sys.argv[1:]):
        if i > 0:
            time.sleep(RATE_LIMIT_SECONDS)
        print(f"Fetching {repo_id} ...")
        candidate, safe_id = fetch_candidate(repo_id)
        out_path = STAGING_DIR / f"{safe_id}.json"
        with open(out_path, "w") as f:
            json.dump(candidate, f, indent=2)
        print(f"  -> {out_path} (candidate only — review before adding to data/models/)")


if __name__ == "__main__":
    main()

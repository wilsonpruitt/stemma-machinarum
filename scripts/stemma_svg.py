"""Draw one family of the Stemma as a manuscript-style stemma (SVG).

Pilot for Phase 3. Time runs down the page (release month); closed models
are hollow "lost exemplars"; datasets sit in their own band; contamination
(distillation, feedback) is drawn as dashed diagonals. Line form encodes the
relation, colour encodes the evidence tag (declared is plain ink).

Usage: .venv/bin/python scripts/stemma_svg.py > export/llama-family.svg
"""
import json
import sys
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Hand-set columns for the pilot family; heights come from the data.
LANES = {
    "text-davinci-003": 110, "chatgpt": 250,
    "alpaca-52k": 350, "sharegpt-vicuna": 450,
    "alpaca-7b": 560, "vicuna-7b-v1-3": 620, "vicuna-7b-v1-5": 600,
    "llama-7b": 780, "llama-2-7b": 780, "code-llama-7b": 780,
    "codellama-7b-instruct": 700, "codellama-7b-python": 860,
    "llama-2-7b-chat": 880, "nous-hermes-llama-2-7b": 1010,
    "open-llama-7b": 960,
    "llama-2-13b": 1180, "wizardlm-13b-v1-2": 1140, "vicuna-13b-v1-5": 1290,
    "llama-2-70b": 1400,
}
SHORT = {
    "text-davinci-003": "text-davinci-003", "chatgpt": "ChatGPT",
    "alpaca-52k": "Alpaca 52K", "sharegpt-vicuna": "ShareGPT",
    "alpaca-7b": "Alpaca 7B", "vicuna-7b-v1-3": "Vicuna 7B v1.3",
    "vicuna-7b-v1-5": "Vicuna 7B v1.5", "vicuna-13b-v1-5": "Vicuna 13B v1.5",
    "llama-7b": "LLaMA 7B", "llama-2-7b": "Llama 2 7B", "llama-2-13b": "Llama 2 13B",
    "llama-2-70b": "Llama 2 70B", "llama-2-7b-chat": "Llama 2-Chat 7B",
    "code-llama-7b": "Code Llama 7B", "codellama-7b-instruct": "… Instruct",
    "codellama-7b-python": "… Python", "nous-hermes-llama-2-7b": "Nous-Hermes 7B",
    "wizardlm-13b-v1-2": "WizardLM 13B", "open-llama-7b": "OpenLLaMA 7B",
}

FORM = {
    "fine_tuned_from": "weights", "merged_from": "weights", "quantized_from": "weights", "adapter_on": "weights",
    "trained_on": "data",
    "distilled_from_outputs": "contamination", "feedback_from": "contamination",
    "successor_in_series": "design", "same_architecture_retrained": "design", "design_follows": "design",
}

TOP, MONTH_PX, MIN_GAP = 110, 100, 44
START = (2022, 11)


def month_y(date):
    y, m = int(date[:4]), int(date[5:7])
    d = int(date[8:10]) if len(date) >= 10 else 15
    months = (y - START[0]) * 12 + (m - START[1]) + (d - 1) / 30
    return TOP + months * MONTH_PX


def load():
    recs = {}
    for kind in ("models", "datasets"):
        for p in (ROOT / "data" / kind).glob("*.json"):
            d = json.loads(p.read_text())
            if d["id"] in LANES:
                recs[d["id"]] = {"kind": kind, **d}
    edges = [json.loads(l) for l in (ROOT / "data/edges/edges.jsonl").read_text().splitlines() if l.strip()]
    edges = [e for e in edges if e["child"] in recs and e["parent"] in recs]
    return recs, edges


def layout(recs, edges):
    pos = {}
    undated = []
    for i, r in recs.items():
        date = (r.get("release_date") or {}).get("value")
        if date:
            pos[i] = [LANES[i], month_y(date)]
        else:
            undated.append(i)
    # An undated dataset sits just above the earliest model trained on it.
    for i in undated:
        kids = [pos[e["child"]][1] for e in edges if e["parent"] == i and e["child"] in pos]
        pos[i] = [LANES[i], min(kids) - MIN_GAP]
    # A child is never drawn level with its parent: push it down a notch.
    for _ in range(len(recs)):
        for e in edges:
            c, p = pos[e["child"]], pos[e["parent"]]
            if c[1] < p[1] + MIN_GAP:
                c[1] = p[1] + MIN_GAP
    return pos, undated


def svg(recs, edges, pos, undated):
    W = 1520
    H = int(max(y for _, y in pos.values()) + 120)
    o = []
    o.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="Georgia, serif" role="img" aria-labelledby="t">')
    o.append('<title id="t">The LLaMA family, drawn as a stemma</title>')
    o.append("""<style>
  svg { --bg:#fbfaf7; --ink:#1d1c1a; --muted:#6a665e; --rule:#dcd7cc;
        --uploader:#245e7a; --weights:#6b4a10; --behavior:#5a3a7a; --alleged:#9a2a1a; background:var(--bg); }
  @media (prefers-color-scheme: dark) {
    svg { --bg:#17161a; --ink:#e8e5dd; --muted:#a09b90; --rule:#34313a;
          --uploader:#7fbfe0; --weights:#dcb86a; --behavior:#c4a4e8; --alleged:#f09a88; }
  }
  .axis { stroke:var(--rule); stroke-width:1; }
  .month { fill:var(--muted); font:11px system-ui, sans-serif; }
  .band { fill:var(--muted); font:11px system-ui, sans-serif; letter-spacing:.08em; text-transform:uppercase; }
  .lbl { fill:var(--ink); font-size:13px; paint-order:stroke; stroke:var(--bg); stroke-width:4px; stroke-linejoin:round; }
  .sub { fill:var(--muted); font:italic 11px Georgia, serif; paint-order:stroke; stroke:var(--bg); stroke-width:4px; }
  .e { fill:none; stroke:var(--ink); }
  .weights { stroke-width:2.2; }
  .data { stroke-width:1.2; }
  .contamination { stroke-width:1.6; stroke-dasharray:6 4; }
  .design { stroke-width:1; stroke-dasharray:1 3; stroke-linecap:round; opacity:.8; }
  .ev-declared_by_uploader { stroke:var(--uploader); }
  .ev-inferred_weights { stroke:var(--weights); }
  .ev-inferred_behavior { stroke:var(--behavior); }
  .ev-alleged { stroke:var(--alleged); }
  .open { fill:var(--ink); }
  .closed { fill:var(--bg); stroke:var(--ink); stroke-width:1.6; stroke-dasharray:3 2; }
  .ds { fill:var(--bg); stroke:var(--ink); stroke-width:1.4; }
  .lgd { fill:var(--ink); font:12px system-ui, sans-serif; }
</style>""")

    # Month rules down the left margin.
    y0, m0 = START
    for k in range(0, 11):
        y, m = y0 + (m0 - 1 + k) // 12, (m0 - 1 + k) % 12 + 1
        yy = TOP + k * MONTH_PX
        o.append(f'<line class="axis" x1="20" x2="{W-20}" y1="{yy:.0f}" y2="{yy:.0f}" opacity=".45"/>')
        o.append(f'<text class="month" x="20" y="{yy-4:.0f}">{y}-{m:02d}</text>')

    # Band headers.
    for x, label in ((190, "Closed · known by outputs"), (400, "Datasets"), (1000, "Open weights")):
        o.append(f'<text class="band" x="{x}" y="60" text-anchor="middle">{label}</text>')

    # Edges under nodes.
    for e in edges:
        (cx, cy), (px, py) = pos[e["child"]], pos[e["parent"]]
        form = FORM[e["relation"]]
        ev = e["evidence"]
        title = escape(f'{e["child"]} ← {e["relation"]} ← {e["parent"]} ({ev})')
        if form == "weights" and cx != px:
            mid = py + (cy - py) * 0.7
            d = f"M{px},{py} L{px},{mid:.0f} L{cx},{mid:.0f} L{cx},{cy}"
        else:
            d = f"M{px},{py} L{cx},{cy}"
        o.append(f'<a href="{escape(e["source"])}"><path class="e {form} ev-{ev}" d="{d}"><title>{title}</title></path></a>')

    # Nodes.
    for i, (x, y) in pos.items():
        r = recs[i]
        href = f'/{"models" if r["kind"] == "models" else "datasets"}/{i}/'
        closed = r.get("weights_status") in ("closed", "api_only")
        if r["kind"] == "datasets":
            shape = f'<rect class="ds" x="{x-7}" y="{y-7}" width="14" height="14"/>'
        elif closed:
            shape = f'<circle class="closed" cx="{x}" cy="{y}" r="8"/>'
        else:
            shape = f'<circle class="open" cx="{x}" cy="{y}" r="5.5"/>'
        date = (r.get("release_date") or {}).get("value") or "date not recorded"
        sub = "closed" if closed else ("undated" if i in undated else date)
        o.append(f'<a href="{href}"><g>{shape}'
                 f'<text class="lbl" x="{x+12}" y="{y+4}">{escape(SHORT[i])}</text>'
                 f'<text class="sub" x="{x+12}" y="{y+18}">{escape(sub)}</text>'
                 f'<title>{escape(r["name"])}</title></g></a>')

    # Legend.
    ly = H - 70
    items = [
        ('<line class="e weights" x1="0" x2="34" y1="0" y2="0"/>', "weights descend (fine-tuned)"),
        ('<line class="e data" x1="0" x2="34" y1="0" y2="0"/>', "trained on dataset"),
        ('<line class="e contamination" x1="0" x2="34" y1="0" y2="0"/>', "contamination: distilled from outputs"),
        ('<line class="e design" x1="0" x2="34" y1="0" y2="0"/>', "design only: successor / follows"),
        ('<line class="e weights ev-declared_by_uploader" x1="0" x2="34" y1="0" y2="0"/>', "blue: declared by uploader, not developer"),
    ]
    x = 20
    for k, (mark, text) in enumerate(items):
        col, row = k % 3, k // 3
        gx, gy = 20 + col * 410, ly + row * 24
        o.append(f'<g transform="translate({gx},{gy})">{mark}<text class="lgd" x="44" y="4">{escape(text)}</text></g>')
    o.append(f'<text class="month" x="20" y="{H-14}">Ink lines are declared by the developer. Every line links to its source; every node to its record.</text>')
    o.append("</svg>")
    return "\n".join(o)


if __name__ == "__main__":
    recs, edges = load()
    missing = set(LANES) - set(recs)
    if missing:
        sys.exit(f"no record for: {sorted(missing)}")
    pos, undated = layout(recs, edges)
    sys.stdout.write(svg(recs, edges, pos, undated))

#!/usr/bin/env python3
"""Export the Stemma dataset as a graph: JSON (nodes/edges) and GraphML.

Usage:
    python3 scripts/export_graph.py [--out-dir DIR]

Produces:
    <out-dir>/graph.json      nodes + edges, edges carry their evidence tag
    <out-dir>/graph.graphml   same graph, GraphML for Gephi/yEd/networkx
"""
import argparse
import json
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"


def load_models():
    nodes = {}
    for path in sorted((DATA_DIR / "models").glob("*.json")):
        with open(path) as f:
            record = json.load(f)
        nodes[record["id"]] = {
            "id": record["id"],
            "name": record.get("name"),
            "developer": record.get("developer"),
            "release_date": record.get("release_date", {}).get("value"),
            "weights_status": record.get("weights_status"),
        }
    return nodes


def load_edges():
    edges = []
    edges_path = DATA_DIR / "edges" / "edges.jsonl"
    if not edges_path.exists():
        return edges
    for line in edges_path.read_text().splitlines():
        line = line.strip()
        if line:
            edges.append(json.loads(line))
    return edges


def write_json(nodes, edges, out_dir: Path):
    graph = {"nodes": list(nodes.values()), "edges": edges}
    with open(out_dir / "graph.json", "w") as f:
        json.dump(graph, f, indent=2)


def write_graphml(nodes, edges, out_dir: Path):
    ns = "http://graphml.graphdrawing.org/xmlns"
    ET.register_namespace("", ns)
    root = ET.Element(f"{{{ns}}}graphml")

    for key_id, attr_name, for_ in [
        ("d_name", "name", "node"),
        ("d_developer", "developer", "node"),
        ("d_release_date", "release_date", "node"),
        ("d_weights_status", "weights_status", "node"),
        ("d_relation", "relation", "edge"),
        ("d_evidence", "evidence", "edge"),
        ("d_source", "source", "edge"),
        ("d_via", "via", "edge"),
    ]:
        key = ET.SubElement(root, f"{{{ns}}}key")
        key.set("id", key_id)
        key.set("for", for_)
        key.set("attr.name", attr_name)
        key.set("attr.type", "string")

    graph_el = ET.SubElement(root, f"{{{ns}}}graph")
    graph_el.set("edgedefault", "directed")

    for node in nodes.values():
        node_el = ET.SubElement(graph_el, f"{{{ns}}}node")
        node_el.set("id", node["id"])
        for key_id, field in [
            ("d_name", "name"),
            ("d_developer", "developer"),
            ("d_release_date", "release_date"),
            ("d_weights_status", "weights_status"),
        ]:
            data_el = ET.SubElement(node_el, f"{{{ns}}}data")
            data_el.set("key", key_id)
            data_el.text = str(node.get(field) or "")

    for i, edge in enumerate(edges):
        edge_el = ET.SubElement(graph_el, f"{{{ns}}}edge")
        edge_el.set("id", f"e{i}")
        edge_el.set("source", edge["parent"])
        edge_el.set("target", edge["child"])
        for key_id, field in [
            ("d_relation", "relation"),
            ("d_evidence", "evidence"),
            ("d_source", "source"),
            ("d_via", "via"),
        ]:
            data_el = ET.SubElement(edge_el, f"{{{ns}}}data")
            data_el.set("key", key_id)
            data_el.text = str(edge.get(field) or "")

    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")
    tree.write(out_dir / "graph.graphml", xml_declaration=True, encoding="UTF-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default=str(ROOT / "export"))
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    nodes = load_models()
    edges = load_edges()

    write_json(nodes, edges, out_dir)
    write_graphml(nodes, edges, out_dir)

    print(f"Exported {len(nodes)} nodes, {len(edges)} edges to {out_dir}/")


if __name__ == "__main__":
    main()

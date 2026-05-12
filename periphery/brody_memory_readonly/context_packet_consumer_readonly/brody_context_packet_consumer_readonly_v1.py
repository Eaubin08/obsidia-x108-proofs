import argparse
import json
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET


BOUNDARY_FALSE_KEYS = [
    "memory_decision",
    "allowed_to_decide",
    "emits_act",
    "kernel_binding",
    "x108_runtime_binding",
    "x108_merge",
    "kernel_mutation",
    "x108_mutation",
]


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def clean_text(value, max_chars=1400):
    if not value:
        return ""
    text = re.sub(r"\s+", " ", str(value)).strip()
    return text[:max_chars]


def read_docx_text(path: Path, max_chars=1400):
    try:
        with zipfile.ZipFile(path) as z:
            xml = z.read("word/document.xml")
        root = ET.fromstring(xml)
        ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
        parts = [node.text for node in root.findall(".//w:t", ns) if node.text]
        return clean_text(" ".join(parts), max_chars=max_chars)
    except Exception:
        return ""


def read_local_excerpt(path_value, max_chars=1400):
    if not path_value:
        return ""

    path = Path(path_value)
    if not path.exists() or not path.is_file():
        return ""

    suffix = path.suffix.lower()

    if suffix == ".docx":
        return read_docx_text(path, max_chars=max_chars)

    if suffix in {
        ".md", ".txt", ".json", ".jsonl", ".py", ".ps1", ".csv",
        ".lean", ".yaml", ".yml", ".toml", ".html", ".css", ".js", ".ts"
    }:
        try:
            raw = path.read_text(encoding="utf-8", errors="ignore")
            return clean_text(raw, max_chars=max_chars)
        except Exception:
            return ""

    return ""


def load_packet(packet_json):
    path = Path(packet_json)
    if not path.exists():
        raise RuntimeError(f"MISSING_PACKET_JSON={packet_json}")

    packet = json.loads(path.read_text(encoding="utf-8"))

    if packet.get("status") != "BRODY_CONTEXT_PACKET_QUERY_READONLY_PASS":
        raise RuntimeError(f"BAD_PACKET_STATUS={packet.get('status')}")

    for key in BOUNDARY_FALSE_KEYS:
        if packet.get(key) is not False:
            raise RuntimeError(f"BOUNDARY_VIOLATION_{key}={packet.get(key)}")

    if packet.get("decision_authority") != "KX108_ONLY":
        raise RuntimeError(f"BAD_DECISION_AUTHORITY={packet.get('decision_authority')}")

    return packet


def build_response(packet, max_items=6):
    query = packet.get("query", "")
    items = packet.get("context_packet", {}).get("items", []) or []

    selected = []

    for item in items[:max_items]:
        excerpt = clean_text(item.get("excerpt"), max_chars=1400)
        if not excerpt:
            excerpt = read_local_excerpt(item.get("path"), max_chars=1400)

        selected.append({
            "rank": item.get("rank"),
            "id": item.get("id"),
            "title": item.get("title"),
            "path": item.get("path") or "",
            "tags": item.get("tags") or [],
            "score": item.get("score"),
            "source_ref": item.get("source_ref") or item.get("path") or item.get("title") or item.get("id"),
            "excerpt": excerpt,
            "has_material": bool(excerpt),
        })

    sources_cited = all(bool(x.get("source_ref")) for x in selected)
    material_count = sum(1 for x in selected if x.get("has_material"))

    response_lines = []
    response_lines.append("# BRODY LOCAL RESPONSE — READONLY")
    response_lines.append("")
    response_lines.append(f"- query: {query}")
    response_lines.append("- role: CONTEXT_CONSUMER")
    response_lines.append("- memory_role: GUIDE_CONTEXT_NAVIGATION_ONLY")
    response_lines.append("- decision_authority: KX108_ONLY")
    response_lines.append("- emits_act: false")
    response_lines.append("- kernel_mutation: false")
    response_lines.append("- x108_runtime_binding: false")
    response_lines.append("")
    response_lines.append("## Réponse locale")
    response_lines.append("")
    response_lines.append(
        "Le packet readonly fournit une surface de contexte exploitable pour orienter la réponse Brody. "
        "La sortie ci-dessous reste une consommation documentaire locale : elle ne décide pas, ne déclenche aucune action, "
        "et ne modifie pas X108."
    )
    response_lines.append("")
    response_lines.append("## Items structurants")
    response_lines.append("")

    for item in selected:
        response_lines.append(f"### {item.get('rank')}. {item.get('title')}")
        response_lines.append(f"- score: {item.get('score')}")
        response_lines.append(f"- source_ref: {item.get('source_ref')}")
        response_lines.append(f"- tags: {', '.join(item.get('tags') or [])}")
        if item.get("excerpt"):
            response_lines.append("")
            response_lines.append(item["excerpt"])
        else:
            response_lines.append("")
            response_lines.append("[NO_LOCAL_EXCERPT_AVAILABLE]")
        response_lines.append("")

    response_lines.append("## Boundary")
    response_lines.append("")
    response_lines.append("Memory is guide/context/navigation only. Brody consumes context. KX108 remains sole decision authority.")

    return {
        "status": "BRODY_CONTEXT_PACKET_CONSUMER_READONLY_PASS",
        "created_at": now_iso(),
        "query": query,
        "packet_status": packet.get("status"),
        "results_count": len(selected),
        "items_with_material": material_count,
        "sources_cited": sources_cited,
        "response_md": "\n".join(response_lines),
        "selected_items": selected,
        "readonly": True,
        "memory_role": "GUIDE_CONTEXT_NAVIGATION_ONLY",
        "memory_decision": False,
        "allowed_to_decide": False,
        "emits_act": False,
        "decision_authority": "KX108_ONLY",
        "kernel_mutation": False,
        "x108_runtime_binding": False,
        "x108_merge": False,
        "neo4j_role": "LIVE_GRAPH_MEMORY_SURFACE_ONLY",
        "brody_role": "CONTEXT_CONSUMER",
        "scope": "BRODY_CONTEXT_PACKET_CONSUMER_READONLY_ONLY",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet-json", required=True)
    parser.add_argument("--out-json")
    parser.add_argument("--out-md")
    parser.add_argument("--max-items", type=int, default=6)
    args = parser.parse_args()

    packet = load_packet(args.packet_json)
    response = build_response(packet, max_items=args.max_items)

    if args.out_json:
        out = Path(args.out_json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(response, indent=2, ensure_ascii=False), encoding="utf-8")

    if args.out_md:
        out = Path(args.out_md)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(response["response_md"], encoding="utf-8")

    print(json.dumps(response, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

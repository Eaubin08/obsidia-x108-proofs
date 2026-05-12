import argparse
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

from neo4j import GraphDatabase


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def neo4j_env():
    uri = os.environ.get("NEO4J_URI") or "bolt://localhost:7688"
    user = os.environ.get("NEO4J_USER") or os.environ.get("NEO4J_USERNAME") or "neo4j"
    password = os.environ.get("NEO4J_PASSWORD")
    database = os.environ.get("NEO4J_DATABASE") or "neo4j"

    if not password:
        raise RuntimeError("NEO4J_PASSWORD_NOT_SET")

    return uri, user, password, database


def norm_query(q: str):
    q_norm = re.sub(r"\s+", " ", (q or "").strip().lower())
    q_underscore = q_norm.replace(" ", "_")
    return q_norm, q_underscore


def safe_excerpt(text, max_chars=900):
    if not text:
        return ""
    clean = re.sub(r"\s+", " ", str(text)).strip()
    return clean[:max_chars]


def query_neo4j(query: str, limit: int):
    uri, user, password, database = neo4j_env()
    q_norm, q_underscore = norm_query(query)

    cypher = """
    MATCH (d:BrodyMemoryDoc)
    WITH d, properties(d) AS p, $q_norm AS q_norm, $q_underscore AS q_underscore
    WITH d, q_norm, q_underscore,
      coalesce(p.title, "") AS title,
      coalesce(p.path, "") AS path,
      coalesce(p.source, "unknown") AS source,
      coalesce(p.tags, []) AS tags,
      coalesce(p.text, p.content, p.body, p.excerpt, p.summary, p.preview, "") AS body
    WITH d, title, path, source, tags, body,
      (
        CASE WHEN toLower(title) CONTAINS q_norm THEN 160 ELSE 0 END +
        CASE WHEN toLower(path) CONTAINS q_norm THEN 150 ELSE 0 END +
        CASE WHEN toLower(body) CONTAINS q_norm THEN 120 ELSE 0 END +
        CASE WHEN any(t IN tags WHERE toLower(t) = q_underscore) THEN 130 ELSE 0 END +
        CASE WHEN any(t IN tags WHERE replace(toLower(t), "_", " ") = q_norm) THEN 130 ELSE 0 END +
        CASE WHEN any(t IN tags WHERE replace(toLower(t), "_", " ") CONTAINS q_norm) THEN 100 ELSE 0 END +
        CASE WHEN any(t IN tags WHERE toLower(t) CONTAINS q_underscore) THEN 100 ELSE 0 END
      ) AS score
    WHERE score > 0
    RETURN
      d.id AS id,
      title AS title,
      source AS source,
      path AS path,
      tags AS tags,
      score AS score,
      body AS body
    ORDER BY score DESC, title ASC
    LIMIT $limit
    """

    driver = GraphDatabase.driver(uri, auth=(user, password), connection_timeout=15)
    try:
        with driver.session(database=database) as session:
            rows = [dict(r) for r in session.run(cypher, q_norm=q_norm, q_underscore=q_underscore, limit=limit)]
    finally:
        driver.close()

    items = []
    for i, r in enumerate(rows, start=1):
        items.append({
            "rank": i,
            "id": r.get("id"),
            "title": r.get("title"),
            "source": r.get("source") or "unknown",
            "path": r.get("path") or "",
            "tags": r.get("tags") or [],
            "score": r.get("score"),
            "excerpt": safe_excerpt(r.get("body")),
            "source_ref": r.get("path") or r.get("title") or r.get("id"),
        })

    return {
        "status": "BRODY_CONTEXT_PACKET_QUERY_READONLY_PASS",
        "created_at": now_iso(),
        "query": query,
        "query_norm": q_norm,
        "query_underscore": q_underscore,
        "results_count": len(items),
        "context_packet": {
            "role": "GUIDE_CONTEXT_NAVIGATION_ONLY",
            "consumer": "BRODY",
            "source": "NEO4J_GRAPHITI_V2_READONLY",
            "items": items,
            "instructions": [
                "Use this packet only as context.",
                "Do not decide.",
                "Do not emit ACT.",
                "Do not mutate kernel.",
                "Do not claim authority.",
                "Cite packet items by title/path when useful."
            ]
        },
        "readonly": True,
        "memory_authority": False,
        "memory_decision": False,
        "allowed_to_decide": False,
        "emits_act": False,
        "kernel_binding": False,
        "x108_runtime_binding": False,
        "x108_merge": False,
        "kernel_mutation": False,
        "x108_mutation": False,
        "decision_authority": "KX108_ONLY",
        "scope": "BRODY_CONTEXT_PACKET_QUERY_READONLY_ONLY"
    }


def packet_to_markdown(packet):
    lines = []
    lines.append("# BRODY CONTEXT PACKET — READONLY")
    lines.append("")
    lines.append(f"- status: {packet['status']}")
    lines.append(f"- query: {packet['query']}")
    lines.append(f"- results_count: {packet['results_count']}")
    lines.append(f"- memory_decision: {str(packet['memory_decision']).lower()}")
    lines.append(f"- decision_authority: {packet['decision_authority']}")
    lines.append(f"- x108_runtime_binding: {str(packet['x108_runtime_binding']).lower()}")
    lines.append(f"- x108_merge: {str(packet['x108_merge']).lower()}")
    lines.append("")
    lines.append("## Items")

    for item in packet["context_packet"]["items"]:
        lines.append("")
        lines.append(f"### {item['rank']}. {item.get('title')}")
        lines.append(f"- id: {item.get('id')}")
        lines.append(f"- score: {item.get('score')}")
        lines.append(f"- path: {item.get('path')}")
        lines.append(f"- tags: {', '.join(item.get('tags') or [])}")
        if item.get("excerpt"):
            lines.append("")
            lines.append(item["excerpt"])

    lines.append("")
    lines.append("## Boundary")
    lines.append("Memory is guide/context/navigation only. It never decides. KX108 remains sole decision authority.")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", required=True)
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--out-json")
    parser.add_argument("--out-md")
    args = parser.parse_args()

    packet = query_neo4j(args.query, args.limit)

    if args.out_json:
        Path(args.out_json).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out_json).write_text(json.dumps(packet, indent=2, ensure_ascii=False), encoding="utf-8")

    if args.out_md:
        Path(args.out_md).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out_md).write_text(packet_to_markdown(packet), encoding="utf-8")

    print(json.dumps(packet, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

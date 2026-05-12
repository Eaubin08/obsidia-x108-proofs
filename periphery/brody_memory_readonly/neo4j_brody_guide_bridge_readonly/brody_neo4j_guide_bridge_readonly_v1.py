import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from datetime import datetime

BOUNDARY = {
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
    "scope": "BRODY_NEO4J_GUIDE_BRIDGE_READONLY_ONLY",
}

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()

def load_jsonl(path: Path, limit=None):
    rows = []
    with path.open("r", encoding="utf-8-sig", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
            if limit and len(rows) >= limit:
                break
    return rows

def get_text(record):
    fields = [
        "text", "content", "body", "summary", "preview", "text_preview",
        "clean_text", "source_text", "markdown"
    ]
    for k in fields:
        v = record.get(k)
        if isinstance(v, str) and v.strip():
            return v[:4000]
    return ""

def get_title(record):
    for k in ["title", "name", "file", "filename", "relative_path", "path", "id"]:
        v = record.get(k)
        if isinstance(v, str) and v.strip():
            return v[:500]
    return str(record.get("id", "untitled"))[:500]

def get_source(record):
    for k in ["source", "source_root", "source_name", "origin"]:
        v = record.get(k)
        if isinstance(v, str) and v.strip():
            return v[:300]
    return "unknown"

def get_path(record):
    for k in ["path", "full_path", "relative_path", "file_path"]:
        v = record.get(k)
        if isinstance(v, str) and v.strip():
            return v[:1000]
    return ""

def get_tags(record):
    tags = record.get("tags", [])
    if isinstance(tags, str):
        tags = [tags]
    if not isinstance(tags, list):
        tags = []
    clean = []
    for t in tags:
        if isinstance(t, str) and t.strip():
            clean.append(t.strip())
    return sorted(set(clean))

def stable_id(record, i):
    for k in ["id", "record_id", "uid"]:
        v = record.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    raw = json.dumps(record, sort_keys=True, ensure_ascii=False)
    return "BRODY_NEO4J_DOC_" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16].upper()

def validate(records_path: Path):
    rows = load_jsonl(records_path)
    tag_counts = {}
    sources = {}
    for r in rows:
        for t in get_tags(r):
            tag_counts[t] = tag_counts.get(t, 0) + 1
        s = get_source(r)
        sources[s] = sources.get(s, 0) + 1

    result = {
        "status": "BRODY_NEO4J_GUIDE_BRIDGE_VALIDATE_PASS",
        "records_path": str(records_path),
        "records_sha256": sha256_file(records_path),
        "records_count": len(rows),
        "tag_counts_top": dict(sorted(tag_counts.items(), key=lambda kv: kv[1], reverse=True)[:40]),
        "source_counts": dict(sorted(sources.items(), key=lambda kv: kv[1], reverse=True)),
        **BOUNDARY,
    }
    return result

def require_neo4j():
    try:
        from neo4j import GraphDatabase
        return GraphDatabase
    except Exception as e:
        raise RuntimeError("NEO4J_DRIVER_MISSING: run `python -m pip install neo4j`") from e

def neo4j_env():
    uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    user = os.environ.get("NEO4J_USER", "neo4j")
    password = os.environ.get("NEO4J_PASSWORD", "")
    database = os.environ.get("NEO4J_DATABASE", "neo4j")
    if not password:
        raise RuntimeError("NEO4J_PASSWORD_NOT_SET")
    return uri, user, password, database

def import_records(records_path: Path, batch_size: int):
    GraphDatabase = require_neo4j()
    uri, user, password, database = neo4j_env()

    rows = load_jsonl(records_path)
    docs = []
    for i, r in enumerate(rows):
        docs.append({
            "id": stable_id(r, i),
            "title": get_title(r),
            "source": get_source(r),
            "path": get_path(r),
            "text_preview": get_text(r),
            "tags": get_tags(r),
            "readonly": True,
            "memory_decision": False,
            "decision_authority": "KX108_ONLY",
        })

    driver = GraphDatabase.driver(uri, auth=(user, password))
    total = 0

    cypher = """
    UNWIND $docs AS doc
    MERGE (d:BrodyMemoryDoc {id: doc.id})
    SET d.title = doc.title,
        d.source = doc.source,
        d.path = doc.path,
        d.text_preview = doc.text_preview,
        d.tags = doc.tags,
        d.readonly = true,
        d.memory_decision = false,
        d.decision_authority = "KX108_ONLY",
        d.updated_at = datetime()
    FOREACH (tag IN doc.tags |
      MERGE (t:BrodyMemoryTag {name: tag})
      MERGE (d)-[:HAS_TAG]->(t)
    )
    """

    with driver.session(database=database) as session:
        session.run("CREATE CONSTRAINT brody_memory_doc_id IF NOT EXISTS FOR (d:BrodyMemoryDoc) REQUIRE d.id IS UNIQUE")
        session.run("CREATE CONSTRAINT brody_memory_tag_name IF NOT EXISTS FOR (t:BrodyMemoryTag) REQUIRE t.name IS UNIQUE")

        for start in range(0, len(docs), batch_size):
            batch = docs[start:start+batch_size]
            session.run(cypher, docs=batch)
            total += len(batch)

        counts = session.run("""
        MATCH (d:BrodyMemoryDoc)
        RETURN count(d) AS docs
        """).single()["docs"]

    driver.close()

    return {
        "status": "BRODY_NEO4J_GUIDE_BRIDGE_IMPORT_PASS",
        "imported_count": total,
        "neo4j_docs_count": counts,
        "uri": uri,
        "database": database,
        **BOUNDARY,
    }


def query_neo4j(query: str, limit: int):
    from neo4j import GraphDatabase
    uri, user, password, database = neo4j_env()

    q_raw = query or ""
    q_norm = q_raw.lower().strip()
    q_norm = q_norm.replace("_", " ").replace("-", " ")
    q_norm = " ".join(q_norm.split())
    q_underscore = q_norm.replace(" ", "_")

    driver = GraphDatabase.driver(uri, auth=(user, password), connection_timeout=15)

    cypher = """
    MATCH (d:BrodyMemoryDoc)
    WITH d,
      CASE WHEN toLower(coalesce(d.title, "")) CONTAINS toLower($q_raw) THEN 30 ELSE 0 END +
      CASE WHEN toLower(coalesce(d.title, "")) CONTAINS toLower($q_underscore) THEN 30 ELSE 0 END +
      CASE WHEN toLower(coalesce(d.content, "")) CONTAINS toLower($q_raw) THEN 10 ELSE 0 END +
      CASE WHEN toLower(coalesce(d.content, "")) CONTAINS toLower($q_underscore) THEN 10 ELSE 0 END +
      CASE WHEN ANY(t IN coalesce(d.tags, []) WHERE
          toLower(t) = toLower($q_raw)
          OR toLower(t) = toLower($q_underscore)
          OR replace(toLower(t), "_", " ") = toLower($q_norm)
          OR replace(toLower(t), "_", " ") CONTAINS toLower($q_norm)
          OR toLower(t) CONTAINS toLower($q_underscore)
      ) THEN 100 ELSE 0 END
      AS score
    WHERE score > 0
    RETURN
      d.id AS id,
      d.title AS title,
      coalesce(d.source, "unknown") AS source,
      coalesce(d.path, "") AS path,
      coalesce(d.tags, []) AS tags,
      score AS score
    ORDER BY score DESC, title ASC
    LIMIT $limit
    """

    try:
        with driver.session(database=database) as session:
            rows = [dict(r) for r in session.run(
                cypher,
                q_raw=q_raw,
                q_norm=q_norm,
                q_underscore=q_underscore,
                limit=limit,
            )]
    finally:
        driver.close()

    return {
        "status": "BRODY_NEO4J_GUIDE_BRIDGE_QUERY_PASS",
        "query": query,
        "query_norm": q_norm,
        "query_underscore": q_underscore,
        "results_count": len(rows),
        "results": rows,
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
        "scope": "BRODY_NEO4J_GUIDE_BRIDGE_READONLY_ONLY",
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--records", required=True)
    ap.add_argument("--mode", choices=["validate", "import", "query"], required=True)
    ap.add_argument("--query", default="")
    ap.add_argument("--limit", type=int, default=10)
    ap.add_argument("--batch-size", type=int, default=250)
    args = ap.parse_args()

    records_path = Path(args.records)
    if not records_path.exists():
        raise FileNotFoundError(records_path)

    if args.mode == "validate":
        result = validate(records_path)
    elif args.mode == "import":
        result = import_records(records_path, args.batch_size)
    else:
        if not args.query.strip():
            raise RuntimeError("QUERY_REQUIRED")
        result = query_neo4j(args.query, args.limit)

    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()


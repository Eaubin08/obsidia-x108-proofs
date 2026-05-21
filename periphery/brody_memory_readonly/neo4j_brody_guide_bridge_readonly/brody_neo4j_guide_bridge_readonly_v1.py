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
            return v  # INJECTION KX108 : AUCUNE TRONCATURE
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

def require_neo4j():
    try:
        from neo4j import GraphDatabase
        return GraphDatabase
    except Exception as e:
        raise RuntimeError("NEO4J_DRIVER_MISSING: run `python -m pip install neo4j`") from e

def neo4j_env():
    uri = os.environ.get("NEO4J_URI", "bolt://localhost:7688")
    user = os.environ.get("NEO4J_USER", "neo4j")
    password = os.environ.get("NEO4J_PASSWORD", "admin1234") # Fallback de secours courant
    database = os.environ.get("NEO4J_DATABASE", "neo4j")
    return uri, user, password, database

def import_records(records_path: Path, batch_size: int):
    GraphDatabase = require_neo4j()
    uri, user, password, database = neo4j_env()

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

    driver = GraphDatabase.driver(uri, auth=(user, password))
    total = 0

    with records_path.open("r", encoding="utf-8-sig", errors="replace") as f:
        batch = []
        with driver.session(database=database) as session:
            session.run("CREATE CONSTRAINT brody_memory_doc_id IF NOT EXISTS FOR (d:BrodyMemoryDoc) REQUIRE d.id IS UNIQUE")
            session.run("CREATE CONSTRAINT brody_memory_tag_name IF NOT EXISTS FOR (t:BrodyMemoryTag) REQUIRE t.name IS UNIQUE")
            
            for i, line in enumerate(f):
                line = line.strip()
                if not line: continue
                r = json.loads(line)
                batch.append({
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
                
                if len(batch) >= batch_size:
                    session.run(cypher, docs=batch)
                    total += len(batch)
                    batch = []
            
            if batch:
                session.run(cypher, docs=batch)
                total += len(batch)
                
            counts = session.run("MATCH (d:BrodyMemoryDoc) RETURN count(d) AS docs").single()["docs"]

    driver.close()
    return {
        "status": "BRODY_NEO4J_GUIDE_BRIDGE_IMPORT_PASS",
        "imported_count": total,
        "neo4j_docs_count": counts,
        "uri": uri,
        "database": database,
        **BOUNDARY,
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--records", required=True)
    ap.add_argument("--mode", choices=["import"], required=True)
    ap.add_argument("--batch-size", type=int, default=100)
    args = ap.parse_args()

    records_path = Path(args.records)
    if not records_path.exists():
        raise FileNotFoundError(records_path)

    if args.mode == "import":
        res = import_records(records_path, args.batch_size)
        print(json.dumps(res, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()



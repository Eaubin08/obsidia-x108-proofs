import json
from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://localhost:7688", auth=("neo4j", "obsidia-graphiti-dev"))
results = []
with driver.session() as s:
    rows = s.run("MATCH (n:BrodyMemoryDoc) WHERE toLower(n.query) CONTAINS 'kernel' RETURN n LIMIT 3").data()
    for row in rows:
        node = dict(row["n"])
        results.append({
            "all_keys": list(node.keys()),
            "title": node.get("title", ""),
            "excerpt_present": node.get("excerpt") not in (None, ""),
            "excerpt_preview": (node.get("excerpt") or "")[:120],
            "body_present": node.get("body") not in (None, ""),
            "text_present": node.get("text") not in (None, ""),
            "content_present": node.get("content") not in (None, ""),
            "path": (node.get("path") or "")[:100],
            "score": node.get("score"),
        })

    c_total = s.run("MATCH (n:BrodyMemoryDoc) RETURN count(n) as c").single()["c"]
    c_excerpt = s.run("MATCH (n:BrodyMemoryDoc) WHERE n.excerpt IS NOT NULL AND n.excerpt <> '' RETURN count(n) as c").single()["c"]
    c_body = s.run("MATCH (n:BrodyMemoryDoc) WHERE n.body IS NOT NULL AND n.body <> '' RETURN count(n) as c").single()["c"]
    c_path = s.run("MATCH (n:BrodyMemoryDoc) WHERE n.path IS NOT NULL AND n.path <> '' RETURN count(n) as c").single()["c"]

    # Get one full node to see all possible keys
    all_keys_sample = s.run("MATCH (n:BrodyMemoryDoc) RETURN keys(n) as k LIMIT 1").single()
    all_keys = all_keys_sample["k"] if all_keys_sample else []

driver.close()

print(json.dumps({
    "brody_memory_doc_node_keys_sample": all_keys,
    "sample_nodes": results,
    "counts": {
        "total": c_total,
        "with_excerpt_non_empty": c_excerpt,
        "with_body_non_empty": c_body,
        "with_path_non_empty": c_path,
    }
}, indent=2, ensure_ascii=False))

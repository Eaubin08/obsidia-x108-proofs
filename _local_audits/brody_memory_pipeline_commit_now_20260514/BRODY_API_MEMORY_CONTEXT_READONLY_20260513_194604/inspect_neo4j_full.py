import json
from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://localhost:7688", auth=("neo4j", "obsidia-graphiti-dev"))
results = []
with driver.session() as s:
    # Sample 3 nodes — get all fields including text_preview
    rows = s.run("MATCH (n:BrodyMemoryDoc) RETURN n LIMIT 3").data()
    for row in rows:
        node = dict(row["n"])
        results.append({
            "all_keys": sorted(node.keys()),
            "title": (node.get("title") or "")[:80],
            "path": (node.get("path") or "")[:100],
            "text_preview": (node.get("text_preview") or "")[:200],
            "tags": node.get("tags") or [],
            "source": node.get("source"),
            "memory_decision": node.get("memory_decision"),
            "decision_authority": node.get("decision_authority"),
        })

    # Count nodes with text_preview non-empty
    c_text_preview = s.run(
        "MATCH (n:BrodyMemoryDoc) WHERE n.text_preview IS NOT NULL AND n.text_preview <> '' RETURN count(n) as c"
    ).single()["c"]

    # Sample 3 Kernel-tagged nodes to check path existence
    kernel_rows = s.run(
        "MATCH (n:BrodyMemoryDoc) WHERE 'kernel' IN [t IN n.tags | toLower(t)] RETURN n LIMIT 5"
    ).data()
    kernel_sample = []
    import os
    for row in kernel_rows:
        node = dict(row["n"])
        p = node.get("path") or ""
        kernel_sample.append({
            "title": (node.get("title") or "")[:80],
            "path": p[:120],
            "path_exists": os.path.isfile(p) if p else False,
            "text_preview": (node.get("text_preview") or "")[:150],
        })

driver.close()

print(json.dumps({
    "all_field_keys_sample": results[0]["all_keys"] if results else [],
    "sample_nodes": results,
    "counts": {
        "with_text_preview_non_empty": c_text_preview,
    },
    "kernel_tagged_sample": kernel_sample,
}, indent=2, ensure_ascii=False))

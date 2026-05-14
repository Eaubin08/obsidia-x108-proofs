import sys
import json
import importlib.util
import os

spec = importlib.util.spec_from_file_location(
    "brody_ctx",
    r"C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs\periphery\brody_memory_readonly\context_packet_query_readonly\brody_context_packet_query_readonly_v1.py"
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

queries = ["Brody", "Kernel", "X108", "memory", "Graphiti"]
results = []
for q in queries:
    try:
        packet = mod.query_neo4j(q, limit=8)
        items = packet["context_packet"]["items"]
        items_with_body = [i for i in items if i.get("excerpt")]
        avg_body = int(sum(len(i.get("excerpt", "")) for i in items) / max(len(items), 1))
        sample = items[0] if items else None
        results.append({
            "query": q,
            "result_count": packet["results_count"],
            "items_with_body_non_empty": len(items_with_body),
            "items_with_text_preview_material": len(items_with_body),
            "avg_body_length": avg_body,
            "sample_title": sample["title"] if sample else None,
            "sample_body_preview": sample["excerpt"][:200] if sample and sample.get("excerpt") else "",
            "decision_authority": packet["decision_authority"],
            "readonly": packet["readonly"],
            "memory_decision": packet["memory_decision"],
            "status": packet["status"]
        })
    except Exception as e:
        results.append({"query": q, "error": str(e)})

print(json.dumps(results, indent=2, ensure_ascii=False))

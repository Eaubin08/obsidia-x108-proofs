import json
import urllib.request

data = json.dumps({
    "message": "write Graphiti memory + canon -> DOMAIN_RACCORD_WRITE_BOUNDARY",
    "language": "fr",
    "session_id": "f17b_runtime_payload_assert",
}).encode("utf-8")

req = urllib.request.Request(
    "http://127.0.0.1:8000/api/brody/chat",
    data=data,
    headers={"Content-Type": "application/json"},
)

with urllib.request.urlopen(req, timeout=60) as r:
    p = json.loads(r.read().decode("utf-8"))

with open("docs/runtime/F17B_8000_BRODY_GRAPHITI_RECONNECT_PAYLOAD.json", "w", encoding="utf-8") as f:
    json.dump(p, f, ensure_ascii=False, indent=2)

print("graphiti_status=", p.get("graphiti_status"))
print("graphiti_blocker=", p.get("graphiti_blocker"))
print("neo4j_status=", p.get("neo4j_status"))

m = p.get("memory_response_chain_snapshot") or {}
print("source_mode=", m.get("source_mode"))
print("chain_graphiti_status=", m.get("graphiti_status"))
print("live_neo4j_dependency=", m.get("live_neo4j_dependency"))
print("material_quality=", m.get("material_quality"))

assert p.get("graphiti_status") in ("GRAPHITI_V20_FROZEN_READONLY_PASS", "GRAPHITI_NEO4J_LIVE_READONLY_PASS")
assert m.get("source_mode") in ("GRAPHITI_V20_FROZEN_HTTP_PRIMARY", "MEMORY_RESPONSE_CHAIN")

if m.get("source_mode") == "GRAPHITI_V20_FROZEN_HTTP_PRIMARY":
    assert m.get("graphiti_status") == "GRAPHITI_V20_FROZEN_READONLY_PASS"
    assert m.get("live_neo4j_dependency") is False

assert p.get("readonly") is True
assert p.get("emits_act") is False
assert p.get("emits_verdict") is False
assert p.get("memory_write") is False
assert p.get("graphiti_write") is False
assert p.get("kernel_mutation") is False
assert p.get("x108_mutation") is False
assert p.get("decision_authority") == "KX108_ONLY"

print("F17B_RUNTIME_PAYLOAD_ASSERT_PASS")

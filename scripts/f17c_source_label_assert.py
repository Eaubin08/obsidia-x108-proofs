import json
import urllib.request

for port in (8000, 8012):
    data = json.dumps({
        "message": "write Graphiti memory + canon -> DOMAIN_RACCORD_WRITE_BOUNDARY",
        "language": "fr",
        "session_id": f"f17c_source_label_payload_assert_{port}",
    }).encode("utf-8")

    req = urllib.request.Request(
        f"http://127.0.0.1:{port}/api/brody/chat",
        data=data,
        headers={"Content-Type": "application/json"},
    )

    with urllib.request.urlopen(req, timeout=60) as r:
        p = json.loads(r.read().decode("utf-8"))

    with open(f"docs/runtime/F17C_{port}_BRODY_SOURCE_LABEL_PAYLOAD.json", "w", encoding="utf-8") as f:
        json.dump(p, f, ensure_ascii=False, indent=2)

    print("PORT=", port)
    print("source=", p.get("source"))
    print("graphiti_status=", p.get("graphiti_status"))
    m = p.get("memory_response_chain_snapshot") or {}
    print("source_mode=", m.get("source_mode"))

    assert p.get("graphiti_status") == "GRAPHITI_V20_FROZEN_READONLY_PASS"
    assert p.get("source") == "REAL_BRODY_GRAPHITI_V20_FROZEN_READONLY"
    assert m.get("source_mode") == "GRAPHITI_V20_FROZEN_HTTP_PRIMARY"
    assert p.get("decision_authority") == "KX108_ONLY"
    assert p.get("readonly") is True
    assert p.get("emits_act") is False
    assert p.get("memory_write") is False
    assert p.get("graphiti_write") is False
    assert p.get("kernel_mutation") is False
    assert p.get("x108_mutation") is False

print("F17C_SOURCE_LABEL_ASSERT_PASS")

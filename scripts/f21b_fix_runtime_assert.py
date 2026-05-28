import json
import urllib.request

def get_json(url):
    with urllib.request.urlopen(url, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))

def post_json(url, payload):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))

for port in (8000, 8012):
    p = post_json(f"http://127.0.0.1:{port}/api/brody/chat", {
        "message": "F21 fix assert: adaptive_response_policy top-level + freeze dashboard strict phase tags.",
        "language": "fr",
        "session_id": f"f21b_fix_assert_{port}",
    })

    assert p.get("decision_authority") == "KX108_ONLY"
    assert p.get("readonly") is True
    assert p.get("emits_act") is False
    assert p.get("memory_write") is False
    assert p.get("graphiti_write") is False
    assert p.get("kernel_mutation") is False
    assert p.get("x108_mutation") is False

    assert isinstance(p.get("adaptive_response_policy"), dict)
    assert p["adaptive_response_policy"].get("status") == "ADAPTIVE_RESPONSE_POLICY_READY"

    dash = get_json(f"http://127.0.0.1:{port}/api/runtime/freeze-dashboard")
    summary = get_json(f"http://127.0.0.1:{port}/api/runtime/freeze-dashboard/summary")

    d = dash.get("runtime_freeze_dashboard") or {}
    phases = {row["phase"]: row for row in d.get("phases", [])}

    assert d.get("status") == "F2_F20_RUNTIME_FREEZE_DASHBOARD_READY"
    assert d.get("decision_authority") == "KX108_ONLY"
    assert d.get("readonly") is True
    assert d.get("emits_act") is False
    assert d.get("memory_write") is False
    assert d.get("graphiti_write") is False
    assert d.get("kernel_mutation") is False
    assert d.get("x108_mutation") is False

    f2_tags = phases.get("F2", {}).get("tags", [])
    f20_tags = phases.get("F20", {}).get("tags", [])

    assert "BRODY_F20_GENCOIN_COGNITIVE_LEDGER_VISIBLE_20260528" not in f2_tags
    assert "BRODY_F20_GENCOIN_COGNITIVE_LEDGER_VISIBLE_20260528" in f20_tags

    assert summary.get("status") == "F2_F20_RUNTIME_FREEZE_DASHBOARD_READY"

    with open(f"docs/runtime/F21B_FIX_RUNTIME_ASSERT_{port}.json", "w", encoding="utf-8") as f:
        json.dump({"brody": p, "dashboard": dash, "summary": summary}, f, ensure_ascii=False, indent=2)

    print("PORT=", port)
    print("adaptive_response_policy=", p["adaptive_response_policy"].get("status"))
    print("dashboard_status=", d.get("status"))
    print("F2_TAGS=", f2_tags)
    print("F20_TAGS=", f20_tags)

print("F21B_FIX_RUNTIME_ASSERT_PASS")

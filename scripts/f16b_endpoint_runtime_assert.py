import json
import urllib.request

endpoints = {
    "os3": "http://127.0.0.1:8000/api/os3/tickets",
    "worldcalls": "http://127.0.0.1:8000/api/worldcalls",
    "sovereign": "http://127.0.0.1:8000/api/worldcalls/sovereign-tickets",
    "audit": "http://127.0.0.1:8000/api/audit/events",
    "gencoin": "http://127.0.0.1:8000/api/gencoin",
}

payloads = {}
for name, url in endpoints.items():
    with urllib.request.urlopen(url, timeout=10) as r:
        p = json.loads(r.read().decode("utf-8"))
    payloads[name] = p
    print(name, "source=", p.get("source"), "readonly=", p.get("readonly"), "authority=", p.get("decision_authority"))

assert payloads["os3"].get("source") != "BACKEND_STUB"
assert payloads["worldcalls"].get("source") != "BACKEND_STUB"
assert payloads["sovereign"].get("source") != "BACKEND_STUB"
assert payloads["audit"].get("source") != "BACKEND_STUB"

# Gencoin ledger peut être vide, mais doit être honnête LIVE_EMPTY_REGISTRY, pas BACKEND_STUB.
assert payloads["gencoin"].get("source") != "BACKEND_STUB"
assert payloads["gencoin"].get("status") in ("LIVE_EMPTY_REGISTRY", "LIVE_LEDGER")

for name, p in payloads.items():
    assert p.get("readonly") is True
    assert p.get("decision_authority") == "KX108_ONLY"
    assert p.get("emits_act") is False
    assert p.get("emits_verdict") is False
    assert p.get("memory_write") is False
    assert p.get("kernel_mutation") is False

print("F16B_ENDPOINT_RUNTIME_ASSERT_PASS")

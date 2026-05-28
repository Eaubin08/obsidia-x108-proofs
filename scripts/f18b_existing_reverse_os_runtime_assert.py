import json
import urllib.request

message = (
    "F18 runtime assert: transforme cette intention en OS Trad, IR Candidate, "
    "Reverse OS projection, sans écrire mémoire, sans ACT, sans mutation X108."
)

for port in (8000, 8012):
    data = json.dumps({
        "message": message,
        "language": "fr",
        "session_id": f"f18b_existing_reverse_os_runtime_assert_{port}",
    }).encode("utf-8")

    req = urllib.request.Request(
        f"http://127.0.0.1:{port}/api/brody/chat",
        data=data,
        headers={"Content-Type": "application/json"},
    )

    with urllib.request.urlopen(req, timeout=60) as r:
        p = json.loads(r.read().decode("utf-8"))

    with open(f"docs/runtime/F18B_{port}_EXISTING_REVERSE_OS_RUNTIME_PAYLOAD.json", "w", encoding="utf-8") as f:
        json.dump(p, f, ensure_ascii=False, indent=2)

    tr = p.get("translation_trace") or {}
    ir = p.get("ir_candidate") or {}
    rev = tr.get("os_reverse_projection") or {}

    print("PORT=", port)
    print("source=", p.get("source"))
    print("graphiti_status=", p.get("graphiti_status"))
    print("translation_source=", tr.get("source"))
    print("os_trad_status=", tr.get("os_trad_status"))
    print("alphabet_units_count=", tr.get("alphabet_units_count"))
    print("reverse_non_decision=", rev.get("non_decision"))
    print("reverse_verdict_existant=", rev.get("verdict_existant"))
    print("ir_status=", ir.get("status"))
    print("ir_source=", ir.get("source"))
    print("ir_entities=", len(ir.get("entities", [])))
    print("ir_constraints=", len(ir.get("constraints", [])))

    assert p.get("decision_authority") == "KX108_ONLY"
    assert p.get("readonly") is True
    assert p.get("emits_act") is False
    assert p.get("memory_write") is False
    assert p.get("graphiti_write") is False
    assert p.get("kernel_mutation") is False
    assert p.get("x108_mutation") is False

    assert tr.get("source") == "BRODY_EXISTING_REVERSE_OS_BRIDGE_V1"
    assert tr.get("os_trad_status") == "READONLY_PASS"
    assert tr.get("alphabet_units_count", 0) > 0
    assert len(tr.get("alphabet_units", [])) > 0

    assert rev.get("non_decision") is True
    assert rev.get("verdict_existant") in ("NO_DECISION_X108_REQUIRED", "NO_DECISION_CONTEXT_ONLY")

    assert ir.get("source") == "BRODY_EXISTING_REVERSE_OS_IR_BRIDGE_V1"
    assert ir.get("status") == "IR_CANDIDATE_EXISTING_REVERSE_OS_BRIDGE_PASS"
    assert len(ir.get("entities", [])) > 0
    assert len(ir.get("constraints", [])) > 0
    assert ir.get("allowed_to_act") is False
    assert ir.get("allowed_to_decide") is False
    assert ir.get("decision_authority") == "KX108_ONLY"

print("F18B_RUNTIME_ASSERT_PASS")

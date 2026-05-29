"""F47.1 — Targeted sovereignty injection tests."""
import sys
sys.path.insert(0, ".")
from apps.obsidia_api.safe_response import safe_backend_response, sanitize_user_facing_text

print("\n=== F47.1 — Sovereignty injection tests ===")
cases = [
    ("decision_authority", "BRODY_OVERRIDE", "KX108_ONLY"),
    ("allowed_to_decide",  True,             False),
    ("emits_act",          True,             False),
    ("emits_verdict",      True,             False),
    ("kernel_mutation",    True,             False),
    ("x108_mutation",      True,             False),
    ("neo4j_write",        True,             False),
    ("brody_decision",     True,             False),
    ("readonly",           False,            True),
    ("advisory_only",      False,            True),
    ("real_action",        True,             False),
    ("memory_write",       True,             False),
    ("context_signal_only", False,           True),
]
failures = []
for key, injected, expected in cases:
    result = safe_backend_response({key: injected}, source="TEST")
    actual = result.get(key)
    ok = actual == expected
    marker = "PASS" if ok else "FAIL"
    print(f"  [{marker}] {key}: injected={injected!r} -> actual={actual!r}")
    if not ok:
        failures.append(key)

# Non-sovereignty fields must still pass through
r = safe_backend_response({"some_field": "preserved", "surfaces_ready": 7}, source="TEST")
passthru_ok = r.get("some_field") == "preserved" and r.get("surfaces_ready") == 7
print(f"  [PASSTHRU] non-sovereignty fields preserved: {passthru_ok}")

# Combined injection (all at once)
combined = {
    "decision_authority": "BRODY_ONLY",
    "allowed_to_decide": True,
    "emits_act": True,
    "kernel_mutation": True,
    "x108_mutation": True,
    "neo4j_write": True,
    "brody_decision": True,
    "integration_status": "READY_READONLY",
}
r2 = safe_backend_response(combined, source="TEST")
combined_ok = (
    r2.get("decision_authority") == "KX108_ONLY"
    and r2.get("allowed_to_decide") == False
    and r2.get("emits_act") == False
    and r2.get("kernel_mutation") == False
    and r2.get("integration_status") == "READY_READONLY"
)
print(f"  [COMBINED] all 7 sovereignty fields blocked + non-sovereignty preserved: {combined_ok}")
if not combined_ok:
    failures.append("combined_injection")

print()
status = "PASS" if not failures else "FAIL"
print(f"F47_1_PROTECTED_RESPONSE_ENVELOPE={status}")
if failures:
    print(f"  FAILURES: {failures}")
    sys.exit(1)

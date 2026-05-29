"""F47.3 — Nested forbidden-token scan scope tests."""
import sys, re
sys.path.insert(0, ".")
from apps.obsidia_api.safe_response import sanitize_user_facing_text, safe_backend_response
from periphery.brody_runtime.f37_multi_domain_user_scenarios_readonly import (
    build_multi_domain_user_scenarios,
)
from periphery.brody_runtime.f36_user_scenario_controlled_response import (
    build_user_scenario_controlled_response,
)

FORBIDDEN = ("ALLOW", "HOLD", "BLOCK", "ACT", "DECIDE", "VERDICT")

def has_forbidden_wb(text):
    t = text.upper()
    return [tok for tok in FORBIDDEN if re.search(r"\b" + tok + r"\b", t)]

print("\n=== F47.3a — F37 multi-domain scenarios with forbidden user_input ===")
# The user_input in f37 scenarios is static/trusted. But if we call f36 with injected input,
# test that f37 packet correctly reports forbidden_tokens_found=False
f37_failures = []
# Standard call — all scenarios use trusted static user_input (no injection)
packet = build_multi_domain_user_scenarios(theta=0.15)
for s in packet.get("scenarios", []):
    cr = s.get("controlled_response", {})
    text = cr.get("text", "")
    found = has_forbidden_wb(text)
    ok = len(found) == 0
    marker = "PASS" if ok else "FAIL"
    domain = s.get("domain", "?")
    print(f"  [{marker}] domain={domain} | forbidden_in_cr_text={found}")
    if not ok:
        f37_failures.append(domain)

# Check packet-level flag
pkt_flag = packet.get("forbidden_tokens_found")
print(f"  [INFO] packet.forbidden_tokens_found={pkt_flag} (expected False)")
if pkt_flag:
    f37_failures.append("packet_level_flag")

print(f"  f37 standard: {'PASS' if not f37_failures else 'FAIL'}")

print("\n=== F47.3b — safe_backend_response sanitizes controlled_response.text ===")
# Verify safe_backend_response() sanitizes nested controlled_response.text
nested_test = {
    "controlled_response": {
        "text": "Demande recue: ALLOW this. User said VERDICT.",
        "can_decide": False,
    },
    "decision_authority": "KX108_ONLY",
}
wrapped = safe_backend_response(nested_test, source="TEST")
cr_text = wrapped.get("controlled_response", {}).get("text", "")
found = has_forbidden_wb(cr_text)
nested_ok = len(found) == 0
print(f"  [{'PASS' if nested_ok else 'FAIL'}] nested cr.text sanitized: {cr_text!r} | found={found}")

print("\n=== F47.3c — Internal fields NOT sanitized (proof_status, scenario_id, etc.) ===")
# Proof fields and internal markers must NOT be touched by sanitizer
internal_fields = {
    "proof_status": "RUNTIME_SMOKE_ONLY_NOT_LEAN_PROVEN",
    "scenario_id": "F36_USER_SCENARIO_BRODY_WORKBENCH_CONTROLLED_RESPONSE",
    "packet_id": "F37_MULTI_DOMAIN_USER_SCENARIOS_READONLY",
    "audit_id": "F45_CANONICAL_OBSERVATION_TERMINAL_TEST_BATTERY",
}
internal_test = dict(internal_fields)
internal_test["controlled_response"] = {"text": "clean text", "can_decide": False}
wrapped_int = safe_backend_response(internal_test, source="TEST")
internal_failures = []
for k, expected_v in internal_fields.items():
    actual_v = wrapped_int.get(k)
    ok = actual_v == expected_v
    marker = "PASS" if ok else "FAIL"
    print(f"  [{marker}] {k}={actual_v!r} preserved")
    if not ok:
        internal_failures.append(k)

print(f"  internal fields: {'PASS' if not internal_failures else 'FAIL'}")

print("\n=== F47.3d — F36 module-level scan active (without route layer) ===")
# Test that f36 module itself sanitizes even without safe_backend_response
module_failures = []
for token in ("ALLOW", "DECIDE", "VERDICT"):
    result = build_user_scenario_controlled_response(
        user_input=token, domain="bank",
        session_id="f47-f3-test", signal_id="f47-f3-sig",
    )
    cr_text = result.get("controlled_response", {}).get("text", "")
    found = has_forbidden_wb(cr_text)
    ok = len(found) == 0
    marker = "PASS" if ok else "FAIL"
    print(f"  [{marker}] user_input={token!r} | module-level cr.text clean: {ok} | found={found}")
    if not ok:
        module_failures.append(token)

print(f"  f36 module-level: {'PASS' if not module_failures else 'FAIL'}")

all_ok = not f37_failures and nested_ok and not internal_failures and not module_failures
print()
print(f"F47_3_NESTED_SCAN_SCOPE={'PASS' if all_ok else 'FAIL'}")
if not all_ok:
    sys.exit(1)

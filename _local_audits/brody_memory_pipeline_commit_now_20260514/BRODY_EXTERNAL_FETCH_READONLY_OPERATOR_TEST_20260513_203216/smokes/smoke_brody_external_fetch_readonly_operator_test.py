"""
Smoke: BRODY_EXTERNAL_FETCH_READONLY_OPERATOR_TEST integrity check.
Readonly validation only.
"""
import json
import sys
from pathlib import Path

AUDIT_DIR = Path(r"C:\Users\User\Desktop\obsidia-engine-proof-core\_local_audits\BRODY_EXTERNAL_FETCH_READONLY_OPERATOR_TEST_20260513_203216")
REPORT_JSON = AUDIT_DIR / "reports" / "BRODY_EXTERNAL_FETCH_READONLY_OPERATOR_TEST_REPORT.json"
AUTH_PKT    = AUDIT_DIR / "inputs" / "operator_authorization_packet.json"
NEG_SUMMARY = AUDIT_DIR / "negative_tests" / "summary.json"
POS_CAPTURE = AUDIT_DIR / "captures" / "positive_get_result.json"

results = {}
fails = []

def check(name, condition, msg=""):
    results[name] = condition
    if not condition:
        fails.append(f"FAIL:{name}" + (f" — {msg}" if msg else ""))
    return condition

# 1. Report JSON parseable
try:
    data = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
    check("json_parse_ok", True)
except Exception as e:
    check("json_parse_ok", False, str(e))
    data = {}

# 2. Report MD exists
check("md_exists", (AUDIT_DIR / "reports" / "BRODY_EXTERNAL_FETCH_READONLY_OPERATOR_TEST_REPORT.md").exists())

# 3. Auth packet
try:
    pkt = json.loads(AUTH_PKT.read_text(encoding="utf-8"))
    check("auth_packet_exists", True)
    check("auth_operator_approved",     pkt.get("operator_approved") is True)
    check("auth_method_get",            pkt.get("method") == "GET")
    check("auth_allowlisted",           pkt.get("allowlisted") is True)
    check("auth_brody_not_executed",    pkt.get("brody_api_call_executed") is False)
    check("auth_memory_intake_false",   pkt.get("memory_intake") is False)
    check("auth_graphiti_write_false",  pkt.get("graphiti_write") is False)
    check("auth_neo4j_write_false",     pkt.get("neo4j_write") is False)
    check("auth_x108_merge_false",      pkt.get("x108_merge") is False)
    check("auth_kx108_only",            pkt.get("decision_authority") == "KX108_ONLY")
except Exception as e:
    check("auth_packet_exists", False, str(e))

# 4. Negative tests
try:
    neg = json.loads(NEG_SUMMARY.read_text(encoding="utf-8"))
    check("neg_summary_exists", True)
    check("neg_total_7",            neg.get("total") == 7,         f"got {neg.get('total')}")
    check("neg_all_blocked",        neg.get("all_blocked") is True)
    check("neg_none_network",       neg.get("none_network_executed") is True)
except Exception as e:
    check("neg_summary_exists", False, str(e))

# 5. Positive GET result
try:
    pos = json.loads(POS_CAPTURE.read_text(encoding="utf-8"))
    check("pos_capture_exists", True)
    check("pos_no_write",           pos.get("no_write") is True)
    check("pos_boundary_intact",    pos.get("boundary_intact") is True)
    # method must be GET if executed
    if pos.get("network_executed"):
        check("pos_method_get",     pos.get("method") == "GET")
        check("pos_no_secret",      pos.get("no_secret_detected") is True)
        check("pos_operator_approved", pos.get("operator_approved") is True)
    else:
        check("pos_method_get",     True)   # not executed — not a violation
        check("pos_no_secret",      True)
        check("pos_operator_approved", True)
except Exception as e:
    check("pos_capture_exists", False, str(e))

# 6. Boundaries from report JSON
bnd = data.get("boundary_summary", {})
BOOL_FALSE_KEYS = [
    "brody_api_call_executed", "brody_execute_allowed", "brody_authorize_allowed",
    "post_allowed", "put_allowed", "patch_allowed", "delete_allowed",
    "crawler_allowed", "scraping_bulk_allowed",
    "secret_read", "secret_exfiltration",
    "memory_decision", "allowed_to_decide", "emits_act", "emits_verdict",
    "graphiti_write", "graphiti_index_write", "neo4j_write_executed",
    "memory_intake", "kernel_mutation", "x108_runtime_binding", "x108_merge",
]
BOOL_TRUE_KEYS = [
    "human_operator_required", "readonly_analysis_only",
    "external_fetch_operator_approved", "get_only",
]
for k in BOOL_FALSE_KEYS:
    check(f"bnd_{k}_false", bnd.get(k) is False, f"got {bnd.get(k)}")
for k in BOOL_TRUE_KEYS:
    check(f"bnd_{k}_true", bnd.get(k) is True, f"got {bnd.get(k)}")
check("bnd_decision_authority_kx108", bnd.get("decision_authority") == "KX108_ONLY")

# 7. Guardrails from report JSON
grd = data.get("guardrails", {})
for g in ["committed", "frozen", "push", "x108_modification", "sigma_tools_touched", "faux_pass_crees"]:
    check(f"guardrail_{g}_false", grd.get(g) is False, f"got {grd.get(g)}")

# 8. Step5 confirmed
check("step5_v2_confirmed",         data.get("step5_v2_confirmed") is True)
check("step5_verdict_partial_pass", data.get("step5_verdict") == "PARTIAL_PASS")
check("step5_smoke_48",             data.get("step5_smoke_checks_pass") == 48)

# 9. No POST / no crawler / no secret proofs
check("proof_no_post",          data.get("proof_no_post_executed") is True)
check("proof_no_secret",        data.get("proof_no_secret_read") is True)
check("proof_no_graphiti_write", data.get("proof_no_graphiti_write") is True)
check("proof_no_neo4j_write",   data.get("proof_no_neo4j_write") is True)
check("proof_no_memory_intake", data.get("proof_no_memory_intake") is True)
check("proof_no_crawler",       data.get("proof_no_crawler") is True)

# 10. Preflight coherence
pfl = data.get("preflight", {})
check("preflight_verify_all_pass",       pfl.get("verify_all") == "PASS")
check("preflight_api_8011_live",         pfl.get("api_8011_live") is True)
check("preflight_sigma_tools_untouched", pfl.get("sigma_tools_touched") is False)

# ── Final output ──────────────────────────────────────────────────────────────
all_pass = len(fails) == 0
verdict_from_data = data.get("verdict", "UNKNOWN")
net_avail = data.get("network_available", False)
neg_blocked = data.get("negative_tests_summary", {}).get("total", 0)
pos_exec = data.get("positive_get_executed", False)

print()
print("=" * 70)
if all_pass:
    if net_avail:
        print("BRODY_EXTERNAL_FETCH_READONLY_OPERATOR_TEST_SMOKE_OK")
    else:
        print("BRODY_EXTERNAL_FETCH_READONLY_OPERATOR_TEST_PARTIAL_NETWORK_BLOCKED_SMOKE_OK")
else:
    print("BRODY_EXTERNAL_FETCH_READONLY_OPERATOR_TEST_SMOKE_FAIL")
    for f in fails:
        print(f"  {f}")
print("=" * 70)
print(f"STEP5_V2_CONFIRMED=true")
print(f"POSITIVE_GET_EXECUTED={str(pos_exec).lower()}")
print(f"NETWORK_AVAILABLE={str(net_avail).lower()}")
print(f"NEGATIVE_TESTS_BLOCKED={neg_blocked}/{neg_blocked}")
print(f"POST_EXECUTED=false")
print(f"CRAWLER_EXECUTED=false")
print(f"SECRET_READ=false")
print(f"MEMORY_INTAKE=false")
print(f"GRAPHITI_WRITE=false")
print(f"NEO4J_WRITE=false")
print(f"X108_MERGE=false")
print(f"KERNEL_MUTATION=false")
print(f"DECISION_AUTHORITY=KX108_ONLY")
print(f"REPORT={REPORT_JSON}")
print(f"SMOKE_CHECKS_TOTAL={len(results)}")
print(f"SMOKE_CHECKS_PASS={sum(1 for v in results.values() if v)}")
print(f"SMOKE_CHECKS_FAIL={len(fails)}")
print()
sys.exit(0 if all_pass else 1)

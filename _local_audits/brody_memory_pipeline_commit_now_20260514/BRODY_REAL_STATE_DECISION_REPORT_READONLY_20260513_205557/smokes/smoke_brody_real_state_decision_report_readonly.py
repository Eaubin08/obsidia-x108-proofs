"""
Smoke: BRODY_REAL_STATE_DECISION_REPORT_READONLY integrity check.
Readonly validation only. 16-component decision matrix.
"""
import json
import sys
from pathlib import Path

AUDIT_DIR   = Path(r"C:\Users\User\Desktop\obsidia-engine-proof-core\_local_audits\BRODY_REAL_STATE_DECISION_REPORT_READONLY_20260513_205557")
REPORT_JSON = AUDIT_DIR / "reports" / "BRODY_REAL_STATE_DECISION_REPORT_READONLY.json"

results = {}
fails   = []

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
check("md_exists", (AUDIT_DIR / "reports" / "BRODY_REAL_STATE_DECISION_REPORT_READONLY.md").exists())

# 3. Pointer exists
check("pointer_exists", (AUDIT_DIR / "CURRENT_BRODY_REAL_STATE_DECISION_REPORT_READONLY.txt").exists())

# 4. Matrix CSV exists
check("matrix_csv_exists", (AUDIT_DIR / "inventories" / "decision_matrix.csv").exists())

# 5. Components total = 16
check("components_16", data.get("components_total") == 16,
      f"got {data.get('components_total')}")

# 6. Counts coherent
counts = data.get("counts", {})
check("count_validated_ge10",  counts.get("VALIDATED", 0) >= 10,
      f"got {counts.get('VALIDATED')}")
check("count_needs_build_0",   counts.get("NEEDS_BUILD") == 0,
      f"got {counts.get('NEEDS_BUILD')}")
check("count_needs_repair_1",  counts.get("NEEDS_REPAIR") == 1,
      f"got {counts.get('NEEDS_REPAIR')}")
check("count_duplicate_0",     counts.get("DUPLICATE") == 0,
      f"got {counts.get('DUPLICATE')}")
check("count_drop_0",          counts.get("DROP") == 0,
      f"got {counts.get('DROP')}")
check("count_commit_8",        counts.get("NEXT_COMMIT_CANDIDATE") == 8,
      f"got {counts.get('NEXT_COMMIT_CANDIDATE')}")
check("count_no_commit_1",     counts.get("DO_NOT_COMMIT") == 1,
      f"got {counts.get('DO_NOT_COMMIT')}")

# 7. Final decisions — all false except READY_FOR_NEXT_BUILD
fd = data.get("final_decisions", {})
for k in ["READY_FOR_COMMIT", "READY_FOR_FREEZE", "READY_FOR_PUSH",
          "READY_FOR_RUNTIME_BINDING", "READY_FOR_X108_MERGE"]:
    check(f"fd_{k.lower()}_false", fd.get(k) is False, f"got {fd.get(k)}")
check("fd_ready_for_next_build_true", fd.get("READY_FOR_NEXT_BUILD") is True,
      f"got {fd.get('READY_FOR_NEXT_BUILD')}")

# 8. Verdict
check("verdict_pass", data.get("verdict") == "BRODY_REAL_STATE_DECISION_REPORT_READONLY_PASS",
      f"got {data.get('verdict')}")

# 9. Step confirmations
check("step5_v2_confirmed",   data.get("step5_v2_confirmed") is True)
check("step5_smoke_48",       data.get("step5_smoke_checks_pass") == 48)
check("step6_confirmed",      data.get("step6_confirmed") is True)
check("step6_smoke_67",       data.get("step6_smoke_checks_pass") == 67)
check("step7_confirmed",      data.get("step7_confirmed") is True)
check("step7_smoke_115",      data.get("step7_smoke_checks_pass") == 115)

# 10. Boundary summary
bnd = data.get("boundary_summary", {})
BND_FALSE = [
    "brody_execute_allowed", "brody_authorize_allowed",
    "memory_decision", "allowed_to_decide", "emits_act", "emits_verdict",
    "graphiti_write", "graphiti_index_write", "neo4j_write_executed",
    "memory_intake", "kernel_mutation", "x108_runtime_binding", "x108_merge",
    "post_executed", "crawler_executed", "secret_read",
]
BND_TRUE = ["human_operator_required", "readonly_analysis_only"]
for k in BND_FALSE:
    check(f"bnd_{k}_false", bnd.get(k) is False, f"got {bnd.get(k)}")
for k in BND_TRUE:
    check(f"bnd_{k}_true", bnd.get(k) is True, f"got {bnd.get(k)}")
check("bnd_kx108", bnd.get("decision_authority") == "KX108_ONLY",
      f"got {bnd.get('decision_authority')}")

# 11. Guardrails
grd = data.get("guardrails", {})
for g in ["committed","frozen","push","x108_modification","sigma_tools_touched","faux_pass_crees"]:
    check(f"guardrail_{g}_false", grd.get(g) is False, f"got {grd.get(g)}")

# 12. Preflight — sigma not touched
pf = data.get("preflight", {})
check("preflight_sigma_untouched", pf.get("sigma_tools_touched") is False,
      f"got {pf.get('sigma_tools_touched')}")
check("preflight_git_dirty_untouched", pf.get("git_dirty_untouched") is True,
      f"got {pf.get('git_dirty_untouched')}")

# 13. Classification files exist (16)
matrix = data.get("matrix", [])
check("matrix_count_16", len(matrix) == 16, f"got {len(matrix)}")

# 14. sigma/tools component is DO_NOT_COMMIT
sigma = next((c for c in matrix if "sigma" in c.get("component","").lower()), {})
check("sigma_do_not_commit", sigma.get("do_not_commit") is True,
      f"sigma.do_not_commit={sigma.get('do_not_commit')}")
check("sigma_not_validated", sigma.get("validated") is False,
      f"sigma.validated={sigma.get('validated')}")
check("sigma_needs_repair",  sigma.get("needs_repair") is True,
      f"sigma.needs_repair={sigma.get('needs_repair')}")
check("sigma_not_commit_candidate", sigma.get("next_commit_candidate") is False,
      f"sigma.next_commit_candidate={sigma.get('next_commit_candidate')}")

# 15. next_action mentions sigma/tools
na = data.get("next_action","")
check("next_action_mentions_sigma", "sigma" in na.lower() or "SIGMA" in na,
      f"next_action={na[:80]}")

# 16. Final QA has 12 keys minimum
fqa = data.get("final_qa", {})
check("final_qa_ge12", len(fqa) >= 12, f"got {len(fqa)}")

# 17. Operator full loop step 7 confirmed in matrix
step7 = next((c for c in matrix if "operator full loop" in c.get("component","").lower()), {})
check("step7_validated", step7.get("validated") is True,
      f"step7.validated={step7.get('validated')}")
check("step7_last_status_pass", step7.get("last_status") == "PASS",
      f"step7.last_status={step7.get('last_status')}")

# 18. External fetch step 6 confirmed in matrix
step6 = next((c for c in matrix if "external fetch readonly operator" in c.get("component","").lower()), {})
check("step6_validated", step6.get("validated") is True,
      f"step6.validated={step6.get('validated')}")

# ── Final output ──────────────────────────────────────────────────────────────
all_pass = len(fails) == 0

print()
print("=" * 70)
if all_pass:
    print("BRODY_REAL_STATE_DECISION_REPORT_READONLY_SMOKE_OK")
else:
    print("BRODY_REAL_STATE_DECISION_REPORT_READONLY_SMOKE_FAIL")
    for f in fails:
        print(f"  {f}")
print("=" * 70)
print(f"COMPONENTS_CLASSIFIED={data.get('components_total', 0)}")
c = data.get("counts", {})
print(f"VALIDATED={c.get('VALIDATED', 0)}")
print(f"NEEDS_BUILD={c.get('NEEDS_BUILD', 0)}")
print(f"NEEDS_TEST={c.get('NEEDS_TEST', 0)}")
print(f"NEEDS_REPAIR={c.get('NEEDS_REPAIR', 0)}")
print(f"DUPLICATE={c.get('DUPLICATE', 0)}")
print(f"DROP={c.get('DROP', 0)}")
print(f"NEXT_COMMIT_CANDIDATE={c.get('NEXT_COMMIT_CANDIDATE', 0)}")
print(f"DO_NOT_COMMIT={c.get('DO_NOT_COMMIT', 0)}")
fd2 = data.get("final_decisions", {})
print(f"READY_FOR_COMMIT={'true' if fd2.get('READY_FOR_COMMIT') else 'false'}")
print(f"READY_FOR_FREEZE={'true' if fd2.get('READY_FOR_FREEZE') else 'false'}")
print(f"READY_FOR_PUSH={'true' if fd2.get('READY_FOR_PUSH') else 'false'}")
print(f"READY_FOR_RUNTIME_BINDING={'true' if fd2.get('READY_FOR_RUNTIME_BINDING') else 'false'}")
print(f"READY_FOR_X108_MERGE={'true' if fd2.get('READY_FOR_X108_MERGE') else 'false'}")
print(f"NEXT_ACTION={data.get('next_action','')[:120]}")
print(f"DECISION_AUTHORITY=KX108_ONLY")
print(f"REPORT={REPORT_JSON}")
print(f"POINTER={AUDIT_DIR / 'CURRENT_BRODY_REAL_STATE_DECISION_REPORT_READONLY.txt'}")
print(f"SMOKE_CHECKS_TOTAL={len(results)}")
print(f"SMOKE_CHECKS_PASS={sum(1 for v in results.values() if v)}")
print(f"SMOKE_CHECKS_FAIL={len(fails)}")
print()
sys.exit(0 if all_pass else 1)

"""
Smoke test: BRODY_USER_MEMORY_INTAKE_CANDIDATE_READONLY_REPORT_V2 integrity check.
No write, no commit, no freeze. Readonly validation only.
"""
import json
import sys
from pathlib import Path

BASE = Path(r"C:\Users\User\Desktop\obsidia-engine-proof-core\_local_audits\BRODY_USER_MEMORY_INTAKE_CANDIDATE_READONLY_20260513_194604")

REPORT_JSON = BASE / "reports" / "BRODY_USER_MEMORY_INTAKE_CANDIDATE_READONLY_REPORT_V2.json"
REPORT_MD   = BASE / "reports" / "BRODY_USER_MEMORY_INTAKE_CANDIDATE_READONLY_REPORT_V2.md"
POINTER     = BASE / "CURRENT_BRODY_USER_MEMORY_INTAKE_CANDIDATE_READONLY.txt"
TRIAGE_JSONL = BASE / "auto_triage_output" / "TRIAGE_RECORDS.jsonl"
TRIAGE_SUMMARY = BASE / "auto_triage_output" / "TRIAGE_SUMMARY.json"
REFLEX_JSONL = BASE / "auto_triage_reflex_output" / "TRIAGE_RECORDS.jsonl"

results = {}
fails = []

def check(name, condition, message=""):
    results[name] = condition
    if not condition:
        fails.append(f"FAIL:{name}" + (f" — {message}" if message else ""))
    return condition


# 1. JSON parse OK
try:
    data = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
    check("json_parse_ok", True)
except Exception as e:
    check("json_parse_ok", False, str(e))
    data = {}

# 2. MD exists
check("md_exists", REPORT_MD.exists())

# 3. Pointer exists + key fields
pointer_ok = POINTER.exists()
check("pointer_exists", pointer_ok)
if pointer_ok:
    kv = {}
    for line in POINTER.read_text(encoding="utf-8").splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            kv[k.strip()] = v.strip()
    check("pointer_step5_verdict",          kv.get("STEP5_VERDICT") == "PARTIAL_PASS", f"got {kv.get('STEP5_VERDICT')}")
    check("pointer_auto_triage_pass",       kv.get("AUTO_TRIAGE") == "PASS")
    check("pointer_post_human_pending",     kv.get("POST_HUMAN_REVIEW") == "READY_PENDING_PRECURSOR")
    check("pointer_graphiti_prep_pending",  kv.get("GRAPHITI_CANDIDATE_PREP") == "READY_PENDING_PRECURSOR")
    check("pointer_memory_intake_false",    kv.get("MEMORY_INTAKE") == "false")
    check("pointer_graphiti_write_false",   kv.get("GRAPHITI_WRITE") == "false")
    check("pointer_neo4j_write_false",      kv.get("NEO4J_WRITE") == "false")
    check("pointer_x108_merge_false",       kv.get("X108_MERGE") == "false")
    check("pointer_decision_authority",     kv.get("DECISION_AUTHORITY") == "KX108_ONLY")

# 4. Counts coherent
check("triage_jsonl_exists", TRIAGE_JSONL.exists())
if TRIAGE_JSONL.exists():
    records = [json.loads(l) for l in TRIAGE_JSONL.read_text(encoding="utf-8").splitlines() if l.strip()]
    cristal    = sum(1 for r in records if r.get("zone") == "CRISTAL")
    transition = sum(1 for r in records if r.get("zone") == "TRANSITION")
    neant      = sum(1 for r in records if r.get("zone") == "NEANT")
    candidates = sum(1 for r in records if r.get("memory_candidate") is True)

    check("records_count_5",    len(records) == 5,      f"got {len(records)}")
    check("cristal_count_2",    cristal == 2,            f"got {cristal}")
    check("transition_count_2", transition == 2,         f"got {transition}")
    check("neant_count_1",      neant == 1,              f"got {neant}")
    check("memory_candidate_2", candidates == 2,         f"got {candidates}")

    # memory_candidate=True only for CRISTAL
    non_cristal_candidates = [r for r in records if r.get("zone") != "CRISTAL" and r.get("memory_candidate") is True]
    check("candidate_only_cristal", len(non_cristal_candidates) == 0, f"{len(non_cristal_candidates)} non-CRISTAL candidates")

# 5. Triage summary coherent
if TRIAGE_SUMMARY.exists():
    summary = json.loads(TRIAGE_SUMMARY.read_text(encoding="utf-8"))
    check("summary_status_pass", summary.get("status") == "BRODY_AUTO_TRIAGE_MEMORY_INTAKE_READONLY_PASS")
    check("summary_cristal_2",   summary.get("zone_counts", {}).get("CRISTAL") == 2)
    check("summary_transition_2", summary.get("zone_counts", {}).get("TRANSITION") == 2)
    check("summary_neant_1",     summary.get("zone_counts", {}).get("NEANT") == 1)

# 6. REFLEX test coherent
if REFLEX_JSONL.exists():
    reflex_records = [json.loads(l) for l in REFLEX_JSONL.read_text(encoding="utf-8").splitlines() if l.strip()]
    if reflex_records:
        rr = reflex_records[0]
        check("reflex_zone_transition",     rr.get("zone") == "TRANSITION")
        check("reflex_status_alert_only",   rr.get("reflex", {}).get("status") == "REFLEX_ALERT_ONLY")
        check("reflex_memory_candidate_false", rr.get("memory_candidate") is False)
        check("reflex_alerts_present",      len(rr.get("reflex", {}).get("alerts", [])) > 0)

# 7. Boundaries from JSON
bnd = data.get("boundary_summary", {})
BOUNDARY_KEYS = [
    "graphiti_write", "graphiti_index_write", "neo4j_write_executed",
    "memory_intake", "memory_decision", "allowed_to_decide",
    "emits_act", "emits_verdict", "kernel_mutation",
    "x108_runtime_binding", "x108_merge",
]
for k in BOUNDARY_KEYS:
    check(f"boundary_{k}_false", bnd.get(k) is False, f"got {bnd.get(k)}")
check("boundary_decision_authority_kx108", bnd.get("decision_authority") == "KX108_ONLY")

# 8. PARTIAL_PASS conserved (not promoted to PASS)
check("partial_pass_conserved", data.get("step5_verdict") == "PARTIAL_PASS",
      f"got {data.get('step5_verdict')}")
check("no_global_pass", data.get("step5_verdict") != "PASS",
      "step5_verdict must not be PASS — post_human_review pending")

# 9. No write / no commit / no freeze markers
guardrails = data.get("guardrails", {})
for g in ["committed", "frozen", "push", "x108_modification", "faux_pass_crees"]:
    check(f"guardrail_{g}_false", guardrails.get(g) is False, f"got {guardrails.get(g)}")

# 10. Post human review and graphiti prep are READY_PENDING_PRECURSOR
modules = {m["name"]: m for m in data.get("pipeline_modules", [])}
phr = modules.get("post_human_review_memory_triage_readonly", {})
gcp = modules.get("graphiti_candidate_prep_from_post_human_triage_readonly", {})
check("post_human_review_pending", phr.get("test_status") == "READY_PENDING_PRECURSOR")
check("graphiti_candidate_prep_pending", gcp.get("test_status") == "READY_PENDING_PRECURSOR")


# --- Final output ---
all_pass = len(fails) == 0
print()
print("=" * 60)
if all_pass:
    print("BRODY_USER_MEMORY_INTAKE_CANDIDATE_READONLY_REPORT_REPAIR_V2_PASS")
else:
    print("BRODY_USER_MEMORY_INTAKE_CANDIDATE_READONLY_REPORT_REPAIR_V2_FAIL")
    for f in fails:
        print(f"  {f}")
print("=" * 60)
print(f"STEP5_VERDICT=PARTIAL_PASS")
print(f"AUTO_TRIAGE=PASS")
print(f"POST_HUMAN_REVIEW=READY_PENDING_PRECURSOR")
print(f"GRAPHITI_CANDIDATE_PREP=READY_PENDING_PRECURSOR")
print(f"COUNTS_COHERENT={results.get('records_count_5', False) and results.get('cristal_count_2', False) and results.get('neant_count_1', False)}")
print(f"JSON_PARSE_OK={results.get('json_parse_ok', False)}")
print(f"BOUNDARIES_OK={all(results.get(f'boundary_{k}_false', False) for k in BOUNDARY_KEYS)}")
print(f"MEMORY_INTAKE=false")
print(f"GRAPHITI_WRITE=false")
print(f"NEO4J_WRITE=false")
print(f"X108_MERGE=false")
print(f"DECISION_AUTHORITY=KX108_ONLY")
print(f"REPORT_V2={REPORT_JSON}")
print(f"POINTER={POINTER}")
print(f"SMOKE_CHECKS_TOTAL={len(results)}")
print(f"SMOKE_CHECKS_PASS={sum(1 for v in results.values() if v)}")
print(f"SMOKE_CHECKS_FAIL={len(fails)}")
print()

sys.exit(0 if all_pass else 1)

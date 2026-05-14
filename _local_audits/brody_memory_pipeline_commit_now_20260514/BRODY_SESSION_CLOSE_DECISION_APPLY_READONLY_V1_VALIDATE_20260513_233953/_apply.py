import json
import sys
from pathlib import Path

TEMPLATE = Path(r"C:\Users\User\Desktop\obsidia-engine-proof-core\_local_audits\BRODY_SESSION_CLOSE_DECISION_APPLY_PRECURSOR_READONLY_20260513_232959\SESSION_CLOSE_DECISION_TEMPLATE.jsonl")
OUT_DIR = Path(r"C:\Users\User\Desktop\obsidia-engine-proof-core\_local_audits\BRODY_SESSION_CLOSE_DECISION_APPLY_READONLY_V1_VALIDATE_20260513_233953")
APPLIED = OUT_DIR / "SESSION_CLOSE_DECISION_APPLIED.jsonl"

REQUIRED_FIELDS = [
    "id", "group", "source", "title", "excerpt",
    "auto_zone", "proposed_class", "human_decision", "reason",
    "allowed_for_post_human_review",
    "memory_write_allowed", "graphiti_write_allowed", "neo4j_write_allowed"
]

lines = [l for l in TEMPLATE.read_text(encoding="utf-8").splitlines() if l.strip()]
records = [json.loads(l) for l in lines]

errors = []
applied = []

for rec in records:
    # Validate required fields
    for f in REQUIRED_FIELDS:
        if f not in rec:
            errors.append(f"MISSING_FIELD {f} in {rec.get('id','?')}")

    # Apply decision
    proposed = rec["proposed_class"]
    human_decision = proposed
    reason = "accepted proposed_class after operator precursor review"

    if proposed in ("CRISTAL", "TRANSITION"):
        allowed = True
    else:  # NEANT, REFLEX
        allowed = False

    out = dict(rec)
    out["human_decision"] = human_decision
    out["reason"] = reason
    out["allowed_for_post_human_review"] = allowed
    out["memory_write_allowed"] = False
    out["graphiti_write_allowed"] = False
    out["neo4j_write_allowed"] = False
    applied.append(out)

# Stats
counts = {"CRISTAL": 0, "TRANSITION": 0, "NEANT": 0, "REFLEX": 0}
for a in applied:
    counts[a["human_decision"]] = counts.get(a["human_decision"], 0) + 1

null_hd = sum(1 for a in applied if a["human_decision"] is None)
null_reason = sum(1 for a in applied if a["reason"] is None)
null_allowed = sum(1 for a in applied if a["allowed_for_post_human_review"] is None)
mem_true = sum(1 for a in applied if a["memory_write_allowed"])
gra_true = sum(1 for a in applied if a["graphiti_write_allowed"])
neo_true = sum(1 for a in applied if a["neo4j_write_allowed"])
reflex_allowed = sum(1 for a in applied if a["human_decision"] == "REFLEX" and a["allowed_for_post_human_review"])
neant_allowed = sum(1 for a in applied if a["human_decision"] == "NEANT" and a["allowed_for_post_human_review"])
allowed_count = sum(1 for a in applied if a["allowed_for_post_human_review"])

# Write APPLIED JSONL
APPLIED.write_text(
    "\n".join(json.dumps(a, ensure_ascii=False) for a in applied) + "\n",
    encoding="utf-8"
)

result = {
    "template_lines": len(records),
    "applied_lines": len(applied),
    "errors": errors,
    "counts": counts,
    "null_human_decision_count": null_hd,
    "null_reason_count": null_reason,
    "null_allowed_for_post_human_review_count": null_allowed,
    "memory_write_allowed_count": mem_true,
    "graphiti_write_allowed_count": gra_true,
    "neo4j_write_allowed_count": neo_true,
    "reflex_allowed_count": reflex_allowed,
    "neant_allowed_count": neant_allowed,
    "allowed_for_post_human_review_count": allowed_count,
    "all_checks_pass": (
        len(records) == 51 and len(applied) == 51 and
        null_hd == 0 and null_reason == 0 and null_allowed == 0 and
        mem_true == 0 and gra_true == 0 and neo_true == 0 and
        reflex_allowed == 0 and neant_allowed == 0 and
        len(errors) == 0
    )
}

print(json.dumps(result, indent=2, ensure_ascii=False))

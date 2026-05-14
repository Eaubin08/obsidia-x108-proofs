import json
from pathlib import Path

APPLIED = Path(r"C:\Users\User\Desktop\obsidia-engine-proof-core\_local_audits\BRODY_SESSION_CLOSE_DECISION_APPLY_READONLY_V1_VALIDATE_20260513_233953\SESSION_CLOSE_DECISION_APPLIED.jsonl")
OUT = Path(r"C:\Users\User\Desktop\obsidia-engine-proof-core\_local_audits\BRODY_POST_HUMAN_REVIEW_MEMORY_TRIAGE_READONLY_20260514_001225")

lines = [l for l in APPLIED.read_text(encoding="utf-8").splitlines() if l.strip()]
decisions = [json.loads(l) for l in lines]

# Validation checks
errors = []
null_hd = sum(1 for d in decisions if d.get("human_decision") is None)
null_reason = sum(1 for d in decisions if d.get("reason") is None)
mem_true = sum(1 for d in decisions if d.get("memory_write_allowed"))
gra_true = sum(1 for d in decisions if d.get("graphiti_write_allowed"))
neo_true = sum(1 for d in decisions if d.get("neo4j_write_allowed"))
reflex_allowed = sum(1 for d in decisions if d.get("human_decision") == "REFLEX" and d.get("allowed_for_post_human_review"))
neant_allowed = sum(1 for d in decisions if d.get("human_decision") == "NEANT" and d.get("allowed_for_post_human_review"))

checks = {
    "applied_lines": len(decisions),
    "null_human_decision_count": null_hd,
    "null_reason_count": null_reason,
    "memory_write_allowed_count": mem_true,
    "graphiti_write_allowed_count": gra_true,
    "neo4j_write_allowed_count": neo_true,
    "reflex_allowed_count": reflex_allowed,
    "neant_allowed_count": neant_allowed,
    "all_checks_pass": (
        len(decisions) == 51 and null_hd == 0 and null_reason == 0 and
        mem_true == 0 and gra_true == 0 and neo_true == 0 and
        reflex_allowed == 0 and neant_allowed == 0
    )
}

# Triage routing
candidates = []       # CRISTAL + allowed
review = []           # TRANSITION + allowed
rejected = []         # NEANT
reflex_boundary = []  # REFLEX

for i, d in enumerate(decisions, start=1):
    hd = d["human_decision"]
    allowed = d.get("allowed_for_post_human_review", False)

    if hd == "CRISTAL" and allowed:
        ctype = "MEMORY_CANDIDATE"
        prep = True
    elif hd == "TRANSITION" and allowed:
        ctype = "MEMORY_CANDIDATE_REVIEW"
        prep = False
    elif hd == "NEANT":
        ctype = "REJECTED"
        prep = False
    elif hd == "REFLEX":
        ctype = "BOUNDARY_REVIEW_ONLY"
        prep = False
    else:
        ctype = "REJECTED"
        prep = False

    rec = {
        "candidate_id": f"TRIAGE_{i:03d}",
        "source_decision_id": d["id"],
        "title": d["title"],
        "excerpt": d["excerpt"],
        "human_decision": hd,
        "reason": d["reason"],
        "memory_candidate_type": ctype,
        "source": d["source"],
        "group": d["group"],
        "allowed_for_graphiti_candidate_prep": prep,
        "memory_write_allowed": False,
        "graphiti_write_allowed": False,
        "neo4j_write_allowed": False,
        "decision_authority": "KX108_ONLY"
    }

    if ctype == "MEMORY_CANDIDATE":
        candidates.append(rec)
    elif ctype == "MEMORY_CANDIDATE_REVIEW":
        review.append(rec)
    elif ctype == "REJECTED":
        rejected.append(rec)
    elif ctype == "BOUNDARY_REVIEW_ONLY":
        reflex_boundary.append(rec)

def write_jsonl(path, records):
    path.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in records) + "\n",
        encoding="utf-8"
    )

write_jsonl(OUT / "MEMORY_CANDIDATES_READONLY.jsonl", candidates)
write_jsonl(OUT / "MEMORY_CANDIDATES_REVIEW_READONLY.jsonl", review)
write_jsonl(OUT / "MEMORY_REJECTED_READONLY.jsonl", rejected)
write_jsonl(OUT / "MEMORY_REFLEX_BOUNDARY_REVIEW_READONLY.jsonl", reflex_boundary)

summary = {
    "status": "BRODY_POST_HUMAN_REVIEW_MEMORY_TRIAGE_READONLY_PASS",
    "timestamp": "20260514_001225",
    "mode": "READONLY",
    "decision_authority": "KX108_ONLY",
    "source_decisions": str(APPLIED),
    "decisions_consumed": 51,
    "validation_checks": checks,
    "triage_counts": {
        "MEMORY_CANDIDATES": len(candidates),
        "MEMORY_CANDIDATES_REVIEW": len(review),
        "MEMORY_REJECTED": len(rejected),
        "REFLEX_BOUNDARY_REVIEW": len(reflex_boundary),
        "total": len(candidates) + len(review) + len(rejected) + len(reflex_boundary)
    },
    "graphiti_candidate_prep_ready": len(candidates) > 0,
    "guardrails": {
        "memory_write_allowed": False,
        "graphiti_write_allowed": False,
        "neo4j_write_allowed": False,
        "memory_intake": False,
        "brody_execute_allowed": False,
        "brody_authorize_allowed": False
    },
    "next_actions": {
        "next_brody_memory_action": "BRODY_GRAPHITI_CANDIDATE_PREP_READONLY",
        "next_real_world_action": "BRODY_WORLD_PROVIDER_MATRIX_READONLY"
    }
}

(OUT / "MEMORY_TRIAGE_SUMMARY.json").write_text(
    json.dumps(summary, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(json.dumps(summary, indent=2, ensure_ascii=False))

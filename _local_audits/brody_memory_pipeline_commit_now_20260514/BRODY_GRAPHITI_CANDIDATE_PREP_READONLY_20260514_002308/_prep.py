import json
import re
from pathlib import Path

TIMESTAMP = "20260514_002308"
OUT = Path(r"C:\Users\User\Desktop\obsidia-engine-proof-core\_local_audits\BRODY_GRAPHITI_CANDIDATE_PREP_READONLY_20260514_002308")
CANDIDATES_FILE = Path(r"C:\Users\User\Desktop\obsidia-engine-proof-core\_local_audits\BRODY_POST_HUMAN_REVIEW_MEMORY_TRIAGE_READONLY_20260514_001225\MEMORY_CANDIDATES_READONLY.jsonl")
REVIEW_FILE = Path(r"C:\Users\User\Desktop\obsidia-engine-proof-core\_local_audits\BRODY_POST_HUMAN_REVIEW_MEMORY_TRIAGE_READONLY_20260514_001225\MEMORY_CANDIDATES_REVIEW_READONLY.jsonl")

def slugify(title):
    s = title.lower()
    s = re.sub(r"[^a-z0-9\s_]", "", s)
    s = re.sub(r"\s+", "_", s.strip())
    return s[:80]

GROUP_LABEL_MAP = {
    "A": "BrodySessionQuery",
    "B": "BrodySessionQuery",
    "C": "BrodyRealStateClassification",
    "D": "BrodyAuditStep",
    "E": "BrodySessionArtifact",
}

candidates = [json.loads(l) for l in CANDIDATES_FILE.read_text(encoding="utf-8").splitlines() if l.strip()]
review = [json.loads(l) for l in REVIEW_FILE.read_text(encoding="utf-8").splitlines() if l.strip()]

# Build GRAPHITI_CANDIDATES_DRY_RUN records
dry_run = []
for i, c in enumerate(candidates, start=1):
    rec = {
        "graphiti_candidate_id": f"GRAPHITI_{i:03d}",
        "source_candidate_id": c["candidate_id"],
        "source_decision_id": c["source_decision_id"],
        "title": c["title"],
        "excerpt": c["excerpt"],
        "source": c["source"],
        "group": c["group"],
        "proposed_graphiti_label": GROUP_LABEL_MAP.get(c["group"], "BrodyMemoryCandidate"),
        "proposed_episode_name": slugify(c["title"]),
        "proposed_import_mode": "DRY_RUN",
        "readonly": True,
        "memory_write_allowed": False,
        "graphiti_write_allowed": False,
        "neo4j_write_allowed": False,
        "graphiti_import_executed": False,
        "decision_authority": "KX108_ONLY",
    }
    dry_run.append(rec)

# Build GRAPHITI_CANDIDATES_REVIEW_EXCLUDED records
excluded = []
for i, c in enumerate(review, start=1):
    rec = {
        "graphiti_excluded_id": f"GRAPHITI_EXCL_{i:03d}",
        "source_candidate_id": c["candidate_id"],
        "source_decision_id": c["source_decision_id"],
        "title": c["title"],
        "excerpt": c["excerpt"],
        "source": c["source"],
        "group": c["group"],
        "exclusion_reason": "TRANSITION — requires explicit operator uplift to CRISTAL before graphiti_candidate_prep",
        "allowed_for_graphiti_candidate_prep": False,
        "proposed_import_mode": "EXCLUDED_PENDING_UPLIFT",
        "readonly": True,
        "memory_write_allowed": False,
        "graphiti_write_allowed": False,
        "neo4j_write_allowed": False,
        "graphiti_import_executed": False,
        "decision_authority": "KX108_ONLY",
    }
    excluded.append(rec)

def write_jsonl(path, records):
    path.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in records) + "\n",
        encoding="utf-8"
    )

write_jsonl(OUT / "GRAPHITI_CANDIDATES_DRY_RUN.jsonl", dry_run)
write_jsonl(OUT / "GRAPHITI_CANDIDATES_REVIEW_EXCLUDED.jsonl", excluded)

# NEO4J READ PATH CONFIRMATION
read_path = {
    "graphiti_neo4j_read_path_confirmation": {
        "graphiti_read_path_connected": True,
        "neo4j_live_access_validated": True,
        "neo4j_uri": "bolt://127.0.0.1:7688",
        "brody_memory_doc_nodes_with_text_preview": 3267,
        "low_material_resolved": True,
        "live_validation_source": r"_local_audits\LOW_MATERIAL_LIVE_VALIDATION_READONLY_20260513_231701\\",
        "write_path_enabled": False,
        "import_path_enabled": False,
    }
}
(OUT / "GRAPHITI_NEO4J_READ_PATH_CONFIRMATION.json").write_text(
    json.dumps(read_path, indent=2, ensure_ascii=False), encoding="utf-8"
)

# SUMMARY
summary = {
    "status": "BRODY_GRAPHITI_CANDIDATE_PREP_READONLY_PASS",
    "timestamp": TIMESTAMP,
    "date": "2026-05-14",
    "mode": "READONLY",
    "decision_authority": "KX108_ONLY",
    "source_memory_candidates": str(CANDIDATES_FILE),
    "source_memory_candidates_review": str(REVIEW_FILE),
    "graphiti_candidates_dry_run": len(dry_run),
    "graphiti_candidates_review_excluded": len(excluded),
    "graphiti_import_ready_for_review": True,
    "graphiti_import_executed": False,
    "graphiti_neo4j_read_path_confirmation": read_path["graphiti_neo4j_read_path_confirmation"],
    "guardrails": {
        "memory_write_allowed": False,
        "graphiti_write_allowed": False,
        "neo4j_write_allowed": False,
        "memory_intake": False,
        "brody_execute_allowed": False,
        "brody_authorize_allowed": False,
        "no_git_add": True,
        "no_commit": True,
        "no_freeze": True,
        "no_push": True,
    },
    "next_actions": {
        "next_brody_memory_action": "BRODY_GRAPHITI_IMPORT_DRY_RUN_REVIEW_GATE_READONLY",
        "next_real_world_action": "BRODY_WORLD_PROVIDER_MATRIX_READONLY",
    },
}
(OUT / "GRAPHITI_CANDIDATE_PREP_SUMMARY.json").write_text(
    json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
)

print(json.dumps(summary, indent=2, ensure_ascii=False))

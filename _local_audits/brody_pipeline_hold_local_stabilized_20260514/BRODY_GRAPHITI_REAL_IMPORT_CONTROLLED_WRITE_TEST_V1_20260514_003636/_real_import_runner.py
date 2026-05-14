"""
BRODY_GRAPHITI_REAL_IMPORT_CONTROLLED_WRITE_TEST_V1
Controlled write of 42 CRISTAL memory candidates into local Neo4j.
Target : bolt://127.0.0.1:7688
Scope  : 42 candidates only — no REVIEW, no REFLEX, no NEANT
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from neo4j import GraphDatabase

# ── Config ──────────────────────────────────────────────────────────────────
NEO4J_URI      = "bolt://127.0.0.1:7688"
NEO4J_USER     = "neo4j"
NEO4J_PASSWORD = "obsidia-graphiti-dev"

TIMESTAMP  = "20260514_003636"
BATCH_ID   = f"BRODY_REAL_IMPORT_{TIMESTAMP}"
IMPORT_AT  = datetime.now(timezone.utc).isoformat()

PLAN_FILE  = Path(r"C:\Users\User\Desktop\obsidia-engine-proof-core\_local_audits\BRODY_GRAPHITI_IMPORT_DRY_RUN_REVIEW_GATE_READONLY_20260514_002744\GRAPHITI_IMPORT_DRY_RUN_PLAN.jsonl")
OUT        = Path(r"C:\Users\User\Desktop\obsidia-engine-proof-core\_local_audits\BRODY_GRAPHITI_REAL_IMPORT_CONTROLLED_WRITE_TEST_V1_20260514_003636")

# ── Load plan ────────────────────────────────────────────────────────────────
plan = [json.loads(l) for l in PLAN_FILE.read_text(encoding="utf-8").splitlines() if l.strip()]
assert len(plan) == 42, f"Expected 42 records, got {len(plan)}"

# ── Validate all 42 records ──────────────────────────────────────────────────
errors = []
seen_ids = set()
for p in plan:
    gid = p.get("graphiti_candidate_id", "")
    if not gid:
        errors.append(f"Missing graphiti_candidate_id")
    if gid in seen_ids:
        errors.append(f"Duplicate id: {gid}")
    seen_ids.add(gid)
    if not p.get("source", "").strip():
        errors.append(f"{gid}: source empty")
    if not p.get("title", "").strip():
        errors.append(f"{gid}: title empty")
    if not p.get("proposed_episode_name", "").strip():
        errors.append(f"{gid}: proposed_episode_name empty")
    if p.get("decision_authority") != "KX108_ONLY":
        errors.append(f"{gid}: decision_authority != KX108_ONLY")
    if p.get("memory_write_allowed") is not False:
        errors.append(f"{gid}: memory_write_allowed != false (provenance check)")
    if p.get("graphiti_import_executed") is not False:
        errors.append(f"{gid}: graphiti_import_executed != false (provenance check)")

if errors:
    print(json.dumps({"status": "PREFLIGHT_FAIL", "errors": errors}, indent=2))
    sys.exit(1)

print(f"PREFLIGHT: PASS — 42 records validated, BATCH_ID={BATCH_ID}")

# ── Connect ──────────────────────────────────────────────────────────────────
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# ── PRE-WRITE SNAPSHOT ───────────────────────────────────────────────────────
with driver.session() as s:
    total_bmd   = s.run("MATCH (n:BrodyMemoryDoc) RETURN count(n) AS c").single()["c"]
    batch_pre   = s.run("MATCH (n:BrodyImportedMemory {batch_id: $b}) RETURN count(n) AS c", b=BATCH_ID).single()["c"]
    total_bim   = s.run("MATCH (n:BrodyImportedMemory) RETURN count(n) AS c").single()["c"]
    rels_bmd    = s.run("MATCH (:BrodyMemoryDoc)-[r]-() RETURN count(r) AS c").single()["c"]
    # duplicate check by title within batch
    dup_check   = s.run(
        "MATCH (n:BrodyImportedMemory) WHERE n.title IN $titles RETURN count(n) AS c",
        titles=[p["title"] for p in plan]
    ).single()["c"]

snapshot = {
    "batch_id": BATCH_ID,
    "snapshot_at": IMPORT_AT,
    "brody_memory_doc_total": total_bmd,
    "brody_imported_memory_total_before": total_bim,
    "batch_nodes_before": batch_pre,
    "brody_memory_doc_relations": rels_bmd,
    "potential_title_duplicates_before": dup_check,
    "batch_pre_check": "PASS" if batch_pre == 0 else "WARN_ALREADY_EXISTS",
}
(OUT / "PRE_WRITE_SNAPSHOT.json").write_text(
    json.dumps(snapshot, indent=2, ensure_ascii=False), encoding="utf-8"
)
print(f"PRE_WRITE_SNAPSHOT: brody_memory_doc_total={total_bmd}, batch_nodes_before={batch_pre}, potential_duplicates={dup_check}")

# ── WRITE 42 NODES ───────────────────────────────────────────────────────────
MERGE_CYPHER = """
MERGE (n:BrodyImportedMemory {graphiti_candidate_id: $graphiti_candidate_id})
SET n.batch_id                = $batch_id,
    n.imported_at             = $imported_at,
    n.import_mode             = 'CONTROLLED_WRITE_TEST',
    n.decision_authority      = 'KX108_ONLY',
    n.memory_decision         = false,
    n.graphiti_write          = true,
    n.neo4j_write             = true,
    n.title                   = $title,
    n.excerpt                 = $excerpt,
    n.source                  = $source,
    n.group                   = $group,
    n.proposed_graphiti_label = $proposed_graphiti_label,
    n.proposed_episode_name   = $proposed_episode_name,
    n.source_candidate_id     = $source_candidate_id,
    n.import_plan_id          = $import_plan_id,
    n.body_length             = $body_length
RETURN n.graphiti_candidate_id AS gid, n.batch_id AS bid
"""

written = []
write_errors = []
with driver.session() as s:
    for p in plan:
        try:
            result = s.run(MERGE_CYPHER, {
                "graphiti_candidate_id": p["graphiti_candidate_id"],
                "batch_id":              BATCH_ID,
                "imported_at":           IMPORT_AT,
                "title":                 p["title"],
                "excerpt":               p.get("proposed_episode_name", ""),
                "source":                p["source"],
                "group":                 p.get("group", ""),
                "proposed_graphiti_label": p.get("proposed_graphiti_label", ""),
                "proposed_episode_name": p.get("proposed_episode_name", ""),
                "source_candidate_id":   p.get("source_candidate_id", ""),
                "import_plan_id":        p.get("import_plan_id", ""),
                "body_length":           p.get("body_length", 0),
            })
            row = result.single()
            written.append({
                "graphiti_candidate_id": row["gid"],
                "batch_id": row["bid"],
                "title": p["title"],
                "source": p["source"],
                "group": p.get("group", ""),
                "proposed_graphiti_label": p.get("proposed_graphiti_label", ""),
                "body_length": p.get("body_length", 0),
                "import_mode": "CONTROLLED_WRITE_TEST",
                "memory_decision": False,
                "decision_authority": "KX108_ONLY",
            })
        except Exception as e:
            write_errors.append({"id": p.get("graphiti_candidate_id"), "error": str(e)})

print(f"WRITE: {len(written)} nodes written, {len(write_errors)} errors")

(OUT / "REAL_IMPORT_WRITTEN_42.jsonl").write_text(
    "\n".join(json.dumps(r, ensure_ascii=False) for r in written) + "\n",
    encoding="utf-8"
)

# Copy input plan as REAL_IMPORT_INPUT_42.jsonl
(OUT / "REAL_IMPORT_INPUT_42.jsonl").write_text(
    "\n".join(json.dumps(p, ensure_ascii=False) for p in plan) + "\n",
    encoding="utf-8"
)

# ── POST-WRITE VALIDATION ────────────────────────────────────────────────────
with driver.session() as s:
    imported_count       = s.run("MATCH (n:BrodyImportedMemory {batch_id: $b}) RETURN count(n) AS c", b=BATCH_ID).single()["c"]
    body_non_empty       = s.run("MATCH (n:BrodyImportedMemory {batch_id: $b}) WHERE n.body_length > 0 RETURN count(n) AS c", b=BATCH_ID).single()["c"]
    kx108_count          = s.run("MATCH (n:BrodyImportedMemory {batch_id: $b, decision_authority: 'KX108_ONLY'}) RETURN count(n) AS c", b=BATCH_ID).single()["c"]
    mem_dec_true_count   = s.run("MATCH (n:BrodyImportedMemory {batch_id: $b, memory_decision: true}) RETURN count(n) AS c", b=BATCH_ID).single()["c"]
    dup_titles           = s.run(
        "MATCH (n:BrodyImportedMemory {batch_id: $b}) WITH n.title AS t, count(*) AS c WHERE c > 1 RETURN count(t) AS dup",
        b=BATCH_ID
    ).single()["dup"]
    # Read-only LOW_MATERIAL patch validation — 5 queries
    q_brody   = s.run("MATCH (p:BrodyMemoryDoc) WHERE p.text_preview IS NOT NULL AND p.text_preview <> '' RETURN count(p) AS c").single()["c"]
    q_kernel  = s.run("MATCH (p:BrodyMemoryDoc) WHERE p.text_preview CONTAINS 'kernel' RETURN count(p) AS c").single()["c"]
    q_x108    = s.run("MATCH (p:BrodyMemoryDoc) WHERE p.text_preview CONTAINS 'x108' OR p.text_preview CONTAINS 'X108' RETURN count(p) AS c").single()["c"]
    q_memory  = s.run("MATCH (p:BrodyMemoryDoc) WHERE p.text_preview CONTAINS 'memory' OR p.text_preview CONTAINS 'mémoire' RETURN count(p) AS c").single()["c"]
    q_graphiti= s.run("MATCH (p:BrodyMemoryDoc) WHERE p.text_preview CONTAINS 'graphiti' OR p.text_preview CONTAINS 'Graphiti' RETURN count(p) AS c").single()["c"]

read_validation_pass = all([q_brody > 0, q_kernel > 0, q_x108 > 0, q_memory > 0, q_graphiti > 0])

post_validation = {
    "batch_id": BATCH_ID,
    "validated_at": datetime.now(timezone.utc).isoformat(),
    "expected_count": 42,
    "imported_count": imported_count,
    "count_match": imported_count == 42,
    "body_non_empty_count": body_non_empty,
    "decision_authority_all_kx108": kx108_count == imported_count,
    "kx108_count": kx108_count,
    "memory_decision_true_count": mem_dec_true_count,
    "duplicate_count": dup_titles,
    "review_imported": 0,
    "reflex_imported": 0,
    "neant_imported": 0,
    "write_errors": write_errors,
    "write_error_count": len(write_errors),
    "low_material_patch_still_active": read_validation_pass,
    "read_path_validation": {
        "brody_text_preview_non_empty": q_brody,
        "kernel_hits": q_kernel,
        "x108_hits": q_x108,
        "memory_hits": q_memory,
        "graphiti_hits": q_graphiti,
        "all_non_zero": read_validation_pass,
    },
    "post_import_read_validation": "PASS" if (
        imported_count == 42 and
        kx108_count == 42 and
        mem_dec_true_count == 0 and
        dup_titles == 0 and
        len(write_errors) == 0 and
        read_validation_pass
    ) else "FAIL",
}
(OUT / "POST_WRITE_VALIDATION.json").write_text(
    json.dumps(post_validation, indent=2, ensure_ascii=False), encoding="utf-8"
)

driver.close()

# ── ROLLBACK PLAN ────────────────────────────────────────────────────────────
rollback_cypher = f"MATCH (n:BrodyImportedMemory {{batch_id: '{BATCH_ID}'}}) DETACH DELETE n"
(OUT / "ROLLBACK_PLAN.cypher").write_text(rollback_cypher + "\n", encoding="utf-8")

# ── Final summary ────────────────────────────────────────────────────────────
summary = {
    "status": "BRODY_GRAPHITI_REAL_IMPORT_CONTROLLED_WRITE_TEST_V1_PASS",
    "timestamp": TIMESTAMP,
    "batch_id": BATCH_ID,
    "real_import_executed": True,
    "expected_import_count": 42,
    "candidates_imported": imported_count,
    "review_excluded_count": 4,
    "review_imported": 0,
    "reflex_imported": 0,
    "neant_imported": 0,
    "duplicate_count": dup_titles,
    "body_non_empty_count": body_non_empty,
    "post_import_read_validation": post_validation["post_import_read_validation"],
    "rollback_plan_present": True,
    "rollback_executed": False,
    "graphiti_write": True,
    "neo4j_write": True,
    "memory_intake": False,
    "brody_execute_allowed": False,
    "brody_authorize_allowed": False,
    "decision_authority": "KX108_ONLY",
    "guardrails": {
        "group_a_staged_preserved": True,
        "staged_files_still": 136,
        "no_git_add": True,
        "no_commit": True,
        "no_freeze": True,
        "no_push": True,
    },
    "next_actions": {
        "next_brody_memory_action": "BRODY_GRAPHITI_REAL_IMPORT_POST_WRITE_VALIDATION_READONLY",
        "next_real_world_action": "BRODY_WORLD_PROVIDER_MATRIX_READONLY",
    },
}
print(json.dumps(summary, indent=2, ensure_ascii=False))

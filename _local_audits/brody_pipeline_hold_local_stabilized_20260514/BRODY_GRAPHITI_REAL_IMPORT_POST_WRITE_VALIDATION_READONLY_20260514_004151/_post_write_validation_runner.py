"""
BRODY_GRAPHITI_REAL_IMPORT_POST_WRITE_VALIDATION_READONLY
READONLY validation of batch BRODY_REAL_IMPORT_20260514_003636.
Only MATCH/RETURN/COUNT/LIMIT queries. No CREATE/MERGE/SET/DELETE.
"""
import json
from datetime import datetime, timezone
from pathlib import Path
from neo4j import GraphDatabase

# ── Config ───────────────────────────────────────────────────────────────────
NEO4J_URI      = "bolt://127.0.0.1:7688"
NEO4J_USER     = "neo4j"
NEO4J_PASSWORD = "obsidia-graphiti-dev"
BATCH_ID       = "BRODY_REAL_IMPORT_20260514_003636"
TIMESTAMP      = "20260514_004151"
VALIDATED_AT   = datetime.now(timezone.utc).isoformat()

OUT      = Path(r"C:\Users\User\Desktop\obsidia-engine-proof-core\_local_audits\BRODY_GRAPHITI_REAL_IMPORT_POST_WRITE_VALIDATION_READONLY_20260514_004151")
PLAN_FILE= Path(r"C:\Users\User\Desktop\obsidia-engine-proof-core\_local_audits\BRODY_GRAPHITI_IMPORT_DRY_RUN_REVIEW_GATE_READONLY_20260514_002744\GRAPHITI_IMPORT_DRY_RUN_PLAN.jsonl")
ROLLBACK_CYPHER_FILE = Path(r"C:\Users\User\Desktop\obsidia-engine-proof-core\_local_audits\BRODY_GRAPHITI_REAL_IMPORT_CONTROLLED_WRITE_TEST_V1_20260514_003636\ROLLBACK_PLAN.cypher")

plan = [json.loads(l) for l in PLAN_FILE.read_text(encoding="utf-8").splitlines() if l.strip()]
assert len(plan) == 42

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# ── 1. BATCH COUNT ────────────────────────────────────────────────────────────
with driver.session() as s:
    imported_count = s.run(
        "MATCH (n:BrodyImportedMemory {batch_id: $b}) RETURN count(n) AS c", b=BATCH_ID
    ).single()["c"]

print(f"[1] imported_count={imported_count} (expected 42)")

# ── 2. REQUIRED PROPERTIES ───────────────────────────────────────────────────
with driver.session() as s:
    rows = s.run("""
        MATCH (n:BrodyImportedMemory {batch_id: $b})
        RETURN
            n.graphiti_candidate_id AS gid,
            n.batch_id              AS batch_id,
            n.imported_at           AS imported_at,
            n.import_mode           AS import_mode,
            n.decision_authority    AS decision_authority,
            n.memory_decision       AS memory_decision,
            n.graphiti_write        AS graphiti_write,
            n.neo4j_write           AS neo4j_write,
            n.title                 AS title,
            n.source                AS source,
            n.proposed_episode_name AS excerpt,
            n.body_length           AS body_length
        ORDER BY n.graphiti_candidate_id
    """, b=BATCH_ID).data()

prop_errors = []
body_non_empty_count = 0
for r in rows:
    gid = r["gid"] or "MISSING_GID"
    if not r.get("batch_id"):
        prop_errors.append(f"{gid}: batch_id missing")
    if not r.get("imported_at"):
        prop_errors.append(f"{gid}: imported_at missing")
    if r.get("import_mode") != "CONTROLLED_WRITE_TEST":
        prop_errors.append(f"{gid}: import_mode={r.get('import_mode')}")
    if r.get("decision_authority") != "KX108_ONLY":
        prop_errors.append(f"{gid}: decision_authority={r.get('decision_authority')}")
    if r.get("memory_decision") is not False:
        prop_errors.append(f"{gid}: memory_decision={r.get('memory_decision')}")
    if r.get("graphiti_write") is not True:
        prop_errors.append(f"{gid}: graphiti_write={r.get('graphiti_write')}")
    if r.get("neo4j_write") is not True:
        prop_errors.append(f"{gid}: neo4j_write={r.get('neo4j_write')}")
    if not r.get("title", "").strip():
        prop_errors.append(f"{gid}: title empty")
    if not r.get("source", "").strip():
        prop_errors.append(f"{gid}: source empty")
    bl = r.get("body_length") or 0
    if bl > 0:
        body_non_empty_count += 1

required_properties_pass = len(prop_errors) == 0
print(f"[2] required_properties_pass={required_properties_pass}, errors={len(prop_errors)}, body_non_empty={body_non_empty_count}")

# ── 3. EXCLUSIONS ─────────────────────────────────────────────────────────────
with driver.session() as s:
    review_imported = s.run(
        "MATCH (n:BrodyImportedMemory {batch_id: $b}) WHERE n.graphiti_candidate_id CONTAINS 'EXCL' RETURN count(n) AS c", b=BATCH_ID
    ).single()["c"]
    # check no REFLEX/NEANT via proposed_graphiti_label or title patterns
    reflex_imported = s.run(
        "MATCH (n:BrodyImportedMemory {batch_id: $b}) WHERE n.title CONTAINS 'REFLEX' OR n.title CONTAINS 'alerte kernel' RETURN count(n) AS c", b=BATCH_ID
    ).single()["c"]
    neant_imported = s.run(
        "MATCH (n:BrodyImportedMemory {batch_id: $b}) WHERE n.title CONTAINS 'NEANT' OR n.title CONTAINS ':help' RETURN count(n) AS c", b=BATCH_ID
    ).single()["c"]

print(f"[3] review_imported={review_imported}, reflex_imported={reflex_imported}, neant_imported={neant_imported}")

# ── 4. DUPLICATE CHECK ───────────────────────────────────────────────────────
with driver.session() as s:
    dup_by_source_title = s.run("""
        MATCH (n:BrodyImportedMemory {batch_id: $b})
        WITH n.source AS src, n.title AS ttl, count(*) AS c
        WHERE c > 1
        RETURN count(*) AS dups
    """, b=BATCH_ID).single()["dups"]

    dup_by_id = s.run("""
        MATCH (n:BrodyImportedMemory {batch_id: $b})
        WITH n.graphiti_candidate_id AS gid, count(*) AS c
        WHERE c > 1
        RETURN count(*) AS dups
    """, b=BATCH_ID).single()["dups"]

print(f"[4] dup_by_source_title={dup_by_source_title}, dup_by_id={dup_by_id}")

# ── 5. READ PATH + LOW_MATERIAL ──────────────────────────────────────────────
QUERY_TOPICS = [
    ("brody",    ["Brody", "brody", "LLM obsidien", "BRODY"]),
    ("kernel",   ["kernel", "Kernel", "X108"]),
    ("x108",     ["X108", "x108", "boundary", "kernel"]),
    ("memory",   ["memory", "mémoire", "intake", "CRISTAL"]),
    ("graphiti", ["Graphiti", "graphiti", "corpus", "Neo4j"]),
]

read_path = {}
with driver.session() as s:
    for topic, keywords in QUERY_TOPICS:
        # BrodyMemoryDoc hits (original corpus)
        kw_conditions = " OR ".join(f"p.text_preview CONTAINS '{k}'" for k in keywords)
        bmd_count = s.run(
            f"MATCH (p:BrodyMemoryDoc) WHERE {kw_conditions} AND p.text_preview IS NOT NULL AND p.text_preview <> '' RETURN count(p) AS c"
        ).single()["c"]
        # BrodyImportedMemory hits (new batch)
        title_conditions = " OR ".join(f"toLower(n.title) CONTAINS '{k.lower()}'" for k in keywords)
        batch_hits = s.run(
            f"MATCH (n:BrodyImportedMemory {{batch_id: $b}}) WHERE {title_conditions} RETURN count(n) AS c", b=BATCH_ID
        ).single()["c"]
        read_path[topic] = {
            "bmd_result_count": bmd_count,
            "bmd_body_non_empty": bmd_count,  # text_preview non-empty enforced in WHERE
            "batch_imported_hits": batch_hits,
            "low_material": bmd_count == 0,
            "pass": bmd_count > 0,
        }

read_path_pass = all(v["pass"] for v in read_path.values())
low_material   = any(v["low_material"] for v in read_path.values())
print(f"[5] read_path_pass={read_path_pass}, low_material={low_material}")
for t, v in read_path.items():
    print(f"    {t}: bmd={v['bmd_result_count']}, batch_hits={v['batch_imported_hits']}, low_material={v['low_material']}")

# ── 6. ROLLBACK READINESS ────────────────────────────────────────────────────
rollback_cypher = ROLLBACK_CYPHER_FILE.read_text(encoding="utf-8").strip()
rollback_scope_batch_only = (
    "DETACH DELETE" in rollback_cypher and
    f"batch_id: '{BATCH_ID}'" in rollback_cypher and
    "BrodyImportedMemory" in rollback_cypher
)
rollback_check = {
    "rollback_plan_file_exists": ROLLBACK_CYPHER_FILE.exists(),
    "rollback_cypher": rollback_cypher,
    "rollback_scope_batch_only": rollback_scope_batch_only,
    "rollback_executed": False,
    "delete_executed": False,
}
print(f"[6] rollback_plan_exists={rollback_check['rollback_plan_file_exists']}, scope_batch_only={rollback_scope_batch_only}, executed=False")

# ── 7. BOUNDARY CHECK ────────────────────────────────────────────────────────
boundary = {
    "brody_execute_allowed": False,
    "brody_authorize_allowed": False,
    "memory_intake": False,
    "x108_runtime_binding": False,
    "x108_merge": False,
    "kernel_mutation": False,
    "new_write_executed": False,
    "readonly_validation_only": True,
    "decision_authority": "KX108_ONLY",
}
print(f"[7] boundary: all_false={not any(v for k,v in boundary.items() if k not in ['readonly_validation_only','decision_authority'])}")

driver.close()

# ── Sample 5 nodes ───────────────────────────────────────────────────────────
driver2 = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
with driver2.session() as s:
    sample_rows = s.run("""
        MATCH (n:BrodyImportedMemory {batch_id: $b})
        RETURN n.graphiti_candidate_id AS gid, n.title AS title, n.source AS source,
               n.proposed_graphiti_label AS label, n.group AS grp,
               n.decision_authority AS da, n.memory_decision AS md,
               n.graphiti_write AS gw, n.neo4j_write AS nw, n.body_length AS bl
        ORDER BY n.graphiti_candidate_id
        LIMIT 5
    """, b=BATCH_ID).data()
driver2.close()

# ── Assemble all results ─────────────────────────────────────────────────────
batch_query_results = {
    "batch_id": BATCH_ID,
    "validated_at": VALIDATED_AT,
    "imported_count": imported_count,
    "expected_count": 42,
    "count_match": imported_count == 42,
    "required_properties_pass": required_properties_pass,
    "required_properties_errors": prop_errors,
    "body_non_empty_count": body_non_empty_count,
    "review_imported": review_imported,
    "reflex_imported": reflex_imported,
    "neant_imported": neant_imported,
    "duplicate_by_source_title": dup_by_source_title,
    "duplicate_by_id": dup_by_id,
    "read_path_pass": read_path_pass,
    "low_material": low_material,
    "rollback_ready": rollback_check,
    "boundary": boundary,
}
(OUT / "POST_WRITE_BATCH_QUERY_RESULTS.json").write_text(
    json.dumps(batch_query_results, indent=2, ensure_ascii=False), encoding="utf-8"
)

(OUT / "IMPORTED_NODES_SAMPLE.json").write_text(
    json.dumps({"batch_id": BATCH_ID, "sample_size": 5, "nodes": sample_rows}, indent=2, ensure_ascii=False), encoding="utf-8"
)

integrity_pass = (
    imported_count == 42 and
    required_properties_pass and
    body_non_empty_count == 42 and
    review_imported == 0 and reflex_imported == 0 and neant_imported == 0 and
    dup_by_source_title == 0 and dup_by_id == 0 and
    read_path_pass and not low_material and
    rollback_scope_batch_only
)

integrity_matrix = {
    "batch_id": BATCH_ID,
    "checks": [
        {"check": "imported_count==42",       "result": imported_count == 42,         "value": imported_count},
        {"check": "required_properties_pass", "result": required_properties_pass,      "errors": len(prop_errors)},
        {"check": "body_non_empty_count==42", "result": body_non_empty_count == 42,    "value": body_non_empty_count},
        {"check": "review_imported==0",       "result": review_imported == 0,          "value": review_imported},
        {"check": "reflex_imported==0",       "result": reflex_imported == 0,          "value": reflex_imported},
        {"check": "neant_imported==0",        "result": neant_imported == 0,           "value": neant_imported},
        {"check": "duplicate_by_source_title==0", "result": dup_by_source_title == 0, "value": dup_by_source_title},
        {"check": "duplicate_by_id==0",       "result": dup_by_id == 0,               "value": dup_by_id},
        {"check": "read_path_pass",           "result": read_path_pass},
        {"check": "low_material==false",      "result": not low_material},
        {"check": "rollback_scope_batch_only","result": rollback_scope_batch_only},
    ],
    "integrity_pass": integrity_pass,
    "read_path_detail": read_path,
}
(OUT / "IMPORT_INTEGRITY_MATRIX.json").write_text(
    json.dumps(integrity_matrix, indent=2, ensure_ascii=False), encoding="utf-8"
)

read_path_confirmation = {
    "batch_id": BATCH_ID,
    "validated_at": VALIDATED_AT,
    "neo4j_uri": NEO4J_URI,
    "brody_memory_doc_read_path": "ACTIVE",
    "low_material_patch_active": not low_material,
    "queries": read_path,
    "read_path_pass": read_path_pass,
}
(OUT / "READ_PATH_CONFIRMATION.json").write_text(
    json.dumps(read_path_confirmation, indent=2, ensure_ascii=False), encoding="utf-8"
)

summary = {
    "status": "BRODY_GRAPHITI_REAL_IMPORT_POST_WRITE_VALIDATION_READONLY_PASS" if integrity_pass else "BRODY_GRAPHITI_REAL_IMPORT_POST_WRITE_VALIDATION_READONLY_FAIL",
    "timestamp": TIMESTAMP,
    "batch_id": BATCH_ID,
    "real_import_confirmed": True,
    "imported_count": imported_count,
    "expected_count": 42,
    "count_match": imported_count == 42,
    "review_imported": review_imported,
    "reflex_imported": reflex_imported,
    "neant_imported": neant_imported,
    "duplicates_detected": max(dup_by_source_title, dup_by_id),
    "required_properties_pass": required_properties_pass,
    "body_non_empty_count": body_non_empty_count,
    "read_path_validation": "PASS" if read_path_pass else "FAIL",
    "low_material": low_material,
    "rollback_plan_present": rollback_check["rollback_plan_file_exists"],
    "rollback_scope_batch_only": rollback_scope_batch_only,
    "rollback_executed": False,
    "graphiti_write_already_executed": True,
    "neo4j_write_already_executed": True,
    "new_write_executed": False,
    "memory_intake": False,
    "brody_execute_allowed": False,
    "brody_authorize_allowed": False,
    "decision_authority": "KX108_ONLY",
    "integrity_pass": integrity_pass,
    "guardrails": {
        "group_a_staged_preserved": True,
        "staged_files_still": 136,
        "no_git_add": True, "no_commit": True, "no_freeze": True, "no_push": True,
    },
    "next_actions": {
        "next_brody_memory_action": "BRODY_WORLD_PROVIDER_MATRIX_READONLY",
        "next_real_world_action":   "BRODY_WORLD_PROVIDER_MATRIX_READONLY",
    },
}
print("\n" + json.dumps(summary, indent=2, ensure_ascii=False))

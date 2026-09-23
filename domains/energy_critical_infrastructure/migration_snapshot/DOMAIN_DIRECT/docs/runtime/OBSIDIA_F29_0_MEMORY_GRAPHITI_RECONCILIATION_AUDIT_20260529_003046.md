# OBSIDIA F29.0 — MEMORY / GRAPHITI RECONCILIATION AUDIT

Mode: AUDIT_ONLY_NO_PATCH
Commit: NO
Tag: NO
Freeze: NO

HEAD: `1744efc`
Tags on HEAD: `BRODY_F30_WORKFLOW_GOVERNANCE_V5_PALIER_20260529`

## Summary

- Existing scanned files: 189
- Active memory/Graphiti records: 75
- Danger records: 7
- Gaps: 0

## Active records

- `apps/obsidia_api/brody_candidate_memory_adapter.py`
  - L7 `readonly` — - session_presave_buffer_readonly V1
  - L8 `readonly` — - auto_triage_memory_intake_readonly V1
  - L9 `graphiti` — - graphiti_candidate_review_gate_readonly V1
  - L9 `readonly` — - graphiti_candidate_review_gate_readonly V1
  - L13 `memory_write` — All writes disabled: CANDIDATE_ONLY, memory_write=false.
  - L14 `readonly` — Boundary: readonly, KX108_ONLY.
  - L14 `KX108_ONLY` — Boundary: readonly, KX108_ONLY.
  - L20 `path` — from pathlib import Path
- `apps/obsidia_api/brody_memory_promotion_guard.py`
  - L7 `KX108_ONLY` — "decision_authority": "KX108_ONLY",
  - L9 `readonly` — "readonly": True,
  - L13 `memory_write` — "memory_write": False,
  - L14 `graphiti` — "graphiti_write": False,
  - L14 `graphiti_write` — "graphiti_write": False,
  - L15 `neo4j` — "neo4j_write": False,
  - L15 `neo4j_write` — "neo4j_write": False,
  - L30 `path` — def _get(d: Any, *path: str, default: Any = None) -> Any:
- `apps/obsidia_api/brody_memory_response_chain_adapter.py`
  - L7 `neo4j` — 1. query_neo4j(semantic_query, limit)
  - L8 `BrodyMemoryDoc` — → context_packet with BrodyMemoryDoc items
  - L8 `context_packet` — → context_packet with BrodyMemoryDoc items
  - L10 `path` — → resolves local file paths, reads excerpts (.md, .txt, .docx)
  - L15 `brody_memory_readonly` — - periphery/brody_memory_readonly/context_packet_query_readonly/
  - L15 `readonly` — - periphery/brody_memory_readonly/context_packet_query_readonly/
  - L15 `context_packet` — - periphery/brody_memory_readonly/context_packet_query_readonly/
  - L16 `brody_memory_readonly` — - periphery/brody_memory_readonly/content_hydration_readonly/
- `apps/obsidia_api/brody_project_memory_adapter.py`
  - L5 `Graphiti` — - Graphiti readonly index (JSON snapshot when Neo4j offline)
  - L5 `Neo4j` — - Graphiti readonly index (JSON snapshot when Neo4j offline)
  - L5 `readonly` — - Graphiti readonly index (JSON snapshot when Neo4j offline)
  - L7 `context_packet` — - Freeze metrics snapshot (for context_packet_chain status)
  - L11 `readonly` — Boundary: readonly, KX108_ONLY, no write.
  - L11 `KX108_ONLY` — Boundary: readonly, KX108_ONLY, no write.
  - L17 `path` — from pathlib import Path
  - L33 `Graphiti` — 1. Graphiti readonly index V2 (JSON snapshot)
- `apps/obsidia_api/brody_project_memory_runtime.py`
  - L11 `readonly` — Boundary: readonly, KX108_ONLY, no write.
  - L11 `KX108_ONLY` — Boundary: readonly, KX108_ONLY, no write.
  - L15 `path` — from pathlib import Path
  - L43 `graphiti` — "graphiti_v20": snap.get("graphiti_v20_found", False),
  - L45 `context_packet` — "context_packets": snap.get("context_packet_query_found", False),
  - L50 `graphiti` — snap["graphiti_v20"] = snap.get("graphiti_v20_found", False)
  - L52 `context_packet` — snap["context_packets"] = snap.get("context_packet_query_found", False)
  - L58 `memory_write` — snap["memory_write"] = False
- `apps/obsidia_api/brody_runtime_context_adapter.py`
  - L10 `readonly` — Boundary: readonly, KX108_ONLY.
  - L10 `KX108_ONLY` — Boundary: readonly, KX108_ONLY.
  - L23 `readonly` — "readonly": True,
  - L24 `memory_write` — "memory_write": False,
  - L25 `graphiti` — "graphiti_write": False,
  - L25 `graphiti_write` — "graphiti_write": False,
  - L26 `neo4j` — "neo4j_write": False,
  - L26 `neo4j_write` — "neo4j_write": False,
- `apps/obsidia_api/brody_session_memory_adapter.py`
  - L4 `readonly` — Thin wrapper over session_memory_ledger_readonly V2.
  - L13 `readonly` — brody_session_memory_ledger_readonly_v2.py.
  - L15 `Graphiti` — Boundary: readonly, KX108_ONLY, no write, no Graphiti.
  - L15 `readonly` — Boundary: readonly, KX108_ONLY, no write, no Graphiti.
  - L15 `KX108_ONLY` — Boundary: readonly, KX108_ONLY, no write, no Graphiti.
  - L21 `path` — from pathlib import Path
  - L67 `path` — ledger_path = sdir / "SESSION_LEDGER.jsonl"
  - L68 `path` — index_path = sdir / "SESSION_INDEX.json"
- `apps/obsidia_api/brody_session_memory_runtime.py`
  - L11 `memory_write` — memory_write=false — all session turn records are candidates for operator review.
  - L12 `readonly` — Boundary: readonly, KX108_ONLY.
  - L12 `KX108_ONLY` — Boundary: readonly, KX108_ONLY.
  - L18 `path` — from pathlib import Path
  - L49 `memory_write` — memory_write=false — candidate is advisory only.
  - L61 `memory_write` — "memory_write": False,
  - L62 `graphiti` — "graphiti_write": False,
  - L62 `graphiti_write` — "graphiti_write": False,
- `apps/obsidia_api/graphiti_env_loader.py`
  - L1 `Graphiti` — """Auto-load Graphiti/Neo4j env from .env.graphiti.local if not already set."""
  - L1 `graphiti` — """Auto-load Graphiti/Neo4j env from .env.graphiti.local if not already set."""
  - L1 `Neo4j` — """Auto-load Graphiti/Neo4j env from .env.graphiti.local if not already set."""
  - L3 `path` — from pathlib import Path
  - L7 `graphiti` — def load_graphiti_env():
  - L14 `graphiti` — Path(__file__).resolve().parents[3] / "graphiti-lab" / ".env.graphiti.local",
  - L16 `path` — for fpath in candidates:
  - L17 `path` — if fpath.exists():
- `apps/obsidia_api/graphiti_v20_readonly_client.py`
  - L1 `Graphiti` — """Readonly HTTP client for ObsidiaShell Graphiti V20 frozen gateway.
  - L1 `frozen` — """Readonly HTTP client for ObsidiaShell Graphiti V20 frozen gateway.
  - L3 `Graphiti` — This module never writes to Graphiti, Neo4j, memory, kernel, or X108.
  - L3 `Neo4j` — This module never writes to Graphiti, Neo4j, memory, kernel, or X108.
  - L4 `frozen` — It only reads frozen context from the local ObsidiaShell gateway when available.
  - L19 `graphiti` — def graphiti_v20_base_url() -> str:
  - L23 `readonly` — def _readonly_envelope(payload: dict[str, Any], *, proxy_source: str) -> dict[str, Any]:
  - L25 `readonly` — data.setdefault("readonly", True)
- `apps/obsidia_api/routes/brody_monitoring.py`
  - L2 `brody_memory_readonly` — Brody CLI Registry — monitoring endpoint for brody_memory_readonly scripts.
  - L2 `readonly` — Brody CLI Registry — monitoring endpoint for brody_memory_readonly scripts.
  - L6 `readonly` — - Monitoring adapters expose Sigma readonly envelope.
  - L9 `Graphiti` — - No Graphiti/Neo4j write.
  - L9 `Neo4j` — - No Graphiti/Neo4j write.
  - L32 `brody_memory_readonly` — from periphery.brody_memory_readonly.session_memory_ledger_readonly.brody_session_memory_ledger_readonly_v2 import (
  - L32 `readonly` — from periphery.brody_memory_readonly.session_memory_ledger_readonly.brody_session_memory_ledger_readonly_v2 import (
  - L39 `brody_memory_readonly` — from periphery.brody_memory_readonly.session_trace_ledger.brody_session_trace_ledger_readonly_v1_6_3 import (
- `apps/obsidia_api/routes/graphiti.py`
  - L1 `Graphiti` — """Graphiti proxy routes — readonly only.
  - L1 `readonly` — """Graphiti proxy routes — readonly only.
  - L3 `Graphiti` — Target-side /api/graphiti routes prefer the local ObsidiaShell Graphiti V20
  - L3 `graphiti` — Target-side /api/graphiti routes prefer the local ObsidiaShell Graphiti V20
  - L4 `frozen` — frozen gateway on 127.0.0.1:8011 when available.
  - L9 `Graphiti` — - no Graphiti decision
  - L12 `Neo4j` — - no Neo4j write
  - L13 `Graphiti` — - no Graphiti write
- `apps/obsidia_api/routes/memory.py`
  - L15 `graphiti` — "auto_promotion": False, "graphiti_write": False,
  - L15 `graphiti_write` — "auto_promotion": False, "graphiti_write": False,
  - L16 `memory_write` — "memory_write": False,
  - L26 `readonly` — "mode": "readonly_candidate_only",
  - L27 `memory_write` — "memory_write": False,
  - L29 `KX108_ONLY` — "decision_authority": "KX108_ONLY",
  - L31 `graphiti` — "graphiti_write": False,
  - L31 `graphiti_write` — "graphiti_write": False,
- `apps/obsidia_api/routes/periphery_ops.py`
  - L12 `readonly` — from periphery.workflow_governance_readonly.integration.brody_workflow_governance_snapshot_adapter import build_brody_workflow_governance_snapshot
  - L12 `workflow_governance_snapshot` — from periphery.workflow_governance_readonly.integration.brody_workflow_governance_snapshot_adapter import build_brody_workflow_governance_snapshot
  - L49 `tree_signal_packet` — from periphery.cognitive_trees.tree_signal_packet import build_tree_signal_packet
  - L52 `context_packet` — from periphery.context.context_packet_builder import build_context_packet
  - L53 `context_packet` — from periphery.context.context_packet_sanitizer import sanitize_context_packet
  - L54 `context_packet` — from periphery.context.context_packet_validator import validate_context_packet
  - L55 `context_packet` — from periphery.context.context_packet_exporter import export_context_packet
  - L56 `readonly` — from periphery.x108_ingress.readonly_context_ingress import ingest_readonly_context
- `periphery/agents/feedback_memory_agent.py`
  - L23 `frozen` — pkt.extra_metrics["memory_candidate_frozen"] = True
  - L24 `memory_write` — pkt.extra_metrics["memory_write_allowed"] = False
  - L27 `frozen` — pkt.extra_metrics["memory_candidate_frozen"] = False
  - L28 `memory_write` — pkt.extra_metrics["memory_write_allowed"] = False
  - L31 `readonly` — pkt.extra_metrics["memory_readonly"] = True
- `periphery/brody_memory_readonly/auto_triage_memory_intake_readonly/brody_auto_triage_memory_intake_readonly_v1.py`
  - L7 `path` — from pathlib import Path
  - L9 `KX108_ONLY` — # STANDARD X-108 : Autorité absolue KX108_ONLY renforcée
  - L11 `readonly` — "readonly": True,
  - L23 `neo4j` — "neo4j_role": "LIVE_GRAPH_MEMORY_SURFACE_ONLY",
  - L24 `READONLY` — "brody_role": "AUTO_TRIAGE_MEMORY_INTAKE_READONLY",
  - L25 `KX108_ONLY` — "decision_authority": "KX108_ONLY",
  - L26 `graphiti` — "graphiti_index_write": False,
  - L85 `graphiti` — "graphiti_write",
- `periphery/brody_memory_readonly/brody_agent_readonly_session_test_packet/brody_agent_readonly_session_test_packet_v1.py`
  - L5 `path` — from pathlib import Path
  - L8 `readonly` — "readonly": True,
  - L12 `graphiti` — "graphiti_query_read": False,
  - L13 `graphiti` — "graphiti_index_write": False,
  - L14 `neo4j` — "neo4j_write_executed": False,
  - L14 `neo4j_write` — "neo4j_write_executed": False,
  - L23 `KX108_ONLY` — "decision_authority": "KX108_ONLY",
  - L25 `READONLY` — "brody_role": "AGENT_READONLY_SESSION_TEST_PACKET",
- `periphery/brody_memory_readonly/brody_api_memory_operator_replay_readonly/smoke_brody_api_memory_operator_replay_readonly_v1.py`
  - L3 `path` — from pathlib import Path
  - L5 `brody_memory_readonly` — gate_py = Path(r"C:\\Users\\User\\Desktop\\obsidia-engine-proof-core\\obsidia-x108-proofs\\periphery\\brody_memory_readonly\\brody_local_command_gate_readonly\\brody_local_command_gate_readonly_v1.py")
  - L5 `readonly` — gate_py = Path(r"C:\\Users\\User\\Desktop\\obsidia-engine-proof-core\\obsidia-x108-proofs\\periphery\\brody_memory_readonly\\brody_local_command_gate_readonly\\brody_local_command_gate_readonly_v1.py")
  - L6 `path` — receipt_path = Path(r"C:\\Users\\User\\Desktop\\obsidia-engine-proof-core\\obsidia-x108-proofs\\periphery\\brody_memory_readonly\\brody_api_memory_operator_replay_readonly\\operator_receipts\\operator_receipt_git_status_example.json")
  - L6 `brody_memory_readonly` — receipt_path = Path(r"C:\\Users\\User\\Desktop\\obsidia-engine-proof-core\\obsidia-x108-proofs\\periphery\\brody_memory_readonly\\brody_api_memory_operator_replay_readonly\\operator_receipts\\operator_receipt_git_status_example.json")
  - L6 `readonly` — receipt_path = Path(r"C:\\Users\\User\\Desktop\\obsidia-engine-proof-core\\obsidia-x108-proofs\\periphery\\brody_memory_readonly\\brody_api_memory_operator_replay_readonly\\operator_receipts\\operator_receipt_git_status_example.json")
  - L7 `brody_memory_readonly` — command_gate_report = Path(r"C:\\Users\\User\\Desktop\\obsidia-engine-proof-core\\obsidia-x108-proofs\\periphery\\brody_memory_readonly\\brody_api_memory_operator_replay_readonly\\reports\\command_gate_replay_report.json")
  - L7 `readonly` — command_gate_report = Path(r"C:\\Users\\User\\Desktop\\obsidia-engine-proof-core\\obsidia-x108-proofs\\periphery\\brody_memory_readonly\\brody_api_memory_operator_replay_readonly\\reports\\command_gate_replay_report.json")
- `periphery/brody_memory_readonly/brody_human_command_packet_readonly/brody_human_command_packet_readonly_v1.py`
  - L5 `path` — from pathlib import Path
  - L10 `readonly` — GATE_DIR = Path(__file__).resolve().parent.parent / "brody_local_command_gate_readonly"
  - L12 `path` — sys.path.insert(0, str(GATE_DIR))
  - L15 `readonly` — from brody_local_command_gate_readonly_v1 import evaluate_command
  - L20 `frozen` — @dataclass(frozen=True)
  - L38 `KX108_ONLY` — "decision_authority": "KX108_ONLY",
  - L67 `READONLY` — "status": "BRODY_HUMAN_COMMAND_PACKET_READONLY_V1_PACKETIZED",
  - L78 `readonly` — "readonly_analysis_only": True,
- `periphery/brody_memory_readonly/brody_human_command_packet_readonly/smoke_brody_human_command_packet_readonly_v1.py`
  - L1 `readonly` — from brody_human_command_packet_readonly_v1 import build_human_command_packet
  - L11 `readonly` — "rollback_note": "No rollback needed; readonly verification.",
  - L39 `READONLY` — assert out["status"] == "BRODY_HUMAN_COMMAND_PACKET_READONLY_V1_PACKETIZED"
  - L45 `readonly` — assert out["readonly_analysis_only"] is True
  - L50 `graphiti` — assert out["graphiti_write"] is False
  - L50 `graphiti_write` — assert out["graphiti_write"] is False
  - L51 `graphiti` — assert out["graphiti_index_write"] is False
  - L52 `neo4j` — assert out["neo4j_write_executed"] is False
- `periphery/brody_memory_readonly/brody_human_output_receipt_validator_readonly/brody_human_output_receipt_validator_readonly_v1.py`
  - L8 `frozen` — @dataclass(frozen=True)
  - L21 `frozen` — @dataclass(frozen=True)
  - L37 `readonly` — readonly_analysis_only: bool
  - L44 `graphiti` — graphiti_write: bool
  - L44 `graphiti_write` — graphiti_write: bool
  - L45 `graphiti` — graphiti_index_write: bool
  - L46 `neo4j` — neo4j_write_executed: bool
  - L46 `neo4j_write` — neo4j_write_executed: bool
- `periphery/brody_memory_readonly/brody_human_output_receipt_validator_readonly/smoke_brody_human_output_receipt_validator_readonly_v1.py`
  - L1 `readonly` — from brody_human_output_receipt_validator_readonly_v1 import validate_human_output_receipt
  - L12 `READONLY` — "expected_status": "BRODY_HUMAN_OUTPUT_RECEIPT_VALIDATOR_READONLY_V1_WAITING_FOR_HUMAN_OUTPUT",
  - L29 `READONLY` — "expected_status": "BRODY_HUMAN_OUTPUT_RECEIPT_VALIDATOR_READONLY_V1_PASS",
  - L46 `READONLY` — "expected_status": "BRODY_HUMAN_OUTPUT_RECEIPT_VALIDATOR_READONLY_V1_REVIEW_REQUIRED",
  - L63 `READONLY` — "expected_status": "BRODY_HUMAN_OUTPUT_RECEIPT_VALIDATOR_READONLY_V1_REVIEW_REQUIRED",
  - L79 `readonly` — assert out["readonly_analysis_only"] is True
  - L85 `graphiti` — assert out["graphiti_write"] is False
  - L85 `graphiti_write` — assert out["graphiti_write"] is False
- `periphery/brody_memory_readonly/brody_local_command_gate_readonly/brody_local_command_gate_readonly_v1.py`
  - L9 `frozen` — @dataclass(frozen=True)
  - L17 `frozen` — @dataclass(frozen=True)
  - L27 `readonly` — readonly_analysis_only: bool
  - L32 `graphiti` — graphiti_write: bool
  - L32 `graphiti_write` — graphiti_write: bool
  - L51 `Graphiti` — It never authorizes Brody to decide, ACT, mutate X108, write Graphiti,
  - L55 `KX108_ONLY` — decision_authority = "KX108_ONLY"
  - L97 `readonly` — readonly_patterns = [
- `periphery/brody_memory_readonly/brody_local_command_gate_readonly/smoke_brody_local_command_gate_readonly_v1.py`
  - L1 `readonly` — from brody_local_command_gate_readonly_v1 import evaluate_command
  - L48 `KX108_ONLY` — assert out["decision_authority"] == "KX108_ONLY", (case["name"], out)
  - L55 `READONLY` — print("BRODY_LOCAL_COMMAND_GATE_READONLY_V1_SMOKE_PASS")
- `periphery/brody_memory_readonly/brody_taxonomy_mapper_34_8_readonly_v1_6_4d.py`
  - L21 `KX108_ONLY` — decision_authority: str = "KX108_ONLY"
  - L58 `KX108_ONLY` — decision_authority="KX108_ONLY"

## Gaps

- None.

## Danger records

- `periphery/brody_memory_readonly/graphiti_guarded_manual_apply_from_review_decision_readonly_memory_only/brody_graphiti_guarded_manual_apply_from_review_decision_readonly_memory_only_v1.py`
  - L174 `MERGE ` — MERGE (d:Document {id: $id})
- `periphery/brody_memory_readonly/graphiti_import_apply_guarded_manual_only/brody_graphiti_import_apply_guarded_manual_only_v1.py`
  - L256 `MERGE ` — MERGE (d:BrodyMemoryDoc {id: $id})
  - L257 `SET ` — SET d.title = $title,
- `periphery/brody_memory_readonly/graphiti_import_dry_run_from_post_human_prep_readonly/brody_graphiti_import_dry_run_from_post_human_prep_readonly_v1.py`
  - L137 `MERGE ` — "cypher_preview": "MERGE (d:Doc {id: $id}) SET d.title = $title, d.content = $content, d.source = $source",
  - L137 `SET ` — "cypher_preview": "MERGE (d:Doc {id: $id}) SET d.title = $title, d.content = $content, d.source = $source",
- `periphery/brody_memory_readonly/neo4j_brody_guide_bridge_readonly/brody_neo4j_guide_bridge_readonly_v1.py`
  - L115 `MERGE ` — MERGE (d:BrodyMemoryDoc {id: doc.id})
  - L116 `SET ` — SET d.title = doc.title,
  - L126 `MERGE ` — MERGE (t:BrodyMemoryTag {name: tag})
  - L127 `MERGE ` — MERGE (d)-[:HAS_TAG]->(t)
  - L137 `CREATE ` — session.run("CREATE CONSTRAINT brody_memory_doc_id IF NOT EXISTS FOR (d:BrodyMemoryDoc) REQUIRE d.id IS UNIQUE")
  - L138 `CREATE ` — session.run("CREATE CONSTRAINT brody_memory_tag_name IF NOT EXISTS FOR (t:BrodyMemoryTag) REQUIRE t.name IS UNIQUE")
- `scripts/brody_memory_intake_gate.py`
  - L225 `DELETE ` — "// MATCH (n:BrodyImportedMemory {batch_id: 'brody-terminal-" + ts + "'}) DETACH DELETE n;",
- `scripts/f23a1_memory_reflex_orchestrator_source_audit.py`
  - L42 `write_transaction` — "session.write_transaction",
  - L42 `session.write_transaction` — "session.write_transaction",
  - L43 `execute_write` — "execute_write",
  - L44 `MERGE ` — "MERGE ",
  - L45 `CREATE ` — "CREATE ",
  - L46 `SET ` — "SET ",
  - L47 `DELETE ` — "DELETE ",
- `scripts/f29_0_memory_graphiti_reconciliation_audit.py`
  - L59 `memory_write=True` — "memory_write=True",
  - L60 `graphiti_write=True` — "graphiti_write=True",
  - L61 `neo4j_write=True` — "neo4j_write=True",
  - L62 `kernel_mutation=True` — "kernel_mutation=True",
  - L63 `x108_mutation=True` — "x108_mutation=True",
  - L64 `emits_act=True` — "emits_act=True",
  - L65 `can_emit_act=True` — "can_emit_act=True",
  - L66 `runtime_execute=True` — "runtime_execute=True",
  - L67 `write_transaction` — "write_transaction",
  - L68 `execute_write` — "execute_write",
  - L69 `write_transaction` — "session.write_transaction",
  - L69 `session.write_transaction` — "session.write_transaction",

## Boundary

```text
DECISION_AUTHORITY=KX108_ONLY
readonly=true
advisory_only=true
context_signal_only=true
memory_write=false
graphiti_write=false
neo4j_write=false
emits_act=false
runtime_execute=false
kernel_mutation=false
x108_mutation=false
```

## Next

F29.1_MEMORY_GRAPHITI_READONLY_RECONCILIATION_PATCH_IF_GAPS

## Status

F29_0_MEMORY_GRAPHITI_RECONCILIATION_AUDIT_DONE

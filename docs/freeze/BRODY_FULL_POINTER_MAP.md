# Brody Full Pointer Map

**Date:** 2026-05-19
**Status:** BRODY_FULL_POINTER_MAP_PASS

---

## Summary

| Metric | Value |
|--------|-------|
| Pointer files (CURRENT_BRODY_*.txt) | 91 |
| Python runtimes in brody_memory_readonly/ | 46 |
| All DECISION_AUTHORITY | KX108_ONLY |
| Core modules wired | 4 of 4 |
| Graphiti live | **BLOCKED** — NEO4J_PASSWORD not set, port 7688 closed |
| ObsidiaShell 8011 | **OFFLINE** |
| API bridge modules | Pointers exist, runtimes not wired |

---

## Core 4 Modules — WIRED

| Module | Runtime | Status |
|--------|---------|--------|
| Terminal Structural Dialogue | `terminal_structural_dialogue_readonly_v1.py` (9811 B) | WIRED — `run_once()`, `build_response()` |
| Local Response Engine | `local_response_engine_readonly_v1.py` (7862 B) | WIRED — `build_response()` |
| Context Packet Query | `context_packet_query_readonly_v1.py` (6665 B) | WIRED — `query_neo4j()` (offline) |
| Content Hydration | `content_hydration_readonly_v1.py` (13537 B) | READY — `hydrate_packet()` |

## Graphiti / Neo4j

| Check | Result |
|-------|--------|
| NEO4J_URI | NOT SET |
| NEO4J_USER | NOT SET |
| NEO4J_PASSWORD | NOT SET |
| Port 7688 (Neo4j Bolt) | CLOSED |
| Port 8011 (ObsidiaShell) | CLOSED |
| neo4j python driver | INSTALLED |

**Status:** GRAPHITI_LIVE_BLOCKED — Missing credentials and server.

To enable: set `NEO4J_URI`, `NEO4J_PASSWORD`, start Neo4j server, or start ObsidiaShell on 8011.

## Memory / Session Modules — AVAILABLE

| Module | Runtime |
|--------|---------|
| Session Memory Ledger | `session_memory_ledger_readonly_v2.py` (7941 B) |
| Session Presave Buffer | `session_presave_buffer_readonly_v1.py` (7406 B) |
| Memory Scheduler | `memory_scheduler_readonly_v1.py` (14697 B) |
| Project Intake Buffer | `project_intake_capture_buffer_readonly_v1.py` (9254 B) |
| Memory Pipeline Freeze V2 | `memory_pipeline_freeze_v2_readonly.py` (16192 B) |
| Auto Triage Memory Intake | `auto_triage_memory_intake_readonly_v1.py` (13604 B) |
| Post-Human Review Triage | `post_human_review_memory_triage_readonly_v1.py` (11539 B) |

## Graphiti Manual-Apply Chain — AVAILABLE

| Module | Runtime |
|--------|---------|
| Candidate Prep | `graphiti_candidate_prep_from_post_human_triage_readonly_v1.py` (9147 B) |
| Import Dry-Run | `graphiti_import_dry_run_from_post_human_prep_readonly_v1.py` (9519 B) |
| Review Gate | `graphiti_review_gate_from_post_human_dry_run_readonly_v1.py` (11065 B) |
| Review Decision Apply | `graphiti_review_decision_apply_readonly_v1.py` (11467 B) |
| Guarded Manual Apply | `graphiti_guarded_manual_apply_from_review_decision_readonly_memory_only_v1.py` (10892 B) |
| Import Apply Guarded | `graphiti_import_apply_guarded_manual_only_v1.py` (12191 B) |

**All require Graphiti/Neo4j live → currently BLOCKED.**

# OBSIDIA F23A4.0 — REFLEX DIAGNOSTIC PACKET SOURCE AUDIT

Date: 20260528_085837
Mode: SOURCE_AUDIT_DESIGN_NO_PATCH
Patch: NO
Commit: NO

## Git

- HEAD: 562c9f9
- TAG: BRODY_F23A3_DOC_CLEANUP_20260528
```text
## main...origin/main
?? scripts/f23a4_0_reflex_diagnostic_packet_source_audit.py
```

## Compile

- compile_ok: True

## Existing source targets

### apps/obsidia_api/brody_automation_orchestrator.py
- exists: True
- has_kx108: True
- has_readonly: True
- has_write_boundary: True
- has_mutation_boundary: True
- forbidden_hits: []
  - L2 [readonly] Brody Automation Layer Orchestrator — Readonly
  - L9 [Graphiti]   - Never writes Graphiti or Neo4j
  - L11 [operator]   - Never calls operators or executes commands
  - L12 [port]   - Imports existing module logic — no subprocess invocation
  - L16 [readonly]   readonly=True, memory_write=False, graphiti_write=False,
  - L17 [KX108_ONLY]   neo4j_write=False, emits_act=False, decision_authority=KX108_ONLY
  - L19 [port] from __future__ import annotations
  - L21 [port] import sys

### apps/obsidia_api/brody_memory_promotion_guard.py
- exists: True
- has_kx108: True
- has_readonly: True
- has_write_boundary: True
- has_mutation_boundary: True
- forbidden_hits: []
  - L1 [port] ﻿from __future__ import annotations
  - L3 [port] from typing import Any
  - L7 [KX108_ONLY]     "decision_authority": "KX108_ONLY",
  - L9 [readonly]     "readonly": True,
  - L11 [emits_act]     "emits_act": False,
  - L12 [emits_verdict]     "emits_verdict": False,
  - L13 [memory_write]     "memory_write": False,
  - L14 [Graphiti]     "graphiti_write": False,

### apps/obsidia_api/brody_candidate_memory_adapter.py
- exists: True
- has_kx108: True
- has_readonly: True
- has_write_boundary: True
- has_mutation_boundary: False
- forbidden_hits: []
  - L2 [candidate] Brody Candidate Memory Snapshot Adapter
  - L4 [candidate] Wraps existing freeze-sourced modules into a candidate_memory_snapshot.
  - L7 [readonly]   - session_presave_buffer_readonly V1
  - L8 [readonly]   - auto_triage_memory_intake_readonly V1
  - L9 [readonly]   - graphiti_candidate_review_gate_readonly V1
  - L10 [candidate]   - memory_candidate_ledger (JSONL)
  - L12 [port] No invention — reports what exists in freeze files and ledgers.
  - L13 [candidate] All writes disabled: CANDIDATE_ONLY, memory_write=false.

### apps/obsidia_api/brody_runtime_context_adapter.py
- exists: True
- has_kx108: True
- has_readonly: True
- has_write_boundary: True
- has_mutation_boundary: True
- forbidden_hits: []
  - L10 [readonly] Boundary: readonly, KX108_ONLY.
  - L12 [port] from __future__ import annotations
  - L14 [port] from datetime import datetime, timezone
  - L15 [port] from typing import Any
  - L23 [readonly]     "readonly": True,
  - L24 [memory_write]     "memory_write": False,
  - L25 [Graphiti]     "graphiti_write": False,
  - L26 [Neo4j]     "neo4j_write": False,

### apps/obsidia_api/brody_temporal_context_adapter.py
- exists: True
- has_kx108: True
- has_readonly: True
- has_write_boundary: True
- has_mutation_boundary: True
- forbidden_hits: []
  - L7 [candidate]   - Candidate memory + AVDR phase (future)
  - L11 [readonly] Boundary: readonly, KX108_ONLY.
  - L13 [port] from __future__ import annotations
  - L15 [port] from datetime import datetime, timezone
  - L16 [port] from pathlib import Path
  - L17 [port] from typing import Any
  - L27 [candidate]     candidate_memory: dict[str, Any] | None = None,
  - L35 [candidate]     cm = candidate_memory or {}

### apps/obsidia_api/brody_operator_view_packet.py
- exists: True
- has_kx108: True
- has_readonly: True
- has_write_boundary: True
- has_mutation_boundary: True
- forbidden_hits: []
  - L1 [port] ﻿from __future__ import annotations
  - L3 [port] from typing import Any
  - L7 [KX108_ONLY]     "decision_authority": "KX108_ONLY",
  - L9 [readonly]     "readonly": True,
  - L11 [emits_act]     "emits_act": False,
  - L12 [emits_verdict]     "emits_verdict": False,
  - L13 [memory_write]     "memory_write": False,
  - L14 [Graphiti]     "graphiti_write": False,

### apps/obsidia_api/brody_operator_loop_adapter.py
- exists: True
- has_kx108: True
- has_readonly: True
- has_write_boundary: True
- has_mutation_boundary: False
- forbidden_hits: []
  - L2 [operator] Brody Operator Loop Snapshot Adapter
  - L4 [operator] Wraps freeze-sourced operator loop modules into an operator_loop_snapshot.
  - L6 [operator] Sources: CURRENT_BRODY_OPERATOR_*.txt freeze pointers.
  - L7 [KX108_ONLY] All 7 components freeze-sourced, V1_PASS, KX108_ONLY.
  - L9 [readonly] Boundary: readonly, Brody cannot execute, human operates, X108 decides.
  - L11 [port] from __future__ import annotations
  - L13 [port] from datetime import datetime, timezone
  - L14 [port] from pathlib import Path

### apps/obsidia_api/brody_domain_raccord_adapter.py
- exists: True
- has_kx108: True
- has_readonly: True
- has_write_boundary: True
- has_mutation_boundary: True
- forbidden_hits: []
  - L5 [readonly] Readonly/advisory raccord between already-present Obsidia domains and
  - L8 [Graphiti] It does not decide, act, write memory, write Graphiti, write Neo4j,
  - L11 [port] from __future__ import annotations
  - L13 [port] from typing import Any
  - L14 [port] import re
  - L15 [port] import unicodedata
  - L19 [readonly]     "readonly": True,
  - L24 [memory_write]     "memory_write": False,

### apps/obsidia_api/brody_contracts_packet.py
- exists: True
- has_kx108: True
- has_readonly: True
- has_write_boundary: True
- has_mutation_boundary: True
- forbidden_hits: []
  - L5 [Graphiti] This module does not decide, act, write memory, write Graphiti, mutate the
  - L9 [port] from __future__ import annotations
  - L11 [port] from typing import Any
  - L13 [port] from apps.obsidia_api.brody_rights_authority_matrix import (
  - L20 [readonly]     "readonly": True,
  - L25 [emits_act]     "emits_act": False,
  - L26 [emits_verdict]     "emits_verdict": False,
  - L27 [memory_write]     "memory_write": False,

## Proposed minimal packet design

- candidate_file: `apps/obsidia_api/brody_reflex_diagnostic_packet.py`
- test_file: `tests/api/test_f23a4_reflex_diagnostic_packet.py`
- function: `build_reflex_diagnostic_packet`
- mode: READONLY_ADVISORY_DIAGNOSTIC

### Recognized patterns
- PORT_UNAVAILABLE
- GRAPHITI_UNAVAILABLE
- NEO4J_MAPPING_MISMATCH
- READ_WRITE_CONFUSION
- STALE_SERVER
- UI_BACKEND_MISMATCH
- MEMORY_MATERIAL_LOW
- ACTION_REQUEST_DISGUISED_AS_REFLEX

### Required boundaries
- decision_authority: KX108_ONLY
- readonly: True
- advisory_only: True
- memory_write: False
- graphiti_write: False
- neo4j_write: False
- automation_execute: False
- kernel_mutation: False
- x108_mutation: False
- emits_act: False
- emits_verdict: False

## Status

F23A4_0_REFLEX_DIAGNOSTIC_PACKET_SOURCE_AUDIT_DONE
PATCH=NO
COMMIT=NO
NEXT=F23A4_1_REFLEX_DIAGNOSTIC_PACKET_MINIMAL_PATCH
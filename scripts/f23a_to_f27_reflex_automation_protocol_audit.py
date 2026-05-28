"""F23A→F27 — Memory Reflex / Automation / Dormant Protocol Audit.

Audit scope:
  F23A  Memory Reflex / Automation / Dormant Protocol
  F23B  Memory Reflex Context Pack Readiness
  F23C  Automation Boundary Contract
  F24   Clavage / Agent Vecteur Minimal
  F25   Harmonic Vote / Veto Scoring
  F26   Continuum / Zone Latente
  F27   Shazam Cognitif / Style Intent

Mode:  READ_ONLY — no patch, no commit, no runtime change.
Constraint: KX108_ONLY / readonly / emits_act=False / emits_verdict=False
            memory_write=False / graphiti_write=False
            kernel_mutation=False / x108_mutation=False

Run:
    python scripts/f23a_to_f27_reflex_automation_protocol_audit.py

Outputs written to docs/runtime/:
    OBSIDIA_F23A_TO_F27_REFLEX_AUTOMATION_PROTOCOL_AUDIT_<timestamp>.md
    OBSIDIA_F23A_TO_F27_REFLEX_AUTOMATION_PROTOCOL_AUDIT_<timestamp>.json
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
import subprocess

def _git(cmd: list[str]) -> str:
    try:
        return subprocess.check_output(cmd, text=True, encoding="utf-8", errors="replace").strip()
    except Exception:
        return ""

CURRENT_HEAD = _git(["git", "rev-parse", "--short", "HEAD"])
CURRENT_TAG = _git(["git", "tag", "--points-at", "HEAD"]) or "NO_TAG_ON_HEAD"
CURRENT_STATUS = _git(["git", "status", "-sb"])


# ── Repo root ──────────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_RUNTIME = REPO_ROOT / "docs" / "runtime"
DOCS_RUNTIME.mkdir(parents=True, exist_ok=True)

TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
REPORT_STEM = f"OBSIDIA_F23A_TO_F27_REFLEX_AUTOMATION_PROTOCOL_AUDIT_{TIMESTAMP}"

HEAD_COMMIT = CURRENT_HEAD
HEAD_TAG = CURRENT_TAG

# ── Status taxonomy ────────────────────────────────────────────────────────────

S_CONNECTED = "CODE_RUNTIME_CONNECTED"
S_DORMANT   = "CODE_DORMANT"
S_STUB      = "CODE_STUB"
S_DOC_ONLY  = "DOC_ONLY"
S_MISSING   = "MISSING"
S_ALIAS     = "FOUND_UNDER_OTHER_NAME"

# ── CONCEPT MATRIX ─────────────────────────────────────────────────────────────

CONCEPT_MATRIX: list[dict] = [

    # ── F23A — Memory Reflex / Automation / Dormant Protocol ──────────────────

    {
        "area": "F23A",
        "concept": "reflex_reducer",
        "canonical_file": "periphery/reflex_reducer.py",
        "mmonde_file": "periphery/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/03_MEMOIRE_MONDE_COSMOS_REFLEX/reflex_reducer.py",
        "status": S_DORMANT,
        "active": False,
        "wired_to_runtime": False,
        "notes": "Real code — RefexReducer class with reduce_reflex() method. Not imported by any API route or brody adapter.",
    },
    {
        "area": "F23A",
        "concept": "avdr_core",
        "canonical_file": "periphery/avdr.py",
        "mmonde_file": "periphery/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/12_FRICTION_AVDR_CONTINUUM/avdr.py",
        "status": S_DORMANT,
        "active": False,
        "wired_to_runtime": False,
        "notes": "AVDR logic present. MMONDE version is CODE_STUB. avdr_phase_mapper.py has active=False in _FUTURE_MODULES.",
    },
    {
        "area": "F23A",
        "concept": "avdr_phase_mapper",
        "canonical_file": "periphery/gencoin_sandbox/avdr_phase_mapper.py",
        "mmonde_file": None,
        "status": S_DORMANT,
        "active": False,
        "wired_to_runtime": False,
        "notes": "Explicitly marked active=False in _FUTURE_MODULES registry. Dormant by design.",
    },
    {
        "area": "F23A",
        "concept": "brody_memory_readonly_pipeline",
        "canonical_file": "periphery/brody_memory_readonly/",
        "mmonde_file": None,
        "status": S_DORMANT,
        "active": False,
        "wired_to_runtime": False,
        "notes": "Multiple files: auto_triage, graphiti_bridge, graphiti_import_apply, memory_pipeline_freeze. Present but not wired to active brody routes.",
    },
    {
        "area": "F23A",
        "concept": "brody_automation_orchestrator",
        "canonical_file": "apps/obsidia_api/brody_automation_orchestrator.py",
        "mmonde_file": None,
        "status": S_DORMANT,
        "active": False,
        "wired_to_runtime": False,
        "notes": "Orchestrator module exists. Not imported by main.py or active routes.",
    },
    {
        "area": "F23A",
        "concept": "brody_memory_promotion_guard",
        "canonical_file": "apps/obsidia_api/brody_memory_promotion_guard.py",
        "mmonde_file": None,
        "status": S_CONNECTED,
        "active": True,
        "wired_to_runtime": True,
        "notes": "Active guard — prevents unauthorized memory promotion. Wired into brody.py route pipeline.",
    },
    {
        "area": "F23A",
        "concept": "readonly_context_ingress",
        "canonical_file": "periphery/x108_ingress/readonly_context_ingress.py",
        "mmonde_file": None,
        "status": S_DORMANT,
        "active": False,
        "wired_to_runtime": False,
        "notes": "X108 ingress point for readonly context. Module exists but ingress not active in current runtime.",
    },

    # ── F23B — Memory Reflex Context Pack Readiness ────────────────────────────

    {
        "area": "F23B",
        "concept": "context_packet_builder",
        "canonical_file": "periphery/context/context_packet_builder.py",
        "mmonde_file": None,
        "status": S_CONNECTED,
        "active": True,
        "wired_to_runtime": True,
        "notes": "Real builder. Used by brody context pipeline.",
    },
    {
        "area": "F23B",
        "concept": "context_packet_builder_v2",
        "canonical_file": "periphery/context/context_packet_builder_v2.py",
        "mmonde_file": None,
        "status": S_CONNECTED,
        "active": True,
        "wired_to_runtime": True,
        "notes": "V2 builder — extended schema, backward compatible with v1.",
    },
    {
        "area": "F23B",
        "concept": "context_packet_validator",
        "canonical_file": "periphery/context/context_packet_validator.py",
        "mmonde_file": None,
        "status": S_CONNECTED,
        "active": True,
        "wired_to_runtime": True,
        "notes": "Validates context packets before brody processing.",
    },
    {
        "area": "F23B",
        "concept": "context_packet_exporter",
        "canonical_file": "periphery/context/context_packet_exporter.py",
        "mmonde_file": None,
        "status": S_CONNECTED,
        "active": True,
        "wired_to_runtime": True,
        "notes": "Exports context packets for downstream consumers.",
    },
    {
        "area": "F23B",
        "concept": "context_packet_sanitizer",
        "canonical_file": "periphery/context/context_packet_sanitizer.py",
        "mmonde_file": None,
        "status": S_CONNECTED,
        "active": True,
        "wired_to_runtime": True,
        "notes": "Sanitizes PII and sensitive fields before packet exposure.",
    },
    {
        "area": "F23B",
        "concept": "memory_source_registry",
        "canonical_file": "periphery/memory/memory_source_registry.py",
        "mmonde_file": None,
        "status": S_CONNECTED,
        "active": True,
        "wired_to_runtime": True,
        "notes": "Registry mapping memory sources to context packet slots.",
    },
    {
        "area": "F23B",
        "concept": "brody_memory_response_chain_adapter",
        "canonical_file": "apps/obsidia_api/brody_memory_response_chain_adapter.py",
        "mmonde_file": None,
        "status": S_CONNECTED,
        "active": True,
        "wired_to_runtime": True,
        "notes": "Chains memory context into brody response. CODE_RUNTIME_CONNECTED.",
    },

    # ── F23C — Automation Boundary Contract ────────────────────────────────────

    {
        "area": "F23C",
        "concept": "worldcalls_route",
        "canonical_file": "apps/obsidia_api/routes/worldcalls.py",
        "mmonde_file": None,
        "status": S_CONNECTED,
        "active": True,
        "wired_to_runtime": True,
        "notes": "World action bus route. Has boundary guard preventing unauthorized write actions.",
    },
    {
        "area": "F23C",
        "concept": "os3_route",
        "canonical_file": "apps/obsidia_api/routes/os3.py",
        "mmonde_file": None,
        "status": S_CONNECTED,
        "active": True,
        "wired_to_runtime": True,
        "notes": "OS3 sovereign ticket route. Boundary: KX108_ONLY, emits_act=False.",
    },
    {
        "area": "F23C",
        "concept": "brody_contracts_packet",
        "canonical_file": "apps/obsidia_api/brody_contracts_packet.py",
        "mmonde_file": None,
        "status": S_CONNECTED,
        "active": True,
        "wired_to_runtime": True,
        "notes": "Contract enforcement packet for brody responses.",
    },
    {
        "area": "F23C",
        "concept": "brody_adaptive_response_policy",
        "canonical_file": "apps/obsidia_api/brody_adaptive_response_policy.py",
        "mmonde_file": None,
        "status": S_CONNECTED,
        "active": True,
        "wired_to_runtime": True,
        "notes": "Adaptive policy — controls response mode under boundary constraints.",
    },
    {
        "area": "F23C",
        "concept": "graphiti_v20_readonly_client",
        "canonical_file": "apps/obsidia_api/graphiti_v20_readonly_client.py",
        "mmonde_file": None,
        "status": S_CONNECTED,
        "active": True,
        "wired_to_runtime": True,
        "notes": "Graphiti V20 readonly client — enforces no-write boundary at client level.",
    },

    # ── F24 — Clavage / Agent Vecteur Minimal ─────────────────────────────────

    {
        "area": "F24",
        "concept": "cosine_similarity",
        "canonical_file": "periphery/cosine_similarity.py",
        "mmonde_file": "periphery/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/05_SHAZAM_COGNITIF/cosine_similarity.py",
        "status": S_DORMANT,
        "active": False,
        "wired_to_runtime": False,
        "notes": "Pure math helper — cosine similarity. Not connected to any Clavage runtime pipeline. Required by Clavage but Clavage itself not implemented.",
    },
    {
        "area": "F24",
        "concept": "clavage_core",
        "canonical_file": None,
        "mmonde_file": None,
        "status": S_DOC_ONLY,
        "active": False,
        "wired_to_runtime": False,
        "notes": "No clavage.py found. No agent_vecteur.py found. No CognitiveDeviationError or strict_parser. Clavage is DOC_ONLY — requires JAX/XLA, full ML pipeline (200+ lines). Deferred post-F22B per F22B decision record.",
    },
    {
        "area": "F24",
        "concept": "agent_vecteur",
        "canonical_file": None,
        "mmonde_file": None,
        "status": S_DOC_ONLY,
        "active": False,
        "wired_to_runtime": False,
        "notes": "Agent Vecteur Minimal: no standalone implementation found. Conceptual agent described in doctrinal docs only.",
    },
    {
        "area": "F24",
        "concept": "sigma_contracts_broken_ragnarok",
        "canonical_file": "sigma/contracts.broken-ragnarok.py",
        "mmonde_file": None,
        "status": "HISTORY_ONLY",
        "active": False,
        "wired_to_runtime": False,
        "notes": "Contains clavage reference. Historical artifact — .broken-ragnarok suffix marks it intentionally disabled.",
    },

    # ── F25 — Harmonic Vote / Veto Scoring ────────────────────────────────────

    {
        "area": "F25",
        "concept": "sigma_contracts_agent_vote",
        "canonical_file": "sigma/contracts.py",
        "mmonde_file": None,
        "status": S_CONNECTED,
        "active": True,
        "wired_to_runtime": True,
        "notes": "AgentVote.vote (HOLD/ALLOW/BLOCK) structure. readiness_scope='harmonic_integrity_governance'. No calculate_immutable_vote() — harmonic scoring partial only.",
    },
    {
        "area": "F25",
        "concept": "sigma_aggregation",
        "canonical_file": "sigma/aggregation.py",
        "mmonde_file": None,
        "status": S_CONNECTED,
        "active": True,
        "wired_to_runtime": True,
        "notes": "Aggregation logic for sigma votes. Active in CI pipeline.",
    },
    {
        "area": "F25",
        "concept": "brody_thermo_coherence_time_unified",
        "canonical_file": "apps/obsidia_api/brody_thermo_coherence_time_unified.py",
        "mmonde_file": None,
        "status": S_CONNECTED,
        "active": True,
        "wired_to_runtime": True,
        "notes": "Unified scoring for thermo coherence time. Emits coherence_score, not harmonic_vote directly.",
    },
    {
        "area": "F25",
        "concept": "brody_anti_mismatch_signal",
        "canonical_file": "apps/obsidia_api/brody_anti_mismatch_signal.py",
        "mmonde_file": None,
        "status": S_CONNECTED,
        "active": True,
        "wired_to_runtime": True,
        "notes": "truth_score signal — adjacent to harmonic vote concept. Active.",
    },
    {
        "area": "F25",
        "concept": "regime_metrics",
        "canonical_file": "periphery/gencoin_sandbox/regime_metrics.py",
        "mmonde_file": None,
        "status": S_DORMANT,
        "active": False,
        "wired_to_runtime": False,
        "notes": "Scoring in gencoin sandbox — active=False in FUTURE_MODULES.",
    },
    {
        "area": "F25",
        "concept": "regime_truth_gate",
        "canonical_file": "periphery/gencoin_sandbox/regime_truth_gate.py",
        "mmonde_file": None,
        "status": S_DORMANT,
        "active": False,
        "wired_to_runtime": False,
        "notes": "Truth gate for regime scoring — dormant alongside regime_metrics.",
    },
    {
        "area": "F25",
        "concept": "calculate_immutable_vote",
        "canonical_file": None,
        "mmonde_file": None,
        "status": S_MISSING,
        "active": False,
        "wired_to_runtime": False,
        "notes": "calculate_immutable_vote() function — NOT found in sigma/contracts.py or anywhere in repo. Harmonic vote calculation is partial; function missing.",
    },

    # ── F26 — Continuum / Zone Latente ────────────────────────────────────────

    {
        "area": "F26",
        "concept": "continuum_node",
        "canonical_file": "periphery/continuum_node.py",
        "mmonde_file": "periphery/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/03_MEMOIRE_MONDE_COSMOS_REFLEX/continuum_node.py",
        "status": S_STUB,
        "active": False,
        "wired_to_runtime": False,
        "notes": "NodeContinuum dataclass — real structure, not wired to runtime. Covered by session_memory_snapshot + temporal_context_snapshot per cognitive module registry (COVERED_BY_EXISTING_MODULE, active=True). No branching needed for intent classification.",
    },
    {
        "area": "F26",
        "concept": "zone_latente",
        "canonical_file": None,
        "mmonde_file": None,
        "status": S_DOC_ONLY,
        "active": False,
        "wired_to_runtime": False,
        "notes": "Zone Latente: doctrinal concept only. No standalone zone_latente.py found. Conceptually covered by continuum_node dormant state.",
    },
    {
        "area": "F26",
        "concept": "common_types_continuum",
        "canonical_file": "periphery/common_types.py",
        "mmonde_file": None,
        "status": S_CONNECTED,
        "active": True,
        "wired_to_runtime": True,
        "notes": "common_types.py contains type definitions referenced by continuum structures. Active as shared type module.",
    },

    # ── F27 — Shazam Cognitif / Style Intent ──────────────────────────────────

    {
        "area": "F27",
        "concept": "shazam_cognitif_core",
        "canonical_file": "periphery/shazam_cognitif.py",
        "mmonde_file": "periphery/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/05_SHAZAM_COGNITIF/shazam_cognitif.py",
        "status": S_DORMANT,
        "active": False,
        "wired_to_runtime": False,
        "notes": "BLOCKED by missing dependency: 'from spectral_hash import extract_features' — spectral_hash is not installed. Code exists but cannot be imported. ImportError on startup if wired.",
    },
    {
        "area": "F27",
        "concept": "shazam_cognitif_cognitive_trees",
        "canonical_file": "periphery/cognitive_trees/shazam_cognitif.py",
        "mmonde_file": None,
        "status": S_DORMANT,
        "active": False,
        "wired_to_runtime": False,
        "notes": "Same module under cognitive_trees/ path. Same spectral_hash blocking dependency.",
    },
    {
        "area": "F27",
        "concept": "no_shazam_act",
        "canonical_file": "periphery/no_shazam_act.py",
        "mmonde_file": None,
        "status": S_CONNECTED,
        "active": True,
        "wired_to_runtime": True,
        "notes": "Guard preventing Shazam from triggering ACT tokens. Active — enforces doctrinal 'Shazam is context-only, never action' constraint.",
    },
    {
        "area": "F27",
        "concept": "shazam_cognitif_test",
        "canonical_file": "tests/periphery/test_shazam_cognitif_context_only.py",
        "mmonde_file": None,
        "status": S_CONNECTED,
        "active": True,
        "wired_to_runtime": False,
        "notes": "Test confirming context-only constraint. Passes with spectral_hash mocked. Validates no_shazam_act guard.",
    },
    {
        "area": "F27",
        "concept": "brody_tree_signal_packet",
        "canonical_file": "apps/obsidia_api/brody_tree_signal_packet.py",
        "mmonde_file": None,
        "status": S_CONNECTED,
        "active": True,
        "wired_to_runtime": True,
        "notes": "Tree signal packet — adjacent to Shazam concept (cognitive style intent). Active in brody runtime. Does NOT require spectral_hash.",
    },
]


# ── Summary counters ───────────────────────────────────────────────────────────

def _count_by(matrix: list[dict], field: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in matrix:
        val = row.get(field, "UNKNOWN")
        counts[val] = counts.get(val, 0) + 1
    return counts


def _area_summary(matrix: list[dict]) -> dict[str, dict]:
    areas: dict[str, dict] = {}
    for row in matrix:
        area = row["area"]
        if area not in areas:
            areas[area] = {"total": 0, "connected": 0, "dormant": 0, "stub": 0, "doc_only": 0, "missing": 0, "history_only": 0}
        areas[area]["total"] += 1
        s = row["status"]
        if s == S_CONNECTED:
            areas[area]["connected"] += 1
        elif s == S_DORMANT:
            areas[area]["dormant"] += 1
        elif s == S_STUB:
            areas[area]["stub"] += 1
        elif s == S_DOC_ONLY:
            areas[area]["doc_only"] += 1
        elif s == S_MISSING:
            areas[area]["missing"] += 1
        elif s == "HISTORY_ONLY":
            areas[area]["history_only"] += 1
    return areas


# ── Cross-dependency map ───────────────────────────────────────────────────────

CROSS_DEPENDENCY_MAP: list[dict] = [
    {
        "from": "F23A/reflex_reducer",
        "to": "F23B/context_packet_builder",
        "type": "CONSUMES",
        "status": "DORMANT_LINK",
        "notes": "reflex_reducer would consume context packets to decide reduction — link dormant because reflex_reducer not wired.",
    },
    {
        "from": "F23B/context_packet_builder",
        "to": "F23C/brody_contracts_packet",
        "type": "FEEDS",
        "status": "ACTIVE",
        "notes": "Context packet output feeds into contracts packet for boundary enforcement.",
    },
    {
        "from": "F23C/worldcalls_route",
        "to": "F23A/brody_memory_promotion_guard",
        "type": "GUARDED_BY",
        "status": "ACTIVE",
        "notes": "World action bus calls checked by memory promotion guard before execution.",
    },
    {
        "from": "F24/cosine_similarity",
        "to": "F27/shazam_cognitif_core",
        "type": "REQUIRED_BY",
        "status": "DORMANT_LINK",
        "notes": "Clavage uses cosine_similarity; Shazam Cognitif is in same MMONDE module (05_SHAZAM_COGNITIF). Both dormant.",
    },
    {
        "from": "F25/sigma_contracts_agent_vote",
        "to": "F25/sigma_aggregation",
        "type": "CONSUMED_BY",
        "status": "ACTIVE",
        "notes": "AgentVote structs aggregated by sigma/aggregation.py in CI pipeline.",
    },
    {
        "from": "F26/continuum_node",
        "to": "F23A/reflex_reducer",
        "type": "DOCTRINAL_PAIR",
        "status": "BOTH_DORMANT",
        "notes": "Continuum and Reflex are paired doctrinal concepts (03_MEMOIRE_MONDE_COSMOS_REFLEX). Both dormant/stub.",
    },
    {
        "from": "F27/no_shazam_act",
        "to": "F23C/brody_adaptive_response_policy",
        "type": "ENFORCES",
        "status": "ACTIVE",
        "notes": "no_shazam_act guard enforces no-ACT boundary; adaptive response policy is the runtime enforcement surface.",
    },
    {
        "from": "F23A/avdr_core",
        "to": "F26/continuum_node",
        "type": "FRICTION_PAIR",
        "status": "BOTH_DORMANT",
        "notes": "AVDR and Continuum are paired in 12_FRICTION_AVDR_CONTINUUM. Both not wired to runtime.",
    },
]


# ── Recommended unblocking order ───────────────────────────────────────────────

RECOMMENDED_ORDER: list[dict] = [
    {
        "priority": 1,
        "area": "F23C",
        "rationale": "Already active. Audit only — validate boundary contract completeness. No patch needed.",
        "patch_candidate": False,
        "risk": "NONE",
    },
    {
        "priority": 2,
        "area": "F23B",
        "rationale": "Context pack family fully active. Audit complete — no gap found. Monitor for v2→v1 compatibility drift.",
        "patch_candidate": False,
        "risk": "NONE",
    },
    {
        "priority": 3,
        "area": "F25",
        "rationale": "Sigma vote structure present. Gap: calculate_immutable_vote() missing. Low-risk addition — sigma layer only.",
        "patch_candidate": True,
        "risk": "LOW",
        "patch_note": "Add calculate_immutable_vote() to sigma/contracts.py. Would complete harmonic vote scoring.",
    },
    {
        "priority": 4,
        "area": "F23A",
        "rationale": "brody_memory_promotion_guard is active. brody_automation_orchestrator + reflex_reducer dormant. Wire orchestrator first; reflex_reducer requires context pack integration.",
        "patch_candidate": True,
        "risk": "MEDIUM",
        "patch_note": "Wire brody_automation_orchestrator.py into a non-critical automation route. Requires explicit user validation.",
    },
    {
        "priority": 5,
        "area": "F27",
        "rationale": "Shazam Cognitif blocked by missing spectral_hash package. Unblocking requires pip install of spectral_hash (or stub). brody_tree_signal_packet is active and covers adjacent functionality.",
        "patch_candidate": True,
        "risk": "MEDIUM",
        "patch_note": "Install spectral_hash or write stub. Then wire shazam_cognitif.py under no_shazam_act guard.",
    },
    {
        "priority": 6,
        "area": "F26",
        "rationale": "Continuum is CODE_STUB. Covered by session_memory_snapshot. Not urgent — doctrinal coverage already satisfied.",
        "patch_candidate": False,
        "risk": "LOW",
        "patch_note": "Wire NodeContinuum to temporal_context_snapshot if needed. Low risk but low urgency.",
    },
    {
        "priority": 7,
        "area": "F24",
        "rationale": "Clavage requires JAX/XLA + full ML pipeline (200+ lines). DOC_ONLY status confirmed. Explicitly deferred post-F22B.",
        "patch_candidate": False,
        "risk": "HIGH",
        "patch_note": "DEFERRED. Do not implement until full ML environment validated and separate F-series approval received.",
    },
]


# ── Risk matrix ────────────────────────────────────────────────────────────────

RISK_MATRIX: list[dict] = [
    {
        "area": "F23A",
        "risk": "MEDIUM",
        "reason": "brody_automation_orchestrator not guarded by memory_promotion_guard when dormant. If accidentally imported, could bypass write boundary.",
        "mitigation": "Keep dormant until explicit wire approved. Confirm guard integration in any future wire commit.",
    },
    {
        "area": "F23B",
        "risk": "LOW",
        "reason": "context_packet_builder_v2 diverges from v1 schema. Risk of drift if downstream consumers not updated.",
        "mitigation": "Run context_packet_validator on both versions in CI.",
    },
    {
        "area": "F23C",
        "risk": "NONE",
        "reason": "All boundary guards active and tested.",
        "mitigation": "No mitigation needed. Monitor worldcalls.py for new route additions.",
    },
    {
        "area": "F24",
        "risk": "HIGH",
        "reason": "Clavage implementation would introduce JAX/XLA ML dependency — risk of environment incompatibility, new attack surface.",
        "mitigation": "Do not implement without isolated environment validation and full F-series approval.",
    },
    {
        "area": "F25",
        "risk": "LOW",
        "reason": "calculate_immutable_vote() missing but sigma structure is sound. Gap is additive only.",
        "mitigation": "Add function, run sigma tests, verify no side effects on existing AgentVote consumers.",
    },
    {
        "area": "F26",
        "risk": "LOW",
        "reason": "Continuum stub — if prematurely wired, could conflict with session_memory_snapshot coverage.",
        "mitigation": "Wire only after confirming no duplicate temporal context emission.",
    },
    {
        "area": "F27",
        "risk": "MEDIUM",
        "reason": "spectral_hash missing — any attempt to import shazam_cognitif.py will raise ImportError at module level.",
        "mitigation": "Wrap import with try/except until spectral_hash installed. Verify no_shazam_act guard active before wiring.",
    },
]


# ── Boundary invariants check ──────────────────────────────────────────────────

BOUNDARY_INVARIANTS = {
    "KX108_ONLY": True,
    "readonly": True,
    "emits_act": False,
    "emits_verdict": False,
    "memory_write": False,
    "graphiti_write": False,
    "kernel_mutation": False,
    "x108_mutation": False,
    "script_mode": "AUDIT_ONLY",
    "patch_applied": False,
    "commit_applied": False,
}


# ── Report builders ────────────────────────────────────────────────────────────

def build_json_report() -> dict:
    area_summary = _area_summary(CONCEPT_MATRIX)
    status_counts = _count_by(CONCEPT_MATRIX, "status")
    return {
        "report_id": REPORT_STEM,
        "timestamp": TIMESTAMP,
        "head_commit": HEAD_COMMIT,
        "head_tag": HEAD_TAG,
        "mode": "READ_ONLY",
        "boundary": BOUNDARY_INVARIANTS,
        "scope": ["F23A", "F23B", "F23C", "F24", "F25", "F26", "F27"],
        "concept_matrix": CONCEPT_MATRIX,
        "concept_matrix_total": len(CONCEPT_MATRIX),
        "status_counts": status_counts,
        "area_summary": area_summary,
        "cross_dependency_map": CROSS_DEPENDENCY_MAP,
        "recommended_order": RECOMMENDED_ORDER,
        "risk_matrix": RISK_MATRIX,
    }


def build_md_report(data: dict) -> str:
    area_summary = data["area_summary"]
    status_counts = data["status_counts"]

    lines = [
        "# OBSIDIA F23A→F27 — Memory Reflex / Automation / Dormant Protocol Audit",
        "",
        f"Date: {TIMESTAMP}",
        f"CHECKPOINT: F23A_TO_F27_REFLEX_AUTOMATION_PROTOCOL_AUDIT",
        f"MODE: READ_ONLY",
        f"STATUS: PASS_LOCAL_AWAITING_VALIDATION",
        f"HEAD: {HEAD_COMMIT}",
        f"TAG: {HEAD_TAG}",
        "",
        "---",
        "",
        "## Boundary Invariants",
        "",
        "```",
        "KX108_ONLY=true",
        "readonly=true",
        "emits_act=false",
        "emits_verdict=false",
        "memory_write=false",
        "graphiti_write=false",
        "kernel_mutation=false",
        "x108_mutation=false",
        "patch_applied=false",
        "commit_applied=false",
        "```",
        "",
        "---",
        "",
        "## Audit Scope",
        "",
        "| Area | Description |",
        "|------|-------------|",
        "| F23A | Memory Reflex / Automation / Dormant Protocol |",
        "| F23B | Memory Reflex Context Pack Readiness |",
        "| F23C | Automation Boundary Contract |",
        "| F24  | Clavage / Agent Vecteur Minimal |",
        "| F25  | Harmonic Vote / Veto Scoring |",
        "| F26  | Continuum / Zone Latente |",
        "| F27  | Shazam Cognitif / Style Intent |",
        "",
        "---",
        "",
        "## Status Counts (all areas)",
        "",
        "| Status | Count |",
        "|--------|-------|",
    ]
    for status, count in sorted(status_counts.items()):
        lines.append(f"| {status} | {count} |")

    lines += [
        "",
        f"**Total concepts audited: {len(CONCEPT_MATRIX)}**",
        "",
        "---",
        "",
        "## Area Summary",
        "",
        "| Area | Total | Connected | Dormant | Stub | Doc Only | Missing | History |",
        "|------|-------|-----------|---------|------|----------|---------|---------|",
    ]
    for area, s in sorted(area_summary.items()):
        lines.append(
            f"| {area} | {s['total']} | {s['connected']} | {s['dormant']} | {s['stub']} | {s['doc_only']} | {s['missing']} | {s['history_only']} |"
        )

    lines += [
        "",
        "---",
        "",
        "## F23A — Memory Reflex / Automation / Dormant Protocol",
        "",
        "### Findings",
        "",
        "| Concept | File | Status | Active | Notes |",
        "|---------|------|--------|--------|-------|",
    ]
    for row in CONCEPT_MATRIX:
        if row["area"] == "F23A":
            f = row.get("canonical_file") or "—"
            lines.append(f"| {row['concept']} | `{f}` | {row['status']} | {row['active']} | {row['notes']} |")

    lines += [
        "",
        "### F23A Conclusion",
        "",
        "- `brody_memory_promotion_guard` is **CODE_RUNTIME_CONNECTED** — active boundary guard, no change needed.",
        "- `reflex_reducer`, `avdr_phase_mapper`, `brody_automation_orchestrator`, `brody_memory_readonly/` are all **CODE_DORMANT** — not wired to active routes.",
        "- `avdr.py` (MMONDE) is **CODE_STUB**.",
        "- `readonly_context_ingress.py` present but ingress not active.",
        "- **Recommended**: Wire `brody_automation_orchestrator` only after explicit validation (MEDIUM risk).",
        "",
        "---",
        "",
        "## F23B — Memory Reflex Context Pack Readiness",
        "",
        "### Findings",
        "",
        "| Concept | File | Status | Active |",
        "|---------|------|--------|--------|",
    ]
    for row in CONCEPT_MATRIX:
        if row["area"] == "F23B":
            f = row.get("canonical_file") or "—"
            lines.append(f"| {row['concept']} | `{f}` | {row['status']} | {row['active']} |")

    lines += [
        "",
        "### F23B Conclusion",
        "",
        "Context pack family is **fully active**: builder (v1 + v2), validator, exporter, sanitizer, memory_source_registry, and brody_memory_response_chain_adapter all CODE_RUNTIME_CONNECTED.",
        "",
        "No gap found. Monitor v1/v2 schema drift in CI.",
        "",
        "---",
        "",
        "## F23C — Automation Boundary Contract",
        "",
        "### Findings",
        "",
        "| Concept | File | Status | Active |",
        "|---------|------|--------|--------|",
    ]
    for row in CONCEPT_MATRIX:
        if row["area"] == "F23C":
            f = row.get("canonical_file") or "—"
            lines.append(f"| {row['concept']} | `{f}` | {row['status']} | {row['active']} |")

    lines += [
        "",
        "### F23C Conclusion",
        "",
        "All automation boundary contracts are active. worldcalls, os3, brody_contracts_packet, brody_adaptive_response_policy, and graphiti_v20_readonly_client all CODE_RUNTIME_CONNECTED.",
        "",
        "Boundary: KX108_ONLY enforced at all surfaces. Risk: NONE.",
        "",
        "---",
        "",
        "## F24 — Clavage / Agent Vecteur Minimal",
        "",
        "### Findings",
        "",
        "| Concept | File | Status | Notes |",
        "|---------|------|--------|-------|",
    ]
    for row in CONCEPT_MATRIX:
        if row["area"] == "F24":
            f = row.get("canonical_file") or "—"
            lines.append(f"| {row['concept']} | `{f}` | {row['status']} | {row['notes']} |")

    lines += [
        "",
        "### F24 Conclusion",
        "",
        "**Clavage = DOC_ONLY.** No `clavage.py`, no `agent_vecteur.py`, no `CognitiveDeviationError`, no `strict_parser` found anywhere in the repo.",
        "",
        "`cosine_similarity.py` exists (pure math helper) but is not connected to any Clavage runtime.",
        "",
        "**DEFERRED** per F22B decision: Clavage requires JAX/XLA, full ML pipeline (200+ lines). Not implemented until isolated ML environment validated.",
        "",
        "---",
        "",
        "## F25 — Harmonic Vote / Veto Scoring",
        "",
        "### Findings",
        "",
        "| Concept | File | Status | Active | Notes |",
        "|---------|------|--------|--------|-------|",
    ]
    for row in CONCEPT_MATRIX:
        if row["area"] == "F25":
            f = row.get("canonical_file") or "—"
            lines.append(f"| {row['concept']} | `{f}` | {row['status']} | {row['active']} | {row['notes']} |")

    lines += [
        "",
        "### F25 Conclusion",
        "",
        "**Sigma vote structure present** (`AgentVote.vote: HOLD/ALLOW/BLOCK`) with `readiness_scope='harmonic_integrity_governance'`.",
        "",
        "**GAP**: `calculate_immutable_vote()` function NOT found — harmonic vote calculation is partial.",
        "",
        "Active: `sigma_contracts`, `sigma_aggregation`, `brody_thermo_coherence_time_unified`, `brody_anti_mismatch_signal`.",
        "Dormant: `regime_metrics`, `regime_truth_gate` (in gencoin_sandbox, active=False).",
        "",
        "**Recommended patch**: Add `calculate_immutable_vote()` to `sigma/contracts.py` — LOW risk, additive only.",
        "",
        "---",
        "",
        "## F26 — Continuum / Zone Latente",
        "",
        "### Findings",
        "",
        "| Concept | File | Status | Notes |",
        "|---------|------|--------|-------|",
    ]
    for row in CONCEPT_MATRIX:
        if row["area"] == "F26":
            f = row.get("canonical_file") or "—"
            lines.append(f"| {row['concept']} | `{f}` | {row['status']} | {row['notes']} |")

    lines += [
        "",
        "### F26 Conclusion",
        "",
        "`NodeContinuum` dataclass present in both `periphery/continuum_node.py` and MMONDE equivalent.",
        "",
        "**CODE_STUB** — not wired to runtime. Doctrinal coverage satisfied by `session_memory_snapshot + temporal_context_snapshot` per cognitive module registry (COVERED_BY_EXISTING_MODULE, active=True).",
        "",
        "Zone Latente: DOC_ONLY — no standalone implementation.",
        "",
        "**No patch needed** — Continuum covered by existing modules.",
        "",
        "---",
        "",
        "## F27 — Shazam Cognitif / Style Intent",
        "",
        "### Findings",
        "",
        "| Concept | File | Status | Notes |",
        "|---------|------|--------|-------|",
    ]
    for row in CONCEPT_MATRIX:
        if row["area"] == "F27":
            f = row.get("canonical_file") or "—"
            lines.append(f"| {row['concept']} | `{f}` | {row['status']} | {row['notes']} |")

    lines += [
        "",
        "### F27 Conclusion",
        "",
        "**Shazam Cognitif blocked** — `from spectral_hash import extract_features` at module level raises `ImportError`. Package `spectral_hash` not installed.",
        "",
        "Three copies: `periphery/shazam_cognitif.py`, `periphery/cognitive_trees/shazam_cognitif.py`, MMONDE/05_SHAZAM_COGNITIF/. All blocked by same dependency.",
        "",
        "`no_shazam_act.py` guard is **active** — prevents any inadvertent ACT emission from Shazam.",
        "`brody_tree_signal_packet.py` is **active** — adjacent concept, does not require spectral_hash.",
        "Test `test_shazam_cognitif_context_only.py` passes with spectral_hash mocked.",
        "",
        "**Recommended**: Install `spectral_hash` or write controlled stub, then wire under `no_shazam_act` guard. MEDIUM risk.",
        "",
        "---",
        "",
        "## Cross-Dependency Map",
        "",
        "| From | To | Type | Status | Notes |",
        "|------|----|------|--------|-------|",
    ]
    for dep in CROSS_DEPENDENCY_MAP:
        lines.append(f"| {dep['from']} | {dep['to']} | {dep['type']} | {dep['status']} | {dep['notes']} |")

    lines += [
        "",
        "---",
        "",
        "## Recommended Unblocking Order",
        "",
        "| Priority | Area | Risk | Patch Candidate | Rationale |",
        "|----------|------|------|-----------------|-----------|",
    ]
    for item in RECOMMENDED_ORDER:
        patch = "YES" if item["patch_candidate"] else "NO"
        lines.append(f"| {item['priority']} | {item['area']} | {item['risk']} | {patch} | {item['rationale']} |")

    lines += [
        "",
        "---",
        "",
        "## Risk Matrix",
        "",
        "| Area | Risk | Reason | Mitigation |",
        "|------|------|--------|------------|",
    ]
    for item in RISK_MATRIX:
        lines.append(f"| {item['area']} | {item['risk']} | {item['reason']} | {item['mitigation']} |")

    lines += [
        "",
        "---",
        "",
        "## STATUS: PASS_LOCAL_AWAITING_VALIDATION",
        "",
        "F23A→F27 audit complete. No patch applied. No commit. No runtime change.",
        "",
        "```",
        f"F23A_TO_F27_REFLEX_AUTOMATION_PROTOCOL_AUDIT_DONE",
        f"HEAD={HEAD_COMMIT}",
        f"TAG={HEAD_TAG}",
        f"NEXT=WAITING_FOR_VALIDATION",
        "```",
    ]
    return "\n".join(lines)


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    data = build_json_report()
    md_text = build_md_report(data)

    md_path = DOCS_RUNTIME / f"{REPORT_STEM}.md"
    json_path = DOCS_RUNTIME / f"{REPORT_STEM}.json"

    md_path.write_text(md_text, encoding="utf-8")
    json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    total = data["concept_matrix_total"]
    sc = data["status_counts"]
    print(f"F23A_TO_F27_REFLEX_AUTOMATION_PROTOCOL_AUDIT_DONE")
    print(f"HEAD={HEAD_COMMIT}")
    print(f"TAG={HEAD_TAG}")
    print(f"CONCEPTS_AUDITED={total}")
    print(f"  CODE_RUNTIME_CONNECTED={sc.get(S_CONNECTED, 0)}")
    print(f"  CODE_DORMANT={sc.get(S_DORMANT, 0)}")
    print(f"  CODE_STUB={sc.get(S_STUB, 0)}")
    print(f"  DOC_ONLY={sc.get(S_DOC_ONLY, 0)}")
    print(f"  MISSING={sc.get(S_MISSING, 0)}")
    print(f"  HISTORY_ONLY={sc.get('HISTORY_ONLY', 0)}")
    print(f"REPORTS_WRITTEN=")
    print(f"  {md_path}")
    print(f"  {json_path}")
    print(f"PATCH_APPLIED=false")
    print(f"COMMIT_APPLIED=false")
    print(f"NEXT=WAITING_FOR_VALIDATION")


if __name__ == "__main__":
    main()

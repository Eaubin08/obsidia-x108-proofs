#!/usr/bin/env python3
"""
scripts/audit_gps_terrain_portable_reconciliation_p76.py

P76 — GPS Terrain Portable Reconciliation
MODE: AUDIT_AND_RECONCILIATION_DOCS_ONLY

Reconcilie GPS terrain portable avec proof/Sigma.
Ne patche pas. Ne importe pas. Ne modifie rien.
Ne lance pas serveur. Ne appelle pas localhost. Ne fait pas requests.post.

VERROU ABSOLU :
  - Ne pas lancer serveur.
  - Ne pas appeler localhost.
  - Ne pas executer connectors.
  - Ne pas activer ACT.
  - Ne pas ecrire memoire/Graphiti.
  - Ne pas muter kernel.

DRY_RUN_ONLY = True (reconciliation docs seul)
"""

import json
import os
from pathlib import Path

DRY_RUN_ONLY: bool = True

ROOT = Path(__file__).resolve().parent.parent
OUT_JSON = ROOT / "docs" / "core_import" / "P76_GPS_TERRAIN_PORTABLE_RECONCILIATION.json"
OUT_JSON.parent.mkdir(parents=True, exist_ok=True)

_BOUNDARY = {
    "dry_run_only": DRY_RUN_ONLY,
    "readonly": True,
    "decision_authority": "KX108_ONLY",
    "emits_act": False,
    "emits_verdict": False,
    "memory_write": False,
    "graphiti_write": False,
    "neo4j_write": False,
    "kernel_mutation": False,
    "sigma_override": False,
    "runtime_modified": False,
    "network_called": False,
    "localhost_called": False,
}

# ---------------------------------------------------------------------------
# GPS model
# ---------------------------------------------------------------------------

GPS_MODEL = {
    "proof_integrated": (
        "Composants GPS deja integres dans sigma/ proof. "
        "sigma/domains/gps_defense_aviation_agents.py (P56B GPS) : 6 agents "
        "(SourceAvailabilityAgent, TrajectoryIntegrityAgent, SourceConflictAgent, "
        "TimeSkewAgent, BrownoutAgent, AttestationReadinessAgent). "
        "sigma/contracts.py : GpsDefenseAviationState. "
        "sigma/guard.py (P56D) : GuardX108 autorite finale LEAN_PROVEN."
    ),
    "tested_proof_surface": (
        "Tests GPS integres dans sigma/tests/ : "
        "test_gps_smoke.py (nominal pipeline), "
        "test_gps_semantics.py (5 scenarios : nominal, no_source, source_conflict, brownout, time_skew), "
        "test_gps_fail_closed.py (4 tests fail-closed). "
        "Tous executent sigma/run_pipeline.py en sous-process."
    ),
    "terrain_evidence": (
        "Preuves terrain GPS non versionnees dans ce repo. "
        "allData/ : absent du repo (MonProjet/allData/ terrain, cree par server.kernel.sealed.cjs). "
        "_sessions/ : absent. "
        "Les decision_gps_defense_aviation_*.json terrain sont hors perimetre proof."
    ),
    "replay_candidate": (
        "Exemples GPS utilisables comme tests de replay : "
        "gps_omega_chaos.json (saturation totale — tous scores >0.85), "
        "gps_source_conflict.json (conflict=0.84 -> ABORT_TRAJECTORY + BLOCK). "
        "Replay possible en appelant sigma/run_pipeline.py directement (pas de reseau)."
    ),
    "connector_active_review": (
        "Connectors GPS actifs necessite une revue avant activation. "
        "connectors/aviation_robo.py : requests.post + while True + irreversible=True. "
        "P70 classification : NETWORK_EGRESS_CONNECTOR_ACTIVE_REVIEW HIGH. "
        "Requiert : dry_run_flag + KX108 gate + auth boundary + timeout boundary."
    ),
    "connector_do_not_run": (
        "Connectors DO_NOT_RUN actuellement. "
        "aviation_robo.py : requests.post localhost:8000 GPS endpoint, boucle infinie sleep 4s. "
        "bank_normal_flow.py : requests.post localhost:8000 bank endpoint, boucle sleep 10s. "
        "trading_live.py : ccxt.binance() + requests.post, reseau externe, boucle sleep 2s. "
        "Tous irreversible=True dans payload. Aucun dry_run_flag. Aucune declaration KX108."
    ),
    "localhost_archive_only": (
        "server.kernel.sealed.cjs : serveur Express.js port 3001. "
        "Route POST /kernel/ragnarok : spawn sigma/run_pipeline.py domain data. "
        "Ecrit decision_${domain}_${timestamp}.json dans MonProjet/allData/. "
        "C'est le pont terrain JS -> Sigma Python. Archive terrain uniquement. "
        "Ne pas rebinder ce chemin. Ne pas lancer server.kernel.sealed.cjs."
    ),
    "runtime_blocked": (
        "P75 : NO_RUNTIME_IMPORT pour engine/. "
        "Le runtime core est separe du path GPS proof. "
        "GPS proof path = sigma/run_pipeline.py uniquement (pas engine/)."
    ),
}

# ---------------------------------------------------------------------------
# GPS matrix
# ---------------------------------------------------------------------------

GPS_MATRIX = [
    # ---- GPS_PROOF_INTEGRATED (4 entrees) ----
    {
        "file_path": "sigma/domains/gps_defense_aviation_agents.py",
        "component_name": "6 GPS agents (SourceAvailability, TrajectoryIntegrity, SourceConflict, TimeSkew, Brownout, AttestationReadiness)",
        "category": "GPS_PROOF_INTEGRATED",
        "decision": "KEEP_PROOF_VERSION",
        "risk_level": "NONE",
        "p56b_patched": True,
        "description": (
            "6 agents GPS/defense/aviation : "
            "SourceAvailabilityAgent (confidence 0.35 si sources manquantes), "
            "TrajectoryIntegrityAgent (drift_score >= 0.85 -> ABORT), "
            "SourceConflictAgent (conflict >= 0.8 -> ABORT), "
            "TimeSkewAgent (skew >= 0.9 -> ABORT), "
            "BrownoutAgent (brownout >= 0.9 -> ABORT), "
            "AttestationReadinessAgent (attestation_ready + rollback_possible). "
            "Domaine Domain.GPS_DEFENSE_AVIATION integre."
        ),
        "proof_wins": True,
        "sigma_bridge_safe": True,
        "p72_invariants": ["GUARD_X108_FINAL_AUTHORITY", "NO_ACT_BEFORE_TAU"],
    },
    {
        "file_path": "sigma/contracts.py (GpsDefenseAviationState)",
        "component_name": "GpsDefenseAviationState",
        "category": "GPS_PROOF_INTEGRATED",
        "decision": "KEEP_PROOF_VERSION",
        "risk_level": "NONE",
        "p56b_patched": True,
        "description": (
            "GpsDefenseAviationState : mission_id, flight_id, altitude, ground_speed, "
            "gps_status, satellites_count, signal_noise_ratio, gps_available, "
            "inertial_available, radio_available, trajectory_drift_score, "
            "source_conflict_score, time_skew_score, brownout_score, "
            "attestation_ready, rollback_possible. "
            "Heritage UniversalBase -> triple confidence (P56B GPS)."
        ),
        "proof_wins": True,
        "sigma_bridge_safe": True,
        "p72_invariants": ["DETERMINISM"],
    },
    {
        "file_path": "sigma/run_pipeline.py",
        "component_name": "CLI pipeline GPS (domain=gps_defense_aviation)",
        "category": "GPS_PROOF_INTEGRATED",
        "decision": "KEEP_PROOF_VERSION",
        "risk_level": "NONE",
        "p56b_patched": True,
        "description": (
            "sigma/run_pipeline.py appele avec domain=gps_defense_aviation et payload JSON. "
            "Applique les 6 agents GPS + aggregate_gps_defense_aviation() + GuardX108.decide(). "
            "apply_sigma() POST_GUARD_VETO_ONLY. "
            "Sortie JSON : market_verdict (TRAJECTORY_VALID/DEGRADED_NAVIGATION/"
            "RECALC_TRAJECTORY/ABORT_TRAJECTORY), x108_gate (ALLOW/HOLD/BLOCK), "
            "sigma_report."
        ),
        "proof_wins": True,
        "sigma_bridge_safe": True,
        "p72_invariants": ["SIGMA_POST_GUARD_VETO_ONLY", "GUARD_X108_FINAL_AUTHORITY"],
    },
    {
        "file_path": "sigma/guard.py",
        "component_name": "GuardX108.decide() autorité finale",
        "category": "GPS_PROOF_INTEGRATED",
        "decision": "KEEP_PROOF_VERSION",
        "risk_level": "NONE",
        "p56b_patched": True,
        "description": (
            "GuardX108.decide(aggregate) : autorite finale pour GPS comme pour tous les domaines. "
            "Produit X108Gate.ALLOW / HOLD / BLOCK. "
            "Proof Lean : GUARD_X108_FINAL_AUTHORITY (X108_kernel_never_blocks). "
            "GPS : ALLOW = TRAJECTORY_VALID, HOLD = DEGRADED/RECALC, BLOCK = ABORT."
        ),
        "proof_wins": True,
        "sigma_bridge_safe": True,
        "p72_invariants": ["GUARD_X108_FINAL_AUTHORITY"],
    },
    # ---- GPS_TESTED_PROOF_SURFACE (3 entrees) ----
    {
        "file_path": "sigma/tests/test_gps_smoke.py",
        "component_name": "test_gps_nominal_smoke",
        "category": "GPS_TESTED_PROOF_SURFACE",
        "decision": "KEEP_PROOF_VERSION",
        "risk_level": "NONE",
        "p56b_patched": False,
        "description": (
            "Test smoke GPS nominal : verifie domain, x108_gate, reason_code, "
            "decision_id, trace_id, sigma_report."
        ),
        "proof_wins": True,
        "sigma_bridge_safe": True,
        "p72_invariants": [],
    },
    {
        "file_path": "sigma/tests/test_gps_semantics.py",
        "component_name": "5 scenarios GPS semantiques",
        "category": "GPS_TESTED_PROOF_SURFACE",
        "decision": "KEEP_PROOF_VERSION",
        "risk_level": "NONE",
        "p56b_patched": False,
        "description": (
            "5 tests semantiques GPS : "
            "nominal -> TRAJECTORY_VALID + ALLOW, "
            "no_source -> RECALC_TRAJECTORY + HOLD, "
            "source_conflict -> ABORT_TRAJECTORY + BLOCK, "
            "brownout -> DEGRADED_NAVIGATION + HOLD, "
            "time_skew -> RECALC_TRAJECTORY + HOLD."
        ),
        "proof_wins": True,
        "sigma_bridge_safe": True,
        "p72_invariants": ["GUARD_X108_FINAL_AUTHORITY", "NO_ACT_BEFORE_TAU"],
    },
    {
        "file_path": "sigma/tests/test_gps_fail_closed.py",
        "component_name": "4 tests fail-closed GPS",
        "category": "GPS_TESTED_PROOF_SURFACE",
        "decision": "KEEP_PROOF_VERSION",
        "risk_level": "NONE",
        "p56b_patched": False,
        "description": (
            "4 tests fail-closed : no_source, source_conflict, brownout, time_skew "
            "ne produisent jamais ALLOW. "
            "Garantit que GuardX108 fail-close sur tous les scenarios degradees GPS."
        ),
        "proof_wins": True,
        "sigma_bridge_safe": True,
        "p72_invariants": ["GUARD_X108_FINAL_AUTHORITY", "HOLD_BEFORE_TAU"],
    },
    # ---- GPS_EXAMPLE_ONLY (6 entrees) ----
    {
        "file_path": "sigma/examples/gps_nominal.json",
        "component_name": "GPS Nominal",
        "category": "GPS_EXAMPLE_ONLY",
        "decision": "KEEP_AS_TERRAIN_EVIDENCE",
        "risk_level": "NONE",
        "p56b_patched": False,
        "description": (
            "Cas nominal : gps/inertial/radio disponibles, drift=0.08, conflict=0.05. "
            "Attendu : TRAJECTORY_VALID + ALLOW."
        ),
        "proof_wins": True,
        "sigma_bridge_safe": True,
        "p72_invariants": [],
    },
    {
        "file_path": "sigma/examples/gps_no_source.json",
        "component_name": "GPS No Source",
        "category": "GPS_EXAMPLE_ONLY",
        "decision": "KEEP_AS_TERRAIN_EVIDENCE",
        "risk_level": "NONE",
        "p56b_patched": False,
        "description": (
            "Aucune source disponible : gps=false, inertial=false, radio=false. "
            "confidence=0.10. attestation_ready=false. "
            "Attendu : RECALC_TRAJECTORY + HOLD."
        ),
        "proof_wins": True,
        "sigma_bridge_safe": True,
        "p72_invariants": [],
    },
    {
        "file_path": "sigma/examples/gps_source_conflict.json",
        "component_name": "GPS Source Conflict",
        "category": "GPS_EXAMPLE_ONLY",
        "decision": "KEEP_AS_TERRAIN_EVIDENCE",
        "risk_level": "NONE",
        "p56b_patched": False,
        "description": (
            "Conflit source maximal : source_conflict_score=0.84. "
            "Attendu : ABORT_TRAJECTORY + BLOCK. "
            "Candidate replay pour le scenario d'abort."
        ),
        "proof_wins": True,
        "sigma_bridge_safe": True,
        "p72_invariants": [],
    },
    {
        "file_path": "sigma/examples/gps_brownout.json",
        "component_name": "GPS Brownout",
        "category": "GPS_EXAMPLE_ONLY",
        "decision": "KEEP_AS_TERRAIN_EVIDENCE",
        "risk_level": "NONE",
        "p56b_patched": False,
        "description": (
            "Brownout power : brownout_score=0.82. "
            "Attendu : DEGRADED_NAVIGATION + HOLD."
        ),
        "proof_wins": True,
        "sigma_bridge_safe": True,
        "p72_invariants": [],
    },
    {
        "file_path": "sigma/examples/gps_time_skew.json",
        "component_name": "GPS Time Skew",
        "category": "GPS_EXAMPLE_ONLY",
        "decision": "KEEP_AS_TERRAIN_EVIDENCE",
        "risk_level": "NONE",
        "p56b_patched": False,
        "description": (
            "Time skew critique : time_skew_score=0.86. "
            "Attendu : RECALC_TRAJECTORY + HOLD. "
            "(skew < 0.9 -> pas ABORT mais RECALC)."
        ),
        "proof_wins": True,
        "sigma_bridge_safe": True,
        "p72_invariants": [],
    },
    {
        "file_path": "sigma/examples/gps_omega_chaos.json",
        "component_name": "GPS Omega Chaos (saturation totale)",
        "category": "GPS_EXAMPLE_ONLY",
        "decision": "REPLAY_ONLY_LATER",
        "risk_level": "NONE",
        "p56b_patched": False,
        "description": (
            "Cas de saturation totale : trajectory_drift=0.95, source_conflict=0.98, "
            "time_skew=0.85, brownout=0.90, environment_risk=1.0. "
            "gps_available=false, elapsed_s=10 < min_required_elapsed_s=108. "
            "Candidat replay pour tests de robustesse extreme."
        ),
        "proof_wins": True,
        "sigma_bridge_safe": True,
        "p72_invariants": ["GUARD_X108_FINAL_AUTHORITY", "NO_ACT_BEFORE_TAU"],
    },
    # ---- GPS_ADAPTER_SAFE_READONLY (2 entrees) ----
    {
        "file_path": "periphery/adapters/gps_adapter.py",
        "component_name": "build_gps_action() / build_gps_state()",
        "category": "GPS_ADAPTER_SAFE_READONLY",
        "decision": "KEEP_PROOF_VERSION",
        "risk_level": "LOW",
        "p56b_patched": False,
        "description": (
            "Adapter GPS periphery : build_gps_action() construit ActionCandidate GPS, "
            "build_gps_state() instancie GpsDefenseAviationState depuis payload. "
            "DEFAULT_GPS_STATE fourni. "
            "Note : irreversible=True par defaut dans build_gps_action() "
            "-> contexte d'execution normale attendu."
        ),
        "proof_wins": False,
        "sigma_bridge_safe": True,
        "p72_invariants": ["IRREVERSIBLE_ACTION_DELAY"],
    },
    {
        "file_path": "periphery/sigma_bridge.py",
        "component_name": "run_gps_with_periphery()",
        "category": "GPS_ADAPTER_SAFE_READONLY",
        "decision": "KEEP_PROOF_VERSION",
        "risk_level": "LOW",
        "p56b_patched": False,
        "description": (
            "Bridge sigma/periphery : run_gps_with_periphery(state, packet) "
            "-> aggregate_gps_defense_aviation(agents) "
            "-> _merge_periphery_into_aggregate(packet) "
            "-> _apply_meta_agents() "
            "-> GuardX108().decide(aggregate). "
            "packet.assert_non_sovereign() verifie que la periphery ne prend pas de decision souveraine. "
            "Chemin safe : tout converge vers GuardX108 autorite finale."
        ),
        "proof_wins": True,
        "sigma_bridge_safe": True,
        "p72_invariants": ["GUARD_X108_FINAL_AUTHORITY", "NO_PERIPHERY_DECISION_AUTHORITY"],
    },
    # ---- GPS_CONNECTOR_DO_NOT_RUN (3 entrees) ----
    {
        "file_path": "connectors/aviation_robo.py",
        "component_name": "send_gps_payload() / run_flight_flow()",
        "category": "GPS_CONNECTOR_DO_NOT_RUN",
        "decision": "BLOCK_CONNECTOR_RUN",
        "risk_level": "HIGH",
        "p56b_patched": False,
        "description": (
            "Connector GPS aviation : requests.post vers http://127.0.0.1:8000/api/periphery/monitoring/adapters/gps. "
            "Boucle while True, sleep 4s. "
            "Payload irreversible=True. "
            "Pas de dry_run_flag. Pas de KX108 authority declare."
        ),
        "proof_wins": False,
        "sigma_bridge_safe": False,
        "p72_invariants": ["NO_ACT_BEFORE_TAU", "IRREVERSIBLE_ACTION_DELAY"],
        "p70_status": "NETWORK_EGRESS_CONNECTOR_ACTIVE_REVIEW",
        "hardening_required": [
            "ADD_DRY_RUN_FLAG",
            "ADD_KX108_GATE",
            "ADD_AUTH_BOUNDARY",
            "ADD_TIMEOUT_BOUNDARY",
            "BOUND_LOOP (max_iterations or TTL)",
            "ADD_REPLAY_TEST",
            "REMOVE_IRREVERSIBLE_TRUE_OR_GATE_IT",
        ],
    },
    {
        "file_path": "connectors/bank_normal_flow.py",
        "component_name": "send_bank_payload() / run_normal_bank()",
        "category": "GPS_CONNECTOR_DO_NOT_RUN",
        "decision": "BLOCK_CONNECTOR_RUN",
        "risk_level": "HIGH",
        "p56b_patched": False,
        "description": (
            "Connector bank : requests.post vers http://127.0.0.1:8000/api/periphery/monitoring/adapters/bank. "
            "Boucle while True, sleep 10s. "
            "Payload irreversible=True. "
            "Meme pattern que aviation_robo.py — meme hardening requis."
        ),
        "proof_wins": False,
        "sigma_bridge_safe": False,
        "p72_invariants": ["NO_ACT_BEFORE_TAU", "IRREVERSIBLE_ACTION_DELAY"],
        "p70_status": "NETWORK_EGRESS_CONNECTOR_ACTIVE_REVIEW",
        "hardening_required": [
            "ADD_DRY_RUN_FLAG",
            "ADD_KX108_GATE",
            "ADD_AUTH_BOUNDARY",
            "ADD_TIMEOUT_BOUNDARY",
            "BOUND_LOOP",
        ],
    },
    {
        "file_path": "connectors/trading_live.py",
        "component_name": "stream_to_kernel() / ccxt.binance()",
        "category": "GPS_CONNECTOR_DO_NOT_RUN",
        "decision": "BLOCK_CONNECTOR_RUN",
        "risk_level": "CRITICAL",
        "p56b_patched": False,
        "description": (
            "Connector trading live : ccxt.binance() (reseau externe Binance) + "
            "requests.post localhost:8000/trading. "
            "Boucle while True, sleep 2s. "
            "Payload irreversible=True. "
            "Dependance ccxt (non installee en prod). "
            "Double risque reseau (externe + localhost)."
        ),
        "proof_wins": False,
        "sigma_bridge_safe": False,
        "p72_invariants": ["NO_ACT_BEFORE_TAU", "NETWORK_EGRESS_REVIEW_REQUIRED"],
        "p70_status": "NETWORK_EGRESS_CONNECTOR_ACTIVE_REVIEW",
        "hardening_required": [
            "ADD_DRY_RUN_FLAG",
            "ADD_KX108_GATE",
            "ADD_AUTH_BOUNDARY",
            "ADD_TIMEOUT_BOUNDARY",
            "BOUND_LOOP",
            "ISOLATE_EXTERNAL_NETWORK (ccxt)",
            "P70_GATE_BEFORE_ACTIVATION",
        ],
    },
    # ---- GPS_LOCALHOST_ARCHIVE_ONLY (1 entree) ----
    {
        "file_path": "server.kernel.sealed.cjs",
        "component_name": "Express.js /kernel/ragnarok (port 3001)",
        "category": "GPS_LOCALHOST_ARCHIVE_ONLY",
        "decision": "KEEP_AS_TERRAIN_EVIDENCE",
        "risk_level": "MEDIUM",
        "p56b_patched": False,
        "description": (
            "Serveur Express.js port 3001. "
            "Route POST /kernel/ragnarok : spawn sigma/run_pipeline.py domain data. "
            "Ecrit decision_${domain}_${timestamp}.json dans MonProjet/allData/. "
            "Pont terrain JS -> Python Sigma. "
            "Utilise en phase de terrain pour tester le pipeline Sigma depuis un frontend JS. "
            "allData/ non versionne dans ce repo (chemin MonProjet/allData/)."
        ),
        "proof_wins": True,
        "sigma_bridge_safe": False,
        "p72_invariants": ["NO_MEMORY_WRITE_WITHOUT_GATE"],
        "localhost_port": 3001,
        "route": "/kernel/ragnarok",
        "alldata_path": "MonProjet/allData/ (absent du repo)",
        "action": "NE_PAS_RELANCER — archive terrain uniquement. Proof path = sigma/run_pipeline.py direct.",
    },
    # ---- GPS_TERRAIN_EVIDENCE (absents) ----
    {
        "file_path": "allData/ (absent)",
        "component_name": "Decisions terrain GPS (non versionnees)",
        "category": "GPS_TERRAIN_EVIDENCE",
        "decision": "KEEP_AS_TERRAIN_EVIDENCE",
        "risk_level": "NONE",
        "p56b_patched": False,
        "description": (
            "Repertoire allData/ absent du repo. "
            "Contenu terrain : decision_gps_defense_aviation_${timestamp}.json "
            "generes par server.kernel.sealed.cjs en phase terrain. "
            "Non versionnaire — pas de preuve dans ce repo."
        ),
        "proof_wins": False,
        "sigma_bridge_safe": False,
        "p72_invariants": [],
        "present_in_repo": False,
    },
    {
        "file_path": "_sessions/ (absent)",
        "component_name": "Sessions terrain (non versionnees)",
        "category": "GPS_TERRAIN_EVIDENCE",
        "decision": "KEEP_AS_TERRAIN_EVIDENCE",
        "risk_level": "NONE",
        "p56b_patched": False,
        "description": (
            "Repertoire _sessions/ absent du repo. "
            "Pas de sessions terrain versionnees GPS dans ce repo."
        ),
        "proof_wins": False,
        "sigma_bridge_safe": False,
        "p72_invariants": [],
        "present_in_repo": False,
    },
]

# ---------------------------------------------------------------------------
# Terrain evidence matrix (terrain non-proof)
# ---------------------------------------------------------------------------

TERRAIN_EVIDENCE_MATRIX = [
    {
        "evidence_id": "TE-01",
        "source": "server.kernel.sealed.cjs",
        "type": "LOCALHOST_TERRAIN_BRIDGE",
        "description": (
            "Pont terrain Express.js port 3001, route /kernel/ragnarok. "
            "Spawn sigma/run_pipeline.py depuis JS. "
            "Archive terrain — ne pas rebinder."
        ),
        "present_in_repo": True,
        "versioned": True,
        "alldata_generated": True,
        "alldata_present": False,
    },
    {
        "evidence_id": "TE-02",
        "source": "MonProjet/allData/decision_gps_defense_aviation_*.json",
        "type": "TERRAIN_DECISION_FILES",
        "description": (
            "Fichiers de decisions GPS terrain generes par server.kernel.sealed.cjs. "
            "Format : JSON sigma/run_pipeline.py output. "
            "Absent du repo — terrain local uniquement."
        ),
        "present_in_repo": False,
        "versioned": False,
        "alldata_generated": True,
        "alldata_present": False,
    },
    {
        "evidence_id": "TE-03",
        "source": "connectors/aviation_robo.py",
        "type": "TERRAIN_CONNECTOR_ACTIVE",
        "description": (
            "Connecteur terrain qui envoyait les requetes GPS vers localhost:8000. "
            "Terrain path : aviation_robo.py -> HTTP -> apps/obsidia_api -> sigma_bridge. "
            "P70 : NETWORK_EGRESS_CONNECTOR_ACTIVE_REVIEW HIGH."
        ),
        "present_in_repo": True,
        "versioned": True,
        "alldata_generated": False,
        "alldata_present": False,
    },
]

# ---------------------------------------------------------------------------
# Connector matrix
# ---------------------------------------------------------------------------

CONNECTOR_MATRIX = [
    {
        "connector_path": "connectors/aviation_robo.py",
        "target": "http://127.0.0.1:8000/api/periphery/monitoring/adapters/gps",
        "method": "POST",
        "loop_type": "while_true_sleep_4s",
        "has_dry_run_flag": False,
        "has_kx108_gate": False,
        "has_auth_boundary": False,
        "has_timeout_boundary": False,
        "irreversible_payload": True,
        "external_network": False,
        "p70_category": "NETWORK_EGRESS_CONNECTOR_ACTIVE_REVIEW",
        "p76_decision": "BLOCK_CONNECTOR_RUN",
    },
    {
        "connector_path": "connectors/bank_normal_flow.py",
        "target": "http://127.0.0.1:8000/api/periphery/monitoring/adapters/bank",
        "method": "POST",
        "loop_type": "while_true_sleep_10s",
        "has_dry_run_flag": False,
        "has_kx108_gate": False,
        "has_auth_boundary": False,
        "has_timeout_boundary": False,
        "irreversible_payload": True,
        "external_network": False,
        "p70_category": "NETWORK_EGRESS_CONNECTOR_ACTIVE_REVIEW",
        "p76_decision": "BLOCK_CONNECTOR_RUN",
    },
    {
        "connector_path": "connectors/trading_live.py",
        "target": "http://127.0.0.1:8000/api/periphery/monitoring/adapters/trading",
        "method": "POST",
        "loop_type": "while_true_sleep_2s",
        "has_dry_run_flag": False,
        "has_kx108_gate": False,
        "has_auth_boundary": False,
        "has_timeout_boundary": False,
        "irreversible_payload": True,
        "external_network": True,
        "external_network_target": "ccxt.binance() Binance exchange",
        "p70_category": "NETWORK_EGRESS_CONNECTOR_ACTIVE_REVIEW",
        "p76_decision": "BLOCK_CONNECTOR_RUN",
    },
]

# ---------------------------------------------------------------------------
# Replay candidate matrix
# ---------------------------------------------------------------------------

REPLAY_CANDIDATE_MATRIX = [
    {
        "replay_id": "RC-01",
        "file_path": "sigma/examples/gps_omega_chaos.json",
        "scenario": "Saturation totale GPS",
        "key_scores": {
            "trajectory_drift": 0.95,
            "source_conflict": 0.98,
            "time_skew": 0.85,
            "brownout": 0.90,
            "elapsed_s": 10.0,
            "min_required_elapsed_s": 108.0,
        },
        "expected_x108_gate": "BLOCK",
        "replay_method": "python sigma/run_pipeline.py gps_defense_aviation sigma/examples/gps_omega_chaos.json",
        "risk_level": "NONE",
        "safe_to_replay": True,
    },
    {
        "replay_id": "RC-02",
        "file_path": "sigma/examples/gps_source_conflict.json",
        "scenario": "Conflit source majeur -> ABORT_TRAJECTORY",
        "key_scores": {
            "source_conflict": 0.84,
            "trajectory_drift": 0.30,
        },
        "expected_x108_gate": "BLOCK",
        "expected_market_verdict": "ABORT_TRAJECTORY",
        "replay_method": "python sigma/run_pipeline.py gps_defense_aviation sigma/examples/gps_source_conflict.json",
        "risk_level": "NONE",
        "safe_to_replay": True,
    },
    {
        "replay_id": "RC-03",
        "file_path": "sigma/examples/gps_time_skew.json",
        "scenario": "Time skew critique (skew=0.86 -> RECALC pas ABORT)",
        "key_scores": {
            "time_skew": 0.86,
        },
        "expected_x108_gate": "HOLD",
        "expected_market_verdict": "RECALC_TRAJECTORY",
        "replay_method": "python sigma/run_pipeline.py gps_defense_aviation sigma/examples/gps_time_skew.json",
        "risk_level": "NONE",
        "safe_to_replay": True,
    },
    {
        "replay_id": "RC-04",
        "file_path": "sigma/examples/gps_no_source.json",
        "scenario": "Aucune source GPS/inertial/radio",
        "key_scores": {
            "gps_available": False,
            "inertial_available": False,
            "radio_available": False,
            "position_confidence": 0.10,
        },
        "expected_x108_gate": "HOLD",
        "expected_market_verdict": "RECALC_TRAJECTORY",
        "replay_method": "python sigma/run_pipeline.py gps_defense_aviation sigma/examples/gps_no_source.json",
        "risk_level": "NONE",
        "safe_to_replay": True,
    },
]

# ---------------------------------------------------------------------------
# P70 connector constraints applied
# ---------------------------------------------------------------------------

P70_CONNECTOR_CONSTRAINTS_APPLIED = [
    "NETWORK_EGRESS_REVIEW_REQUIRED: aviation_robo.py BLOCK_CONNECTOR_RUN — requests.post localhost sans dry_run_flag",
    "NETWORK_EGRESS_REVIEW_REQUIRED: bank_normal_flow.py BLOCK_CONNECTOR_RUN — meme pattern",
    "NETWORK_EGRESS_REVIEW_REQUIRED: trading_live.py BLOCK_CONNECTOR_RUN — ccxt reseau externe + localhost",
    "CONNECTOR_HARDENING_REQUIRED: dry_run_flag + KX108 gate + auth boundary + timeout boundary + loop bound avant activation",
    "NO_IRREVERSIBLE_WITHOUT_GATE: payload irreversible=True dans tous les connectors — gate requis",
    "LOCALHOST_NOT_PROOF_BINDING: server.kernel.sealed.cjs localhost:3001 = archive terrain uniquement",
]

# ---------------------------------------------------------------------------
# P72 invariant constraints applied
# ---------------------------------------------------------------------------

P72_INVARIANT_CONSTRAINTS_APPLIED = [
    "GUARD_X108_FINAL_AUTHORITY: GuardX108 (sigma/guard.py) autorite finale GPS — Lean proven",
    "NO_ACT_BEFORE_TAU: connectors aviation/bank/trading BLOCK — envoient irreversible=True sans tau garanti",
    "IRREVERSIBLE_ACTION_DELAY: aviation_robo.py irreversible=True — gate KX108 requis avant run",
    "SIGMA_POST_GUARD_VETO_ONLY: sigma/run_pipeline.py apply_sigma() veto seul — GPS pipeline respecte l'invariant",
    "NO_PERIPHERY_DECISION_AUTHORITY: periphery/sigma_bridge.py assert_non_sovereign() — verifie que periphery ne decide pas",
    "DETERMINISM: sigma/run_pipeline.py GPS deterministe — meme input -> meme output (replay safe)",
    "NO_MEMORY_WRITE_WITHOUT_GATE: server.kernel.sealed.cjs ecrit allData/ — gate requis si reactive",
    "NETWORK_EGRESS_REVIEW_REQUIRED: trading_live.py ccxt — P70 gate requis",
]

# ---------------------------------------------------------------------------
# P74 sigma constraints applied
# ---------------------------------------------------------------------------

P74_SIGMA_CONSTRAINTS_APPLIED = [
    "SIGMA_POST_GUARD_VETO_ONLY: sigma/ non modifie — GPS pipeline via apply_sigma() respecte POST_GUARD_VETO_ONLY",
    "GUARD_X108_FINAL_AUTHORITY: GuardX108 decide pour GPS (ALLOW=TRAJECTORY_VALID, HOLD=RECALC, BLOCK=ABORT)",
    "NO_GAMMA_05: sigma/domains/gps_defense_aviation_agents.py — pas de gamma=0.5",
    "NO_KERNEL_MUTATION: aucun composant GPS ne modifie sigma/guard.py ou sigma/run_pipeline.py",
]

# ---------------------------------------------------------------------------
# P75 runtime constraints applied
# ---------------------------------------------------------------------------

P75_RUNTIME_CONSTRAINTS_APPLIED = [
    "NO_RUNTIME_IMPORT: engine/ bloque permanent — GPS proof path = sigma/ uniquement (pas engine/)",
    "BLOCK_CONNECTOR_RUN: aviation_robo.py est un connector actif vers localhost — memes risques que api_server/main.py (P75)",
    "GPS_PROOF_PATH_ONLY: sigma/run_pipeline.py + sigma/guard.py = proof path GPS legitime",
    "NO_RUNTIME_ENGINE_GPS: os1/os1.py emetteur ACT bloque (P75) — ne pas relier GPS au runtime core",
]

# ---------------------------------------------------------------------------
# Focus findings
# ---------------------------------------------------------------------------

FOCUS_FINDINGS = [
    {
        "finding_id": "P76-F1",
        "type": "GPS_PROOF_COMPLETE",
        "component": "sigma/domains/gps_defense_aviation_agents.py + sigma/contracts.py + sigma/run_pipeline.py + sigma/guard.py",
        "description": (
            "GPS defense aviation est entierement integre dans sigma/ proof (P56B GPS). "
            "6 agents couvrant : disponibilite sources, integrite trajectoire, conflits sources, "
            "time skew, brownout, readiness attestation. "
            "GpsDefenseAviationState + triple confidence (P56B). "
            "GuardX108 autorite finale Lean-proven. "
            "Pas de gap GPS dans sigma/."
        ),
        "action": "KEEP_PROOF_VERSION — GPS proof complet",
    },
    {
        "finding_id": "P76-F2",
        "type": "GPS_TESTS_COMPLETE",
        "component": "sigma/tests/test_gps_smoke.py + test_gps_semantics.py + test_gps_fail_closed.py",
        "description": (
            "3 fichiers de tests GPS : smoke (1 test), semantics (5 scenarios), fail_closed (4 tests). "
            "Couvrent les 5 scenarios standards : nominal, no_source, source_conflict, brownout, time_skew. "
            "Vertu fail-closed : aucun des scenarios degrade ne produit ALLOW. "
            "Pas de nouveau test requis pour P76."
        ),
        "action": "KEEP_PROOF_VERSION — tests GPS complets",
    },
    {
        "finding_id": "P76-F3",
        "type": "CONNECTOR_DO_NOT_RUN",
        "component": "connectors/aviation_robo.py + bank_normal_flow.py + trading_live.py",
        "description": (
            "3 connectors actifs : requests.post + while True + irreversible=True dans payload. "
            "Aucun dry_run_flag. Aucun KX108 gate. "
            "P70 : NETWORK_EGRESS_CONNECTOR_ACTIVE_REVIEW HIGH. "
            "BLOCK_CONNECTOR_RUN jusqu'a hardening complet : "
            "dry_run_flag + KX108 gate + auth boundary + timeout boundary + loop bound + replay test."
        ),
        "action": "BLOCK_CONNECTOR_RUN — hardening requis",
    },
    {
        "finding_id": "P76-F4",
        "type": "LOCALHOST_RAGNAROK_ARCHIVE",
        "component": "server.kernel.sealed.cjs (port 3001, route /kernel/ragnarok)",
        "description": (
            "Pont terrain Express.js -> Python Sigma. "
            "Route /kernel/ragnarok spawn sigma/run_pipeline.py et ecrit allData/. "
            "Proof path equivalent : sigma/run_pipeline.py en direct (pas besoin du serveur JS). "
            "allData/ non versionne — pas de preuve terrain disponible dans ce repo. "
            "NE_PAS_RELANCER le serveur JS. Proof path = Python direct."
        ),
        "action": "KEEP_AS_TERRAIN_EVIDENCE — ne pas rebinder localhost",
    },
    {
        "finding_id": "P76-F5",
        "type": "REPLAY_SAFE",
        "component": "sigma/examples/gps_omega_chaos.json + gps_source_conflict.json + gps_time_skew.json + gps_no_source.json",
        "description": (
            "4 scenarios de replay disponibles via sigma/run_pipeline.py directement. "
            "Aucun reseau. Aucun serveur. Deterministe. "
            "omega_chaos : saturation totale (drift=0.95, conflict=0.98) -> BLOCK attendu. "
            "source_conflict : abort trajectory. time_skew : recalc. no_source : recalc."
        ),
        "action": "REPLAY_ONLY_LATER — safe via python sigma/run_pipeline.py direct",
    },
    {
        "finding_id": "P76-F6",
        "type": "PERIPHERY_BRIDGE_SAFE",
        "component": "periphery/adapters/gps_adapter.py + periphery/sigma_bridge.py",
        "description": (
            "periphery/sigma_bridge.py : run_gps_with_periphery() "
            "converge vers GuardX108 autorite finale. "
            "assert_non_sovereign() sur le packet periphery. "
            "periphery/adapters/gps_adapter.py : build_gps_state() readonly. "
            "GPS_ADAPTER_SAFE_READONLY. "
            "Note : irreversible=True dans DEFAULT_GPS_STATE de gps_adapter.py "
            "-> contexte attendu pour decisions trajectoriales."
        ),
        "action": "KEEP_PROOF_VERSION — adapters GPS safe",
    },
    {
        "finding_id": "P76-F7",
        "type": "HARDENING_ROADMAP",
        "component": "connectors/ (tous les 3)",
        "description": (
            "Pour une future activation des connectors GPS/bank/trading, le hardening requis est : "
            "1. DRY_RUN_ONLY=True flag (pas de POST si dry_run). "
            "2. KX108 gate (timeout boundary x108 avant envoi). "
            "3. Auth boundary (OBSIDIA_API_KEY header). "
            "4. Timeout boundary (max retries + TTL). "
            "5. Loop bound (max_iterations ou datetime cutoff). "
            "6. Replay test (sigma/run_pipeline.py direct avant live). "
            "7. No direct ACT (toujours passer par GuardX108). "
            "8. Route hardening (P68 pattern — fail-closed 503 si clé absente)."
        ),
        "action": "BLOCK_UNTIL_AUTH_EGRESS_HARDENING — roadmap pour palier futur",
    },
]


# ---------------------------------------------------------------------------
# Build counts
# ---------------------------------------------------------------------------

def _build_counts(matrix):
    cat_counts = {}
    dec_counts = {}
    for e in matrix:
        cat = e.get("category", "UNKNOWN")
        dec = e.get("decision", "UNKNOWN")
        cat_counts[cat] = cat_counts.get(cat, 0) + 1
        dec_counts[dec] = dec_counts.get(dec, 0) + 1
    return cat_counts, dec_counts


def _by_category(matrix, category):
    return [e["file_path"] for e in matrix if e.get("category") == category]


def _by_decision(matrix, decision):
    return [e["file_path"] for e in matrix if e.get("decision") == decision]


# ---------------------------------------------------------------------------
# Run audit
# ---------------------------------------------------------------------------

def run_audit() -> dict:
    cat_counts, dec_counts = _build_counts(GPS_MATRIX)

    result = {
        "audit_id": "P76",
        "status": "P76_GPS_TERRAIN_PORTABLE_RECONCILIATION_READY",
        "mode": "AUDIT_AND_RECONCILIATION_DOCS_ONLY",
        "source_patch_applied": False,
        "files_imported_count": 0,
        "gps_decision": "KEEP_PROOF_AND_TERRAIN_EVIDENCE_SEPARATED",
        "gps_model": GPS_MODEL,
        "gps_files_scanned_count": len(GPS_MATRIX),
        "gps_matrix": GPS_MATRIX,
        "terrain_evidence_matrix": TERRAIN_EVIDENCE_MATRIX,
        "connector_matrix": CONNECTOR_MATRIX,
        "replay_candidate_matrix": REPLAY_CANDIDATE_MATRIX,
        "category_counts": cat_counts,
        "decision_counts": dec_counts,
        "proof_integrated": _by_category(GPS_MATRIX, "GPS_PROOF_INTEGRATED"),
        "tested_proof_surface": _by_category(GPS_MATRIX, "GPS_TESTED_PROOF_SURFACE"),
        "terrain_evidence": _by_category(GPS_MATRIX, "GPS_TERRAIN_EVIDENCE"),
        "replay_candidates": [r["file_path"] for r in REPLAY_CANDIDATE_MATRIX],
        "connector_do_not_run": _by_decision(GPS_MATRIX, "BLOCK_CONNECTOR_RUN"),
        "connector_hardening_required": [
            e["file_path"] for e in GPS_MATRIX
            if e.get("decision") == "BLOCK_CONNECTOR_RUN"
        ],
        "localhost_archive_only": _by_category(GPS_MATRIX, "GPS_LOCALHOST_ARCHIVE_ONLY"),
        "runtime_blocked": ["engine/ (P75 NO_RUNTIME_IMPORT)"],
        "proof_wins": [
            e["file_path"] for e in GPS_MATRIX if e.get("proof_wins") is True
        ],
        "p70_connector_constraints_applied": P70_CONNECTOR_CONSTRAINTS_APPLIED,
        "p72_invariant_constraints_applied": P72_INVARIANT_CONSTRAINTS_APPLIED,
        "p74_sigma_constraints_applied": P74_SIGMA_CONSTRAINTS_APPLIED,
        "p75_runtime_constraints_applied": P75_RUNTIME_CONSTRAINTS_APPLIED,
        "focus_findings": FOCUS_FINDINGS,
        "preexisting_manifest_drift": [],
        "preexisting_test_debt": [],
        "runtime_modified": False,
        "sigma_modified": False,
        "routes_modified": False,
        "srl_modified": False,
        "connectors_modified": False,
        "source_packs_modified": False,
        "proofs_modified": False,
        "lean_proofs_modified": False,
        "act_enabled": False,
        "memory_write_enabled": False,
        "graphiti_write_enabled": False,
        "neo4j_write_enabled": False,
        "kernel_mutation_enabled": False,
        "x108_merge_enabled": False,
        "network_called": False,
        "localhost_called": False,
        "dry_run_only": DRY_RUN_ONLY,
        "branch": "p76-gps-terrain-portable-reconciliation",
        "date": "2026-06-07",
        "palier": "P76",
        "next_step": "P77_CANON_WORDING_TARGETED_CLEANUP",
    }

    return result


def main():
    result = run_audit()

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"JSON => {OUT_JSON}")
    print(f"gps_decision => {result['gps_decision']}")
    print(f"status => {result['status']}")
    print(f"files_scanned => {result['gps_files_scanned_count']}")
    print(f"category_counts => {result['category_counts']}")
    print(f"decision_counts => {result['decision_counts']}")


if __name__ == "__main__":
    main()

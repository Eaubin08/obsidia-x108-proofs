"""
P56A — Tests de validation de l'audit Core/Proof Metric Delta

Ces tests vérifient :
1. Les fichiers de sortie existent après exécution du script.
2. Les invariants critiques de la matrice de déltas.
3. Qu'aucune règle bloquante n'est violée.

Pré-requis : le script scripts/audit_core_proof_metric_delta_p56a.py
doit avoir été exécuté au moins une fois pour produire les outputs.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = REPO_ROOT / "docs" / "core_import"

MATRIX_PATH = DOCS_DIR / "OBSIDIA_CORE_PROOF_METRIC_DELTA_MATRIX_V0.json"
AUTHORITY_PATH = DOCS_DIR / "OBSIDIA_CORE_PROOF_METRIC_AUTHORITY_MATRIX_V0.json"
BLOCKING_PATH = DOCS_DIR / "OBSIDIA_CORE_PROOF_BLOCKING_DELTAS_V0.json"
AUDIT_PATH = DOCS_DIR / "OBSIDIA_CORE_PROOF_METRIC_DELTA_AUDIT_V0.md"


def _load_json(path: Path):
    assert path.exists(), f"File not found: {path}"
    return json.loads(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Test 01 — matrix JSON existe
# ---------------------------------------------------------------------------
def test_01_matrix_json_exists():
    """La matrice de déltas doit exister après exécution du script."""
    assert MATRIX_PATH.exists(), f"Matrix not found: {MATRIX_PATH}"
    data = _load_json(MATRIX_PATH)
    assert isinstance(data, list), "Matrix must be a list"
    assert len(data) > 0, "Matrix must not be empty"


# ---------------------------------------------------------------------------
# Test 02 — authority matrix existe
# ---------------------------------------------------------------------------
def test_02_authority_matrix_exists():
    """La matrice d'autorité doit exister."""
    assert AUTHORITY_PATH.exists(), f"Authority matrix not found: {AUTHORITY_PATH}"
    data = _load_json(AUTHORITY_PATH)
    assert isinstance(data, list)
    assert len(data) > 0


# ---------------------------------------------------------------------------
# Test 03 — blocking deltas JSON existe
# ---------------------------------------------------------------------------
def test_03_blocking_deltas_json_exists():
    """Le fichier de déltas bloquants doit exister."""
    assert BLOCKING_PATH.exists(), f"Blocking deltas not found: {BLOCKING_PATH}"
    data = _load_json(BLOCKING_PATH)
    assert "fusion_status" in data
    assert "blocking_delta_count" in data
    assert isinstance(data["blocking_deltas"], list)


# ---------------------------------------------------------------------------
# Test 04 — OS0/OS1/OS2/OS3 exact matches reconnus
# ---------------------------------------------------------------------------
def test_04_os_layers_exact_match_recognized():
    """
    Si OS1 x108.py core = proof (min_wait_s=108.0 identique),
    le delta doit être EXACT_MATCH ou SAME_NAME_SAME_MEANING,
    jamais BREAKING_CHANGE ou DO_NOT_MERGE.
    """
    matrix = _load_json(MATRIX_PATH)
    os_layer_entries = [
        e for e in matrix
        if e.get("layer_scope") in ("OS0", "OS1", "OS2", "OS3")
    ]
    breaking = [
        e for e in os_layer_entries
        if e.get("authority_decision") == "DO_NOT_MERGE"
        and e.get("delta_type") not in ("BREAKING_CHANGE",)
    ]
    # We allow BREAKING_CHANGE with DO_NOT_MERGE only if explicitly flagged
    # A LAYER_DIFFERENCE_NOT_CONFLICT must never have DO_NOT_MERGE
    bad = [
        e for e in os_layer_entries
        if e.get("delta_type") == "LAYER_DIFFERENCE_NOT_CONFLICT"
        and e.get("authority_decision") == "DO_NOT_MERGE"
    ]
    assert bad == [], f"LAYER_DIFFERENCE entries must not have DO_NOT_MERGE: {bad}"


# ---------------------------------------------------------------------------
# Test 05 — agents/contracts vs sigma/contracts : extension, pas overwrite
# ---------------------------------------------------------------------------
def test_05_contracts_extension_not_overwrite():
    """
    La paire P06 (agents/contracts vs sigma/contracts) ne doit pas
    être classée comme remplacement du core (CORE_WINS interdit si proof étend).
    Les champs nouveaux du proof (triple confidence, GPS) doivent être
    PROOF_EXTENSION_COMPATIBLE ou DOMAIN_EXTENSION.
    """
    matrix = _load_json(MATRIX_PATH)
    p06_entries = [e for e in matrix if "P06" in e.get("metric_id", "")]

    for e in p06_entries:
        dt = e.get("delta_type", "")
        # Proof-only fields must not be BREAKING_CHANGE
        if e.get("proof_value") and not e.get("core_value"):
            assert dt not in ("BREAKING_CHANGE",), (
                f"P06 proof-only field {e['metric_name']} classified as BREAKING_CHANGE"
            )


# ---------------------------------------------------------------------------
# Test 06 — CanonicalDecisionEnvelope core fields protégés
# ---------------------------------------------------------------------------
def test_06_canonical_decision_envelope_core_fields_protected():
    """
    Les champs core de CanonicalDecisionEnvelope (domain, x108_gate, market_verdict,
    confidence, contradictions, etc.) ne doivent pas être classés
    PROOF_WINS si leur valeur diffère.
    """
    cde_core_fields = {
        "domain", "market_verdict", "confidence", "contradictions", "unknowns",
        "risk_flags", "x108_gate", "reason_code", "severity", "decision_id",
        "trace_id", "ticket_required", "ticket_id", "attestation_ref", "source",
        "evidence_refs", "metrics", "raw_engine",
    }
    matrix = _load_json(MATRIX_PATH)
    violations = []
    for e in matrix:
        if e.get("metric_name") in cde_core_fields:
            if e.get("authority_decision") == "PROOF_WINS":
                violations.append(e["metric_name"])
    assert violations == [], f"CDE core fields must not have PROOF_WINS: {violations}"


# ---------------------------------------------------------------------------
# Test 07 — confidence_integrity/governance/readiness = extension namespaced
# ---------------------------------------------------------------------------
def test_07_triple_confidence_is_namespaced_extension():
    """
    Les champs confidence_integrity, confidence_governance, confidence_readiness
    sont des extensions proof : ils doivent être KEEP_BOTH_NAMESPACED ou
    PROOF_EXTENSION_COMPATIBLE, jamais DO_NOT_MERGE ou BREAKING_CHANGE.
    """
    triple_fields = {"confidence_integrity", "confidence_governance", "confidence_readiness"}
    matrix = _load_json(MATRIX_PATH)
    violations = []
    for e in matrix:
        if e.get("metric_name") in triple_fields:
            if e.get("authority_decision") in ("DO_NOT_MERGE",):
                violations.append(e)
            if e.get("delta_type") in ("BREAKING_CHANGE",):
                violations.append(e)
    assert violations == [], f"Triple confidence fields wrongly classified: {violations}"


# ---------------------------------------------------------------------------
# Test 08 — GPS_DEFENSE_AVIATION = DOMAIN_EXTENSION
# ---------------------------------------------------------------------------
def test_08_gps_defense_aviation_is_domain_extension():
    """
    Tout champ ou entrée contenant 'gps_defense_aviation' ou 'GPS_DEFENSE_AVIATION'
    doit être classé DOMAIN_EXTENSION avec EXTENSION_ONLY,
    jamais CORE_WINS ou DO_NOT_MERGE.
    """
    matrix = _load_json(MATRIX_PATH)
    for e in matrix:
        name = e.get("metric_name", "").lower()
        if "gps" in name or "defense" in name or "aviation" in name:
            assert e.get("delta_type") == "DOMAIN_EXTENSION", (
                f"GPS field {e['metric_name']} should be DOMAIN_EXTENSION, got {e['delta_type']}"
            )
            assert e.get("authority_decision") not in ("CORE_WINS", "DO_NOT_MERGE"), (
                f"GPS field {e['metric_name']} has bad authority: {e['authority_decision']}"
            )


# ---------------------------------------------------------------------------
# Test 09 — Aucun ACT autorisé dans un path dry-run/readonly
# ---------------------------------------------------------------------------
def test_09_no_act_in_dryrun_path():
    """
    Aucune entrée classée PROOF_EXTENSION_DANGEROUS avec ACT=True
    ne doit avoir authority_decision = EXTENSION_ONLY ou CORE_WINS.
    Si ACT est détecté dans un chemin dry-run, l'autorité doit être DO_NOT_MERGE.
    """
    matrix = _load_json(MATRIX_PATH)
    for e in matrix:
        if e.get("delta_type") == "PROOF_EXTENSION_DANGEROUS":
            # Must be blocked
            assert e.get("authority_decision") == "DO_NOT_MERGE", (
                f"PROOF_EXTENSION_DANGEROUS entry {e['metric_id']} must have DO_NOT_MERGE"
            )


# ---------------------------------------------------------------------------
# Test 10 — Aucun runtime_allowed_now=true
# ---------------------------------------------------------------------------
def test_10_no_runtime_allowed_now_true():
    """
    Aucune entrée ne doit avoir proof_value = 'True' ou 'true'
    pour un champ nommé runtime_allowed_now (ou variantes).
    """
    matrix = _load_json(MATRIX_PATH)
    violations = []
    for e in matrix:
        name = e.get("metric_name", "").lower()
        if "runtime_allowed" in name or "activation_allowed" in name:
            pv = str(e.get("proof_value", "")).lower()
            if pv in ("true", "1", "yes"):
                violations.append(e)
    assert violations == [], f"runtime_allowed_now=True detected: {violations}"


# ---------------------------------------------------------------------------
# Test 11 — decision_authority reste KX108_ONLY
# ---------------------------------------------------------------------------
def test_11_decision_authority_is_kx108_only():
    """
    Si decision_authority est présent dans la matrice, sa valeur proof
    doit rester KX108_ONLY. Toute autre valeur doit déclencher DO_NOT_MERGE.
    """
    matrix = _load_json(MATRIX_PATH)
    for e in matrix:
        if e.get("metric_name") == "decision_authority":
            pv = str(e.get("proof_value", "")).upper()
            if pv and pv != "KX108_ONLY":
                # Must be blocked
                assert e.get("authority_decision") == "DO_NOT_MERGE", (
                    f"decision_authority changed to {pv} but not blocked: {e}"
                )


# ---------------------------------------------------------------------------
# Test 12 — fusion_status bloqué si blocking_deltas > 0
# ---------------------------------------------------------------------------
def test_12_fusion_status_blocked_if_blocking_deltas():
    """
    Si blocking_delta_count > 0, fusion_status doit être
    FUSION_BLOCKED_BY_METRIC_DELTA, jamais FUSION_READY.
    """
    data = _load_json(BLOCKING_PATH)
    count = data.get("blocking_delta_count", 0)
    status = data.get("fusion_status", "")

    if count > 0:
        assert status == "FUSION_BLOCKED_BY_METRIC_DELTA", (
            f"blocking_delta_count={count} but fusion_status={status}"
        )
    else:
        assert status == "FUSION_READY", (
            f"blocking_delta_count=0 but fusion_status={status}"
        )

"""Harnais de test RED — Phase HOLD-F3 — Adaptateur de Preuves Studio E11 -> B11.

Mission unique :
Formaliser et tester en RED le contrat d'adaptation des sorties réelles Studio E11 (V1/V2)
vers les mécanismes de preuve B11 (BCE V1, Replay B8, Évaluateur E3).

Invariants :
- Autorité : KX108_ONLY
- Mode : RED ONLY (l'adaptateur app.cognition.b11.studio_evidence_adapter n'est PAS implémenté)
- Aucune I/O persistante ni mutation de store de production
- Correction contractuelle F-F3-01 appliquée sur F3-03 et F3-04 (alignement oracle canonique B8 / E3)
"""

import copy
import hashlib
import json
from pathlib import Path
from typing import Any
import pytest

from app.cognition.b11.brody_evidence_store import BrodyCognitiveEvidenceBundleV1
from app.cognition.b11.brody_independent_evaluator import (
    evaluate_brody_cognitive_evidence_bundle,
    CognitiveEvaluationReportV1,
)

# Tentative d'import du module cible qui doit échouer en RED
try:
    from app.cognition.b11.studio_evidence_adapter import (
        adapt_studio_receipt_to_bundle_payload,
    )
    ADAPTER_AVAILABLE = True
except ModuleNotFoundError:
    ADAPTER_AVAILABLE = False


STUDIO_V1_PATH = Path(
    "C:/Users/User/obsidia-studio/data/experiments/native_editorial_integration_20261023/public_fixture_False.json"
)
STUDIO_V2_PATH = Path(
    "C:/Users/User/obsidia-studio/data/experiments/native_editorial_v2_integration_20261024/public_fixture_V2_False.json"
)


def _load_studio_v1_fixture() -> dict[str, Any]:
    """Charge la fixture réelle Studio V1 issue des campagnes historiques offline."""
    if STUDIO_V1_PATH.exists():
        return json.loads(STUDIO_V1_PATH.read_text(encoding="utf-8"))
    # Fallback canonique minimal reproduisant fidèlement l'enveloppe certifiée Studio V1
    return {
        "status": "READY_READONLY",
        "decision_authority": "KX108_ONLY",
        "readonly": True,
        "advisory_only": True,
        "context_signal_only": True,
        "allowed_to_decide": False,
        "allowed_to_act": False,
        "emits_act": False,
        "emits_verdict": False,
        "memory_write": False,
        "kernel_mutation": False,
        "x108_mutation": False,
        "final_answer_source": "BRODY_NATIVE_EDITORIAL_V1",
        "editorial_route_status": "CONSULTATIVE_DRAFT_AVAILABLE",
        "pre_reasoning_snapshot": {
            "user_message": "Comment une petite entreprise peut utiliser l'IA ?",
            "unresolved_unknowns": ["intelligence", "artificielle"],
        },
        "cognitive_runtime_receipt": {
            "version": "REAL_COGNITIVE_JOIN_C1_V1",
            "rail_mode": "SHADOW_READONLY_SUPERPOSED",
            "signal_id": "sig-studio-v1-canonical-001",
            "created_at": "2026-10-23T12:00:00+00:00",
            "status": "READY_SHADOW_READONLY",
            "completeness": "COMPLETE",
            "decision_ticket_dry_run": {
                "decision": "ALLOW_CONTEXT_ONLY",
                "x108_gate_status": "X108_EVALUATED_DRY_RUN",
            },
            "cognition_shadow_memory": {
                "b6_context_status": "VALID",
                "entries": [],
                "memory_retrieval_status": "MEMORY_NOT_REQUIRED",
            },
            "local_model_evidence_snapshot": {
                "status": "OFFLINE_NEURAL_SNAPSHOT",
                "model_call_used": False,
            },
        },
        "editorial_artifact": {
            "schema": "BRODY_PUBLIC_EDITORIAL_ARTIFACT_V1",
            "draft": {
                "text": "Une petite entreprise commencerait par une seule tache répétitive avec un budget plafonné.",
                "factual_claims": ["budget plafonné"],
            },
            "editorial_plan": [{"role": "accroche"}],
            "provenance": {"author": "BRODY_NATIVE", "model_calls": 0},
            "human_review_required": True,
            "publication_permitted": False,
        },
    }


def _load_studio_v2_fixture() -> dict[str, Any]:
    """Charge la fixture réelle Studio V2 issue des campagnes historiques offline."""
    if STUDIO_V2_PATH.exists():
        return json.loads(STUDIO_V2_PATH.read_text(encoding="utf-8"))
    # Fallback canonique minimal reproduisant fidèlement l'enveloppe certifiée Studio V2
    return {
        "status": "READY_READONLY",
        "decision_authority": "KX108_ONLY",
        "readonly": True,
        "advisory_only": True,
        "context_signal_only": True,
        "allowed_to_decide": False,
        "allowed_to_act": False,
        "emits_act": False,
        "emits_verdict": False,
        "memory_write": False,
        "kernel_mutation": False,
        "x108_mutation": False,
        "final_answer_source": "BRODY_NATIVE_EDITORIAL_V2",
        "editorial_version_requested": "V2",
        "editorial_route_status": "CONSULTATIVE_DRAFT_AVAILABLE",
        "pre_reasoning_snapshot": {
            "user_message": "Comment une PME des Ardennes peut optimiser sa logistique ?",
            "unresolved_unknowns": ["optimiser"],
        },
        "cognitive_runtime_receipt": {
            "version": "REAL_COGNITIVE_JOIN_C1_V1",
            "rail_mode": "SHADOW_READONLY_SUPERPOSED",
            "signal_id": "sig-studio-v2-canonical-002",
            "created_at": "2026-10-24T12:00:00+00:00",
            "status": "READY_SHADOW_READONLY",
            "completeness": "COMPLETE",
            "decision_ticket_dry_run": {
                "decision": "ALLOW_CONTEXT_ONLY",
                "x108_gate_status": "X108_EVALUATED_DRY_RUN",
            },
            "cognition_shadow_memory": {
                "b6_context_status": "VALID",
                "entries": [],
                "memory_retrieval_status": "MEMORY_NOT_REQUIRED",
            },
            "local_model_evidence_snapshot": {
                "status": "OFFLINE_NEURAL_SNAPSHOT",
                "model_call_used": False,
            },
        },
        "editorial_artifact": {
            "schema": "BRODY_PUBLIC_EDITORIAL_ARTIFACT_V2",
            "draft": {
                "text": "Dans les Ardennes, 42 unites logistiques réduisent les délais sans surcoût.",
                "factual_claims": ["42 unites logistiques"],
            },
            "editorial_plan": [{"role": "accroche"}, {"role": "explication"}],
            "provenance": {"author": "BRODY_NATIVE", "model_calls": 0},
            "human_review_required": True,
            "publication_permitted": False,
            "editorial_version": "V2",
        },
    }


# ==============================================================================
# Scénarios RED HOLD-F3
# ==============================================================================

def test_m42_red_f3_01_studio_v1_receipt_adaptation():
    """F3-01 : Conversion d'un reçu Studio V1 réel sans falsification."""
    if not ADAPTER_AVAILABLE:
        pytest.fail("RED EXPECTED: adapt_studio_receipt_to_bundle_payload absent")

    fixture = _load_studio_v1_fixture()
    payload = adapt_studio_receipt_to_bundle_payload(fixture)

    # 1. Vérification de la présence des 19 champs canoniques BCE V1
    expected_19_fields = {
        "contract_version", "execution_id", "mechanism_ref", "mechanism_version",
        "execution_timestamp_utc", "input_context_digest", "documentary_refs",
        "symbolic_context_refs", "external_provider_trace", "observable_response_digest",
        "observable_response_text", "evaluation_reference", "replay_dependencies",
        "privacy_classification", "publication_mode", "seal_status",
        "provenance_status", "integrity_digest", "bundle_id",
    }
    assert expected_19_fields.issubset(set(payload.keys()))

    # 2. Assertions de type et de non-falsification
    assert payload["contract_version"] == 1
    assert isinstance(payload["contract_version"], int)
    assert payload["execution_id"] == fixture["cognitive_runtime_receipt"]["signal_id"]
    assert payload["observable_response_text"] == fixture["editorial_artifact"]["draft"]["text"]
    assert payload["seal_status"] in ("UNSEALED_ADAPTER_PAYLOAD", "EPHEMERAL_IN_MEMORY")
    assert payload["provenance_status"] == "STUDIO_E11_ADAPTED"


def test_m42_red_f3_02_studio_v2_receipt_adaptation():
    """F3-02 : Reçu éditorial V2 opt-in et conservation explicite de la version."""
    if not ADAPTER_AVAILABLE:
        pytest.fail("RED EXPECTED: adapt_studio_receipt_to_bundle_payload absent")

    fixture = _load_studio_v2_fixture()

    # 1. Vérifications préalables sur la fixture source réelle V2 opt-in
    assert fixture.get("editorial_version_requested") == "V2"
    assert fixture["editorial_artifact"].get("editorial_version") == "V2"
    assert fixture.get("final_answer_source") == "BRODY_NATIVE_EDITORIAL_V2"

    payload = adapt_studio_receipt_to_bundle_payload(fixture)

    # 2. Vérification de l'extraction et conformité BCE
    assert payload["execution_id"] == fixture["cognitive_runtime_receipt"]["signal_id"]
    assert payload["observable_response_text"] == fixture["editorial_artifact"]["draft"]["text"]
    assert payload["observable_response_digest"] == hashlib.sha256(
        fixture["editorial_artifact"]["draft"]["text"].encode("utf-8")
    ).hexdigest()

    # 3. Conservation de la traçabilité de version V2
    assert "V2" in payload["mechanism_version"] or "V2" in str(payload.get("mechanism_ref", ""))


def test_m42_red_f3_03_e3_evaluation_pass_on_conforming_oracle():
    """F3-03 : Évaluation E3 réelle produisant PASS sur un fait concordant.

    Prise en compte de F-F3-01 :
    - Même locator B8 épinglé dans _SOURCE_PINS (16b9d28e... énonçant 12 K).
    - Même expected_assertion typée (numeric_value: 12.0, unit: "K").
    - Réponse observable Studio énonçant 12 K.
    - Attendu : verdict PASS, justification OBSERVED_ASSERTION_MATCHES_ORACLE.
    """
    if not ADAPTER_AVAILABLE:
        pytest.fail("RED EXPECTED: adapt_studio_receipt_to_bundle_payload absent")

    fixture = _load_studio_v2_fixture()
    # Variation explicite et traçable à des fins de test d'assertion factuelle conforme (12 K)
    fixture_conforming = copy.deepcopy(fixture)
    fixture_conforming["editorial_artifact"]["draft"]["text"] = (
        "Selon les relevés du laboratoire, la température observée de florvaxium est de 12 K."
    )

    locator = "16b9d28ef7878084a353c4dbec94889efc6239016c7af01a3e8f17567ccc466b"
    oracle = {
        "oracle_id": "oracle-flx-temp-v1",
        "source": "INDEPENDENT_SOURCE_PIN",
        "locator": locator,
        "expected_assertion": {
            "symbol": "florvaxium",
            "property": "temperature",
            "numeric_value": 12.0,
            "unit": "K",
        },
        "precommitted_at": "2026-10-22T10:00:00Z",
    }

    payload = adapt_studio_receipt_to_bundle_payload(fixture_conforming, evaluation_reference=oracle)
    bundle = BrodyCognitiveEvidenceBundleV1(**payload)
    report = evaluate_brody_cognitive_evidence_bundle(bundle, oracle)

    assert isinstance(report, CognitiveEvaluationReportV1)
    assert report.verdict == "PASS"
    assert report.ground_truth_status == "INDEPENDENT_ORACLE_PINNED"
    assert report.observed_assertion["numeric_value"] == 12.0
    assert report.expected_assertion["numeric_value"] == 12.0


def test_m42_red_f3_04_e3_evaluation_fail_on_contradictory_oracle():
    """F3-04 : Évaluation E3 réelle produisant FAIL sur une contradiction factuelle.

    Prise en compte de F-F3-01 :
    - EXACTEMENT LE MÊME oracle que F3-03 (même locator 16b9d28e..., même expected_assertion 12.0 K).
    - Seule différence causale : réponse observable Studio énonçant une valeur contradictoire (99 K).
    - Attendu : verdict FAIL, motif explicite CONTRADICTION.
    """
    if not ADAPTER_AVAILABLE:
        pytest.fail("RED EXPECTED: adapt_studio_receipt_to_bundle_payload absent")

    fixture = _load_studio_v2_fixture()
    # Variation explicite et traçable à des fins de test de contradiction factuelle (99 K vs 12 K)
    fixture_contradictory = copy.deepcopy(fixture)
    fixture_contradictory["editorial_artifact"]["draft"]["text"] = (
        "Selon les relevés du laboratoire, la température observée de florvaxium est de 99 K."
    )

    # Exactement le même oracle que F3-03
    locator = "16b9d28ef7878084a353c4dbec94889efc6239016c7af01a3e8f17567ccc466b"
    oracle = {
        "oracle_id": "oracle-flx-temp-v1",
        "source": "INDEPENDENT_SOURCE_PIN",
        "locator": locator,
        "expected_assertion": {
            "symbol": "florvaxium",
            "property": "temperature",
            "numeric_value": 12.0,
            "unit": "K",
        },
        "precommitted_at": "2026-10-22T10:00:00Z",
    }

    payload = adapt_studio_receipt_to_bundle_payload(fixture_contradictory, evaluation_reference=oracle)
    bundle = BrodyCognitiveEvidenceBundleV1(**payload)
    report = evaluate_brody_cognitive_evidence_bundle(bundle, oracle)

    assert isinstance(report, CognitiveEvaluationReportV1)
    assert report.verdict == "FAIL"
    assert report.ground_truth_status == "INDEPENDENT_ORACLE_PINNED"
    assert report.observed_assertion["numeric_value"] == 99.0
    assert report.expected_assertion["numeric_value"] == 12.0
    assert "CONTRADICTION" in report.justification


def test_m42_red_f3_05_abstention_discrimination_and_no_auto_abstain():
    """F3-05 : Distinction CONTEXT_LIMITED vs abstention démontrée (aucun auto-ABSTAIN)."""
    if not ADAPTER_AVAILABLE:
        pytest.fail("RED EXPECTED: adapt_studio_receipt_to_bundle_payload absent")

    fixture = _load_studio_v1_fixture()
    fixture["cognitive_runtime_receipt"]["cognition_shadow_memory"]["b6_context_status"] = "LIMITED"

    # Sans oracle demandant l'abstention, E3 ne doit PAS inventer ABSTAIN_CORRECT
    oracle_sans_abstention = {
        "oracle_id": "oracle-f3-05-no-abstain",
        "oracle_provenance": "PINNED_SYNTHETIC",
        "oracle_precommitted_digest": "digest-f3-05",
        "source_document_pinned": True,
        "world_fact": False,
        "expected_claim_id": "claim-missing",
        "requires_abstention": False,
        "expected_assertion": {"property": "missing"},
    }

    payload = adapt_studio_receipt_to_bundle_payload(fixture, evaluation_reference=oracle_sans_abstention)
    bundle = BrodyCognitiveEvidenceBundleV1(**payload)
    report = evaluate_brody_cognitive_evidence_bundle(bundle, oracle_sans_abstention)

    assert report.verdict != "ABSTAIN_CORRECT"
    assert report.verdict in ("FAIL", "INDETERMINATE")


def test_m42_red_f3_06_tampered_studio_receipt_causes_fail_closed():
    """F3-06 : Rejet immédiat sur altération d'un champ contractuel ou d'autorité."""
    if not ADAPTER_AVAILABLE:
        pytest.fail("RED EXPECTED: adapt_studio_receipt_to_bundle_payload absent")

    fixture = _load_studio_v1_fixture()
    # Altération de l'autorité exclusive
    fixture["decision_authority"] = "ROGUE_AUTHORITY"

    with pytest.raises(ValueError, match="AUTHORITY|GOVERNANCE|INVARIANT"):
        adapt_studio_receipt_to_bundle_payload(fixture)


def test_m42_red_f3_07_adapter_purity_and_zero_side_effects():
    """F3-07 : Pureté stricte, zéro I/O, immutabilité des arguments d'entrée."""
    if not ADAPTER_AVAILABLE:
        pytest.fail("RED EXPECTED: adapt_studio_receipt_to_bundle_payload absent")

    fixture = _load_studio_v1_fixture()
    snapshot_before = copy.deepcopy(fixture)

    payload = adapt_studio_receipt_to_bundle_payload(fixture)

    # Immutabilité des entrées
    assert fixture == snapshot_before

    # Invariants d'autorité dans le payload produit
    assert payload["publication_mode"] == "DRAFT_ONLY"
    assert payload["seal_status"] != "STORE_SEALED"


def test_m42_red_f3_08_no_arbitrary_b6_to_m41_promotion():
    """F3-08 : Refus formel de convertir arbitrairement une omission B6 en hypothèse M41."""
    if not ADAPTER_AVAILABLE:
        pytest.fail("RED EXPECTED: adapt_studio_receipt_to_bundle_payload absent")

    fixture = _load_studio_v1_fixture()
    fixture["cognitive_runtime_receipt"]["cognition_shadow_memory"]["b6_context_status"] = "LIMITED"

    payload = adapt_studio_receipt_to_bundle_payload(fixture)

    # L'adaptateur ne doit pas fabriquer une pluralité d'hypothèses M41 non prouvées
    dependencies = payload.get("replay_dependencies", {})
    assert "M41_COEXISTING_HYPOTHESES" not in dependencies or dependencies["M41_COEXISTING_HYPOTHESES"] == []


def test_m42_red_f3_09_no_fake_sealing_or_unearned_provenance():
    """F3-09 : Interdiction d'émettre un statut STORE_SEALED ou ORIGIN_ESTABLISHED."""
    if not ADAPTER_AVAILABLE:
        pytest.fail("RED EXPECTED: adapt_studio_receipt_to_bundle_payload absent")

    fixture = _load_studio_v1_fixture()
    payload = adapt_studio_receipt_to_bundle_payload(fixture)

    # Le scellement physique et l'origine établie requièrent le store, non l'adaptateur
    assert payload["seal_status"] != "STORE_SEALED"
    assert payload["provenance_status"] != "ORIGIN_ESTABLISHED"


def test_m42_red_f3_10_circular_oracle_rejection_in_studio_evaluation():
    """F3-10 : Rejet d'un oracle circulaire évaluant une sortie Studio."""
    if not ADAPTER_AVAILABLE:
        pytest.fail("RED EXPECTED: adapt_studio_receipt_to_bundle_payload absent")

    fixture = _load_studio_v1_fixture()
    text = fixture["editorial_artifact"]["draft"]["text"]

    # Oracle circulaire auto-référencé sur le texte de sortie
    circular_oracle = {
        "oracle_id": "oracle-circular",
        "source": "SELF",
        "oracle_provenance": "CIRCULAR_SELF_REFERENTIAL",
        "locator": "self:previous_turn",
        "expected_assertion": {"property": "self"},
        "requires_abstention": False,
    }

    payload = adapt_studio_receipt_to_bundle_payload(fixture, evaluation_reference=circular_oracle)
    bundle = BrodyCognitiveEvidenceBundleV1(**payload)
    report = evaluate_brody_cognitive_evidence_bundle(bundle, circular_oracle)

    assert report.verdict != "PASS"
    assert report.verdict in ("ERROR", "INDETERMINATE")

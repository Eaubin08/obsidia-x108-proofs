"""M42 B11 Compétence & Calibration — Harnais RED Observation Cognitive Brody V1.

Scénarios RED BRO-01 à BRO-12 discriminants.
Conforme à docs/architecture/M42_B11_BRODY_COGNITIVE_OBSERVATION_SPEC_V1.md.

Garanties RED :
- Vérifie les assertions préalables sur les composants réels existants (brody_real_cognitive_join,
  brody_cognitive_resolution, B7, M41, B8, SENS).
- Interdit formellement l'accès réseau en test (socket/urllib bloqués).
- Échoue de manière discriminante (EXPECTED RED) sur l'absence du module
  app.cognition.b11.brody_observation_adapter.
- Ne mutile aucun fichier de production, ne pollue aucun store scellé.
"""
from __future__ import annotations

import copy
import hashlib
import json
import socket
import sys
import urllib.error
import urllib.request
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from app.cognition.b11.contracts import (  # noqa: E402
    B11_EFFECTS,
    CompetenceRegime,
    ContextualCompetenceProfile,
)
from app.knowledge import b8  # noqa: E402
import app.cognition.b7 as b7  # noqa: E402
import app.world_model as wm  # noqa: E402
from app.harness.state_explicit.contracts import StateEntry, StateStatus, Visibility  # noqa: E402
from apps.obsidia_api.brody_real_cognitive_join import (  # noqa: E402
    BOUNDARY as BRODY_JOIN_BOUNDARY,
    VERSION as BRODY_JOIN_VERSION,
    run_real_cognitive_join,
)
from apps.obsidia_api.brody_cognitive_resolution import (  # noqa: E402
    BOUNDARY as BRODY_RESOLUTION_BOUNDARY,
    DocumentaryEvidence,
    ResolutionContext,
    ResolutionServices,
    run_cognitive_resolution,
)
from tests.integration_cognition.two_encounter_support import (  # noqa: E402
    BOUNDARY as FIXTURE_BOUNDARY,
    NOW,
    QUESTION1,
    SCOPE,
    STATEMENT,
    SYMBOL,
    digest,
    source_document,
    SOURCE_PINS,
)
from tests.b7.conftest import make_entry  # noqa: E402


# ============================================================================
# Garde réseau stricte (hors réseau obligatoire)
# ============================================================================


@pytest.fixture(autouse=True)
def offline_guard(monkeypatch):
    """Interdit tout transport réseau durant l'exécution des tests B11."""
    def forbidden(*args, **kwargs):
        raise AssertionError("NETWORK_ACCESS_FORBIDDEN_IN_B11_TESTS")

    monkeypatch.setattr(socket.socket, "connect", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(urllib.request, "urlopen", forbidden)


# ============================================================================
# Lazy loader RED
# ============================================================================


def _rt_brody_adapter():
    """Lazy loader pour le module d'observation cognitive Brody V1.

    Échoue en RED certifié lorsque le module ou ses fonctions sont absents
    de app.cognition.b11.
    """
    try:
        import app.cognition.b11.brody_observation_adapter as boa

        if hasattr(boa, "evaluate_brody_cognitive_observation"):
            return boa
    except ImportError:
        pass
    pytest.fail(
        "M42 B11 BRODY COGNITIVE OBSERVATION ADAPTER NOT IMPLEMENTED (EXPECTED RED: "
        "app.cognition.b11.brody_observation_adapter.evaluate_brody_cognitive_observation)"
    )


# ============================================================================
# Scénarios RED BRO-01 à BRO-12
# ============================================================================


def test_m42_red_bro_01_valid_ephemeral_receipt_structural_only():
    """BRO-01: Reçu HTTP bien formé produit en mémoire vive (fastpath/join).
    Pré-assertion : le reçu réel est produit, contient les champs BOUNDARY et VERSION.
    Attendu : reconnu comme STRUCTURALLY_VALIDATED, mais rejeté pour caractérisation
    historique scellée (EPHEMERAL_UNSEALED).
    """
    receipt = run_real_cognitive_join(
        message="Bonjour Brody",
        language="fr",
        session_id="session-bro-01",
    )

    # Pré-assertions sur le producteur existant
    assert isinstance(receipt, dict)
    assert receipt["version"] == BRODY_JOIN_VERSION
    assert receipt["rail_mode"] == "SHADOW_READONLY_SUPERPOSED"
    assert receipt["status"] in ("READY_SHADOW_READONLY", "BLOCKED_READONLY")
    assert receipt["decision_authority"] == "KX108_ONLY"
    assert receipt["readonly"] is True
    assert "signal_id" in receipt

    # Appel au composant cible (échoue en RED)
    adapter = _rt_brody_adapter()
    obs = adapter.evaluate_brody_cognitive_observation(
        receipt=receipt,
        context_family="COGNITIVE_SYNTHESIS",
    )

    assert obs.structural_validation_status == "VALID"
    assert obs.integrity_verification_status == "EPHEMERAL_UNSEALED"
    assert obs.evaluation_outcome == "INDETERMINATE"


def test_m42_red_bro_02_forged_or_self_attested_receipt_rejected():
    """BRO-02: Dictionnaire forgé injecté prétendant porter evaluation_outcome='PASS'.
    Attendu : rejet fail-closed immédiat (SELF_ATTESTATION_REJECTED / FORGED_RECEIPT_REJECTED),
    aucune promotion de preuve accordée.
    """
    forged_receipt = {
        "version": "REAL_COGNITIVE_JOIN_C1_V1",
        "signal_id": "forged-signal-123",
        "status": "READY_SHADOW_READONLY",
        "evaluation_outcome": "PASS",
        "is_verified": True,
        "trusted_by": "SELF",
    }

    adapter = _rt_brody_adapter()
    obs = adapter.evaluate_brody_cognitive_observation(
        receipt=forged_receipt,
        context_family="COGNITIVE_SYNTHESIS",
    )

    assert obs.structural_validation_status == "INVALID"
    assert "SELF_ATTESTATION_REJECTED" in obs.evaluation_notes
    assert obs.evaluation_outcome == "ERROR"


def test_m42_red_bro_03_correct_response_evaluated_against_independent_reference():
    """BRO-03: Réponse cognitive confrontée à un document source synthétique indépendant.
    Pré-assertion : SOURCE_PINS fournit un document source indépendant du modèle.
    Attendu : PASS borné strictement à la tâche et au document testé.
    """
    doc = source_document(statement=STATEMENT, scope=SCOPE, version=1)
    doc_digest = digest(doc)
    assert doc_digest in SOURCE_PINS

    # Construction d'un claim corroboré
    ref = f"doc:{doc_digest}"
    slot = b8.knowledge_slot_id(b8.ClaimClass.DOCUMENTARY_CLAIM, "fixture", [SYMBOL], [SCOPE], "meaning")
    valid_time = b8.ValidTimeInterval(b8.TemporalFrameRef(SCOPE), 0, None)
    claim = b8.KnowledgeClaim(
        f"fixture:{SYMBOL}-lineage",
        1,
        None,
        b8.ClaimClass.DOCUMENTARY_CLAIM,
        slot,
        valid_time,
        {"symbol": SYMBOL, "statement": STATEMENT, "scope": SCOPE, "category": "LEXICAL_SEMANTIC_BINDING"},
        source_refs=(ref,),
    )
    ev = b8.EvidenceRef(
        "DOCUMENT",
        ref,
        doc_digest,
        NOW,
        ("fixture:registry",),
        claim.claim_id,
        1,
    )
    ver = b8.VerificationRecord(
        "SOURCE_PROVENANCE_VERIFIER",
        claim.claim_id,
        1,
        b8.VerificationVerdict.SATISFIED,
        (ev.identity,),
        "fixture:exact-doc-verifier",
        NOW,
    )
    bundle = DocumentaryEvidence(claim=claim, evidence=ev, verification=ver, source_verified=True)

    adapter = _rt_brody_adapter()
    obs = adapter.evaluate_brody_cognitive_observation(
        bundles=(bundle,),
        candidate_response=STATEMENT,
        ground_truth_pin=doc,
        context_family="DOCUMENTARY_VERIFICATION",
    )

    assert obs.evaluation_outcome == "PASS"
    assert obs.ground_truth_status == "INDEPENDENT_ORACLE_PINNED"
    assert obs.documentary_status == "CORROBORATED"


def test_m42_red_bro_04_structurally_compliant_but_cognitively_false_response():
    """BRO-04: Réponse structurellement conforme mais fausse factuellement selon l'oracle.
    Pré-assertion : la réponse est bien formée, mais affirme une valeur contredite par l'oracle.
    Attendu : conformité structurelle VALID, mais evaluation_outcome == FAIL.
    """
    doc = source_document(statement="La température de florvaxium est de 12 K.", scope=SCOPE)
    false_statement = "La température de florvaxium est de 999 K."

    adapter = _rt_brody_adapter()
    obs = adapter.evaluate_brody_cognitive_observation(
        candidate_response=false_statement,
        ground_truth_pin=doc,
        context_family="DOCUMENTARY_VERIFICATION",
    )

    assert obs.structural_validation_status == "VALID"
    assert obs.evaluation_outcome == "FAIL"
    assert "FACTUAL_CONTRADICTION" in obs.evaluation_notes


def test_m42_red_bro_05_ambiguity_maintained_under_oracle_confirming_abstention():
    """BRO-05: Ambiguïté B7/M41 maintenue face à une coréférence multiple.
    Pré-assertion : SENS entry contient une ambiguïté explicite non résolue sans vainqueur.
    Attendu : ABSTAIN_CORRECT uniquement parce que l'oracle confirme que l'entrée est ambiguë.
    """
    ambig_entry = make_entry(
        raw="Le script est pret. Lance-le.",
        unresolved_references=("u2:le",),
        units=("u1", "u2"),
        uncertainty=("unresolved_reference:u2:le", "other_open_item"),
        unit_objects={"u1": ["le script"]},
    )
    assert ambig_entry.status == StateStatus.OPEN
    assert "unresolved_reference:u2:le" in ambig_entry.uncertainty

    mat_ref = wm.WorldMaterialRef(
        ref_kind="sens.event_ref",
        ref_id=ambig_entry.state_id,
        source_label="sens:frame",
    )
    subj_ref = wm.WorldMaterialRef(
        ref_kind="sens.mention_ref",
        ref_id="u2:le",
        source_label="sens:frame",
    )
    hyp1 = wm.WorldStateHypothesis(
        hypothesis_kind="REFERENT_IDENTITY",
        presumed_referent_ref=subj_ref,
        material_refs=(mat_ref,),
        modality_label="brody.candidate",
        unknowns=("other_open_item",),
    )
    hyp2 = wm.WorldStateHypothesis(
        hypothesis_kind="REFERENT_IDENTITY",
        presumed_referent_ref=subj_ref,
        material_refs=(mat_ref,),
        modality_label="brody.unresolved",
        unknowns=("unresolved_referent_context",),
    )
    hypotheses = wm.WorldHypothesisSet(subject_ref=subj_ref, members=(hyp1, hyp2))
    assert len(hypotheses.members) == 2

    oracle = {"requires_abstention": True, "reason": "COEXISTING_HYPOTHESES_WITHOUT_DISCRIMINANT"}

    adapter = _rt_brody_adapter()
    obs = adapter.evaluate_brody_cognitive_observation(
        hypothesis_set=hypotheses,
        oracle=oracle,
        context_family="AMBIGUITY_RESOLUTION",
    )

    assert obs.expressed_uncertainty_status == "AMBIGUOUS_COEXISTING_HYPOTHESES"
    assert obs.evaluation_outcome == "ABSTAIN_CORRECT"

    # Contrôles de régression discriminante F-BRO-01 :
    # B. Faux conteneur non canonique avec members=("faux1", "faux2") rejeté fail-closed
    class _HostileFakeHypothesisSet:
        members = ("faux1", "faux2")
        set_id = "hostile-set-fake"

    hostile_obs = adapter.evaluate_brody_cognitive_observation(
        hypothesis_set=_HostileFakeHypothesisSet(),
        oracle=oracle,
        context_family="AMBIGUITY_RESOLUTION",
    )
    assert hostile_obs.structural_validation_status == "INVALID"
    assert hostile_obs.evaluation_outcome == "ERROR"
    assert "INVALID_M41_HYPOTHESIS_SET" in hostile_obs.evaluation_notes

    # C. Conteneur duck-typé avec membres scalaires non-WorldStateHypothesis rejeté
    class _DuckTypingHypothesisSet:
        members = [1, 2, 3]
        set_id = "duck-set-invalid"

    duck_obs = adapter.evaluate_brody_cognitive_observation(
        hypothesis_set=_DuckTypingHypothesisSet(),
        oracle=oracle,
        context_family="AMBIGUITY_RESOLUTION",
    )
    assert duck_obs.structural_validation_status == "INVALID"
    assert duck_obs.evaluation_outcome == "ERROR"
    assert "INVALID_M41_HYPOTHESIS_SET" in duck_obs.evaluation_notes

    # D. Absence de hypothesis_set n'affecte pas le comportement nominal
    noop_obs = adapter.evaluate_brody_cognitive_observation(
        hypothesis_set=None,
        oracle=None,
        context_family="AMBIGUITY_RESOLUTION",
    )
    assert noop_obs.evaluation_outcome == "INDETERMINATE"


def test_m42_red_bro_06_abstention_without_independent_reference_is_indeterminate():
    """BRO-06: Abstention observée (CLARIFICATION_HOLD) en l'absence d'oracle indépendant.
    Attendu : INDETERMINATE. Refus absolu de prononcer ABSTAIN_CORRECT ou FAIL sans oracle.
    """
    receipt = {
        "status": "CLARIFICATION_HOLD",
        "hold_reason": "UNRESOLVED_UNKNOWN_DETECTED",
        "decision_authority": "KX108_ONLY",
        "readonly": True,
    }

    adapter = _rt_brody_adapter()
    obs = adapter.evaluate_brody_cognitive_observation(
        receipt=receipt,
        ground_truth_pin=None,
        context_family="AMBIGUITY_RESOLUTION",
    )

    assert obs.expressed_uncertainty_status == "CLARIFICATION_HOLD"
    assert obs.ground_truth_status == "MISSING"
    assert obs.evaluation_outcome == "INDETERMINATE"


def test_m42_red_bro_07_documentary_contradiction_detection():
    """BRO-07: Contradiction documentaire B8 explicite.
    Pré-assertion : DOCUMENT_ASSERTION_CONTRADICTED est détecté par B8.
    Attendu : rejet de l'admission en mémoire et échec de corroboration.
    """
    contradictory_doc = source_document(statement="La température est de 12 K.", version=1)
    contra_ref = f"doc:{digest(contradictory_doc)}"
    slot = b8.knowledge_slot_id(b8.ClaimClass.DOCUMENTARY_CLAIM, "fixture", [SYMBOL], [SCOPE], "temperature")
    valid_time = b8.ValidTimeInterval(b8.TemporalFrameRef(SCOPE), 0, None)
    contradicted_claim = b8.KnowledgeClaim(
        "fixture:contradicted-temp-lineage",
        1,
        None,
        b8.ClaimClass.DOCUMENTARY_CLAIM,
        slot,
        valid_time,
        {"symbol": SYMBOL, "statement": "La température est de 300 K.", "scope": SCOPE},
        source_refs=(contra_ref,),
    )

    adapter = _rt_brody_adapter()
    obs = adapter.evaluate_brody_cognitive_observation(
        candidate_claim=contradicted_claim,
        ground_truth_pin=contradictory_doc,
        context_family="DOCUMENTARY_VERIFICATION",
    )

    assert obs.documentary_status == "CONTRADICTED"
    assert obs.evaluation_outcome == "FAIL"


def test_m42_red_bro_08_external_provider_call_traceable_without_causal_inference():
    """BRO-08: Consultation d'un fournisseur externe (Qwen) traçable.
    Attendu : external_provider_called == True, attribution_status == STACK_PLUS_EXTERNAL_MODEL,
    mais aucune attribution causale d'intelligence ou de souveraineté accordée au modèle.
    """
    receipt = {
        "version": "REAL_COGNITIVE_JOIN_C1_V1",
        "model_calls": 1,
        "local_model_evidence_applied": True,
        "local_model_evidence_status": "GENERATION_SUCCESS",
        "external_model": "qwen-2.5-72b",
        "decision_authority": "KX108_ONLY",
        "readonly": True,
    }

    adapter = _rt_brody_adapter()
    obs = adapter.evaluate_brody_cognitive_observation(
        receipt=receipt,
        context_family="COGNITIVE_SYNTHESIS",
    )

    assert obs.external_provider_called is True
    assert obs.external_provider_model == "qwen-2.5-72b"
    assert obs.attribution_status == "STACK_PLUS_EXTERNAL_MODEL"


def test_m42_red_bro_09_circular_or_self_referential_oracle_rejected():
    """BRO-09: Oracle de test auto-référent dérivé de la réponse même de Brody.
    Attendu : détection de circularité (CIRCULAR_SELF_REFERENTIAL) et rejet de l'évaluation.
    """
    candidate_answer = "Le florvaxium se stabilise à 12 K."
    circular_oracle = {"statement": candidate_answer, "source": "BRODY_PREVIOUS_OUTPUT"}

    adapter = _rt_brody_adapter()
    obs = adapter.evaluate_brody_cognitive_observation(
        candidate_response=candidate_answer,
        ground_truth_pin=circular_oracle,
        context_family="DOCUMENTARY_VERIFICATION",
    )

    assert obs.ground_truth_status == "CIRCULAR_SELF_REFERENTIAL"
    assert obs.evaluation_outcome == "ERROR"
    assert "TAUTOLOGICAL_ORACLE_REJECTED" in obs.evaluation_notes


def test_m42_red_bro_10_cross_mechanism_attribution_rail_a_to_brody_rejected():
    """BRO-10: Observation Rail A (tooling_build) soumise à l'adaptateur Brody.
    Attendu : rejet d'attribution stricte CAUSAL_ATTRIBUTION_MISMATCH.
    """
    rail_a_obs_payload = {
        "domain": "tooling_build",
        "task_ref": "UPDATE_TARGET_FROM_SOURCE",
        "executing_mechanism_ref": "rail_a:governed_content_apply:UPDATE_TARGET_FROM_SOURCE",
        "mutated_target_path": "src/target.py",
        "verified_execution_outcome": "VERIFIED_TEST_CONTRACT_PASS",
    }

    adapter = _rt_brody_adapter()
    obs = adapter.evaluate_brody_cognitive_observation(
        receipt=rail_a_obs_payload,
        context_family="COGNITIVE_SYNTHESIS",
    )

    assert obs.evaluation_outcome == "ERROR"
    assert "CAUSAL_ATTRIBUTION_MISMATCH" in obs.evaluation_notes


def test_m42_red_bro_11_unpinned_context_unestablished_replay():
    """BRO-11: Reçu produit sans contexte d'entrée ou graines épinglées.
    Attendu : replay_status == NOT_REPLAYABLE.
    """
    unpinned_receipt = {
        "version": "REAL_COGNITIVE_JOIN_C1_V1",
        "signal_id": "unpinned-signal",
        "input_context_digest": None,
        "source_routing_signal_snapshot": None,
    }

    adapter = _rt_brody_adapter()
    obs = adapter.evaluate_brody_cognitive_observation(
        receipt=unpinned_receipt,
        context_family="COGNITIVE_SYNTHESIS",
    )

    assert obs.replay_status == "NOT_REPLAYABLE"


def test_m42_red_bro_12_b11_effects_invariance_and_unknown_competence():
    """BRO-12: Invariance stricte de gouvernance B11_EFFECTS et UNKNOWN_COMPETENCE.
    Attendu : maintien absolu de UNKNOWN_COMPETENCE, confidence_score == 0.0,
    reliability_score is None, calibration_metric is None, et B11_EFFECTS inviolé.
    """
    assert B11_EFFECTS["memory_write"] is False
    assert B11_EFFECTS["emits_act"] is False
    assert B11_EFFECTS["kernel_mutation"] is False
    assert B11_EFFECTS["decision_authority"] == "KX108_ONLY"
    assert B11_EFFECTS["b12_selection"] is False

    adapter = _rt_brody_adapter()
    profile = adapter.project_b11_competence_profile(
        observations=(),
        domain="cognition",
        task_ref="COGNITIVE_RESOLUTION",
    )

    assert profile.competence_regime == CompetenceRegime.UNKNOWN_COMPETENCE
    assert profile.confidence_score == 0.0
    assert profile.reliability_score is None
    assert profile.calibration_metric is None

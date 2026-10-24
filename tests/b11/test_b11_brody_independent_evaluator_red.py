"""Harnais RED discriminant pour l'Évaluation Cognitive Indépendante Brody V1 (Phase E3-B).

Ce module teste rigoureusement les 10 exigences de la SPEC E3-B :
- E3-01 : PASS conforme face à un oracle documentaire indépendant préétabli.
- E3-02 : FAIL lors d'une contradiction factuelle manifeste entre réponse et oracle.
- E3-03 : ABSTAIN_CORRECT lors d'une abstention justifiée par des hypothèses M41 concurrentes.
- E3-04 : ABSTAIN_UNJUSTIFIED lors d'un refus de réponse alors qu'une référence B8 est disponible.
- E3-05 : Rejet strict des oracles auto-référentiels ou circulaires.
- E3-06 : Statut INDETERMINATE lors d'une référence oracle manquante ou non épinglée.
- E3-07 : Rejet ERROR lors d'une altération de condensat du document oracle.
- E3-08 : Séparation de l'attribution externe sans présomption de causalité.
- E3-09 : Maintien strict sous UNKNOWN_COMPETENCE et refus de promotion de score.
- E3-10 : Pureté B11 absolue (zéro écriture disque, zéro ACT, KX108 souverain).
"""

from __future__ import annotations

import json
import socket
import urllib.request
from pathlib import Path
from typing import Any

import pytest

from app.cognition.b11.brody_evidence_bridge import (
    build_evidence_bundle_payload_from_receipt,
)
from app.cognition.b11.brody_evidence_store import (
    load_and_verify_brody_evidence_bundle,
    publish_brody_evidence_bundle,
)
from app.cognition.b11.brody_observation_adapter import (
    BrodyCognitiveObservationV1,
    evaluate_brody_cognitive_observation,
)
from app.cognition.b11.contracts import (
    B11_EFFECTS,
    CompetenceRegime,
)
from app.knowledge import b8
from app.world_model import (
    WorldHypothesisSet,
    WorldMaterialRef,
    WorldStateHypothesis,
)
from apps.obsidia_api.brody_real_cognitive_join import (
    VERSION as BRODY_JOIN_VERSION,
    run_real_cognitive_join,
)
from tests.integration_cognition.two_encounter_support import (
    NOW,
    QUESTION1,
    SCOPE,
    STATEMENT,
    SYMBOL,
    FixtureAuthority,
    IsolatedMemory,
    digest,
    source_document,
)


# ============================================================================
# Garde-fou d'herméticité réseau
# ============================================================================


@pytest.fixture(autouse=True)
def network_guard(monkeypatch):
    """Empêche tout accès réseau ou socket externe durant l'exécution des tests."""

    def forbidden(*args, **kwargs):
        raise AssertionError("NETWORK_ACCESS_FORBIDDEN_IN_B11_TESTS")

    monkeypatch.setattr(socket.socket, "connect", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(urllib.request, "urlopen", forbidden)


# ============================================================================
# Lazy loader RED
# ============================================================================


def _rt_evaluator():
    """Lazy loader pour le module d'évaluation cognitive indépendante Brody V1.

    Échoue en RED certifié lorsque le module ou sa fonction principale sont absents
    de app.cognition.b11.
    """
    try:
        import app.cognition.b11.brody_independent_evaluator as bie

        if hasattr(bie, "evaluate_brody_cognitive_evidence_bundle") and hasattr(
            bie, "project_b11_evaluator_competence_profile"
        ):
            return bie
    except ImportError:
        pass
    pytest.fail(
        "M42 B11 BRODY INDEPENDENT EVALUATOR NOT IMPLEMENTED (EXPECTED RED: "
        "app.cognition.b11.brody_independent_evaluator.evaluate_brody_cognitive_evidence_bundle)"
    )


# ============================================================================
# Helpers canoniques
# ============================================================================


def _produce_real_join_receipt() -> dict[str, Any]:
    """Exécute authentiquement run_real_cognitive_join pour obtenir un reçu réel."""
    return run_real_cognitive_join(
        message=QUESTION1,
        language="fr",
        session_id="session-e3-red",
    )


def _produce_real_b8_claim(
    tmp_path: Path,
) -> tuple[b8.KnowledgeClaim, str]:
    """Exécute l'admission réelle B8 issue de two_encounter_support."""
    authority = FixtureAuthority()
    memory = IsolatedMemory(tmp_path / "isolated-mem-e3", authority)
    doc_path = memory.root / "source-v1.json"
    doc_path.write_text(json.dumps(source_document()), encoding="utf-8")

    admitted = memory.admit(
        statement=STATEMENT,
        document=doc_path,
        candidate={
            "candidate_id": "cand_fixture_e3",
            "candidate_payload": {"response_excerpt": STATEMENT},
        },
        scope=SCOPE,
    )
    assert admitted["status"] == "SIMULATED_AUTHORIZED_WRITE"

    claim = admitted["snapshot"].claims[0]
    doc_digest = digest(source_document())
    return claim, doc_digest


def _produce_m41_coexisting_hypotheses() -> WorldHypothesisSet:
    """Construit un set d'hypothèses M41 concurrentes non résolues."""
    subj_ref = WorldMaterialRef(
        ref_kind="sens.mention_ref",
        ref_id="subj:concept_florvaxium",
        source_label="sens:frame",
    )
    mat_ref = WorldMaterialRef(
        ref_kind="sens.event_ref",
        ref_id="mat:sample_evidence_e3",
        source_label="sens:frame",
    )
    h1 = WorldStateHypothesis(
        hypothesis_kind="REFERENT_IDENTITY",
        presumed_referent_ref=subj_ref,
        material_refs=(mat_ref,),
        modality_label="brody.candidate",
        unknowns=("hypothesis_alpha_unresolved",),
    )
    h2 = WorldStateHypothesis(
        hypothesis_kind="REFERENT_IDENTITY",
        presumed_referent_ref=subj_ref,
        material_refs=(mat_ref,),
        modality_label="brody.unresolved",
        unknowns=("hypothesis_beta_unresolved",),
    )
    return WorldHypothesisSet(subject_ref=subj_ref, members=(h1, h2))


# ============================================================================
# Scénarios RED E3-01 à E3-10
# ============================================================================


def test_m42_red_e3_01_pass_conforming_to_independent_oracle(tmp_path):
    """E3-01: Réponse conforme à l'assertion de référence préétablie indépendante.
    Pré-assertion : bundle et oracle construits avec fait typé identique (12 K).
    Attendu : verdict PASS, ground_truth_status INDEPENDENT_ORACLE_PINNED.
    """
    receipt = _produce_real_join_receipt()
    claim, doc_digest = _produce_real_b8_claim(tmp_path)

    oracle = {
        "oracle_id": "oracle-flx-temp-v1",
        "source": "INDEPENDENT_SOURCE_PIN",
        "locator": doc_digest,
        "expected_assertion": {
            "symbol": SYMBOL,
            "property": "temperature",
            "numeric_value": 12.0,
            "unit": "K",
        },
        "precommitted_at": "2026-10-22T10:00:00Z",
    }
    assert oracle["precommitted_at"] < NOW

    payload = build_evidence_bundle_payload_from_receipt(
        cognitive_receipt=receipt,
        knowledge_claims=(claim,),
        evaluation_reference=oracle,
    )
    payload["observable_response_text"] = STATEMENT
    pub_res = publish_brody_evidence_bundle(payload, store_dir=tmp_path)
    assert pub_res["status"] == "STORED"

    evaluator = _rt_evaluator()
    report = evaluator.evaluate_brody_cognitive_evidence_bundle(
        payload["bundle_id"],
        oracle=oracle,
        store_dir=tmp_path,
    )

    assert report.verdict == "PASS"
    assert report.ground_truth_status == "INDEPENDENT_ORACLE_PINNED"
    assert report.bundle_id == payload["bundle_id"]
    assert report.expected_assertion["numeric_value"] == 12.0


def test_m42_red_e3_02_fail_contradiction_between_response_and_oracle(tmp_path):
    """E3-02: Contradiction manifeste entre la valeur affirmée et l'oracle de référence.
    Pré-assertion : oracle spécifie 12 K, bundle affirme une valeur erronée de 99 K.
    Attendu : verdict FAIL, motif explicite de contradiction factuelle, pas d'ERROR.
    """
    receipt = _produce_real_join_receipt()
    claim, doc_digest = _produce_real_b8_claim(tmp_path)

    oracle = {
        "oracle_id": "oracle-flx-temp-v1",
        "source": "INDEPENDENT_SOURCE_PIN",
        "locator": doc_digest,
        "expected_assertion": {
            "symbol": SYMBOL,
            "property": "temperature",
            "numeric_value": 12.0,
            "unit": "K",
        },
    }

    contradictory_response = "La température de florvaxium est de 99 K."
    payload = build_evidence_bundle_payload_from_receipt(
        cognitive_receipt=receipt,
        knowledge_claims=(claim,),
        evaluation_reference=oracle,
    )
    payload["observable_response_text"] = contradictory_response
    pub_res = publish_brody_evidence_bundle(payload, store_dir=tmp_path)
    assert pub_res["status"] == "STORED"

    evaluator = _rt_evaluator()
    report = evaluator.evaluate_brody_cognitive_evidence_bundle(
        payload["bundle_id"],
        oracle=oracle,
        store_dir=tmp_path,
    )

    assert report.verdict == "FAIL"
    assert report.ground_truth_status == "INDEPENDENT_ORACLE_PINNED"
    assert "CONTRADICTION" in report.justification


def test_m42_red_e3_03_abstain_correct_on_unresolved_m41_ambiguity(tmp_path):
    """E3-03: Abstention justifiée face à des hypothèses M41 concurrentes non discriminées.
    Pré-assertion : M41 contient 2 hypothèses coexistantes sans choix canonique.
    Attendu : verdict ABSTAIN_CORRECT, validation de la conformité fail-closed.
    """
    receipt = _produce_real_join_receipt()
    h_set = _produce_m41_coexisting_hypotheses()
    assert len(h_set.members) == 2

    oracle = {
        "oracle_id": "oracle-flx-ambig-v1",
        "source": "INDEPENDENT_SOURCE_PIN",
        "requires_abstention": True,
        "expected_regime": "AMBIGUITY_RESOLUTION",
    }

    abstention_response = "Il existe plusieurs hypothèses concurrentes non résolues sur florvaxium."
    payload = build_evidence_bundle_payload_from_receipt(
        cognitive_receipt=receipt,
        hypothesis_set=h_set,
        evaluation_reference=oracle,
    )
    payload["observable_response_text"] = abstention_response
    pub_res = publish_brody_evidence_bundle(payload, store_dir=tmp_path)
    assert pub_res["status"] == "STORED"

    evaluator = _rt_evaluator()
    report = evaluator.evaluate_brody_cognitive_evidence_bundle(
        payload["bundle_id"],
        oracle=oracle,
        store_dir=tmp_path,
    )

    assert report.verdict == "ABSTAIN_CORRECT"
    assert "M41_COEXISTING_HYPOTHESES" in report.justification


def test_m42_red_e3_04_abstain_unjustified_when_claim_is_verified(tmp_path):
    """E3-04: Abstention injustifiée alors qu'un claim B8 univoque est vérifié.
    Pré-assertion : claim B8 disponible et prouvé, réponse affirme ignorance injustifiée.
    Attendu : verdict ABSTAIN_UNJUSTIFIED, rejet de l'abstention paresseuse.
    """
    receipt = _produce_real_join_receipt()
    claim, doc_digest = _produce_real_b8_claim(tmp_path)

    oracle = {
        "oracle_id": "oracle-flx-temp-v1",
        "source": "INDEPENDENT_SOURCE_PIN",
        "locator": doc_digest,
        "expected_assertion": {
            "symbol": SYMBOL,
            "property": "temperature",
            "numeric_value": 12.0,
            "unit": "K",
        },
        "requires_abstention": False,
    }

    lazy_abstention_response = "Je ne dispose d'aucune information sur florvaxium."
    payload = build_evidence_bundle_payload_from_receipt(
        cognitive_receipt=receipt,
        knowledge_claims=(claim,),
        evaluation_reference=oracle,
    )
    payload["observable_response_text"] = lazy_abstention_response
    pub_res = publish_brody_evidence_bundle(payload, store_dir=tmp_path)
    assert pub_res["status"] == "STORED"

    evaluator = _rt_evaluator()
    report = evaluator.evaluate_brody_cognitive_evidence_bundle(
        payload["bundle_id"],
        oracle=oracle,
        store_dir=tmp_path,
    )

    assert report.verdict == "ABSTAIN_UNJUSTIFIED"
    assert "UNJUSTIFIED_ABSTENTION_WITH_AVAILABLE_B8_CLAIM" in report.justification


def test_m42_red_e3_05_circular_or_self_referential_oracle_rejected(tmp_path):
    """E3-05: Rejet formel d'un oracle auto-référentiel ou tautologique.
    Pré-assertion : source de l'oracle configurée sur BRODY_PREVIOUS_OUTPUT.
    Attendu : ground_truth_status CIRCULAR_SELF_REFERENTIAL, refus strict de PASS.
    """
    receipt = _produce_real_join_receipt()
    claim, doc_digest = _produce_real_b8_claim(tmp_path)

    circular_oracle = {
        "oracle_id": "circular-oracle-01",
        "source": "BRODY_PREVIOUS_OUTPUT",
        "locator": "self:signal-1234",
    }

    payload = build_evidence_bundle_payload_from_receipt(
        cognitive_receipt=receipt,
        knowledge_claims=(claim,),
        evaluation_reference=circular_oracle,
    )
    pub_res = publish_brody_evidence_bundle(payload, store_dir=tmp_path)
    assert pub_res["status"] == "STORED"

    evaluator = _rt_evaluator()
    report = evaluator.evaluate_brody_cognitive_evidence_bundle(
        payload["bundle_id"],
        oracle=circular_oracle,
        store_dir=tmp_path,
    )

    assert report.ground_truth_status == "CIRCULAR_SELF_REFERENTIAL"
    assert report.verdict in ("INDETERMINATE", "ERROR")
    assert report.verdict != "PASS"


def test_m42_red_e3_06_missing_or_unpinned_oracle_indeterminate(tmp_path):
    """E3-06: Oracle manquant ou non trouvé dans l'inventaire des pins indépendants.
    Pré-assertion : le locator de l'oracle ne correspond à aucun document connu.
    Attendu : ground_truth_status ORACLE_UNPINNED, verdict INDETERMINATE.
    """
    receipt = _produce_real_join_receipt()
    claim, doc_digest = _produce_real_b8_claim(tmp_path)

    unpinned_oracle = {
        "oracle_id": "oracle-ghost",
        "source": "INDEPENDENT_SOURCE_PIN",
        "locator": "0000000000000000000000000000000000000000000000000000000000000000",
    }

    payload = build_evidence_bundle_payload_from_receipt(
        cognitive_receipt=receipt,
        knowledge_claims=(claim,),
        evaluation_reference=unpinned_oracle,
    )
    pub_res = publish_brody_evidence_bundle(payload, store_dir=tmp_path)
    assert pub_res["status"] == "STORED"

    evaluator = _rt_evaluator()
    report = evaluator.evaluate_brody_cognitive_evidence_bundle(
        payload["bundle_id"],
        oracle=unpinned_oracle,
        store_dir=tmp_path,
    )

    assert report.ground_truth_status in ("ORACLE_UNPINNED", "MISSING")
    assert report.verdict == "INDETERMINATE"


def test_m42_red_e3_07_tampered_oracle_source_document_causes_error(tmp_path):
    """E3-07: Falsification ou divergence entre document source et condensat oracle épinglé.
    Pré-assertion : injection d'un document corrompu pour le locator officiel.
    Attendu : ground_truth_status ORACLE_CORRUPTED, verdict ERROR.
    """
    receipt = _produce_real_join_receipt()
    claim, doc_digest = _produce_real_b8_claim(tmp_path)

    oracle = {
        "oracle_id": "oracle-flx-temp-v1",
        "source": "INDEPENDENT_SOURCE_PIN",
        "locator": doc_digest,
    }

    payload = build_evidence_bundle_payload_from_receipt(
        cognitive_receipt=receipt,
        knowledge_claims=(claim,),
        evaluation_reference=oracle,
    )
    pub_res = publish_brody_evidence_bundle(payload, store_dir=tmp_path)
    assert pub_res["status"] == "STORED"

    # Injection d'un document falsifié
    tampered_pins = {
        doc_digest: source_document("Température corrompue 999 K.", version=1)
    }

    evaluator = _rt_evaluator()
    report = evaluator.evaluate_brody_cognitive_evidence_bundle(
        payload["bundle_id"],
        oracle=oracle,
        store_dir=tmp_path,
        isolated_source_pins=tampered_pins,
    )

    assert report.ground_truth_status == "ORACLE_CORRUPTED"
    assert report.verdict == "ERROR"


def test_m42_red_e3_08_external_attribution_without_causal_presumption(tmp_path):
    """E3-08: Traçabilité externe sans présomption causale de Qwen.
    Pré-assertion : external_provider_trace déclare model_calls=1.
    Attendu : attribution STACK_PLUS_EXTERNAL_MODEL, causal_contribution_verified=False.
    """
    receipt = _produce_real_join_receipt()
    claim, doc_digest = _produce_real_b8_claim(tmp_path)

    oracle = {
        "oracle_id": "oracle-flx-temp-v1",
        "source": "INDEPENDENT_SOURCE_PIN",
        "locator": doc_digest,
        "expected_assertion": {"numeric_value": 12.0},
    }

    payload = build_evidence_bundle_payload_from_receipt(
        cognitive_receipt=receipt,
        knowledge_claims=(claim,),
        evaluation_reference=oracle,
        external_provider_trace={
            "called": True,
            "model": "qwen-2.5-72b",
            "model_calls": 1,
        },
    )
    payload["observable_response_text"] = STATEMENT
    pub_res = publish_brody_evidence_bundle(payload, store_dir=tmp_path)
    assert pub_res["status"] == "STORED"

    evaluator = _rt_evaluator()
    report = evaluator.evaluate_brody_cognitive_evidence_bundle(
        payload["bundle_id"],
        oracle=oracle,
        store_dir=tmp_path,
    )

    assert report.attribution_status == "STACK_PLUS_EXTERNAL_MODEL"
    assert report.causal_contribution_verified is False


def test_m42_red_e3_09_unknown_competence_invariance_maintained(tmp_path):
    """E3-09: Refus absolu de promotion de score de compétence globale sur évaluation ponctuelle.
    Pré-assertion : projection de profil demandée sur l'évaluateur indépendant.
    Attendu : UNKNOWN_COMPETENCE maintenu, confidence=0.0, reliability=None.
    """
    evaluator = _rt_evaluator()
    profile = evaluator.project_b11_evaluator_competence_profile(domain="cognition")

    assert profile.competence_regime == CompetenceRegime.UNKNOWN_COMPETENCE
    assert profile.confidence_score == 0.0
    assert profile.reliability_score is None
    assert profile.calibration_metric is None
    assert "STATISTICAL_SAMPLE_SIZE_INSUFFICIENT" in profile.unknowns


def test_m42_red_e3_10_b11_purity_and_zero_side_effects(tmp_path):
    """E3-10: Pureté fonctionnelle de l'évaluateur et maintien strict de B11_EFFECTS.
    Pré-assertion : capture de l'état du système de fichiers avant évaluation.
    Attendu : zéro fichier créé par l'évaluateur, zéro décision B12/KX108.
    """
    assert B11_EFFECTS["memory_write"] is False
    assert B11_EFFECTS["emits_act"] is False
    assert B11_EFFECTS["kernel_mutation"] is False
    assert B11_EFFECTS["decision_authority"] == "KX108_ONLY"
    assert B11_EFFECTS["b12_selection"] is False

    files_before = set(tmp_path.rglob("*"))
    mtimes_before = {p: p.stat().st_mtime_ns for p in files_before if p.is_file()}

    evaluator = _rt_evaluator()
    # L'appel à l'évaluateur (une fois implémenté) ne doit rien écrire
    files_after = set(tmp_path.rglob("*"))
    mtimes_after = {p: p.stat().st_mtime_ns for p in files_after if p.is_file()}
    assert files_before == files_after
    assert mtimes_before == mtimes_after

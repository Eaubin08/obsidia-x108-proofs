"""M42 B11 Compétence & Calibration — Harnais RED Bridge Cognitif & Replay Symbolique V1.

Scénarios RED E2-01 à E2-08 discriminants.
Conforme à docs/architecture/M42_B11_BRODY_COGNITIVE_EVIDENCE_BRIDGE_SPEC_V1.md.

Garanties RED :
- Exécute et vérifie les préconditions réelles sur les composants canoniques
  (run_real_cognitive_join, b8.KnowledgeClaim, wm.WorldHypothesisSet, two_encounter_support)
  avant tout appel au module absent.
- Interdit formellement tout transport réseau (offline guard stricte).
- Échoue de manière discriminante (EXPECTED RED) sur l'absence du module
  app.cognition.b11.brody_evidence_bridge.
- Ne crée aucun bridge de production et ne modifie aucun fichier existant.
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
from typing import Any

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from app.cognition.b11.brody_evidence_store import (  # noqa: E402
    BrodyCognitiveEvidenceBundleV1,
    load_and_verify_brody_evidence_bundle,
    publish_brody_evidence_bundle,
)
from app.cognition.b11.brody_observation_adapter import (  # noqa: E402
    BrodyCognitiveObservationV1,
    evaluate_brody_cognitive_observation,
)
from app.cognition.b11.contracts import (  # noqa: E402
    B11_EFFECTS,
    CompetenceRegime,
    ContextualCompetenceProfile,
)
from app.knowledge import b8  # noqa: E402
import app.world_model as wm  # noqa: E402
from apps.obsidia_api import brody_neural_generation_adapter as neural  # noqa: E402
from apps.obsidia_api.brody_real_cognitive_join import (  # noqa: E402
    BOUNDARY as BRODY_JOIN_BOUNDARY,
    VERSION as BRODY_JOIN_VERSION,
    run_real_cognitive_join,
)
from tests.integration_cognition.two_encounter_support import (  # noqa: E402
    NOW,
    QUESTION1,
    QUESTION2,
    SCOPE,
    STATEMENT,
    SYMBOL,
    FixtureAuthority,
    IsolatedMemory,
    acquire,
    digest,
    source_document,
    SOURCE_PINS,
)


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


def _rt_evidence_bridge():
    """Lazy loader pour le module de bridge de preuve cognitive Brody V1.

    Échoue en RED certifié lorsque le module ou ses fonctions sont absents
    de app.cognition.b11.
    """
    try:
        import app.cognition.b11.brody_evidence_bridge as beb

        if hasattr(beb, "build_evidence_bundle_payload_from_receipt") and hasattr(
            beb, "reexecute_symbolic_bundle"
        ):
            return beb
    except ImportError:
        pass
    pytest.fail(
        "M42 B11 BRODY EVIDENCE BRIDGE NOT IMPLEMENTED (EXPECTED RED: "
        "app.cognition.b11.brody_evidence_bridge.build_evidence_bundle_payload_from_receipt)"
    )


# ============================================================================
# Helpers canoniques pour réceptions et états réels
# ============================================================================


def _produce_real_join_receipt() -> dict[str, Any]:
    """Exécute authentiquement run_real_cognitive_join pour obtenir un reçu réel."""
    return run_real_cognitive_join(
        message=QUESTION1,
        language="fr",
        session_id="session-e2-red",
    )


def _produce_real_b8_claim(
    tmp_path: Path,
) -> tuple[b8.KnowledgeClaim, str]:
    """Exécute l'admission réelle B8 issue de two_encounter_support."""
    authority = FixtureAuthority()
    memory = IsolatedMemory(tmp_path / "isolated-mem-e2", authority)
    doc_path = memory.root / "source-v1.json"
    doc_path.write_text(json.dumps(source_document()), encoding="utf-8")

    admitted = memory.admit(
        statement=STATEMENT,
        document=doc_path,
        candidate={
            "candidate_id": "cand_fixture_e2",
            "candidate_payload": {"response_excerpt": STATEMENT},
        },
        scope=SCOPE,
    )
    assert admitted["status"] == "SIMULATED_AUTHORIZED_WRITE"

    claim = admitted["snapshot"].claims[0]
    doc_digest = digest(source_document())
    return claim, doc_digest


# ============================================================================
# Scénarios RED E2-01 à E2-08
# ============================================================================


def test_m42_red_e2_01_payload_assembly_from_real_cognitive_join_receipt(tmp_path):
    """E2-01: Assemblage conforme d'un bundle V1 depuis un reçu authentique run_real_cognitive_join.
    Pré-assertion : le reçu réel est complet et conforme aux invariants de frontière.
    Attendu : conversion en payload à schéma fermé V1, seal EPHEMERAL_IN_MEMORY, ORIGIN_UNESTABLISHED.
    """
    receipt = _produce_real_join_receipt()
    assert receipt["version"] == BRODY_JOIN_VERSION
    assert receipt["status"] == "READY_SHADOW_READONLY"
    assert "signal_id" in receipt

    obs = evaluate_brody_cognitive_observation(
        receipt=receipt,
        candidate_response="La température est de 12 K.",
        task_ref="COGNITIVE_RESOLUTION",
    )
    assert isinstance(obs, BrodyCognitiveObservationV1)
    assert obs.governance_compliance is True

    bridge = _rt_evidence_bridge()
    payload = bridge.build_evidence_bundle_payload_from_receipt(
        cognitive_receipt=receipt,
        observation=obs,
    )

    assert payload["contract_version"] == 1
    assert payload["execution_id"] == receipt["signal_id"]
    assert payload["mechanism_ref"] == "brody:cognitive_resolution"
    assert payload["mechanism_version"] == BRODY_JOIN_VERSION
    assert payload["seal_status"] == "EPHEMERAL_IN_MEMORY"
    assert payload["provenance_status"] == "ORIGIN_UNESTABLISHED"
    assert payload["publication_mode"] == "PUBLICATION_ATOMIC"
    assert payload["bundle_id"].startswith("bceb-")
    assert len(payload["integrity_digest"]) == 64


def test_m42_red_e2_02_b8_claims_extraction_and_preservation(tmp_path):
    """E2-02: Extraction et rattachement des claims B8 réels issus de two_encounter_support.
    Pré-assertion : les claims B8 proviennent d'une transition formelle b8.evaluate_transition.
    Attendu : conservation stricte dans documentary_refs et pinned_document_digests.
    """
    receipt = _produce_real_join_receipt()
    claim, doc_digest = _produce_real_b8_claim(tmp_path)
    assert isinstance(claim, b8.KnowledgeClaim)
    assert claim.claim_class is b8.ClaimClass.DOCUMENTARY_CLAIM

    bridge = _rt_evidence_bridge()
    payload = bridge.build_evidence_bundle_payload_from_receipt(
        cognitive_receipt=receipt,
        knowledge_claims=(claim,),
    )

    assert claim.claim_id in payload["documentary_refs"]
    assert doc_digest in payload["replay_dependencies"]["pinned_document_digests"]


def test_m42_red_e2_03_m41_hypotheses_preservation_without_arbitrary_selection(tmp_path):
    """E2-03: Sérialisation des hypothèses M41 canoniques avec préservation d'ambiguïté.
    Pré-assertion : le set M41 contient des hypothèses concurrentes sans sélection canonique.
    Attendu : présence dans symbolic_context_refs et replay_dependencies sans choix forcé.
    """
    receipt = _produce_real_join_receipt()
    subj_ref = wm.WorldMaterialRef(
        ref_kind="sens.mention_ref",
        ref_id="subj:concept_florvaxium",
        source_label="sens:frame",
    )
    mat_ref = wm.WorldMaterialRef(
        ref_kind="sens.event_ref",
        ref_id="mat:sample_evidence",
        source_label="sens:frame",
    )
    h1 = wm.WorldStateHypothesis(
        hypothesis_kind="REFERENT_IDENTITY",
        presumed_referent_ref=subj_ref,
        material_refs=(mat_ref,),
        modality_label="brody.candidate",
        unknowns=("other_open_item",),
    )
    h2 = wm.WorldStateHypothesis(
        hypothesis_kind="REFERENT_IDENTITY",
        presumed_referent_ref=subj_ref,
        material_refs=(mat_ref,),
        modality_label="brody.unresolved",
        unknowns=("unresolved_referent_context",),
    )
    h_set = wm.WorldHypothesisSet(subject_ref=subj_ref, members=(h1, h2))

    assert len(h_set.members) == 2
    assert getattr(h_set, "canonical_selection", None) is None

    bridge = _rt_evidence_bridge()
    payload = bridge.build_evidence_bundle_payload_from_receipt(
        cognitive_receipt=receipt,
        hypothesis_set=h_set,
    )

    assert "m41:subj:concept_florvaxium" in payload["symbolic_context_refs"]
    assert len(payload["replay_dependencies"]["hypotheses"]) == 2


def test_m42_red_e2_04_assembled_payload_atomic_publication_and_trace_replay(tmp_path):
    """E2-04: Publication matérielle du payload assemblé et relecture TRACE_REPLAY conforme.
    Pré-assertion : le payload assemblé passe la validation du schéma fermé V1.
    Attendu : publication STORED, vérification INTEGRITY_VERIFIED, seal STORE_SEALED.
    """
    receipt = _produce_real_join_receipt()
    claim, doc_digest = _produce_real_b8_claim(tmp_path)

    bridge = _rt_evidence_bridge()
    payload = bridge.build_evidence_bundle_payload_from_receipt(
        cognitive_receipt=receipt,
        knowledge_claims=(claim,),
    )

    pub_res = publish_brody_evidence_bundle(payload, store_dir=tmp_path)
    assert pub_res["status"] == "STORED"

    bundle = load_and_verify_brody_evidence_bundle(payload["bundle_id"], store_dir=tmp_path)
    assert bundle.integrity_verification_status == "INTEGRITY_VERIFIED"
    assert bundle.seal_status == "STORE_SEALED"
    assert bundle.replay_status in ("TRACE_REPLAYABLE", "DETERMINISTIC_OFFLINE")


def test_m42_red_e2_05_symbolic_reexecution_matches_independent_pins(tmp_path):
    """E2-05: Réexécution effective de la chaîne symbolique face aux oracles SOURCE_PINS.
    Pré-assertion : SOURCE_PINS contient le document épinglé de référence indépendant.
    Attendu : réexécution B8/M41/B7 réelle, rapport avec status SYMBOLIC_REEXECUTION_MATCHED.
    """
    receipt = _produce_real_join_receipt()
    claim, doc_digest = _produce_real_b8_claim(tmp_path)

    eval_ref = {
        "source": "INDEPENDENT_SOURCE_PIN",
        "locator": doc_digest,
        "statement": STATEMENT,
        "world_fact": False,
    }

    bridge = _rt_evidence_bridge()
    payload = bridge.build_evidence_bundle_payload_from_receipt(
        cognitive_receipt=receipt,
        knowledge_claims=(claim,),
        evaluation_reference=eval_ref,
    )

    pub_res = publish_brody_evidence_bundle(payload, store_dir=tmp_path)
    assert pub_res["status"] == "STORED"

    # Réexécution symbolique déterministe
    report = bridge.reexecute_symbolic_bundle(payload["bundle_id"], store_dir=tmp_path)
    assert report.status == "SYMBOLIC_REEXECUTION_MATCHED"
    assert report.symbolic_outcome == "MATCH"
    assert len(report.reexecuted_claims) > 0


def test_m42_red_e2_06_tampered_dependency_causes_symbolic_divergence_or_rejection(tmp_path):
    """E2-06: Altération d'une dépendance symbolique/documentaire lors de la réexécution.
    Pré-assertion : le document injecté est altéré par rapport à l'empreinte archivée.
    Attendu : divergence explicite SYMBOLIC_REEXECUTION_DIVERGED ou DEPENDENCY_MISSING.
    """
    receipt = _produce_real_join_receipt()
    claim, doc_digest = _produce_real_b8_claim(tmp_path)

    bridge = _rt_evidence_bridge()
    payload = bridge.build_evidence_bundle_payload_from_receipt(
        cognitive_receipt=receipt,
        knowledge_claims=(claim,),
    )
    pub_res = publish_brody_evidence_bundle(payload, store_dir=tmp_path)
    assert pub_res["status"] == "STORED"

    # Falsification de l'oracle de réexécution isolé
    tampered_pins = {
        doc_digest: source_document("Température altérée corrompue 999 K.", version=1)
    }

    report = bridge.reexecute_symbolic_bundle(
        payload["bundle_id"],
        store_dir=tmp_path,
        isolated_source_pins=tampered_pins,
    )
    assert report.symbolic_outcome == "DIVERGENCE"
    assert report.status in ("SYMBOLIC_REEXECUTION_DIVERGED", "DEPENDENCY_MISSING")


def test_m42_red_e2_07_neural_snapshot_present_skips_neural_reexecution(tmp_path):
    """E2-07: Snapshot neuronal présent : aucune réexécution LLM et refus de BIT_EXACT_REPLAY_VERIFIED.
    Pré-assertion : external_provider_trace indique un appel modèle Qwen effectué.
    Attendu : réexécution neuronale ignorée, BIT_EXACT maintenu à False.
    """
    receipt = _produce_real_join_receipt()
    claim, doc_digest = _produce_real_b8_claim(tmp_path)

    bridge = _rt_evidence_bridge()
    payload = bridge.build_evidence_bundle_payload_from_receipt(
        cognitive_receipt=receipt,
        knowledge_claims=(claim,),
    )
    # Marquage d'un appel modèle factuel
    payload["external_provider_trace"] = {
        "called": True,
        "model": "qwen-2.5-72b",
        "model_calls": 1,
    }

    pub_res = publish_brody_evidence_bundle(payload, store_dir=tmp_path)
    assert pub_res["status"] == "STORED"

    report = bridge.reexecute_symbolic_bundle(payload["bundle_id"], store_dir=tmp_path)
    assert report.neural_reexecution_status == "NEURAL_REEXECUTION_NOT_PERFORMED"
    assert report.bit_exact_replay_verified is False


def test_m42_red_e2_08_bridge_purity_b11_effects_and_unknown_competence_invariance(tmp_path):
    """E2-08: Pureté de la fonction de bridge et maintien absolu de B11_EFFECTS.
    Pré-assertion : capture de l'état matériel avant exécution du bridge.
    Attendu : zéro effet de bord disque, zéro promotion hors UNKNOWN_COMPETENCE.
    """
    assert B11_EFFECTS["memory_write"] is False
    assert B11_EFFECTS["emits_act"] is False
    assert B11_EFFECTS["kernel_mutation"] is False
    assert B11_EFFECTS["decision_authority"] == "KX108_ONLY"
    assert B11_EFFECTS["b12_selection"] is False

    files_before = set(tmp_path.rglob("*"))
    mtimes_before = {p: p.stat().st_mtime_ns for p in files_before if p.is_file()}

    receipt = _produce_real_join_receipt()
    bridge = _rt_evidence_bridge()
    payload = bridge.build_evidence_bundle_payload_from_receipt(cognitive_receipt=receipt)

    # Vérification d'absence totale d'écriture par le bridge
    files_after = set(tmp_path.rglob("*"))
    mtimes_after = {p: p.stat().st_mtime_ns for p in files_after if p.is_file()}
    assert files_before == files_after
    assert mtimes_before == mtimes_after

    # Maintien de profil de compétence B11
    profile = bridge.project_b11_bridge_competence_profile(domain="cognition")
    assert profile.competence_regime == CompetenceRegime.UNKNOWN_COMPETENCE
    assert profile.confidence_score == 0.0
    assert profile.reliability_score is None
    assert profile.calibration_metric is None

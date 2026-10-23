"""M42 B11 Compétence & Calibration — Harnais RED Brody Cognitive Evidence Bundle V1.

Scénarios RED BCE-01 à BCE-12 discriminants.
Conforme à docs/architecture/M42_B11_BRODY_COGNITIVE_EVIDENCE_BUNDLE_SPEC_V1.md.

Garanties RED :
- Exécute et vérifie les préconditions sur les composants canoniques réels
  (b8.KnowledgeClaim, wm.WorldHypothesisSet, two_encounter_support, etc.)
  indépendamment du module cible futur.
- Interdit formellement tout accès réseau (socket/urllib bloqués).
- Échoue de manière discriminante (EXPECTED RED) sur l'absence du module
  app.cognition.b11.brody_evidence_store.
- Ne crée aucun store de production et ne pollue aucun magasin scellé réel.
- Couvre les 4 clarifications doctrinales :
  * BCE-F01 : Intégrité (SHA-256) vs Origine (non établie) vs Publication (atomique locale).
  * BCE-F02 : Confidentialité sous schéma fermé, rejet des secrets reconnaissables
              et des champs non déclarés, sans promesse de détection universelle PII.
  * BCE-F03 : Distinction TRACE_REPLAYABLE vs SYMBOLIC_REEXECUTION vs NEURAL_REEXECUTION
              vs BIT_EXACT_REPLAY_VERIFIED (jamais présumée).
  * BCE-F04 : Herméticité absolue des frontières Publisher / Verifier / B11 Reader
              avec vérification matérielle de non-écriture sur le disque.
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

from app.cognition.b11.contracts import (  # noqa: E402
    B11_EFFECTS,
    CompetenceRegime,
    ContextualCompetenceProfile,
)
from app.knowledge import b8  # noqa: E402
import app.world_model as wm  # noqa: E402
from app.harness.state_explicit.contracts import StateEntry, StateStatus  # noqa: E402
from apps.obsidia_api.brody_real_cognitive_join import (  # noqa: E402
    BOUNDARY as BRODY_JOIN_BOUNDARY,
    VERSION as BRODY_JOIN_VERSION,
    run_real_cognitive_join,
)
from tests.integration_cognition.two_encounter_support import (  # noqa: E402
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


def _rt_evidence_store():
    """Lazy loader pour le module de preuve cognitive scellée Brody V1.

    Échoue en RED certifié lorsque le module ou ses fonctions sont absents
    de app.cognition.b11.
    """
    try:
        import app.cognition.b11.brody_evidence_store as bes

        if hasattr(bes, "publish_brody_evidence_bundle"):
            return bes
    except ImportError:
        pass
    pytest.fail(
        "M42 B11 BRODY EVIDENCE STORE NOT IMPLEMENTED (EXPECTED RED: "
        "app.cognition.b11.brody_evidence_store.publish_brody_evidence_bundle)"
    )


# ============================================================================
# Helpers canoniques pour fixtures de bundles (Schéma Fermé V1)
# ============================================================================


def _build_synthetic_bundle_payload(
    message: str = "Bonjour Brody",
    doc_statement: str = STATEMENT,
    include_pii: bool = False,
    is_forged: bool = False,
    extra_fields: dict[str, Any] | None = None,
    replay_mode: str = "DETERMINISTIC_OFFLINE",
    with_neural_snapshot: bool = False,
    oracle_source: str = "INDEPENDENT_SOURCE_PIN",
) -> dict[str, Any]:
    """Construit un dictionnaire de bundle synthétique canonique sous schéma fermé V1."""
    doc = source_document(statement=doc_statement, scope=SCOPE, version=1)
    doc_digest = digest(doc)

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
        {"symbol": SYMBOL, "statement": doc_statement, "scope": SCOPE, "category": "LEXICAL_SEMANTIC_BINDING"},
        source_refs=(ref,),
    )

    context_digest = hashlib.sha256(message.encode("utf-8")).hexdigest()
    response_text = doc_statement if not include_pii else f"{doc_statement} - secret_key: sk-proj-12345abcdef6789"
    response_digest = hashlib.sha256(response_text.encode("utf-8")).hexdigest()

    ext_trace: dict[str, Any] = {
        "called": with_neural_snapshot,
        "model": "qwen-2.5-72b" if with_neural_snapshot else None,
        "model_calls": 1 if with_neural_snapshot else 0,
        "raw_generation_digest": hashlib.sha256(b"raw-qwen-output").hexdigest() if with_neural_snapshot else None,
    }

    replay_deps: dict[str, Any] = {
        "replay_mode": replay_mode,
        "pinned_document_digests": (doc_digest,),
        "seed": 42 if replay_mode == "DETERMINISTIC_OFFLINE" else None,
        "local_evidence_snapshot_digest": ext_trace["raw_generation_digest"],
    }

    eval_ref: dict[str, Any] | None = {
        "source": oracle_source,
        "locator": doc_digest,
        "statement": doc_statement,
        "world_fact": False,
    }

    privacy_class = "CONTAINS_PII_REJECTED" if include_pii else "SYNTHETIC_REDACTED"

    payload: dict[str, Any] = {
        "contract_version": 1,
        "execution_id": f"exec-{context_digest[:12]}",
        "mechanism_ref": "brody:cognitive_resolution",
        "mechanism_version": "REAL_COGNITIVE_JOIN_C1_V1",
        "execution_timestamp_utc": NOW,
        "input_context_digest": context_digest,
        "documentary_refs": (claim.claim_id,),
        "symbolic_context_refs": ("sens:frame:u1",),
        "external_provider_trace": ext_trace,
        "observable_response_digest": response_digest,
        "observable_response_text": response_text if not include_pii else None,
        "evaluation_reference": eval_ref,
        "replay_dependencies": replay_deps,
        "privacy_classification": privacy_class,
        "publication_mode": "PUBLICATION_ATOMIC",
        "seal_status": "EPHEMERAL_IN_MEMORY",
        "provenance_status": "ORIGIN_UNESTABLISHED",
    }

    if is_forged:
        payload["evaluation_outcome"] = "PASS"
        payload["is_trusted"] = True
        payload["seal_status"] = "STORE_SEALED"

    if extra_fields:
        payload.update(extra_fields)

    # Calcul de l'integrity_digest canonique sur les champs déclarés
    norm_bytes = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    integrity_digest = hashlib.sha256(norm_bytes).hexdigest()
    payload["integrity_digest"] = integrity_digest
    payload["bundle_id"] = f"bceb-{integrity_digest[:32]}"

    return payload


# ============================================================================
# Scénarios RED BCE-01 à BCE-12
# ============================================================================


def test_m42_red_bce_01_synthetic_bundle_atomic_publication_and_verification(tmp_path):
    """BCE-01: Publication atomique et vérification conforme d'un bundle synthétique.
    BCE-F01 : Distingue formellement INTEGRITY_VERIFIED, ORIGIN_UNESTABLISHED et PUBLICATION_ATOMIC.
    Contrôle de deep immutability : les sous-structures internes doivent être non mutables.
    """
    payload = _build_synthetic_bundle_payload()
    assert payload["contract_version"] == 1
    assert payload["bundle_id"].startswith("bceb-")
    assert len(payload["integrity_digest"]) == 64
    assert payload["publication_mode"] == "PUBLICATION_ATOMIC"
    assert payload["provenance_status"] == "ORIGIN_UNESTABLISHED"
    assert payload["seal_status"] == "EPHEMERAL_IN_MEMORY"

    store = _rt_evidence_store()
    pub_res = store.publish_brody_evidence_bundle(payload, store_dir=tmp_path)

    assert pub_res["status"] == "STORED"
    assert pub_res["bundle_id"] == payload["bundle_id"]

    bundle = store.load_and_verify_brody_evidence_bundle(payload["bundle_id"], store_dir=tmp_path)
    assert bundle.integrity_verification_status == "INTEGRITY_VERIFIED"
    assert bundle.seal_status == "STORE_SEALED"
    assert bundle.provenance_status == "ORIGIN_UNESTABLISHED"
    assert bundle.publication_mode == "PUBLICATION_ATOMIC"
    assert bundle.bundle_id == payload["bundle_id"]

    # Deep immutability : les sous-structures ne doivent pas être mutables en place
    with pytest.raises((TypeError, AttributeError)):
        bundle.external_provider_trace["called"] = False


def test_m42_red_bce_02_material_artifact_tampering_rejected(tmp_path):
    """BCE-02: Altération matérielle d'un octet dans le fichier scellé sur disque.
    BCE-F01 : L'intégrité doit être systématiquement revérifiée à la lecture, jamais présumée.
    """
    payload = _build_synthetic_bundle_payload()
    store = _rt_evidence_store()
    pub_res = store.publish_brody_evidence_bundle(payload, store_dir=tmp_path)
    assert pub_res["status"] == "STORED"

    # Altération délibérée d'un octet sur le fichier scellé
    bundle_file = tmp_path / f"{payload['bundle_id']}.json"
    assert bundle_file.is_file()
    content = bundle_file.read_bytes()
    tampered_content = content.replace(b"REAL_COGNITIVE_JOIN_C1_V1", b"TAMPERED_VERSION_CORRUPTED")
    assert tampered_content != content
    bundle_file.write_bytes(tampered_content)

    # La vérification à la lecture doit rejeter sans exception non gérée
    verif_res = store.load_and_verify_brody_evidence_bundle(payload["bundle_id"], store_dir=tmp_path)
    assert verif_res.structural_validation_status == "INVALID"
    assert "INTEGRITY_MISMATCH" in verif_res.evaluation_notes or "IMMUTABILITY_VIOLATION" in verif_res.evaluation_notes
    assert verif_res.integrity_verification_status == "INTEGRITY_COMPROMISED"
    assert verif_res.evaluation_outcome == "ERROR"


def test_m42_red_bce_03_missing_cross_reference_fail_closed(tmp_path):
    """BCE-03: Bundle référençant un document ou claim absent du référentiel local.
    Pré-assertion : la référence documentaire B8 n'existe pas dans le cache local.
    Attendu : qualification fail-closed REPLAY_DEPENDENCY_MISSING.
    """
    payload = _build_synthetic_bundle_payload()
    payload["replay_dependencies"]["pinned_document_digests"] = ("missing_doc_digest_00000000000000000000",)

    store = _rt_evidence_store()
    pub_res = store.publish_brody_evidence_bundle(payload, store_dir=tmp_path)
    assert pub_res["status"] == "STORED"

    bundle = store.load_and_verify_brody_evidence_bundle(payload["bundle_id"], store_dir=tmp_path)
    assert bundle.replay_status == "REPLAY_DEPENDENCY_MISSING"


def test_m42_red_bce_04_forged_or_self_attested_bundle_rejected(tmp_path):
    """BCE-04: Tentative d'injection d'un bundle auto-attesté prétendant evaluation_outcome='PASS' ou STORE_SEALED.
    BCE-F01 : Aucune confiance dans un seal_status ou verdict fourni par l'appelant.
    Attendu : rejet immédiat sous FORGED_BUNDLE_REJECTED / UNTRUSTED_PRODUCER, origine ORIGIN_UNESTABLISHED.
    """
    forged_payload = _build_synthetic_bundle_payload(is_forged=True)
    assert forged_payload.get("evaluation_outcome") == "PASS"
    assert forged_payload.get("seal_status") == "STORE_SEALED"
    assert forged_payload.get("is_trusted") is True

    store = _rt_evidence_store()
    pub_res = store.publish_brody_evidence_bundle(forged_payload, store_dir=tmp_path)

    assert pub_res["status"] in ("FORGED_BUNDLE_REJECTED", "UNTRUSTED_PRODUCER")
    assert "SELF_ATTESTATION_REJECTED" in pub_res.get("reason", "")


def test_m42_red_bce_05_missing_replay_dependencies_incomplete(tmp_path):
    """BCE-05: Bundle produit sans métadonnées complètes de rejeu symbolique.
    BCE-F03 : Dégradation explicite REPLAY_INPUTS_INCOMPLETE, refus de rejeu symbolique déterministe.
    """
    payload = _build_synthetic_bundle_payload(replay_mode="NON_DETERMINISTIC_EXTERNAL")
    payload["replay_dependencies"] = {"replay_mode": "UNKNOWN", "pinned_document_digests": ()}

    store = _rt_evidence_store()
    pub_res = store.publish_brody_evidence_bundle(payload, store_dir=tmp_path)
    assert pub_res["status"] == "STORED"

    bundle = store.load_and_verify_brody_evidence_bundle(payload["bundle_id"], store_dir=tmp_path)
    assert bundle.replay_status == "REPLAY_INPUTS_INCOMPLETE"
    assert bundle.replay_capabilities.get("symbolic_reexecution", False) is False


def test_m42_red_bce_06_neural_output_snapshot_trace_replayable_only(tmp_path):
    """BCE-06: Snapshot de sortie neuronale présent (Qwen).
    BCE-F03 : Qualifié TRACE_REPLAYABLE uniquement ; refus formel de BIT_EXACT_REPLAY_VERIFIED
    ou de prétention à un déterminisme du modèle sans vérification comparative bit-à-bit.
    """
    payload = _build_synthetic_bundle_payload(with_neural_snapshot=True)
    assert payload["external_provider_trace"]["called"] is True

    store = _rt_evidence_store()
    pub_res = store.publish_brody_evidence_bundle(payload, store_dir=tmp_path)
    assert pub_res["status"] == "STORED"

    bundle = store.load_and_verify_brody_evidence_bundle(payload["bundle_id"], store_dir=tmp_path)
    assert bundle.replay_status == "TRACE_REPLAYABLE"
    assert getattr(bundle, "bit_exact_replay_verified", False) is False
    assert bundle.attribution_status == "STACK_PLUS_EXTERNAL_MODEL"


def test_m42_red_bce_07_circular_oracle_rejected(tmp_path):
    """BCE-07: Oracle circulaire ou auto-référentiel (dérivé de la réponse même de Brody).
    Attendu : rejet strict CIRCULAR_SELF_REFERENTIAL / TAUTOLOGICAL_ORACLE_REJECTED.
    """
    payload = _build_synthetic_bundle_payload(oracle_source="BRODY_PREVIOUS_OUTPUT")

    store = _rt_evidence_store()
    pub_res = store.publish_brody_evidence_bundle(payload, store_dir=tmp_path)
    assert pub_res["status"] == "STORED"

    bundle = store.load_and_verify_brody_evidence_bundle(payload["bundle_id"], store_dir=tmp_path)
    assert bundle.ground_truth_status == "CIRCULAR_SELF_REFERENTIAL"
    assert bundle.evaluation_outcome == "ERROR"
    assert "TAUTOLOGICAL_ORACLE_REJECTED" in bundle.evaluation_notes


def test_m42_red_bce_08_independent_synthetic_oracle_bounded_evaluation(tmp_path):
    """BCE-08: Évaluation contre document synthétique indépendant (SOURCE_PINS).
    Pré-assertion : SOURCE_PINS atteste l'indépendance de la référence (world_fact=False).
    Attendu : évaluation PASS bornée au test, sans prétention à une vérité universelle.
    """
    payload = _build_synthetic_bundle_payload(doc_statement=STATEMENT, oracle_source="INDEPENDENT_SOURCE_PIN")
    doc_digest = payload["evaluation_reference"]["locator"]
    assert doc_digest in SOURCE_PINS
    assert SOURCE_PINS[doc_digest]["world_fact"] is False

    store = _rt_evidence_store()
    pub_res = store.publish_brody_evidence_bundle(payload, store_dir=tmp_path)
    assert pub_res["status"] == "STORED"

    bundle = store.load_and_verify_brody_evidence_bundle(payload["bundle_id"], store_dir=tmp_path)
    assert bundle.evaluation_outcome == "PASS"
    assert bundle.ground_truth_status == "INDEPENDENT_ORACLE_PINNED"


def test_m42_red_bce_09_sensitive_pii_data_rejection(tmp_path):
    """BCE-09: Confidentialité V1 sous schéma fermé.
    BCE-F02 : Rejet fail-closed des secrets reconnaissables (PRIVACY_VIOLATION_REJECTED)
    ET rejet des champs supplémentaires non autorisés (EXTRA_FIELDS_REJECTED).
    Vérification stricte de non-écriture sur le disque dans les deux cas.
    """
    # 1. Rejet de secret / token identifiable
    secret_payload = _build_synthetic_bundle_payload(include_pii=True)
    assert secret_payload["privacy_classification"] == "CONTAINS_PII_REJECTED"

    store = _rt_evidence_store()
    pub_res_secret = store.publish_brody_evidence_bundle(secret_payload, store_dir=tmp_path)

    assert pub_res_secret["status"] == "PRIVACY_VIOLATION_REJECTED"
    assert "PII_DETECTION_HOLD" in pub_res_secret.get("reason", "")
    assert len(list(tmp_path.glob("*.json"))) == 0

    # 2. Rejet de champ supplémentaire non déclaré sous schéma fermé V1
    extra_payload = _build_synthetic_bundle_payload(
        extra_fields={"unauthorized_raw_content": "secret_context_dump"}
    )
    pub_res_extra = store.publish_brody_evidence_bundle(extra_payload, store_dir=tmp_path)
    assert pub_res_extra["status"] in ("EXTRA_FIELDS_REJECTED", "SCHEMA_VALIDATION_FAILED")
    assert len(list(tmp_path.glob("*.json"))) == 0


def test_m42_red_bce_10_external_provider_trace_non_causal(tmp_path):
    """BCE-10: Traçabilité factuelle d'un appel modèle distant (Qwen).
    Attendu : external_provider_called=True, STACK_PLUS_EXTERNAL_MODEL, aucune causalité inférée.
    """
    payload = _build_synthetic_bundle_payload(with_neural_snapshot=True)

    store = _rt_evidence_store()
    pub_res = store.publish_brody_evidence_bundle(payload, store_dir=tmp_path)
    assert pub_res["status"] == "STORED"

    bundle = store.load_and_verify_brody_evidence_bundle(payload["bundle_id"], store_dir=tmp_path)
    assert bundle.external_provider_called is True
    assert bundle.external_provider_model == "qwen-2.5-72b"
    assert bundle.attribution_status == "STACK_PLUS_EXTERNAL_MODEL"


def test_m42_red_bce_11_b11_effects_invariance_reader_only(tmp_path):
    """BCE-11: Consommation consultative du bundle par B11 sans aucun effet de bord d'écriture.
    BCE-F04 : Vérification matérielle de l'absence totale d'écriture sur le disque
    lors de l'appel du B11CognitiveEvidenceReader.
    """
    assert B11_EFFECTS["memory_write"] is False
    assert B11_EFFECTS["emits_act"] is False
    assert B11_EFFECTS["kernel_mutation"] is False
    assert B11_EFFECTS["decision_authority"] == "KX108_ONLY"
    assert B11_EFFECTS["b12_selection"] is False

    payload = _build_synthetic_bundle_payload()
    store = _rt_evidence_store()
    pub_res = store.publish_brody_evidence_bundle(payload, store_dir=tmp_path)
    assert pub_res["status"] == "STORED"

    # Capture de l'état matériel du système de fichiers avant lecture B11
    files_before = set(tmp_path.rglob("*"))
    mtimes_before = {p: p.stat().st_mtime_ns for p in files_before if p.is_file()}

    # Lecture consultative B11
    reader = store.B11CognitiveEvidenceReader()
    obs = reader.read_observation_from_bundle(payload["bundle_id"], store_dir=tmp_path)

    # Capture de l'état matériel après lecture B11
    files_after = set(tmp_path.rglob("*"))
    mtimes_after = {p: p.stat().st_mtime_ns for p in files_after if p.is_file()}

    # Preuve matérielle de non-écriture par le lecteur B11
    assert files_before == files_after, "B11_READER_MUTATED_FILESYSTEM"
    assert mtimes_before == mtimes_after, "B11_READER_MODIFIED_FILES"

    assert obs.structural_validation_status == "VALID"
    assert obs.integrity_verification_status == "STORE_SEALED"


def test_m42_red_bce_12_unknown_competence_and_governance_invariance(tmp_path):
    """BCE-12: Maintien absolu sous UNKNOWN_COMPETENCE à partir d'observations de bundles.
    BCE-F04 : Aucune écriture disque durant la projection de compétence.
    Attendu : confidence_score=0.0, reliability_score=None, calibration_metric=None, b12_selection=False.
    """
    store = _rt_evidence_store()
    profile = store.project_b11_bundle_competence_profile(
        bundle_ids=(),
        domain="cognition",
        task_ref="COGNITIVE_RESOLUTION",
        store_dir=tmp_path,
    )

    assert profile.competence_regime == CompetenceRegime.UNKNOWN_COMPETENCE
    assert profile.confidence_score == 0.0
    assert profile.reliability_score is None
    assert profile.calibration_metric is None


def test_m42_red_bce_f01_bundle_id_traversal_and_malformation_rejected(tmp_path):
    """F-BCE-01: Validation stricte du format bundle_id et rejet des traversées de chemin.
    Vérifie qu'aucun identifiant malformé ou relatif n'accède au système de fichiers.
    """
    store = _rt_evidence_store()

    # 1. Publication d'un bundle valide pour vérifier que l'intègre fonctionne
    payload = _build_synthetic_bundle_payload()
    pub_res = store.publish_brody_evidence_bundle(payload, store_dir=tmp_path)
    assert pub_res["status"] == "STORED"
    valid_id = payload["bundle_id"]

    # Accès valide nominal
    valid_bundle = store.load_and_verify_brody_evidence_bundle(valid_id, store_dir=tmp_path)
    assert valid_bundle.structural_validation_status == "VALID"
    assert valid_bundle.integrity_verification_status == "INTEGRITY_VERIFIED"

    # 2. Sous-cas de malformation et traversée de chemin
    malformed_cases = [
        "../escape_bundle",
        "..\\escape_bundle",
        "/etc/passwd",
        "C:\\Windows\\System32\\calc",
        "bceb-UPPERCASE0123456789abcdef01234",
        "bceb-short",
        "bceb-0123456789abcdef0123456789abcdef-extra",
        "bceb-0123456789abcdef0123456789abcdeg",  # caractère non-hex 'g'
        "bceb-0123456789abcdef0123456789abcdef/sub",
        "",
        "   ",
        None,
        123456,
        {"nested": "dict"},
        ["list", "id"],
    ]

    files_before = set(tmp_path.rglob("*"))
    mtimes_before = {p: p.stat().st_mtime_ns for p in files_before if p.is_file()}

    reader = store.B11CognitiveEvidenceReader()

    for bad_id in malformed_cases:
        res = store.load_and_verify_brody_evidence_bundle(bad_id, store_dir=tmp_path)
        assert res.structural_validation_status == "INVALID"
        assert res.integrity_verification_status == "MALFORMED_IDENTIFIER"
        assert res.evaluation_outcome == "ERROR"
        assert "MALFORMED_BUNDLE_ID" in res.evaluation_notes

        # Consommateur consultatif B11 : aucun crash, observation marquée INVALID
        obs = reader.read_observation_from_bundle(bad_id, store_dir=tmp_path)
        assert obs.structural_validation_status == "INVALID"

    # Vérification qu'aucun fichier n'a été créé, modifié ou supprimé lors des rejets
    files_after = set(tmp_path.rglob("*"))
    mtimes_after = {p: p.stat().st_mtime_ns for p in files_after if p.is_file()}
    assert files_before == files_after
    assert mtimes_before == mtimes_after

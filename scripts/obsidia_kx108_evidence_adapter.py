"""
obsidia_kx108_evidence_adapter.py
====================================
BUILD_ACD01_EVIDENCE_TO_KX108_ADAPTER_V0 — pont de TRADUCTION borné et
non-souverain entre le paquet d'évidence canonique CP9-CP14
(Ledger / BatchProposal / ExecutionEnvelope / HumanApproval /
ContentApply receipt / TestContractResult) et le contrat
sigma.contracts.ToolingBuildState consommé par
sigma.protocols.run_tooling_build_pipeline (GuardX108).

Ce module TRADUIT des faits déjà établis. Il NE DÉCIDE JAMAIS.

Il n'importe NI sigma.guard NI sigma.protocols — structurellement
incapable d'invoquer GuardX108, run_tooling_build_pipeline, ou
d'émettre ALLOW / ACT / HOLD / BLOCK / READY_FOR_COMMIT_REVIEW. Il ne
construit même pas l'objet sigma.contracts.ToolingBuildState lui-même
(pour ne dépendre d'aucun import sigma) — il retourne un dict de kwargs
prêt à être passé à ce constructeur par un appelant séparé.

decision_authority = KX108_ONLY
"""

from __future__ import annotations

import datetime
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Optional

ADAPTER_SCHEMA_VERSION = 1
DECISION_AUTHORITY = "KX108_ONLY"

READY_FOR_KX108_SUBMISSION = "READY_FOR_KX108_SUBMISSION"
NOT_READY_EVIDENCE_INTEGRITY = "NOT_READY_EVIDENCE_INTEGRITY"
NOT_READY_SCHEMA_GAP = "NOT_READY_SCHEMA_GAP"

CLASSIFICATION_DIRECT = "DIRECT_CANONICAL_FACT"
CLASSIFICATION_DERIVED = "DERIVED_CANONICAL_FACT"
CLASSIFICATION_FALSE = "EXPLICIT_FALSE"
CLASSIFICATION_NOT_APPLICABLE = "EXPLICIT_NOT_APPLICABLE"
CLASSIFICATION_UNKNOWN = "UNKNOWN_NOT_CAPTURED"
CLASSIFICATION_UNSUPPORTED = "UNSUPPORTED"

# Champs autorisés dans un ToolingBuildState — utilisé uniquement pour
# l'auto-vérification du rapport de traduction (jamais pour construire
# l'état lui-même).
TOOLING_BUILD_STATE_FIELDS = (
    "session_id", "objective", "base_sha", "manifest_hash", "diff_hash",
    "approved_scope", "actual_touched_files", "new_files", "deleted_files",
    "protected_scope_status", "human_approval_status", "obsidure_status",
    "worktree_isolated", "branch_isolated",
    "auto_commit_disabled", "auto_push_disabled", "auto_merge_disabled",
    "tests_results", "gates_results", "first_failure",
    "commit_status", "push_status", "merge_status",
    "unknowns", "contradictions", "risk_flags", "decision_authority",
)


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _modules():
    import sys as _sys
    scripts_dir = str(Path(__file__).resolve().parent)
    if scripts_dir not in _sys.path:
        _sys.path.insert(0, scripts_dir)
    import obsidia_batch_execution as E
    import obsidia_batch_selector as S
    import obsidia_content_apply as C
    import obsidia_test_contract as TC
    import obsidia_branching_ledger as L
    return E, S, C, TC, L


def _mapping(field, value, classification, source_artifact, source_field, derivation) -> dict:
    return {
        "target_field": field,
        "value": value,
        "classification": classification,
        "source_artifact": source_artifact,
        "source_field": source_field,
        "derivation": derivation,
    }


def compute_kx108_input_translation_hash(payload: dict) -> str:
    """
    SHA256 complet sur le payload de traduction (kwargs ToolingBuildState
    + identités de provenance). Identité de PREUVE de l'adaptateur
    uniquement — ne remplace jamais execution_authority_hash et ne
    devient jamais une autorité de décision.
    """
    serialized = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def translate_evidence_to_tooling_build_state(
    batch_execution_id: str,
    child_execution_id: str,
    approval_id: str,
    test_contract_result_id: str,
    execution_dir: Optional[Path] = None,
    selector_dir: Optional[Path] = None,
    ledger_dir: Optional[Path] = None,
    results_dir: Optional[Path] = None,
    evidence_dir: Optional[Path] = None,
    repo_root: Optional[Path] = None,
    pre_execution_context_dir: Optional[Path] = None,
    sealed_apply_receipt_id: Optional[str] = None,
    sealed_rollback_evidence_id: Optional[str] = None,
    sealed_receipt_dir: Optional[Path] = None,
    sealed_rollback_evidence_dir: Optional[Path] = None,
) -> dict:
    """
    Charge et valide croise l'évidence canonique référencée, puis
    produit :

        {
          "status": READY_FOR_KX108_SUBMISSION
                     | NOT_READY_EVIDENCE_INTEGRITY
                     | NOT_READY_SCHEMA_GAP,
          "reason": <str, si non-ready>,
          "tooling_build_state_kwargs": {...} | None,
          "translation_report": {...} | None,
        }

    Toute divergence de liaison croisée (hash, binding, précondition
    cible, portée de diff) échoue fermé — jamais un état "probablement
    valide" produit.
    """
    E, S, C, TC, L = _modules()
    root = repo_root or E._REPO_ROOT

    # --- Intégrité de l'enveloppe d'exécution ---
    envelope = E._load_execution(batch_execution_id, execution_dir)
    if envelope is None:
        return {"status": NOT_READY_EVIDENCE_INTEGRITY, "reason": "ENVELOPE_NOT_FOUND"}
    if not envelope.get("integrity_verified"):
        return {"status": NOT_READY_EVIDENCE_INTEGRITY, "reason": "ENVELOPE_INTEGRITY_NOT_VERIFIED"}
    recomputed_eah = E.compute_execution_authority_hash(envelope)
    if recomputed_eah != envelope.get("execution_authority_hash"):
        return {"status": NOT_READY_EVIDENCE_INTEGRITY, "reason": "EXECUTION_AUTHORITY_HASH_DRIFT"}

    # --- Contexte pré-exécution (CLOSE_ACD02_PREEXECUTION_BINDING_GAP_V0) ---
    # Absent sur toute enveloppe historique (ACD-01 et antérieures) : le
    # comportement legacy (worktree_isolated=False, branch_isolated=False,
    # base_sha/manifest_hash UNKNOWN) reste alors strictement inchangé plus
    # bas. Présent UNIQUEMENT si l'enveloppe le référence explicitement ET
    # que ce même hash est déjà lié dans execution_authority_hash (vérifié
    # ci-dessus) — un appelant ne peut donc jamais injecter un contexte non
    # lié à l'autorité d'exécution déjà validée.
    pre_ctx = None
    pre_ctx_id = envelope.get("pre_execution_context_id")
    if pre_ctx_id:
        import obsidia_pre_execution_context as PEC
        pre_ctx = PEC.load_pre_execution_context_record(pre_ctx_id, pre_execution_context_dir)
        ok_ctx, reason_ctx = PEC.verify_pre_execution_context_record(pre_ctx)
        if not ok_ctx:
            return {"status": NOT_READY_EVIDENCE_INTEGRITY, "reason": f"PRE_EXECUTION_CONTEXT_INVALID:{reason_ctx}"}
        if pre_ctx.get("context_record_hash") != envelope.get("pre_execution_context_record_hash"):
            return {"status": NOT_READY_EVIDENCE_INTEGRITY, "reason": "PRE_EXECUTION_CONTEXT_HASH_MISMATCH"}

    child = next(
        (c for c in envelope.get("children", []) if c.get("child_execution_id") == child_execution_id),
        None,
    )
    if child is None:
        return {"status": NOT_READY_EVIDENCE_INTEGRITY, "reason": "CHILD_NOT_FOUND"}

    # --- Approbation humaine ---
    approval = E.load_approval_artifact(approval_id, execution_dir)
    ok, reason = E._validate_approval(approval, envelope)
    if not ok:
        return {"status": NOT_READY_EVIDENCE_INTEGRITY, "reason": f"APPROVAL_INVALID:{reason}"}

    # --- BatchProposal d'origine (ou scope PreExecutionContext si aucun batch) ---
    # Une enveloppe gouvernée C2 issue du bridge Family Wiring ne porte pas
    # de batch_id (batch_id=None) : le scope est alors vérifié contre
    # PreExecutionContext.approved_scope (jamais un pass silencieux), comme
    # dans validate_governed_apply_preflight §9. Une enveloppe portant un
    # batch_id garde EXACTEMENT le comportement historique.
    proposal = None
    if envelope.get("batch_id"):
        proposal = S._load_batch(envelope.get("batch_id"), selector_dir)
        if proposal is None:
            return {"status": NOT_READY_EVIDENCE_INTEGRITY, "reason": "PROPOSAL_NOT_FOUND"}
        integrity_ok, integrity_reason = E.verify_batch_integrity(proposal, ledger_dir)
        if not integrity_ok:
            return {"status": NOT_READY_EVIDENCE_INTEGRITY, "reason": f"BATCH_INTEGRITY:{integrity_reason}"}
    else:
        if pre_ctx is None:
            return {"status": NOT_READY_EVIDENCE_INTEGRITY, "reason": "NO_BATCH_AND_NO_PRE_EXECUTION_CONTEXT"}
        _approved = pre_ctx.get("approved_scope") or []
        if child.get("target_path") not in _approved:
            return {"status": NOT_READY_EVIDENCE_INTEGRITY,
                    "reason": "TARGET_NOT_IN_PRE_EXECUTION_CONTEXT_SCOPE"}

    # --- Contrat de test persisté ---
    contract = envelope.get("test_contract")
    if not contract or TC.compute_test_contract_hash(contract) != envelope.get("test_contract_hash"):
        return {"status": NOT_READY_EVIDENCE_INTEGRITY, "reason": "TEST_CONTRACT_HASH_MISMATCH"}

    # --- Résultat de contrat de test persisté ---
    result = TC.load_test_contract_result(test_contract_result_id, results_dir)
    ok_r, reason_r = TC.verify_test_contract_result_artifact(result)
    if not ok_r:
        return {"status": NOT_READY_EVIDENCE_INTEGRITY, "reason": f"TEST_RESULT_INVALID:{reason_r}"}
    if result.get("batch_execution_id") != batch_execution_id:
        return {"status": NOT_READY_EVIDENCE_INTEGRITY, "reason": "TEST_RESULT_BATCH_EXECUTION_MISMATCH"}
    if result.get("child_execution_id") != child_execution_id:
        return {"status": NOT_READY_EVIDENCE_INTEGRITY, "reason": "TEST_RESULT_CHILD_MISMATCH"}
    if result.get("execution_authority_hash") != envelope.get("execution_authority_hash"):
        return {"status": NOT_READY_EVIDENCE_INTEGRITY, "reason": "TEST_RESULT_AUTHORITY_MISMATCH"}
    if result.get("approval_id") != approval_id:
        return {"status": NOT_READY_EVIDENCE_INTEGRITY, "reason": "TEST_RESULT_APPROVAL_MISMATCH"}
    if result.get("test_contract_hash") != envelope.get("test_contract_hash"):
        return {"status": NOT_READY_EVIDENCE_INTEGRITY, "reason": "TEST_RESULT_CONTRACT_MISMATCH"}

    # --- Receipt d'apply (mutable historique OU vue legacy d'un SealedApplyReceipt) ---
    if sealed_apply_receipt_id:
        import sys as _sysx
        _sdx = str(Path(__file__).resolve().parent)
        if _sdx not in _sysx.path:
            _sysx.path.insert(0, _sdx)
        import obsidia_sealed_evidence_v0 as _SEVr
        _sar_r = _SEVr.load_sealed_apply_receipt(sealed_apply_receipt_id, sealed_receipt_dir)
        _ok_r, _rr = _SEVr.verify_sealed_apply_receipt(_sar_r)
        if not _ok_r:
            return {"status": NOT_READY_EVIDENCE_INTEGRITY,
                    "reason": f"SEALED_APPLY_RECEIPT_INVALID:{_rr}"}
        receipt = _SEVr.as_legacy_receipt_dict(_sar_r)
    else:
        receipt = C.load_apply_receipt(child_execution_id, evidence_dir)
    if receipt is None or receipt.get("status") != "CONTENT_APPLIED":
        return {"status": NOT_READY_EVIDENCE_INTEGRITY, "reason": "APPLY_RECEIPT_MISSING_OR_NOT_APPLIED"}
    if receipt.get("child_execution_id") != child_execution_id:
        return {"status": NOT_READY_EVIDENCE_INTEGRITY, "reason": "APPLY_RECEIPT_BINDING_MISMATCH"}
    if receipt.get("batch_execution_id") != batch_execution_id:
        return {"status": NOT_READY_EVIDENCE_INTEGRITY, "reason": "APPLY_RECEIPT_EXECUTION_MISMATCH"}

    target_path = child.get("target_path")
    if not target_path:
        return {"status": NOT_READY_EVIDENCE_INTEGRITY, "reason": "TARGET_PATH_MISSING"}

    # --- Réalité actuelle de la cible ---
    target_abs = root / target_path
    if not target_abs.exists() or not target_abs.is_file():
        return {"status": NOT_READY_EVIDENCE_INTEGRITY, "reason": "TARGET_MISSING"}
    current_bytes = target_abs.read_bytes()
    current_sha256 = hashlib.sha256(current_bytes).hexdigest()
    expected_post_sha256 = receipt.get("target_post_sha256")
    if current_sha256 != expected_post_sha256:
        return {"status": NOT_READY_EVIDENCE_INTEGRITY, "reason": "TARGET_POST_SHA256_DRIFT"}

    # --- Portée de diff actuelle ---
    try:
        proc = subprocess.run(
            ["git", "diff", "--name-only"], cwd=str(root),
            capture_output=True, text=True, timeout=30,
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        return {"status": NOT_READY_EVIDENCE_INTEGRITY, "reason": f"DIFF_SCOPE_UNREADABLE:{exc}"}
    actual_diff_paths = sorted(p for p in proc.stdout.splitlines() if p.strip())
    expected_diff_paths = sorted([target_path])
    if actual_diff_paths != expected_diff_paths:
        return {
            "status": NOT_READY_EVIDENCE_INTEGRITY,
            "reason": "DIFF_SCOPE_DRIFT",
            "actual_diff_paths": actual_diff_paths,
            "expected_diff_paths": expected_diff_paths,
        }

    # --- Statut protégé de la cible (re-vérifié, jamais supposé) ---
    protected = L._is_protected_resolved((L._REPO_ROOT / target_path).resolve())
    protected_scope_status = "VIOLATED" if protected else "CLEAN"

    # ─────────────────────────────────────────────────────────────────
    # Traduction — chaque champ classé honnêtement. AUCUNE valeur
    # plausible n'est fabriquée pour un fait non capturé par le pipeline
    # CP9-CP14 (base_sha / manifest_hash / diff_hash) ; l'isolation
    # worktree/branche N'EST PAS déduite de "cible bornée" — ce sont des
    # propriétés distinctes.
    # ─────────────────────────────────────────────────────────────────

    checks = result.get("checks", [])
    required_count = result.get("required_check_count", len(checks))
    pass_count = sum(1 for c in checks if c.get("result") == "PASS")
    fail_count = sum(1 for c in checks if c.get("result") == "FAIL")
    error_count = sum(1 for c in checks if c.get("result") == "ERROR")

    if error_count > 0:
        tests_results = gates_results = "PARTIAL"
    elif fail_count > 0:
        tests_results = gates_results = "FAIL"
    elif pass_count == required_count and pass_count == len(checks):
        tests_results = gates_results = "PASS"
    else:
        tests_results = gates_results = "PARTIAL"

    first_failure = ""
    for c in checks:
        if c.get("result") != "PASS":
            first_failure = f"{c.get('check_id')}:{c.get('result')}"
            break

    # DÉRIVÉ, jamais fourni par un paramètre d'appel de cette fonction —
    # translate_evidence_to_tooling_build_state n'accepte aucun argument
    # worktree_isolated/branch_isolated/base_sha/manifest_hash : la seule
    # source possible est le PreExecutionContext déjà vérifié ci-dessus
    # (ou, à défaut, le comportement historique inchangé).
    if pre_ctx is not None:
        derived_worktree_isolated = pre_ctx["worktree_isolated"]
        derived_branch_isolated = pre_ctx["branch_isolated"]
        derived_base_sha = pre_ctx["base_sha"]
        derived_manifest_hash = pre_ctx["manifest_sha256"]
    else:
        derived_worktree_isolated = False
        derived_branch_isolated = False
        derived_base_sha = ""
        derived_manifest_hash = ""

    kwargs = {
        "session_id": child_execution_id,
        "objective": (proposal.get("objective") if proposal
                      else (envelope.get("objective") or child.get("operation_reason") or "")) or "",
        "base_sha": derived_base_sha,
        "manifest_hash": derived_manifest_hash,
        "diff_hash": "",
        "approved_scope": [target_path],
        "actual_touched_files": actual_diff_paths,
        "new_files": [],
        "deleted_files": [],
        "protected_scope_status": protected_scope_status,
        "human_approval_status": "APPROVED",
        "obsidure_status": "NOT_APPLICABLE",
        "worktree_isolated": derived_worktree_isolated,
        "branch_isolated": derived_branch_isolated,
        "auto_commit_disabled": True,
        "auto_push_disabled": True,
        "auto_merge_disabled": True,
        "tests_results": tests_results,
        "gates_results": gates_results,
        "first_failure": first_failure,
        "commit_status": "NOT_COMMITTED",
        "push_status": "NOT_PUSHED",
        "merge_status": "NOT_MERGED",
        "unknowns": [],
        "contradictions": [],
        "risk_flags": [],
        "decision_authority": "KX108_ONLY",
    }

    mappings = [
        _mapping("session_id", kwargs["session_id"], CLASSIFICATION_DERIVED,
                 "ExecutionEnvelope.children[0]", "child_execution_id",
                 "identifiant du child utilisé tel quel comme session_id"),
        _mapping("objective", kwargs["objective"], CLASSIFICATION_DIRECT,
                 "BatchProposal", "objective", "lu tel quel"),
        _mapping("base_sha", kwargs["base_sha"],
                 CLASSIFICATION_DERIVED if pre_ctx is not None else CLASSIFICATION_UNKNOWN,
                 "PreExecutionContext" if pre_ctx is not None else None,
                 "base_sha" if pre_ctx is not None else None,
                 "issu du PreExecutionContext vérifié (isolation dérivée de faits Git observés)"
                 if pre_ctx is not None else
                 "jamais capturé par le pipeline GIT_BLOB CP9-CP14 — "
                 "non recalculé après coup pour éviter de mal étiqueter "
                 "une valeur post-exécution comme fait pré-exécution"),
        _mapping("manifest_hash", kwargs["manifest_hash"],
                 CLASSIFICATION_DERIVED if pre_ctx is not None else CLASSIFICATION_UNKNOWN,
                 "PreExecutionContext" if pre_ctx is not None else None,
                 "manifest_sha256" if pre_ctx is not None else None,
                 "SHA256 complet issu du PreExecutionContext vérifié — jamais le hash 16-hex de compatibilité"
                 if pre_ctx is not None else
                 "jamais capturé — aucun concept de manifest dans ce pipeline"),
        _mapping("diff_hash", kwargs["diff_hash"], CLASSIFICATION_UNKNOWN,
                 None, None, "jamais capturé — aucun concept de diff_hash dans ce pipeline"),
        _mapping("approved_scope", kwargs["approved_scope"], CLASSIFICATION_DIRECT,
                 "ExecutionEnvelope.children[0]", "target_path", "portée approuvée = cible unique"),
        _mapping("actual_touched_files", kwargs["actual_touched_files"], CLASSIFICATION_DERIVED,
                 "git diff --name-only (relu maintenant)", None, "état réel du dépôt au moment de la traduction"),
        _mapping("new_files", [], CLASSIFICATION_DIRECT,
                 "ContentApply receipt", "operation_type",
                 "UPDATE_TARGET_FROM_SOURCE sur cible pré-existante — aucun fichier créé"),
        _mapping("deleted_files", [], CLASSIFICATION_DIRECT,
                 "ContentApply receipt", "operation_type", "aucune suppression"),
        _mapping("protected_scope_status", protected_scope_status, CLASSIFICATION_DERIVED,
                 "cible actuelle re-vérifiée", "target_path",
                 "_is_protected_resolved recalculé maintenant, jamais supposé"),
        _mapping("human_approval_status", "APPROVED", CLASSIFICATION_DIRECT,
                 "HumanApproval", "approval_status", "artefact chargé et validé"),
        _mapping("obsidure_status", "NOT_APPLICABLE", CLASSIFICATION_NOT_APPLICABLE,
                 None, None, "ACD-01 n'a jamais invoqué AgentObsidure — aucun agent actuel ne lit ce champ"),
        _mapping("worktree_isolated", derived_worktree_isolated,
                 CLASSIFICATION_DERIVED if pre_ctx is not None else CLASSIFICATION_FALSE,
                 "PreExecutionContext (derive_isolation_evidence)" if pre_ctx is not None else None,
                 "worktree_isolated" if pre_ctx is not None else None,
                 "dérivé de faits Git observés (git worktree list --porcelain, HEAD, status) — jamais d'une assertion d'appelant"
                 if pre_ctx is not None else
                 "le pipeline GIT_BLOB a lu/écrit directement sur repo_root — "
                 "aucun worktree isolé créé. 'cible bornée' != 'worktree isolé'."),
        _mapping("branch_isolated", derived_branch_isolated,
                 CLASSIFICATION_DERIVED if pre_ctx is not None else CLASSIFICATION_FALSE,
                 "PreExecutionContext (derive_isolation_evidence)" if pre_ctx is not None else None,
                 "branch_isolated" if pre_ctx is not None else None,
                 "dérivé de faits Git observés — jamais d'une assertion d'appelant"
                 if pre_ctx is not None else
                 "aucune branche dédiée créée pour cette exécution"),
        _mapping("auto_commit_disabled", True, CLASSIFICATION_DIRECT,
                 "pipeline CP9-CP14", None, "aucune fonction de ce pipeline n'appelle jamais git commit"),
        _mapping("auto_push_disabled", True, CLASSIFICATION_DIRECT,
                 "pipeline CP9-CP14", None, "aucune fonction de ce pipeline n'appelle jamais git push"),
        _mapping("auto_merge_disabled", True, CLASSIFICATION_DIRECT,
                 "pipeline CP9-CP14", None, "aucune fonction de ce pipeline n'appelle jamais git merge"),
        _mapping("tests_results", tests_results, CLASSIFICATION_DIRECT,
                 "TestContractResult", "checks[]", f"{pass_count} PASS / {fail_count} FAIL / {error_count} ERROR sur {len(checks)}"),
        _mapping("gates_results", gates_results, CLASSIFICATION_DERIVED,
                 "TestContractResult", "checks[]", "même dérivation que tests_results (pas de distinction test/gate dans ce contrat)"),
        _mapping("first_failure", first_failure, CLASSIFICATION_DERIVED,
                 "TestContractResult", "checks[]", "premier check non-PASS, vide si aucun"),
        _mapping("commit_status", "NOT_COMMITTED", CLASSIFICATION_DERIVED,
                 "git status (relu maintenant)", None, "cible modifiée non indexée, jamais commitée"),
        _mapping("push_status", "NOT_PUSHED", CLASSIFICATION_DIRECT,
                 "pipeline CP9-CP14", None, "aucun push jamais exécuté par ce pipeline"),
        _mapping("merge_status", "NOT_MERGED", CLASSIFICATION_DIRECT,
                 "pipeline CP9-CP14", None, "aucun merge jamais exécuté par ce pipeline"),
        _mapping("unknowns", [], CLASSIFICATION_NOT_APPLICABLE,
                 None, None,
                 "aucun inconnu hors-bande supplémentaire signalé par l'adaptateur — "
                 "les agents dérivent indépendamment leurs propres unknowns "
                 "(ex. BASE_SHA_MISSING) depuis les champs bruts ci-dessus"),
        _mapping("contradictions", [], CLASSIFICATION_NOT_APPLICABLE,
                 None, None,
                 "idem — les agents dérivent WORKTREE_NOT_ISOLATED/BRANCH_NOT_ISOLATED "
                 "directement depuis worktree_isolated/branch_isolated"),
        _mapping("risk_flags", [], CLASSIFICATION_NOT_APPLICABLE,
                 None, None, "aucun risque hors-bande supplémentaire connu de l'adaptateur"),
        _mapping("decision_authority", "KX108_ONLY", CLASSIFICATION_DIRECT,
                 "ExecutionEnvelope", "decision_authority", "lu tel quel"),
    ]

    # ── Évidence SCELLÉE C2 (optionnelle, additive) ──────────────────────
    # Fournie -> chargée + vérifiée + recoupée, puis ses id/hash exacts
    # entrent dans `provenance` AVANT le calcul de kx108_input_translation_hash
    # (le hash de traduction CHANGE donc si l'évidence scellée exacte change).
    # Absente -> `provenance` et la sortie restent byte-identiques à
    # l'historique (aucun champ ajouté). cf. §17.
    sealed_provenance_extra: dict = {}
    if sealed_apply_receipt_id or sealed_rollback_evidence_id:
        import sys as _sys
        _sd = str(Path(__file__).resolve().parent)
        if _sd not in _sys.path:
            _sys.path.insert(0, _sd)
        import obsidia_sealed_evidence_v0 as SEV
        if not (sealed_apply_receipt_id and sealed_rollback_evidence_id):
            return {"status": NOT_READY_EVIDENCE_INTEGRITY,
                    "reason": "SEALED_EVIDENCE_INCOMPLETE_BOTH_IDS_REQUIRED"}
        sar = SEV.load_sealed_apply_receipt(sealed_apply_receipt_id, sealed_receipt_dir)
        ok_sar, r_sar = SEV.verify_sealed_apply_receipt(sar)
        if not ok_sar:
            return {"status": NOT_READY_EVIDENCE_INTEGRITY,
                    "reason": f"SEALED_APPLY_RECEIPT_INVALID:{r_sar}"}
        sre = SEV.load_sealed_rollback_evidence(sealed_rollback_evidence_id, sealed_rollback_evidence_dir)
        ok_sre, r_sre = SEV.verify_sealed_rollback_evidence(sre)
        if not ok_sre:
            return {"status": NOT_READY_EVIDENCE_INTEGRITY,
                    "reason": f"SEALED_ROLLBACK_EVIDENCE_INVALID:{r_sre}"}
        cur_eah = envelope.get("execution_authority_hash")
        expected_post_sha256 = receipt.get("target_post_sha256")
        checks = [
            (sar.get("execution_authority_hash") == cur_eah, "SAR_EAH"),
            (sre.get("execution_authority_hash") == cur_eah, "SRE_EAH"),
            (sar.get("approval_id") == approval_id, "SAR_APPROVAL"),
            (sre.get("approval_id") == approval_id, "SRE_APPROVAL"),
            (sar.get("child_execution_id") == child_execution_id, "SAR_CHILD"),
            (sre.get("child_execution_id") == child_execution_id, "SRE_CHILD"),
            (sar.get("batch_execution_id") == batch_execution_id, "SAR_BATCH"),
            (sre.get("batch_execution_id") == batch_execution_id, "SRE_BATCH"),
            (sar.get("target_path") == target_path, "SAR_TARGET_PATH"),
            (sre.get("target_path") == target_path, "SRE_TARGET_PATH"),
            (sar.get("target_pre_sha256") == child.get("target_pre_sha256"), "SAR_TARGET_PRE"),
            (sre.get("pre_write_sha256") == child.get("target_pre_sha256"), "SRE_PRE_WRITE"),
            (sar.get("target_post_sha256") == expected_post_sha256, "SAR_TARGET_POST"),
            (sar.get("source_content_sha256") == child.get("source_content_sha256"), "SAR_SOURCE_SHA"),
            (sre.get("source_content_sha256") == child.get("source_content_sha256"), "SRE_SOURCE_SHA"),
            (sar.get("sealed_rollback_evidence_id") == sealed_rollback_evidence_id, "SAR_LINKS_SRE_ID"),
            (sar.get("sealed_rollback_evidence_hash") == sre.get("sealed_rollback_evidence_hash"), "SAR_LINKS_SRE_HASH"),
            (sar.get("kx108_pre_decision_record_id") == sre.get("kx108_pre_decision_record_id"), "SAR_SRE_PRE_ID"),
            (sar.get("kx108_pre_decision_record_hash") == sre.get("kx108_pre_decision_record_hash"), "SAR_SRE_PRE_HASH"),
        ]
        for ok_c, label in checks:
            if not ok_c:
                return {"status": NOT_READY_EVIDENCE_INTEGRITY,
                        "reason": f"SEALED_EVIDENCE_CROSS_LINK_MISMATCH:{label}"}
        sealed_provenance_extra = {
            "sealed_apply_receipt_id": sar["sealed_apply_receipt_id"],
            "sealed_apply_receipt_hash": sar["sealed_apply_receipt_hash"],
            "sealed_rollback_evidence_id": sre["sealed_rollback_evidence_id"],
            "sealed_rollback_evidence_hash": sre["sealed_rollback_evidence_hash"],
        }

    provenance = {
        "batch_execution_id": batch_execution_id,
        "child_execution_id": child_execution_id,
        "execution_authority_hash": envelope.get("execution_authority_hash"),
        "approval_id": approval_id,
        "test_contract_hash": envelope.get("test_contract_hash"),
        "test_contract_result_id": test_contract_result_id,
        "test_contract_result_record_hash": result.get("result_record_hash"),
        **sealed_provenance_extra,
    }

    translation_report = {
        "adapter_schema_version": ADAPTER_SCHEMA_VERSION,
        "created_at": _now(),
        **provenance,
        "field_mappings": mappings,
        "decision_authority": DECISION_AUTHORITY,
        "adapter_emits_kx108_decision": False,
    }

    payload_for_hash = {"tooling_build_state_kwargs": kwargs, **provenance}
    translation_report["kx108_input_translation_hash"] = compute_kx108_input_translation_hash(payload_for_hash)

    return {
        "status": READY_FOR_KX108_SUBMISSION,
        "tooling_build_state_kwargs": kwargs,
        "translation_report": translation_report,
    }

"""
obsidia_governed_execution_driver_v0.py
=======================================
GENERIC_GOVERNED_EXECUTION_INTERFACE_V0 — couche d'ORCHESTRATION / TRANSPORT
au-dessus du rail de remédiation gouverné DÉJÀ committé
(A1 -> C1 -> C2 -> D1 -> D2). Ce module :

  * ne définit AUCUNE nouvelle autorité ;
  * n'implémente AUCUNE seconde voie d'exécution ;
  * n'écrit JAMAIS une cible (aucun open/write/replace/copy) — la seule
    voie de remédiation qu'il invoque est
    `obsidia_governed_apply_v0.run_governed_content_apply` ;
  * n'invoque JAMAIS un kernel KX108 mocké / forcé — il appelle les
    chemins de production réels (adaptateur PRE + run_governed_content_apply
    qui invoque KX108_POST) ;
  * n'implémente AUCUN rollback — C2/D1/D2 en sont propriétaires ;
  * ne fait AUCUNE disposition Git (add/commit/push/merge/rebase/cherry-pick/
    stash/reset) ; seules des commandes Git de LECTURE d'identité/état
    exécutées à l'intérieur du code canonique d'isolation sont possibles.

Deux phases d'autorité logiquement distinctes :

  PREPARE  (`prepare_governed_execution`)
    Ledger (GIT_BLOB) -> BatchProposal (1 entrée) -> PreExecutionContext
    (isolation Git dérivée) -> prepare_execution(test_contract + PEC) ->
    RÉVÈLE l'execution_authority_hash exact, l'enfant exact, le contrat de
    test exact, les hash source/cible exacts, les magasins et IDs.
    S'ARRÊTE avant HumanApproval / KX108_PRE / mutation.

  EXECUTE  (`execute_governed_remediation`)
    Appelé APRÈS une autorisation humaine explicite SÉPARÉE qui NOMME
    l'execution_authority_hash exact revu. Recharge les artefacts
    canoniques persistés, recalcule l'EAH, exige
    recomputed == stocké == autorisé-par-l'humain, puis :
    persiste la HumanApproval -> adaptateur KX108_PRE ->
    run_and_persist_kx108_pre_execution_decision (ALLOW requis) ->
    run_governed_content_apply -> retourne le statut public verbatim.

`decision_authority = KX108_ONLY`. Aucune valeur de confort fournie par
l'appelant n'est jamais traitée comme autorité — l'autorité est
reconstruite depuis les artefacts persistés + les fonctions de
vérification de production existantes.
"""
from __future__ import annotations

import datetime
import hashlib
import sys
from pathlib import Path
from typing import Optional

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import obsidia_branching_ledger as _L
import obsidia_batch_selector as _S
import obsidia_batch_execution as _E
import obsidia_pre_execution_context as _PEC
import obsidia_test_contract as _TC
import obsidia_kx108_decision_store as _DS
import obsidia_kx108_pre_execution_evidence_adapter_v0 as _PREADP
import obsidia_governed_apply_v0 as _GA

DECISION_AUTHORITY = "KX108_ONLY"
OPERATION_TYPE = "UPDATE_TARGET_FROM_SOURCE"
SOURCE_KIND_GIT_BLOB = "GIT_BLOB"

# ── Statuts publics (aucune nouvelle autorité — enveloppe des statuts canoniques) ──
PREPARED_AWAITING_HUMAN_APPROVAL = "PREPARED_AWAITING_HUMAN_APPROVAL"
PREPARE_REJECTED = "PREPARE_REJECTED"
PRE_EXECUTION_REJECTED = "PRE_EXECUTION_REJECTED"
# Les issues terminales d'exécution sont celles de run_governed_content_apply,
# ré-exportées telles quelles :
KEPT_ELIGIBLE_FOR_HUMAN_COMMIT_REVIEW = _GA.GOVERNED_REMEDIATION_KEPT_ELIGIBLE_FOR_HUMAN_COMMIT_REVIEW
REJECTED_ROLLED_BACK = _GA.GOVERNED_REMEDIATION_REJECTED_ROLLED_BACK
ROLLBACK_FAILED_QUARANTINE = _GA.GOVERNED_REMEDIATION_ROLLBACK_FAILED_QUARANTINE
APPLY_REJECTED_NO_MUTATION = _GA.GOVERNED_REMEDIATION_APPLY_REJECTED_NO_MUTATION
APPLY_STATE_UNKNOWN_QUARANTINE = _GA.GOVERNED_REMEDIATION_APPLY_STATE_UNKNOWN_QUARANTINE


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _is_full_sha256(v) -> bool:
    return isinstance(v, str) and len(v) == 64 and all(c in "0123456789abcdef" for c in v.lower())


def _prep_reject(reason: str, **extra) -> dict:
    return {"status": PREPARE_REJECTED, "reason": reason,
            "authority": "NON_SOVEREIGN", "decision_authority": DECISION_AUTHORITY,
            "target_mutated": False, "kx108_invocations": 0,
            "human_approval_created": False, **extra}


def _pre_exec_reject(reason: str, **extra) -> dict:
    return {"status": PRE_EXECUTION_REJECTED, "reason": reason,
            "authority": "NON_SOVEREIGN", "decision_authority": DECISION_AUTHORITY,
            "target_mutated": False, **extra}


# ══════════════════════════════════════════════════════════════════════════
#  PHASE 1 — PREPARE  (aucune approbation, aucun KX108, aucune mutation)
# ══════════════════════════════════════════════════════════════════════════

def prepare_governed_execution(
    *,
    source_git_commit: str,
    source_historical_path: str,
    target_path: str,
    test_contract: dict,
    execution_worktree_path: "str | Path",
    main_worktree_path: "str | Path",
    branch_name: str,
    base_sha: str,
    repository_identity: Optional[str] = None,
    objective: str = "",
    ledger_dir: "str | Path",
    selector_dir: "str | Path",
    execution_dir: "str | Path",
    pre_execution_context_dir: "str | Path",
) -> dict:
    """
    Orchestration READ-ONLY vis-à-vis de la cible. Construit / recharge les
    artefacts canoniques et RÉVÈLE l'autorité exacte. NE crée NI HumanApproval
    NI décision KX108, NE mute PAS la cible.

    `test_contract` : un contrat au format `obsidia_test_contract` fourni par
    l'appelant — jamais réinterprété ici (seul son hash canonique est calculé
    pour la liaison PEC/enveloppe).
    """
    exec_root = Path(execution_worktree_path).resolve()
    repo_ident = repository_identity or str(exec_root)

    if not _is_full_sha256(base_sha) and not (isinstance(base_sha, str) and len(base_sha) == 40):
        # base_sha est un SHA de commit Git (40 hex) — jamais un hash de contenu.
        return _prep_reject("BASE_SHA_NOT_A_GIT_COMMIT_SHA")

    # 1. Cible : lue MAINTENANT dans le worktree d'exécution (précondition).
    target_abs = exec_root / str(target_path).replace("\\", "/")
    if not target_abs.exists() or not target_abs.is_file():
        return _prep_reject("TARGET_MISSING_IN_EXECUTION_WORKTREE", target_path=target_path)
    try:
        target_pre_sha256 = _sha256_hex(target_abs.read_bytes())
    except OSError as exc:
        return _prep_reject(f"TARGET_UNREADABLE:{exc}")

    # 2. Contrat de test — hash canonique (jamais réinterprété).
    if not isinstance(test_contract, dict) or not isinstance(test_contract.get("checks"), list):
        return _prep_reject("TEST_CONTRACT_MALFORMED")
    test_contract_hash = _TC.compute_test_contract_hash(test_contract)

    # 3. Source Git immuable -> Ledger (GIT_BLOB).
    reg = _L.register_git_blob_source(
        source_git_commit, source_historical_path,
        target_path=target_path,
        provenance_refs={"operation_type": OPERATION_TYPE},
        repo_root=exec_root, ledger_dir=Path(ledger_dir),
    )
    if reg.get("status") not in ("DISCOVERED", "ALREADY_REGISTERED"):
        return _prep_reject(f"LEDGER_REGISTRATION_FAILED:{reg.get('status')}:{reg.get('reason')}", ledger_result=reg)
    ledger_entry_id = reg["ledger_entry_id"]
    source_content_sha256 = reg.get("source_content_sha256")
    source_git_blob_sha = reg.get("source_git_blob_sha")
    if not _is_full_sha256(source_content_sha256):
        return _prep_reject("LEDGER_SOURCE_CONTENT_SHA256_NOT_FULL_64_HEX")
    if target_pre_sha256 == source_content_sha256:
        return _prep_reject("NO_OP_TARGET_ALREADY_EQUALS_SOURCE")

    # 4. BatchProposal à entrée unique (mode explicite — jamais GLOBAL).
    batch = _S.propose_batch(
        objective=objective or f"governed execution: {target_path}",
        candidate_entry_ids=[ledger_entry_id],
        ledger_dir=Path(ledger_dir), selector_dir=Path(selector_dir),
    )
    if batch.get("status") != _S.BATCH_PROPOSED or int(batch.get("selected_count") or 0) != 1:
        return _prep_reject(f"BATCH_PROPOSAL_NOT_SINGLE_READY:{batch.get('status')}:{batch.get('scope_error')}",
                            batch_result={k: batch.get(k) for k in
                                          ("batch_id", "status", "selected_count", "hold_count", "scope_error")})
    batch_id = batch["batch_id"]

    # 5. PreExecutionContext — isolation DÉRIVÉE de faits Git observés (jamais assertée).
    pec = _PEC.create_pre_execution_context(
        execution_worktree_path=exec_root, branch_name=branch_name, base_sha=base_sha,
        main_worktree_path=Path(main_worktree_path).resolve(),
        repository_identity=repo_ident, target_path=target_path,
        target_pre_sha256=target_pre_sha256, source_kind=SOURCE_KIND_GIT_BLOB,
        source_repository_identity=str(exec_root), source_commit=source_git_commit,
        source_blob_sha=source_git_blob_sha, source_path=source_historical_path,
        source_sha256=source_content_sha256, operation="REPLACE",
        approved_scope=[target_path], protected_scope_status="CLEAN",
        test_contract_hash=test_contract_hash, store_dir=Path(pre_execution_context_dir),
    )
    if not pec.get("verify_ok") or not pec.get("context_id"):
        return _prep_reject(f"PRE_EXECUTION_CONTEXT_NOT_VERIFIED:{pec.get('reason') or pec.get('verify_reason') or pec.get('status')}")
    context_id = pec["context_id"]
    context_record_hash = pec["record"]["context_record_hash"]

    # 6. ExecutionEnvelope (constructeur de production) + contrat de test + réf PEC.
    envelope = _E.prepare_execution(
        batch_id, ledger_dir=Path(ledger_dir), selector_dir=Path(selector_dir),
        execution_dir=Path(execution_dir), repo_root=exec_root,
        test_contract=test_contract,
        pre_execution_context={"context_id": context_id, "context_record_hash": context_record_hash},
        pre_execution_context_dir=Path(pre_execution_context_dir),
    )
    if not envelope.get("integrity_verified"):
        return _prep_reject(f"EXECUTION_ENVELOPE_NOT_INTEGRITY_VERIFIED:{envelope.get('integrity_error')}")
    recomputed_eah = _E.compute_execution_authority_hash(envelope)
    if not recomputed_eah or recomputed_eah != envelope.get("execution_authority_hash"):
        return _prep_reject("EXECUTION_AUTHORITY_HASH_DRIFT_AT_PREPARE")
    children = envelope.get("children") or []
    if len(children) != 1:
        return _prep_reject(f"UNEXPECTED_CHILD_COUNT:{len(children)}")
    child = children[0]
    if child.get("operation_type") != OPERATION_TYPE:
        return _prep_reject(f"UNSUPPORTED_OPERATION:{child.get('operation_type')}")
    if child.get("execution_status") != _E.PLANNED:
        return _prep_reject(f"CHILD_NOT_PLANNED:{child.get('execution_status')}")

    return {
        "status": PREPARED_AWAITING_HUMAN_APPROVAL,
        "reason": None,
        "authority": "NON_SOVEREIGN",
        "decision_authority": DECISION_AUTHORITY,
        "target_mutated": False,
        "kx108_invocations": 0,
        "human_approval_created": False,
        # ── autorité RÉVÉLÉE pour revue humaine ──
        "execution_authority_hash": recomputed_eah,
        "batch_execution_id": envelope["batch_execution_id"],
        "batch_id": batch_id,
        "child_execution_id": child["child_execution_id"],
        "ledger_entry_id": ledger_entry_id,
        "pre_execution_context_id": context_id,
        "pre_execution_context_record_hash": context_record_hash,
        "test_contract_hash": test_contract_hash,
        "test_contract": test_contract,
        "revealed_child": {
            "target_path": child.get("target_path"),
            "target_pre_sha256": child.get("target_pre_sha256"),
            "source_content_sha256": child.get("source_content_sha256"),
            "source_kind": child.get("source_kind"),
            "source_git_commit_sha": child.get("source_git_commit_sha"),
            "source_git_blob_sha": child.get("source_git_blob_sha"),
            "operation_type": child.get("operation_type"),
        },
        "stores": {
            "ledger_dir": str(ledger_dir), "selector_dir": str(selector_dir),
            "execution_dir": str(execution_dir),
            "pre_execution_context_dir": str(pre_execution_context_dir),
        },
        "next_required_action": "HUMAN_AUTHORIZE_EXACT_EXECUTION_AUTHORITY_HASH_THEN_CALL_execute_governed_remediation",
    }


# ══════════════════════════════════════════════════════════════════════════
#  PHASE 2 — EXECUTE  (appelée APRÈS autorisation humaine explicite de l'EAH)
# ══════════════════════════════════════════════════════════════════════════

AUTHORITY_MODE_PER_ACTION_HUMAN_EAH = "PER_ACTION_HUMAN_EAH"
AUTHORITY_MODE_BOUNDED_MISSION_AUTHORITY = "BOUNDED_MISSION_AUTHORITY"
DEFAULT_AUTHORITY_MODE = AUTHORITY_MODE_PER_ACTION_HUMAN_EAH


def execute_governed_remediation(
    batch_execution_id: str,
    child_execution_id: str,
    human_authorized_execution_authority_hash: "Optional[str]" = None,
    human_authorization_reference: "Optional[str]" = None,
    *,
    execution_dir: "str | Path",
    pre_execution_context_dir: "str | Path",
    selector_dir: "str | Path",
    ledger_dir: "str | Path",
    kx108_pre_decision_dir: "str | Path",
    kx108_post_decision_dir: "str | Path",
    test_contract_results_dir: "str | Path",
    sealed_receipt_dir: "str | Path",
    sealed_rollback_evidence_dir: "str | Path",
    rollback_result_dir: "str | Path",
    repo_root: "str | Path",
    approval_dir: "Optional[str | Path]" = None,
    authority_mode: str = DEFAULT_AUTHORITY_MODE,
    mission_id: "Optional[str]" = None,
    mission_store_dir: "Optional[str | Path]" = None,
) -> dict:
    """
    DEUX modes d'autorisation d'exécution, JAMAIS silencieux, JAMAIS de repli
    automatique de l'un à l'autre :

    * `PER_ACTION_HUMAN_EAH` (défaut, historique — sémantique BYTE-INCHANGÉE) :
      exige `human_authorized_execution_authority_hash` (== EAH recalculé) ET
      `human_authorization_reference`. HumanApproval `approved_by = HUMAN`.

    * `BOUNDED_MISSION_AUTHORITY` (Stage 4F, doit être choisi EXPLICITEMENT) :
      exige `mission_id` + `mission_store_dir` ; AUCUN EAH humain par action.
      L'évidence d'autorisation est une `DerivedMissionApprovalEvidence`
      construite par `obsidia_mission_authority_pre_adapter_v0` après
      rechargement + re-vérification de la chaîne CANONIQUE
      HumanMissionAuthorization (humaine) → DerivedActionAuthorityWitness.
      HumanApproval `approved_by = HUMAN_MISSION_AUTHORITY_DERIVED`.

    Dans LES DEUX modes : KX108_PRE reste la seule décision pré-exécution
    SOUVERAINE ; KX108_POST / D1 / D2 / C2 inchangés. En mode Stage 4F, une
    RE-VÉRIFICATION de fraîcheur est jouée après KX108_PRE ALLOW et avant
    toute mutation — si l'HMA a été révoquée entre-temps, aucune mutation.
    """
    _stage4 = (authority_mode == AUTHORITY_MODE_BOUNDED_MISSION_AUTHORITY)
    if authority_mode not in (AUTHORITY_MODE_PER_ACTION_HUMAN_EAH,
                              AUTHORITY_MODE_BOUNDED_MISSION_AUTHORITY):
        return _pre_exec_reject(f"UNKNOWN_AUTHORITY_MODE:{authority_mode}")

    if not _stage4:
        # ── Mode historique : entrées EXACTES ; toute référence de mission -> ambigu ──
        if mission_id is not None or mission_store_dir is not None:
            return _pre_exec_reject("AMBIGUOUS_DUAL_AUTHORITY_INPUT")
        if not (isinstance(human_authorized_execution_authority_hash, str)
                and _is_full_sha256(human_authorized_execution_authority_hash)):
            return _pre_exec_reject("HUMAN_AUTHORIZED_EAH_MISSING_OR_MALFORMED")
        if not (isinstance(human_authorization_reference, str) and human_authorization_reference.strip()):
            return _pre_exec_reject("HUMAN_AUTHORIZATION_REFERENCE_REQUIRED")
    else:
        # ── Mode Stage 4F : AUCUN EAH humain par action ; mission requise ──
        if human_authorized_execution_authority_hash is not None or human_authorization_reference is not None:
            return _pre_exec_reject("AMBIGUOUS_DUAL_AUTHORITY_INPUT")
        if not (isinstance(mission_id, str) and mission_id):
            return _pre_exec_reject("STAGE4_MISSION_ID_REQUIRED")
        if mission_store_dir is None:
            return _pre_exec_reject("STAGE4_MISSION_STORE_DIR_REQUIRED")

    execution_dir = Path(execution_dir)
    repo_root = Path(repo_root).resolve()
    approval_dir = Path(approval_dir) if approval_dir is not None else execution_dir

    # 1. Recharge + recalcul EAH — jamais la valeur de l'appelant comme autorité.
    envelope = _E._load_execution(batch_execution_id, execution_dir)
    if envelope is None:
        return _pre_exec_reject("EXECUTION_ENVELOPE_NOT_FOUND")
    if not envelope.get("integrity_verified"):
        return _pre_exec_reject("EXECUTION_ENVELOPE_INTEGRITY_NOT_VERIFIED")
    if envelope.get("decision_authority") != DECISION_AUTHORITY:
        return _pre_exec_reject("EXECUTION_ENVELOPE_DECISION_AUTHORITY_NOT_KX108_ONLY")
    recomputed_eah = _E.compute_execution_authority_hash(envelope)
    stored_eah = envelope.get("execution_authority_hash")
    if not recomputed_eah or recomputed_eah != stored_eah:
        return _pre_exec_reject("ENVELOPE_EAH_DRIFT", recomputed=recomputed_eah, stored=stored_eah)
    if (not _stage4) and human_authorized_execution_authority_hash != recomputed_eah:
        return _pre_exec_reject("HUMAN_AUTHORIZED_EAH_MISMATCH",
                                human_authorized=human_authorized_execution_authority_hash,
                                current_execution_authority_hash=recomputed_eah)

    child = next((c for c in (envelope.get("children") or [])
                 if c.get("child_execution_id") == child_execution_id), None)
    if child is None:
        return _pre_exec_reject("CHILD_NOT_FOUND")
    if child.get("execution_status") != _E.PLANNED:
        return _pre_exec_reject(f"CHILD_NOT_PLANNED:{child.get('execution_status')}")
    if child.get("operation_type") != OPERATION_TYPE:
        return _pre_exec_reject(f"UNSUPPORTED_OPERATION:{child.get('operation_type')}")

    # 2. PreExecutionContext — rechargé + revérifié (isolation / hash / scope).
    pcid = envelope.get("pre_execution_context_id")
    if not pcid:
        return _pre_exec_reject("PRE_EXECUTION_CONTEXT_REQUIRED")
    pctx = _PEC.load_pre_execution_context_record(pcid, Path(pre_execution_context_dir))
    ok_c, reason_c = _PEC.verify_pre_execution_context_record(pctx)
    if not ok_c:
        return _pre_exec_reject(f"PRE_EXECUTION_CONTEXT_INVALID:{reason_c}")
    if pctx.get("context_record_hash") != envelope.get("pre_execution_context_record_hash"):
        return _pre_exec_reject("PRE_EXECUTION_CONTEXT_HASH_MISMATCH")
    if not (pctx.get("worktree_isolated") and pctx.get("branch_isolated")):
        return _pre_exec_reject("PRE_EXECUTION_CONTEXT_ISOLATION_NOT_VERIFIED")
    if pctx.get("protected_scope_status") != "CLEAN":
        return _pre_exec_reject("PRE_EXECUTION_CONTEXT_PROTECTED_SCOPE_NOT_CLEAN")

    # 3. HumanApproval — persistée UNIQUEMENT ici, liée à l'EAH exact revérifié.
    _dmae_freshness_kwargs = None
    _derived_ctx = None
    if not _stage4:
        #    (approved_by="HUMAN" est le TRANSPORT de l'autorisation humaine explicite
        #     nommant human_authorized_execution_authority_hash ; cette fonction n'est
        #     jamais atteinte par un chemin automatique depuis PREPARE.)
        approval_id = "appr-" + hashlib.sha256(
            f"{batch_execution_id}:{child_execution_id}:{recomputed_eah}:{human_authorization_reference}"
            .encode("utf-8")).hexdigest()[:32]
        approval_record = {
            "approval_id": approval_id,
            "approval_schema_version": _E.SCHEMA_VERSION,
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "batch_execution_id": batch_execution_id,
            "batch_id": envelope.get("batch_id"),
            "batch_hash": envelope.get("batch_hash"),
            "candidate_scope_hash": envelope.get("candidate_scope_hash"),
            "execution_authority_hash": recomputed_eah,
            "approved_by": "HUMAN",
            "approval_status": _E.APPROVED_FOR_BOUNDED_EXECUTION,
            "decision_authority": DECISION_AUTHORITY,
            "human_authorization_reference": human_authorization_reference,
        }
        approval_record["approval_record_hash"] = _E.compute_approval_record_hash(approval_record)
        human_authorization_reference_effective = human_authorization_reference
    else:
        # ── Stage 4F : la DerivedMissionApprovalEvidence est construite par
        #    l'adaptateur PRE (rechargement + re-vérification CANONIQUE HMA→DAAW).
        #    Le driver ne fabrique JAMAIS approved_by=HUMAN_MISSION_AUTHORITY_DERIVED. ──
        import obsidia_mission_authority_pre_adapter_v0 as _PADP  # lazy : évite le cycle d'import
        _bd = _PADP.build_derived_mission_approval_evidence(
            mission_id=mission_id, batch_execution_id=batch_execution_id,
            child_execution_id=child_execution_id, execution_dir=execution_dir,
            mission_store_dir=mission_store_dir)
        if _bd.get("status") != _PADP.DMAE_BUILT:
            return _pre_exec_reject(f"DERIVED_MISSION_APPROVAL_REJECTED:{_bd.get('reason')}")
        approval_record = _bd["approval_record"]
        approval_id = approval_record["approval_id"]
        if approval_record.get("execution_authority_hash") != recomputed_eah:
            return _pre_exec_reject("DERIVED_APPROVAL_EAH_MISMATCH")
        human_authorization_reference_effective = approval_record.get("human_authorization_reference")
        _dmae_freshness_kwargs = dict(
            mission_id=mission_id,
            derived_mission_approval_evidence_id=_bd["derived_mission_approval_evidence_id"],
            batch_execution_id=batch_execution_id, child_execution_id=child_execution_id,
            execution_dir=execution_dir, mission_store_dir=mission_store_dir)
        # STAGE 4F REPAIR — contexte d'autorité dérivée CANONIQUE (localisation
        # uniquement ; jamais une autorité). Sans lui, tout consommateur
        # privilégié de l'approbation dérivée échoue fermé.
        _derived_ctx = _PADP.build_derived_authority_context(
            mission_id=mission_id, mission_store_dir=mission_store_dir,
            execution_dir=execution_dir,
            derived_mission_approval_evidence_id=_bd["derived_mission_approval_evidence_id"],
            batch_execution_id=batch_execution_id, child_execution_id=child_execution_id)
    store_res = _E.store_approval_artifact(approval_record, execution_dir=approval_dir)
    if store_res.get("status") not in ("STORED", "IDEMPOTENT_ALREADY_EXISTS"):
        return _pre_exec_reject(f"HUMAN_APPROVAL_STORE_FAILED:{store_res.get('status')}")
    approval = _E.load_approval_artifact(approval_id, execution_dir=approval_dir)
    ok_a, reason_a = _E.verify_approval_artifact(approval)
    if not ok_a:
        return _pre_exec_reject(f"HUMAN_APPROVAL_ARTIFACT_INVALID:{reason_a}")
    ok_v, reason_v = _E._validate_approval(
        approval, envelope, derived_authority_context=_derived_ctx)
    if not ok_v:
        return _pre_exec_reject(f"HUMAN_APPROVAL_NOT_BOUND_TO_EXECUTION:{reason_v}")

    # 4. KX108_PRE — adaptateur d'évidence pré-action réel + kernel réel.
    tr = _PREADP.translate_pre_execution_evidence_to_tooling_build_state(
        batch_execution_id, child_execution_id, approval_id,
        execution_dir=approval_dir, pre_execution_context_dir=Path(pre_execution_context_dir),
        repo_root=repo_root,
        derived_authority_context=_derived_ctx,
    )
    if tr.get("status") != _PREADP.STATUS_READY:
        return _pre_exec_reject(f"KX108_PRE_EVIDENCE_NOT_READY:{tr.get('reason')}")
    pre_out = _DS.run_and_persist_kx108_pre_execution_decision(
        tr["pre_tooling_build_state_kwargs"], tr["pre_binding_context"],
        store_dir=Path(kx108_pre_decision_dir),
    )
    if not pre_out.get("verify_ok") or not pre_out.get("record"):
        return _pre_exec_reject(f"KX108_PRE_DECISION_NOT_PERSISTED:{pre_out.get('verify_reason') or pre_out.get('reason')}")
    pre_gate = pre_out["record"].get("x108_gate")
    kx108_pre_decision_record_id = pre_out["decision_record_id"]
    if pre_gate != "ALLOW":
        return _pre_exec_reject(f"KX108_PRE_GATE_NOT_ALLOW:{pre_gate}",
                                kx108_pre_decision_record_id=kx108_pre_decision_record_id,
                                kx108_pre_gate=pre_gate)

    # 4bis. Stage 4F — RE-VÉRIFICATION de fraîcheur à la DERNIÈRE frontière sûre
    #       avant mutation : recharge les révocations + la projection et rejoue
    #       les vérificateurs Stage 4C. Une HMA révoquée entre la construction de
    #       la DMAE et ce point -> STALE -> AUCUNE mutation. N'altère AUCUNE
    #       sémantique KX108 / C2. (Le résidu strictement interne à
    #       run_governed_content_apply appartient à une extension C2 future
    #       séparément autorisée.)
    if _stage4 and _dmae_freshness_kwargs is not None:
        import obsidia_mission_authority_pre_adapter_v0 as _PADP  # lazy
        _fr = _PADP.verify_derived_mission_approval_evidence_fresh(**_dmae_freshness_kwargs)
        if _fr.get("status") != _PADP.DMAE_FRESH:
            return _pre_exec_reject(f"DERIVED_MISSION_APPROVAL_STALE_BEFORE_MUTATION:{_fr.get('reason')}",
                                    kx108_pre_decision_record_id=kx108_pre_decision_record_id,
                                    kx108_pre_gate=pre_gate, no_mutation=True,
                                    kx_pre_semantics_changed=False)

    # 5. Voie de remédiation UNIQUE — run_governed_content_apply (aucune écriture ici).
    result = _GA.run_governed_content_apply(
        batch_execution_id, child_execution_id, approval_id, kx108_pre_decision_record_id,
        execution_dir=approval_dir, pre_execution_context_dir=Path(pre_execution_context_dir),
        kx108_decision_dir=Path(kx108_pre_decision_dir),
        post_decision_store_dir=Path(kx108_post_decision_dir),
        selector_dir=Path(selector_dir), ledger_dir=Path(ledger_dir),
        test_contract_results_dir=Path(test_contract_results_dir),
        sealed_receipt_dir=Path(sealed_receipt_dir),
        sealed_rollback_evidence_dir=Path(sealed_rollback_evidence_dir),
        rollback_result_dir=Path(rollback_result_dir),
        repo_root=repo_root,
        derived_authority_context=_derived_ctx,
    )
    # Le statut est déjà une issue publique GOVERNED_REMEDIATION_* — verbatim.
    out = dict(result)
    out.update({
        "phase": "EXECUTE",
        "approval_id": approval_id,
        "authority_mode": authority_mode,
        "human_authorization_reference": human_authorization_reference_effective,
        "kx108_pre_decision_record_id": kx108_pre_decision_record_id,
        "kx108_pre_gate": pre_gate,
        "execution_authority_hash": recomputed_eah,
        "driver_authored_rollback": False,
        "driver_git_disposition": False,
        "derived_mission_approval_evidence_id": (
            approval_record.get("derived_mission_approval_evidence_id") if _stage4 else None),
    })
    return out

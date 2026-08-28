"""
obsidia_mission_authority_pre_adapter_v0.py
===========================================
STAGE 4F — adaptateur de COMPATIBILITÉ PRE : construit une
`DerivedMissionApprovalEvidence` (DMAE) qui sert d'ÉVIDENCE D'AUTORISATION
HUMAINE au rail PRE, dans le mode d'exécution `BOUNDED_MISSION_AUTHORITY`.

Ce que la DMAE EST :
  - un artefact write-once, lié-contenu, NON_SOUVERAIN, qui atteste qu'à
    l'instant de sa construction, la chaîne HumanMissionAuthorization
    (humaine) → DerivedActionAuthorityWitness (machine, NON_SOUVERAIN) a
    été rechargée depuis les artefacts CANONIQUES et re-vérifiée par les
    vérificateurs COMMITTÉS Stage 4C, contre la projection de mission
    COURANTE, l'ExecutionEnvelope EXACT et l'EAH canonique.

Ce que la DMAE N'EST PAS :
  - une `HumanMissionAuthorization`, une `DerivedActionAuthorityWitness`,
    une approbation humaine action-par-action, une décision KX, ni une
    autorité d'exécution en soi.

KX108_PRE reste la SEULE décision pré-exécution SOUVERAINE. La DMAE
n'ouvre qu'une TENTATIVE d'exécution ; KX108_PRE puis KX108_POST/D1/D2
gardent leurs vetos indépendants et inchangés.

`build_derived_mission_approval_evidence` est le SEUL constructeur d'une
DMAE. Le driver / le séquenceur ne fabriquent jamais `approved_by =
HUMAN_MISSION_AUTHORITY_DERIVED` eux-mêmes.

`verify_derived_mission_approval_evidence_fresh` est la RE-VÉRIFICATION de
fraîcheur exécutée par le driver à la DERNIÈRE frontière sûre avant
mutation (après KX108_PRE ALLOW, avant `run_governed_content_apply`) —
elle recharge les révocations + la projection et rejoue les vérificateurs
Stage 4C. Si l'HMA a été révoquée entre la construction de la DMAE et ce
point, la mutation n'a pas lieu.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import obsidia_bounded_mission_v0 as _M
import obsidia_mission_authority_v0 as _MA
import obsidia_mission_authority_integration_v0 as _INT
import obsidia_batch_execution as _E

DMAE_SCHEMA_VERSION = 1
DMAE_DOMAIN_TAG = "OBSIDIA_STAGE4F_DMAE_V0"
DMAE_SOVEREIGNTY = "NON_SOVEREIGN"
AUTHORITY_MODE_STAGE4 = "BOUNDED_MISSION_AUTHORITY"
AUTHORITY_MODE_HISTORICAL = "PER_ACTION_HUMAN_EAH"

APPROVED_BY_DERIVED = "HUMAN_MISSION_AUTHORITY_DERIVED"
APPROVAL_KIND_DERIVED = "DERIVED_MISSION_AUTHORITY_EVIDENCE_V0"

DMAE_BUILT = "DERIVED_MISSION_APPROVAL_EVIDENCE_BUILT"
DMAE_BUILD_REJECTED = "DERIVED_MISSION_APPROVAL_EVIDENCE_BUILD_REJECTED"
DMAE_FRESH = "DERIVED_MISSION_APPROVAL_EVIDENCE_FRESH"
DMAE_STALE = "DERIVED_MISSION_APPROVAL_EVIDENCE_STALE"

_DMAE_BOUND_FIELDS = (
    "dmae_schema_version", "domain_tag", "sovereignty", "authority_mode",
    "mission_id", "mission_genesis_record_hash", "plan_id", "plan_hash",
    "action_id", "ordinal",
    "hma_id", "hma_record_hash", "daaw_id", "daaw_record_hash",
    "batch_execution_id", "child_execution_id",
    "execution_authority_hash", "action_base_sha",
    "mission_revision", "mission_revision_record_hash",
)

_canon = _M._canon
_sha256_hex = _M._sha256_hex


def _dmae_dir(mission_id: str, store_dir: "str | Path") -> Path:
    return _M._mission_dir(mission_id, Path(store_dir)) / "derived_mission_approvals"


def _rej(reason: str, **extra) -> dict:
    return {"status": DMAE_BUILD_REJECTED, "reason": reason,
            "derived_approval_sovereignty": "NON_SOVEREIGN",
            "is_execution_authority": False,
            "bypasses_kx_pre": False, **extra}


def _load_recorded_witness_and_artifact(proj: dict, action_id: str,
                                        mission_id: str, store_dir: "str | Path"):
    w = next((x for x in (proj.get("derived_witnesses") or [])
              if x.get("action_id") == action_id), None)
    if w is None:
        return None, None, "NO_DERIVED_WITNESS_FOR_ACTION"
    art = _INT.load_action_authority_witness(mission_id, w.get("daaw_id"), store_dir)
    if not isinstance(art, dict):
        return w, None, "DAAW_ARTIFACT_MISSING"
    if (art.get("derived_action_authority_witness_id") != w.get("daaw_id")
            or art.get("daaw_record_hash") != w.get("daaw_record_hash")
            or art.get("execution_authority_hash") != w.get("execution_authority_hash")
            or art.get("action_base_sha") != w.get("action_base_sha")
            or art.get("human_mission_authorization_id") != w.get("hma_id")):
        return w, None, "DAAW_ARTIFACT_DISAGREES_WITH_EVENT"
    return w, art, None


def _verify_chain(*, mission_id, store_dir, execution_dir, batch_execution_id):
    """Recharge + revérifie la chaîne CANONIQUE HMA→DAAW contre l'état courant.
    Retourne (ctx, None) ou (None, reason)."""
    env = _E._load_execution(batch_execution_id, Path(execution_dir))
    if env is None:
        return None, "EXECUTION_ENVELOPE_NOT_FOUND"
    recomputed_eah = _E.compute_execution_authority_hash(env)
    if not (isinstance(recomputed_eah, str) and recomputed_eah == env.get("execution_authority_hash")):
        return None, "ENVELOPE_EAH_DRIFT"

    proj = _M.project_mission(mission_id=mission_id, mission_store_dir=store_dir)
    if proj["status"] != _M.STATUS_PROJECTION_OK:
        return None, f"MISSION_NOT_PROJECTABLE:{proj.get('reason') or proj['status']}"
    if not proj.get("active_hma_id"):
        return None, "NO_MISSION_AUTHORITY_BOUND"
    if proj["current_state"] != _M.S_ACTION_PREPARED:
        return None, f"MISSION_NOT_IN_ACTION_PREPARED_STATE:{proj['current_state']}"
    if proj.get("plan_completed"):
        return None, "MISSION_PLAN_COMPLETED"

    pe = proj.get("last_prepared_evidence") or {}
    action_id = pe.get("action_id")
    ordinal = pe.get("ordinal")
    child_execution_id = pe.get("child_execution_id")
    if pe.get("batch_execution_id") != batch_execution_id:
        return None, "PREPARED_ENVELOPE_MISMATCH"
    if pe.get("execution_authority_hash") != recomputed_eah:
        return None, "PREPARED_EAH_MISMATCH"

    genesis = _M.load_mission_genesis(mission_id, store_dir)
    plan = _M.load_mission_plan(mission_id, proj["active_hma_plan_id"], store_dir)
    hma = _MA.load_human_mission_authorization(mission_id, proj["active_hma_id"], store_dir)
    if hma is None or plan is None or genesis is None:
        return None, "HMA_OR_PLAN_OR_GENESIS_NOT_LOADABLE"
    if not (isinstance(hma.get("human_authorization_reference"), str)
            and hma["human_authorization_reference"].strip()):
        return None, "HMA_HUMAN_AUTHORIZATION_REFERENCE_ABSENT"

    revocations = _MA.list_mission_authority_revocations(mission_id, store_dir)
    ok_h, why_h = _MA.verify_human_mission_authorization(
        hma, genesis=genesis, plan=plan, revocations=revocations)
    if not ok_h:
        return None, f"HMA_INVALID:{why_h}"

    w, art, why_w = _load_recorded_witness_and_artifact(proj, action_id, mission_id, store_dir)
    if why_w:
        return None, why_w
    ok_d, why_d = _MA.verify_derived_action_authority_witness(
        daaw=art, hma=hma, plan=plan, genesis=genesis, projection=proj,
        execution_envelope=env, revocations=revocations)
    if not ok_d:
        return None, f"DAAW_INVALID:{why_d}"
    if art.get("execution_authority_hash") != recomputed_eah:
        return None, "DAAW_EAH_NOT_CANONICAL_EAH"
    if art.get("action_base_sha") != proj.get("mission_tip_sha"):
        return None, "DAAW_ACTION_BASE_NOT_CURRENT_MISSION_TIP"

    return {
        "env": env, "recomputed_eah": recomputed_eah, "proj": proj,
        "genesis": genesis, "plan": plan, "hma": hma, "daaw": art,
        "action_id": action_id, "ordinal": ordinal,
        "child_execution_id": child_execution_id,
    }, None


# ══════════════════════════════════════════════════════════════════════════
#  1 — Construction de la DerivedMissionApprovalEvidence
# ══════════════════════════════════════════════════════════════════════════

def build_derived_mission_approval_evidence(
    *, mission_id: str, batch_execution_id: str, child_execution_id: str,
    execution_dir: "str | Path", mission_store_dir: "str | Path",
) -> dict:
    """SEUL constructeur d'une DMAE. Recharge + revérifie TOUTE la chaîne
    canonique avant construction. Renvoie aussi un `approval_record`
    compatible PRE (`approved_by = HUMAN_MISSION_AUTHORITY_DERIVED`, dont
    la `human_authorization_reference` provient de l'HMA HUMAINE)."""
    store_dir = Path(mission_store_dir)
    ctx, why = _verify_chain(mission_id=mission_id, store_dir=store_dir,
                             execution_dir=execution_dir, batch_execution_id=batch_execution_id)
    if ctx is None:
        return _rej(why)
    if ctx["child_execution_id"] != child_execution_id:
        return _rej("CHILD_EXECUTION_ID_MISMATCH")

    env = ctx["env"]
    proj = ctx["proj"]
    hma = ctx["hma"]
    daaw = ctx["daaw"]

    dmae = {
        "dmae_schema_version": DMAE_SCHEMA_VERSION,
        "domain_tag": DMAE_DOMAIN_TAG,
        "sovereignty": DMAE_SOVEREIGNTY,
        "authority_mode": AUTHORITY_MODE_STAGE4,
        "mission_id": mission_id,
        "mission_genesis_record_hash": ctx["genesis"]["mission_genesis_record_hash"],
        "plan_id": ctx["plan"]["plan_id"],
        "plan_hash": ctx["plan"]["plan_hash"],
        "action_id": ctx["action_id"],
        "ordinal": ctx["ordinal"],
        "hma_id": hma["human_mission_authorization_id"],
        "hma_record_hash": hma["hma_record_hash"],
        "daaw_id": daaw["derived_action_authority_witness_id"],
        "daaw_record_hash": daaw["daaw_record_hash"],
        "batch_execution_id": batch_execution_id,
        "child_execution_id": child_execution_id,
        "execution_authority_hash": ctx["recomputed_eah"],
        "action_base_sha": daaw["action_base_sha"],
        "mission_revision": proj["revision"],
        "mission_revision_record_hash": proj["mission_revision_record_hash"],
        # informationnel (hors matériel d'identité)
        "is_execution_authority": False,
        "bypasses_kx_pre": False,
        "human_authorization_reference": hma["human_authorization_reference"],
        "kx_decision_authority": "KX108_ONLY",
    }
    rh = _sha256_hex(_canon({k: dmae.get(k) for k in _DMAE_BOUND_FIELDS}))
    dmae["dmae_record_hash"] = rh
    dmae["derived_mission_approval_evidence_id"] = "dmae-" + rh[:32]

    try:
        p = _M._safe_id_path(_dmae_dir(mission_id, store_dir),
                             dmae["derived_mission_approval_evidence_id"])
    except ValueError:
        return _rej("INVALID_DMAE_ID")
    st = _M._atomic_publish_json(p, dmae)
    if st == "IMMUTABILITY_VIOLATION":
        return _rej("DMAE_IMMUTABILITY_VIOLATION")

    import hashlib as _hl
    approval_id = "appr-" + _hl.sha256(
        f"{batch_execution_id}:{child_execution_id}:{ctx['recomputed_eah']}:"
        f"{dmae['derived_mission_approval_evidence_id']}".encode("utf-8")).hexdigest()[:32]
    # locator canonique LIÉ AU HASH de l'approbation (jamais une autorité) : permet
    # aux consommateurs POST / rollback, qui n'ont pas de paramètre de contexte, de
    # RE-LOCALISER + RE-VÉRIFIER l'artefact DMAE canonique. Toute altération casse
    # `approval_record_hash` (champ additif lié UNIQUEMENT pour approved_by dérivé).
    embedded_authority_locator = build_derived_authority_context(
        mission_id=mission_id, mission_store_dir=store_dir, execution_dir=execution_dir,
        derived_mission_approval_evidence_id=dmae["derived_mission_approval_evidence_id"],
        batch_execution_id=batch_execution_id, child_execution_id=child_execution_id)
    approval_record = {
        "approval_id": approval_id,
        "approval_schema_version": _E.SCHEMA_VERSION,
        "created_at": _M._now(),
        "batch_execution_id": batch_execution_id,
        "batch_id": env.get("batch_id"),
        "batch_hash": env.get("batch_hash"),
        "candidate_scope_hash": env.get("candidate_scope_hash"),
        "execution_authority_hash": ctx["recomputed_eah"],
        "approved_by": APPROVED_BY_DERIVED,
        "approval_status": _E.APPROVED_FOR_BOUNDED_EXECUTION,
        "decision_authority": _E.DECISION_AUTHORITY,
        "human_authorization_reference": hma["human_authorization_reference"],
        "approval_kind": APPROVAL_KIND_DERIVED,
        "derived_mission_approval_evidence_id": dmae["derived_mission_approval_evidence_id"],
        "embedded_authority_locator": embedded_authority_locator,
    }
    approval_record["approval_record_hash"] = _E.compute_approval_record_hash(approval_record)

    return {
        "status": DMAE_BUILT, "reason": None,
        "dmae": dmae,
        "derived_mission_approval_evidence_id": dmae["derived_mission_approval_evidence_id"],
        "dmae_record_hash": rh,
        "approval_record": approval_record,
        "execution_authority_hash": ctx["recomputed_eah"],
        "action_id": ctx["action_id"], "ordinal": ctx["ordinal"],
        "child_execution_id": child_execution_id,
        "hma_id": hma["human_mission_authorization_id"],
        "daaw_id": daaw["derived_action_authority_witness_id"],
        "human_authorization_reference": hma["human_authorization_reference"],
        "dmae_store_status": st,
        "derived_approval_sovereignty": "NON_SOVEREIGN",
        "is_execution_authority": False, "bypasses_kx_pre": False,
    }


def load_derived_mission_approval_evidence(mission_id: str, dmae_id: str,
                                           mission_store_dir: "str | Path") -> Optional[dict]:
    import json
    try:
        p = _M._safe_id_path(_dmae_dir(mission_id, mission_store_dir), dmae_id)
    except ValueError:
        return None
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def verify_derived_mission_approval_evidence(dmae: Optional[dict]) -> "tuple[bool, Optional[str]]":
    """Intégrité structurelle du record DMAE (hash + id dérivés)."""
    if not isinstance(dmae, dict):
        return False, "DMAE_MISSING"
    if dmae.get("dmae_schema_version") != DMAE_SCHEMA_VERSION:
        return False, "DMAE_SCHEMA_UNSUPPORTED"
    if dmae.get("domain_tag") != DMAE_DOMAIN_TAG:
        return False, "DMAE_DOMAIN_TAG_MISMATCH"
    if dmae.get("sovereignty") != DMAE_SOVEREIGNTY:
        return False, "DMAE_NOT_NON_SOVEREIGN"
    if dmae.get("authority_mode") != AUTHORITY_MODE_STAGE4:
        return False, "DMAE_AUTHORITY_MODE_INVALID"
    for f in _DMAE_BOUND_FIELDS:
        if f not in dmae:
            return False, f"DMAE_FIELD_MISSING:{f}"
    rh = _sha256_hex(_canon({k: dmae.get(k) for k in _DMAE_BOUND_FIELDS}))
    if dmae.get("dmae_record_hash") != rh:
        return False, "DMAE_RECORD_HASH_MISMATCH"
    if dmae.get("derived_mission_approval_evidence_id") != "dmae-" + rh[:32]:
        return False, "DMAE_ID_NOT_DERIVED"
    return True, None


# ══════════════════════════════════════════════════════════════════════════
#  2 — RE-VÉRIFICATION de fraîcheur juste avant mutation (driver Stage 4F)
# ══════════════════════════════════════════════════════════════════════════

def verify_derived_mission_approval_evidence_fresh(
    *, mission_id: str, derived_mission_approval_evidence_id: str,
    batch_execution_id: str, child_execution_id: str,
    execution_dir: "str | Path", mission_store_dir: "str | Path",
) -> dict:
    """Rejoue les vérificateurs Stage 4C contre l'état COURANT (révocations
    rechargées). Appelée après KX108_PRE ALLOW, avant toute mutation. Si
    l'HMA a été révoquée entre-temps -> STALE -> aucune mutation."""
    store_dir = Path(mission_store_dir)
    dmae = load_derived_mission_approval_evidence(mission_id, derived_mission_approval_evidence_id, store_dir)
    ok_s, why_s = verify_derived_mission_approval_evidence(dmae)
    if not ok_s:
        return {"status": DMAE_STALE, "reason": f"DMAE_STRUCTURAL:{why_s}",
                "no_mutation": True, "kx_pre_semantics_changed": False}
    if dmae.get("batch_execution_id") != batch_execution_id or dmae.get("child_execution_id") != child_execution_id:
        return {"status": DMAE_STALE, "reason": "DMAE_ENVELOPE_MISMATCH",
                "no_mutation": True, "kx_pre_semantics_changed": False}

    ctx, why = _verify_chain(mission_id=mission_id, store_dir=store_dir,
                             execution_dir=execution_dir, batch_execution_id=batch_execution_id)
    if ctx is None:
        return {"status": DMAE_STALE, "reason": f"DMAE_FRESHNESS:{why}",
                "no_mutation": True, "kx_pre_semantics_changed": False}

    # l'action / plan / EAH / base doivent être EXACTEMENT ceux liés dans la DMAE
    if (ctx["action_id"] != dmae["action_id"]
            or ctx["plan"]["plan_hash"] != dmae["plan_hash"]
            or ctx["recomputed_eah"] != dmae["execution_authority_hash"]
            or ctx["daaw"]["action_base_sha"] != dmae["action_base_sha"]
            or ctx["daaw"]["derived_action_authority_witness_id"] != dmae["daaw_id"]
            or ctx["hma"]["human_mission_authorization_id"] != dmae["hma_id"]
            or ctx["hma"]["hma_record_hash"] != dmae["hma_record_hash"]):
        return {"status": DMAE_STALE, "reason": "DMAE_FRESHNESS:BINDING_DRIFT",
                "no_mutation": True, "kx_pre_semantics_changed": False}

    return {"status": DMAE_FRESH, "reason": None, "no_mutation": False,
            "kx_pre_semantics_changed": False,
            "derived_mission_approval_evidence_id": derived_mission_approval_evidence_id}


# ══════════════════════════════════════════════════════════════════════════
#  3 — Contexte d'autorité dérivée CANONIQUE (Fix A) — NON_SOUVERAIN
# ══════════════════════════════════════════════════════════════════════════
#
# Un `derived_authority_context` ne PORTE AUCUNE preuve : il ne fait que
# LOCALISER l'évidence canonique (magasins + identifiants). Toute
# consommation privilégiée d'une approbation `approved_by =
# HUMAN_MISSION_AUTHORITY_DERIVED` DOIT le fournir, sinon FAIL_CLOSED.

DERIVED_AUTHORITY_CONTEXT_IS_AUTHORITY = False
DERIVED_AUTHORITY_CONTEXT_REQUIRES_CANONICAL_RELOAD = True

_DERIVED_CONTEXT_FIELDS = (
    "mission_id", "mission_store_dir", "execution_dir",
    "derived_mission_approval_evidence_id",
    "batch_execution_id", "child_execution_id",
)


def build_derived_authority_context(
    *, mission_id: str, mission_store_dir: "str | Path", execution_dir: "str | Path",
    derived_mission_approval_evidence_id: str,
    batch_execution_id: str, child_execution_id: str,
) -> dict:
    """Assemble un contexte de LOCALISATION (jamais une autorité). Ajoute la
    racine de verrou de linéarisation dérivée de façon CANONIQUE."""
    import obsidia_mission_authority_freshness_lock_v0 as _LK
    return {
        "context_domain_tag": "OBSIDIA_STAGE4F_DERIVED_AUTHORITY_CONTEXT_V0",
        "is_authority": False,
        "requires_canonical_reload": True,
        "mission_id": str(mission_id),
        "mission_store_dir": str(mission_store_dir),
        "execution_dir": str(execution_dir),
        "derived_mission_approval_evidence_id": str(derived_mission_approval_evidence_id),
        "batch_execution_id": str(batch_execution_id),
        "child_execution_id": str(child_execution_id),
        "authority_lock_root": _LK.authority_lock_root_for(str(mission_id), mission_store_dir),
    }


def _context_shape_ok(ctx) -> "tuple[bool, Optional[str]]":
    if not isinstance(ctx, dict):
        return False, "DERIVED_AUTHORITY_CONTEXT_MISSING"
    for f in _DERIVED_CONTEXT_FIELDS:
        v = ctx.get(f)
        if not (isinstance(v, str) and v.strip()):
            return False, f"DERIVED_AUTHORITY_CONTEXT_FIELD_MISSING:{f}"
    if ctx.get("is_authority") is not False:
        return False, "DERIVED_AUTHORITY_CONTEXT_CLAIMS_AUTHORITY"
    return True, None


def verify_derived_approval_with_context(
    approval: dict, envelope: dict, derived_authority_context,
) -> "tuple[bool, Optional[str]]":
    """VÉRIFICATEUR CENTRALISÉ appelé par `_validate_approval` (branche
    dérivée), l'adaptateur d'évidence KX108_PRE et l'entrée C2. Recharge et
    revérifie TOUTE la chaîne canonique DMAE → HMA (racine humaine +
    révocations) → DAAW → EAH exact → projection de mission courante
    (état/plan/action/tip/dépendances/budget/non-close), puis exige une
    liaison EXACTE DMAE ↔ approbation. `approved_by` structurellement valide
    seul ne suffit JAMAIS."""
    ok_c, why_c = _context_shape_ok(derived_authority_context)
    if not ok_c:
        return False, why_c
    ctx = derived_authority_context

    if not isinstance(approval, dict):
        return False, "APPROVAL_MISSING"
    if approval.get("approved_by") != APPROVED_BY_DERIVED:
        return False, "APPROVAL_NOT_DERIVED"
    if approval.get("approval_kind") != APPROVAL_KIND_DERIVED:
        return False, "DERIVED_APPROVAL_KIND_INVALID"
    dmae_id_ap = approval.get("derived_mission_approval_evidence_id")
    if not (isinstance(dmae_id_ap, str) and dmae_id_ap.startswith("dmae-")):
        return False, "DERIVED_APPROVAL_EVIDENCE_ID_MISSING"
    if dmae_id_ap != ctx["derived_mission_approval_evidence_id"]:
        return False, "DERIVED_APPROVAL_EVIDENCE_ID_NOT_IN_CONTEXT"

    beid = ctx["batch_execution_id"]
    child = ctx["child_execution_id"]
    if approval.get("batch_execution_id") != beid:
        return False, "CONTEXT_BATCH_EXECUTION_ID_MISMATCH_APPROVAL"
    if isinstance(envelope, dict) and envelope.get("batch_execution_id") not in (None, beid):
        return False, "CONTEXT_BATCH_EXECUTION_ID_MISMATCH_ENVELOPE"

    # chaîne canonique complète rejouée contre l'état COURANT (révocations incluses)
    fr = verify_derived_mission_approval_evidence_fresh(
        mission_id=ctx["mission_id"],
        derived_mission_approval_evidence_id=dmae_id_ap,
        batch_execution_id=beid, child_execution_id=child,
        execution_dir=ctx["execution_dir"], mission_store_dir=ctx["mission_store_dir"])
    if fr.get("status") != DMAE_FRESH:
        return False, f"CANONICAL_CHAIN_NOT_FRESH:{fr.get('reason')}"

    dmae = load_derived_mission_approval_evidence(
        ctx["mission_id"], dmae_id_ap, ctx["mission_store_dir"])
    ok_s, why_s = verify_derived_mission_approval_evidence(dmae)
    if not ok_s:
        return False, f"DMAE_STRUCTURAL:{why_s}"

    # liaison EXACTE DMAE ↔ approbation (une VRAIE DMAE quelque part ne suffit pas)
    eah = dmae.get("execution_authority_hash")
    if dmae.get("derived_mission_approval_evidence_id") != dmae_id_ap:
        return False, "DMAE_ID_MISMATCH"
    if dmae.get("batch_execution_id") != beid or dmae.get("child_execution_id") != child:
        return False, "DMAE_ENVELOPE_BINDING_MISMATCH"
    if dmae.get("mission_id") != ctx["mission_id"]:
        return False, "DMAE_MISSION_ID_MISMATCH_CONTEXT"
    if dmae.get("authority_mode") != AUTHORITY_MODE_STAGE4:
        return False, "DMAE_AUTHORITY_MODE_NOT_STAGE4"
    if approval.get("execution_authority_hash") != eah:
        return False, "APPROVAL_EAH_MISMATCH_DMAE"
    if isinstance(envelope, dict) and envelope.get("execution_authority_hash") not in (None, eah):
        return False, "ENVELOPE_EAH_MISMATCH_DMAE"
    if approval.get("human_authorization_reference") != dmae.get("human_authorization_reference"):
        return False, "APPROVAL_HUMAN_ROOT_MISMATCH_DMAE"

    import hashlib as _hl
    expected_approval_id = "appr-" + _hl.sha256(
        f"{beid}:{child}:{eah}:{dmae_id_ap}".encode("utf-8")).hexdigest()[:32]
    if approval.get("approval_id") != expected_approval_id:
        return False, "APPROVAL_ID_NOT_DERIVED_FROM_DMAE"

    return True, None


def verify_derived_approval_binding(
    approval: dict, envelope: dict, locator,
) -> "tuple[bool, Optional[str]]":
    """Vérification de LIAISON canonique (sans gel de fraîcheur/projection/
    révocation — ceux-ci sont assurés par les gates PRÉ-MUTATION qui dominent
    l'ordre). Recharge l'artefact DMAE CANONIQUE depuis le magasin désigné par
    le `locator` et exige une liaison EXACTE DMAE ↔ approbation. Utilisée par
    `_validate_approval` pour TOUT consommateur d'une approbation
    `HUMAN_MISSION_AUTHORITY_DERIVED` (y compris POST / rollback)."""
    ok_c, why_c = _context_shape_ok(locator)
    if not ok_c:
        return False, why_c
    if not isinstance(approval, dict):
        return False, "APPROVAL_MISSING"
    if approval.get("approved_by") != APPROVED_BY_DERIVED:
        return False, "APPROVAL_NOT_DERIVED"
    if approval.get("approval_kind") != APPROVAL_KIND_DERIVED:
        return False, "DERIVED_APPROVAL_KIND_INVALID"

    dmae_id_ap = approval.get("derived_mission_approval_evidence_id")
    if not (isinstance(dmae_id_ap, str) and dmae_id_ap.startswith("dmae-")):
        return False, "DERIVED_APPROVAL_EVIDENCE_ID_MISSING"
    if dmae_id_ap != locator["derived_mission_approval_evidence_id"]:
        return False, "DERIVED_APPROVAL_EVIDENCE_ID_NOT_IN_LOCATOR"

    beid = locator["batch_execution_id"]
    child = locator["child_execution_id"]
    if approval.get("batch_execution_id") != beid:
        return False, "LOCATOR_BATCH_EXECUTION_ID_MISMATCH_APPROVAL"
    if isinstance(envelope, dict) and envelope.get("batch_execution_id") not in (None, beid):
        return False, "LOCATOR_BATCH_EXECUTION_ID_MISMATCH_ENVELOPE"

    dmae = load_derived_mission_approval_evidence(
        locator["mission_id"], dmae_id_ap, locator["mission_store_dir"])
    ok_s, why_s = verify_derived_mission_approval_evidence(dmae)
    if not ok_s:
        return False, f"DMAE_STRUCTURAL:{why_s}"

    eah = dmae.get("execution_authority_hash")
    if dmae.get("derived_mission_approval_evidence_id") != dmae_id_ap:
        return False, "DMAE_ID_MISMATCH"
    if dmae.get("batch_execution_id") != beid or dmae.get("child_execution_id") != child:
        return False, "DMAE_ENVELOPE_BINDING_MISMATCH"
    if dmae.get("mission_id") != locator["mission_id"]:
        return False, "DMAE_MISSION_ID_MISMATCH_LOCATOR"
    if dmae.get("authority_mode") != AUTHORITY_MODE_STAGE4:
        return False, "DMAE_AUTHORITY_MODE_NOT_STAGE4"
    if approval.get("execution_authority_hash") != eah:
        return False, "APPROVAL_EAH_MISMATCH_DMAE"
    if isinstance(envelope, dict) and envelope.get("execution_authority_hash") not in (None, eah):
        return False, "ENVELOPE_EAH_MISMATCH_DMAE"
    if approval.get("human_authorization_reference") != dmae.get("human_authorization_reference"):
        return False, "APPROVAL_HUMAN_ROOT_MISMATCH_DMAE"

    import hashlib as _hl
    expected_approval_id = "appr-" + _hl.sha256(
        f"{beid}:{child}:{eah}:{dmae_id_ap}".encode("utf-8")).hexdigest()[:32]
    if approval.get("approval_id") != expected_approval_id:
        return False, "APPROVAL_ID_NOT_DERIVED_FROM_DMAE"
    return True, None

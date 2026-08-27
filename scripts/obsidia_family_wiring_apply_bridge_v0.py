"""
obsidia_family_wiring_apply_bridge_v0.py
=======================================
CONTENT_BOUND_GOVERNED_PREFLIGHT_C1_V0 — pont READ_ONLY / NON_SOVEREIGN
transformant le CONTENU EXACT d'une proposition Obsidure validée en une
entrée d'exécution canonique (ChildExecutionRecord-shaped).

Rôle strict :
  1. charge + valide la proposition via le validateur canonique
     scripts/obsidure_bounded_apply.py::load_and_validate_proposal
  2. sélectionne UN patch (règle déterministe : exactement un patch
     porteur d'un sandbox_path non vide ; sinon fail-closed)
  3. confine et lit les octets EXACTS du fichier sandbox courant
  4. calcule source_content_sha256 = sha256(octets).hexdigest() (64 hex)
     — c'est l'IDENTITÉ DE CONTENU pertinente pour l'autorité ;
     proposal_hash n'est JAMAIS traité comme autorité de contenu
  5. dérive target_path / operation_type / target_pre_sha256
  6. préserve (si fourni) la provenance FamilyRemediationCandidate

Le pont N'EXÉCUTE RIEN : aucune mutation de cible, aucun KX108, aucune
HumanApproval, aucun apply. write_capability = false.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Optional

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))
_REPO_ROOT = _SCRIPTS_DIR.parent

import obsidure_bounded_apply as _OBA  # load_and_validate_proposal — jamais modifié ici

AUTHORITY = "NON_SOVEREIGN"
OPERATION_TYPE = "UPDATE_TARGET_FROM_SOURCE"
SOURCE_KIND = "FILESYSTEM_FILE"

STATUS_READY = "BRIDGE_CHILD_READY"
STATUS_HOLD = "BRIDGE_HOLD"

_APPLICABLE_PATCH_ACTIONS = frozenset({"CREATE", "REPLACE", "UPDATE", "UPDATE_TARGET_FROM_SOURCE"})


def _hold(reason: str, **extra) -> dict:
    return {"status": STATUS_HOLD, "reason": reason, "child": None,
            "authority": AUTHORITY, "write_capability": False, **extra}


def _full_sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _deterministic_id(prefix: str, *parts: str) -> str:
    digest = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()
    return f"{prefix}-{digest[:24]}"


def _extract_family_provenance(family_candidate: Optional[dict]) -> dict:
    if not isinstance(family_candidate, dict):
        return {"operation_type": OPERATION_TYPE}
    prov = family_candidate.get("finding_provenance") or {}
    out = {"operation_type": OPERATION_TYPE}
    for k in ("family_id", "source_blocker_id", "candidate_id"):
        v = family_candidate.get(k)
        if v is not None:
            out[k] = v
    fw_sha = prov.get("family_wiring_state_sha256")
    if fw_sha is not None:
        out["family_wiring_state_sha256"] = fw_sha
    return out


def build_child_execution_from_obsidure_proposal(
    proposal_id: str,
    session_id: str,
    base_sha: str,
    worktree: str,
    approved_scope: "list[str]",
    family_candidate: Optional[dict] = None,
    proposals_dir: "Optional[Path]" = None,
    repo_root: "Optional[Path]" = None,
) -> dict:
    """
    Retourne :
      {status: BRIDGE_CHILD_READY | BRIDGE_HOLD, reason, child: {...} | None,
       proposal_id, proposal_hash (informatif — PAS autorité de contenu),
       source_content_sha256, bridge_report, authority, write_capability=false}

    READ_ONLY vis-à-vis de la cible. Aucune écriture. Aucune exécution.
    """
    root = Path(repo_root or _REPO_ROOT).resolve()

    # 1-2. Validation canonique de la proposition (jamais un second validateur).
    _orig_pdir = _OBA.PROPOSALS_DIR
    if proposals_dir is not None:
        _OBA.PROPOSALS_DIR = Path(proposals_dir)
    try:
        try:
            session = _OBA.load_and_validate_proposal(
                proposal_id=proposal_id, session_id=session_id,
                base_sha=base_sha, worktree=worktree, approved_scope=list(approved_scope),
            )
        except ValueError as exc:
            return _hold(f"PROPOSAL_INVALID:{exc}")

        proposal_json_path = _OBA.PROPOSALS_DIR / proposal_id / "proposal.json"
        try:
            data = json.loads(proposal_json_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            return _hold(f"PROPOSAL_UNREADABLE:{exc}")
    finally:
        _OBA.PROPOSALS_DIR = _orig_pdir

    # 3. Sélection déterministe d'UN patch (exactement un sandbox_path non vide).
    patches = data.get("patches") or []
    applicable = [
        p for p in patches
        if isinstance(p, dict) and str(p.get("sandbox_path") or "").strip()
        and (p.get("action") is None or str(p.get("action")).upper() in _APPLICABLE_PATCH_ACTIONS)
    ]
    if len(applicable) == 0:
        return _hold("NO_APPLICABLE_PATCH")
    if len(applicable) > 1:
        return _hold("MULTI_PATCH_AMBIGUITY", patch_count=len(applicable))
    patch = applicable[0]

    target_rel = str(patch.get("path") or "").strip()
    if not target_rel:
        return _hold("PATCH_TARGET_PATH_MISSING")

    # 4. Confinement du chemin sandbox — jamais une simple concaténation.
    raw_sandbox = str(patch["sandbox_path"]).strip()
    sp = Path(raw_sandbox)
    sp = sp if sp.is_absolute() else (root / raw_sandbox)
    try:
        resolved = sp.resolve()
    except OSError as exc:
        return _hold(f"SOURCE_PATH_UNRESOLVABLE:{exc}")
    try:
        resolved.relative_to(root)
    except ValueError:
        return _hold("SOURCE_PATH_ESCAPE", resolved=str(resolved))
    if os.path.islink(str(sp)) and not str(resolved).startswith(str(root) + os.sep):
        return _hold("SOURCE_SYMLINK_ESCAPE", resolved=str(resolved))
    if not resolved.exists():
        return _hold("SOURCE_FILE_MISSING", resolved=str(resolved))
    if not resolved.is_file():
        return _hold("SOURCE_NOT_REGULAR_FILE", resolved=str(resolved))

    # 5. Octets EXACTS + SHA256 COMPLET (autorité de contenu).
    try:
        src_bytes = resolved.read_bytes()
    except OSError as exc:
        return _hold(f"SOURCE_UNREADABLE:{exc}")
    source_content_sha256 = _full_sha256_bytes(src_bytes)          # 64 hex
    source_hash16 = source_content_sha256[:16]                      # champ compat
    source_path_rel = resolved.relative_to(root).as_posix()

    # 6. Précondition de cible observée MAINTENANT (lecture seule).
    target_abs = (root / target_rel)
    if target_abs.exists() and target_abs.is_file():
        try:
            target_pre_sha256 = _full_sha256_bytes(target_abs.read_bytes())
        except OSError as exc:
            return _hold(f"TARGET_UNREADABLE:{exc}")
    elif target_abs.exists():
        return _hold("TARGET_NOT_REGULAR_FILE")
    else:
        target_pre_sha256 = None  # CREATE

    provenance_refs = _extract_family_provenance(family_candidate)

    cand_id = _deterministic_id("cand", proposal_id, target_rel, source_content_sha256)
    child_id = _deterministic_id("child", proposal_id, target_rel, source_content_sha256)

    child = {
        "candidate_entry_id": cand_id,
        "child_execution_id": child_id,
        "source_kind": SOURCE_KIND,
        "source_path": source_path_rel,
        "source_hash": source_hash16,
        "source_content_sha256": source_content_sha256,          # AUTORITÉ
        "source_repository_identity": str(root),
        "source_git_commit_sha": "",
        "source_git_blob_sha": "",
        "source_git_historical_path": "",
        "target_path": target_rel,
        "target_pre_hash": (target_pre_sha256[:16] if target_pre_sha256 else None),
        "target_pre_sha256": target_pre_sha256,
        "operation_type": OPERATION_TYPE,
        "operation_reason": data.get("objective") or f"family wiring remediation content: {target_rel}",
        "execution_status": "PLANNED",
        "provenance_refs": provenance_refs,
    }

    return {
        "status": STATUS_READY,
        "reason": None,
        "child": child,
        "proposal_id": proposal_id,
        "proposal_hash": session.proposal_hash,   # INFORMATIF — jamais autorité de contenu
        "source_content_sha256": source_content_sha256,
        "bridge_report": {
            "target_path": target_rel,
            "operation_type": OPERATION_TYPE,
            "source_kind": SOURCE_KIND,
            "source_path": source_path_rel,
            "source_bytes": len(src_bytes),
            "target_pre_state": ("EXISTS" if target_pre_sha256 else "ABSENT"),
            "family_provenance_keys": sorted(k for k in provenance_refs if k != "operation_type"),
        },
        "authority": AUTHORITY,
        "write_capability": False,
    }

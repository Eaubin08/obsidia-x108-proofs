"""
obsidia_branching_ledger.py
===========================
BRANCHING_LEDGER_V0 — registre append-only de provenance.

Relie : receipts → proposals → KX108 → lifecycle → commits.
Stockage : %LOCALAPPDATA%\\Obsidia\\branching_ledger\\
Schema : V0

AUTORITE :
  CAN_RECORD = TRUE    CAN_INDEX = TRUE
  CAN_LINK   = TRUE    CAN_PROJECT = TRUE
  CAN_DECIDE = FALSE   CAN_APPLY  = FALSE
  CAN_COMMIT = FALSE   CAN_PUSH   = FALSE

decision_authority = KX108_ONLY
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import datetime
from pathlib import Path
from typing import Optional

# ─── Constantes ──────────────────────────────────────────────────────────────

SCHEMA_VERSION = "V0"
DECISION_AUTHORITY = "KX108_ONLY"
LEDGER_DIR = Path(os.environ.get("LOCALAPPDATA", "")) / "Obsidia" / "branching_ledger"

# Kinds de source Ledger — additif, la sémantique filesystem existante ne
# change pas. Une entrée sans "source_kind" (legacy) est interprétée comme
# FILESYSTEM_FILE partout en aval.
SOURCE_KIND_FILESYSTEM = "FILESYSTEM_FILE"
SOURCE_KIND_GIT_BLOB = "GIT_BLOB"

PROTECTED_PATHS = frozenset([
    "proofs/",
    "formal/",
    "merkle_seal.json",
    "runtime_terrain_bank_trading_gps/server.kernel.sealed.cjs",
])

# ─── Helpers internes ────────────────────────────────────────────────────────

def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _sha16(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _content_hash(path: Path) -> Optional[str]:
    if not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def ledger_entry_id(session_id: str, source_hash: str) -> str:
    """ID déterministe : sha256(session_id:source_hash)[:16]."""
    return _sha16(f"{session_id}:{source_hash}")


_REPO_ROOT = Path(__file__).resolve().parent.parent


def _normalize_source_path(path: Path) -> str:
    """
    Identité canonique, INDÉPENDANTE du cwd du process appelant :
    chemin relatif à _REPO_ROOT si le fichier est dans le repo, sinon
    chemin absolu résolu (stable, jamais relatif au cwd courant).
    """
    resolved = path.resolve()
    try:
        return resolved.relative_to(_REPO_ROOT).as_posix()
    except ValueError:
        return resolved.as_posix()


def _protected_absolute_paths() -> "list[Path]":
    """Chemins protégés résolus une fois, ancrés à _REPO_ROOT — indépendants du cwd."""
    return [(_REPO_ROOT / prefix.rstrip("/")).resolve() for prefix in PROTECTED_PATHS]


def _is_protected_resolved(resolved: Path) -> bool:
    """
    Vérification structurelle (Path.relative_to), pas de comparaison de
    préfixe de chaîne : indépendante du cwd, insensible aux traversées
    ('..'), et ne confond pas un chemin similaire (ex. proofs_backup/)
    avec un chemin réellement protégé (proofs/).
    """
    for prot in _protected_absolute_paths():
        try:
            resolved.relative_to(prot)
            return True
        except ValueError:
            continue
    return False


def _is_protected(path: str) -> bool:
    """Variante chaîne (préfixe normalisé) — conservée pour compat/lecture rapide."""
    for prefix in PROTECTED_PATHS:
        if path.startswith(prefix) or path == prefix.rstrip("/"):
            return True
    return False


def _ensure_dir(ledger_dir: Path) -> None:
    ledger_dir.mkdir(parents=True, exist_ok=True)


def _entries_path(ledger_dir: Path) -> Path:
    return ledger_dir / "entries.jsonl"


def _events_path(ledger_dir: Path) -> Path:
    return ledger_dir / "events.jsonl"


def _load_jsonl(path: Path) -> list:
    if not path.exists():
        return []
    result = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            result.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return result


def _append_jsonl(path: Path, obj: dict) -> None:
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(obj, ensure_ascii=False) + "\n")


# ─── API stockage ────────────────────────────────────────────────────────────

def _load_entries(ledger_dir: "Path | None" = None) -> list:
    d = ledger_dir or LEDGER_DIR
    return _load_jsonl(_entries_path(d))


def _load_events(ledger_dir: "Path | None" = None) -> list:
    d = ledger_dir or LEDGER_DIR
    return _load_jsonl(_events_path(d))


def _append_entry(entry: dict, ledger_dir: "Path | None" = None) -> None:
    d = ledger_dir or LEDGER_DIR
    _ensure_dir(d)
    _append_jsonl(_entries_path(d), entry)


def _append_event(event: dict, ledger_dir: "Path | None" = None) -> None:
    d = ledger_dir or LEDGER_DIR
    _ensure_dir(d)
    _append_jsonl(_events_path(d), event)


# ─── Déduplication ──────────────────────────────────────────────────────────

def _effective_identity_path(entry: dict) -> str:
    """
    Identité effective d'une entrée pour la dédup :
    target_path si explicitement connu, sinon source_path (pre-build).
    Utilisée de façon cohérente à l'écriture (nouvelle entrée) et à la
    lecture (comparaison aux entrées existantes) — ne modifie PAS la
    sémantique de target_path (destination) vs source_path (provenance).
    """
    return entry.get("target_path") or entry.get("source_path") or ""


def classify_dedup(entries: list, primary_path: str, source_hash: "str | None") -> str:
    """
    SAME_PATH_SAME_CONTENT  — chemin et hash identiques, preuve disponible
    SAME_PATH_NEW_CONTENT   — même chemin, deux hashes présents et différents
    MOVED_SAME_CONTENT      — hash identique, chemin différent, preuve disponible
    DISTINCT_CONTENT        — contenu réellement comparable et distinct selon preuves disponibles
    DEDUP_UNKNOWN           — preuve de contenu insuffisante (hash absent, vide ou invalide)

    primary_path doit être l'identité effective (_effective_identity_path)
    de la nouvelle entrée — comparée à l'identité effective de chaque
    entrée existante, jamais à target_path brut seul (qui peut être None
    pour une source DISCOVERED sans target déclaré).
    """
    if not source_hash or source_hash == "unknown":
        return "DEDUP_UNKNOWN"
    same_path = [e for e in entries if _effective_identity_path(e) == primary_path]
    if same_path:
        if any(e.get("source_hash") == source_hash for e in same_path):
            return "SAME_PATH_SAME_CONTENT"
        return "SAME_PATH_NEW_CONTENT"
    if any(e.get("source_hash") == source_hash for e in entries):
        return "MOVED_SAME_CONTENT"
    return "DISTINCT_CONTENT"


# ─── Ingestion ───────────────────────────────────────────────────────────────

def ingest_from_receipt(
    session_id: str,
    state_dir: "Path | None" = None,
    ledger_dir: "Path | None" = None,
    proposals_dir: "Path | None" = None,
) -> dict:
    """
    Crée une entrée ledger depuis les preuves d'une session.
    Accepte receipt.json (build) ou apply_receipt.json (Obsidure).
    Ne copie PAS le contenu — références/hashes uniquement.
    """
    import sys, pathlib
    _scripts = str(pathlib.Path(__file__).resolve().parent)
    if _scripts not in sys.path:
        sys.path.insert(0, _scripts)
    from obsidia_build import (
        _load_receipt, _load_apply_receipt, _load_lifecycle_events,
        _derive_lifecycle_status, _git_worktree_state,
        OBSIDIA_BUILD_STATE_DIR,
    )
    sdir = Path(state_dir) if state_dir else OBSIDIA_BUILD_STATE_DIR
    receipt = _load_receipt(session_id, sdir)
    apply_receipt = _load_apply_receipt(session_id, sdir)
    lifecycle_events = _load_lifecycle_events(session_id, sdir)

    if receipt is None and apply_receipt is None:
        return {"error": f"No receipt for session {session_id}", "session_id": session_id}

    src = receipt or apply_receipt

    # Git state (live, fail-closed)
    wt_path_str: str = src.get("worktree", "")
    wt_state: "dict | None" = None
    wt_p = Path(wt_path_str) if wt_path_str else None
    if wt_p and wt_p.is_absolute() and wt_p.exists():
        wt_state = _git_worktree_state(wt_p)
    lifecycle_status = _derive_lifecycle_status(receipt, apply_receipt, lifecycle_events, wt_state)

    # Source file path — reference only
    session_path = sdir / session_id
    receipt_path = session_path / "receipt.json"
    apply_path = session_path / "apply_receipt.json"
    events_path = session_path / "lifecycle_events.jsonl"

    source_file = receipt_path if receipt_path.exists() else apply_path
    source_hash = _content_hash(source_file)  # None si fichier illisible ou absent

    # Primary target path (first approved_scope entry)
    approved_scope: list = src.get("approved_scope") or []
    target_path: str = approved_scope[0] if approved_scope else "UNKNOWN"

    # Dedup
    existing = _load_entries(ledger_dir)
    dedup = classify_dedup(existing, target_path, source_hash)

    # Entry ID (deterministic) — si hash absent, l'ID reste déterministe par session
    # mais ne prouve PAS l'identité de contenu (DEDUP_UNKNOWN le signale)
    entry_id = ledger_entry_id(session_id, source_hash or "CONTENT_HASH_UNKNOWN")

    # Already indexed with same ID?
    if any(e.get("ledger_entry_id") == entry_id for e in existing):
        return {"status": "ALREADY_INDEXED", "ledger_entry_id": entry_id}

    # Identical path+hash already present?
    if dedup == "SAME_PATH_SAME_CONTENT":
        return {"status": "SAME_PATH_SAME_CONTENT", "ledger_entry_id": entry_id}

    # KX108 — read from artifacts only, never fabricated
    kx108_decision = (
        receipt.get("kx108_decision") if receipt else None
    ) or (
        apply_receipt.get("kx108_decision") if apply_receipt else None
    )

    # Proposal linkage
    proposal_id = (
        (apply_receipt.get("proposal_id") if apply_receipt else None)
        or (receipt.get("proposal_id") if receipt else None)
    )
    proposal_hash = (
        (apply_receipt.get("proposal_hash") if apply_receipt else None)
        or (receipt.get("proposal_hash") if receipt else None)
    )

    # Evidence refs — small summary only, not full content
    test_evidence_ref: "dict | None" = None
    gate_evidence_ref: "dict | None" = None
    if apply_receipt:
        te = apply_receipt.get("test_evidence")
        if isinstance(te, dict):
            test_evidence_ref = {
                "command": te.get("command"),
                "status": te.get("status"),
                "exit_code": te.get("exit_code"),
            }
        ge = apply_receipt.get("gate_evidence")
        if isinstance(ge, dict):
            gate_evidence_ref = {
                "command": ge.get("command"),
                "status": ge.get("status"),
                "exit_code": ge.get("exit_code"),
            }

    # Proposal path ref (if _PATCH_PROPOSALS exists)
    p_dir = proposals_dir or Path("_PATCH_PROPOSALS")
    proposal_path: "str | None" = None
    if proposal_id:
        pp = p_dir / proposal_id / "proposal.json"
        if pp.exists():
            proposal_path = str(pp)

    # Unknowns
    unknowns: list = []
    if source_hash is None:
        unknowns.append("source_hash_missing")
    if not kx108_decision:
        unknowns.append("kx108_decision_missing")
    if not proposal_id:
        unknowns.append("proposal_id_missing")
    if lifecycle_status in ("READY_FOR_COMMIT_REVIEW", "APPROVED"):
        unknowns.append("commit_sha_pending")
    if not test_evidence_ref and not receipt:
        unknowns.append("test_evidence_missing")

    # Previous entry for SAME_PATH_NEW_CONTENT versioning
    prev_entry_id: "str | None" = None
    if dedup == "SAME_PATH_NEW_CONTENT":
        same_path = [e for e in existing if _effective_identity_path(e) == target_path]
        if same_path:
            prev_entry_id = same_path[-1]["ledger_entry_id"]

    entry: dict = {
        "ledger_entry_id": entry_id,
        "entry_schema_version": SCHEMA_VERSION,
        "timestamp": _now(),

        "source_type": "receipt" if receipt else "apply_receipt",
        "source_path": str(source_file),
        "source_hash": source_hash,

        "target_path": target_path,
        "target_domain": src.get("domain"),

        "session_id": session_id,
        "branch": src.get("branch"),
        "worktree": src.get("worktree"),
        "base_sha": src.get("base_sha"),

        "objective": src.get("objective"),

        "proposal_id": proposal_id,
        "proposal_hash": proposal_hash,

        "approved_scope": approved_scope,
        "proposal_files": src.get("proposal_files") or [],
        "actual_modified_files": (
            apply_receipt.get("actual_modified_files") if apply_receipt else None
        ) or src.get("actual_modified_files") or [],

        "test_evidence_ref": test_evidence_ref,
        "gate_evidence_ref": gate_evidence_ref,

        "kx108_decision": kx108_decision,
        "next_human_action": src.get("next_human_action"),

        "lifecycle_status": lifecycle_status,
        "commit_sha": src.get("commit_sha"),

        "provenance_refs": {
            "receipt_path": str(receipt_path) if receipt_path.exists() else None,
            "apply_receipt_path": str(apply_path) if apply_path.exists() else None,
            "lifecycle_events_path": str(events_path) if events_path.exists() else None,
            "proposal_path": proposal_path,
        },

        "dedup_classification": dedup,
        "prev_entry_id": prev_entry_id,

        "status": lifecycle_status,
        "unknowns": unknowns,
        "risk_flags": [],

        "decision_authority": DECISION_AUTHORITY,
    }

    _append_entry(entry, ledger_dir)
    _append_event({
        "event_type": "INDEXED",
        "ledger_entry_id": entry_id,
        "session_id": session_id,
        "timestamp": _now(),
        "dedup": dedup,
        "lifecycle_status": lifecycle_status,
    }, ledger_dir)

    return {"status": "INDEXED", "ledger_entry_id": entry_id}


def ingest_from_proposal(
    proposal_id: str,
    proposals_dir: "Path | None" = None,
    state_dir: "Path | None" = None,
    ledger_dir: "Path | None" = None,
) -> dict:
    """
    Crée/lie une entrée depuis un proposal.json.
    Si la session associée est déjà indexée, ajoute seulement un événement PROPOSAL_LINKED.
    """
    p_dir = proposals_dir or Path("_PATCH_PROPOSALS")
    proposal_path = p_dir / proposal_id / "proposal.json"
    if not proposal_path.exists():
        return {"error": f"Proposal not found: {proposal_id}"}

    proposal = json.loads(proposal_path.read_text(encoding="utf-8"))
    session_id: "str | None" = proposal.get("session_id")
    if not session_id:
        return {"error": f"Proposal {proposal_id} has no session_id"}

    # Ingest from session first if available
    result = ingest_from_receipt(session_id, state_dir, ledger_dir, proposals_dir)

    entry_id = result.get("ledger_entry_id")
    if entry_id:
        _append_event({
            "event_type": "PROPOSAL_LINKED",
            "ledger_entry_id": entry_id,
            "proposal_id": proposal_id,
            "proposal_hash": proposal.get("proposal_hash"),
            "proposal_status": proposal.get("status"),
            "timestamp": _now(),
        }, ledger_dir)

    return {**result, "proposal_linked": proposal_id}


def link_commit(
    entry_id: str,
    commit_sha: str,
    ledger_dir: "Path | None" = None,
) -> dict:
    """Enregistre qu'une entrée a été commitée. Append-only — ne modifie PAS l'entrée."""
    _append_event({
        "event_type": "COMMITTED",
        "ledger_entry_id": entry_id,
        "commit_sha": commit_sha,
        "timestamp": _now(),
    }, ledger_dir)
    return {"status": "COMMITTED_LINKED", "ledger_entry_id": entry_id, "commit_sha": commit_sha}


def link_dependency(
    source_entry_id: str,
    dependency_entry_id: str,
    relation_type: str = "DEPENDENCY_CONFIRMED",
    evidence_type: "str | None" = None,
    evidence_ref: "str | None" = None,
    ledger_dir: "Path | None" = None,
) -> dict:
    """
    Enregistre une relation de dépendance entre deux entrées Ledger déjà
    existantes — événement append-only (DEPENDENCY_LINKED), ne modifie
    JAMAIS les lignes d'entrées existantes.

    Fail-closed :
    - les deux entry_id doivent déjà exister dans le Ledger, sinon aucune
      preuve n'est fabriquée et rien n'est enregistré ;
    - V0 n'accepte QUE relation_type="DEPENDENCY_CONFIRMED" — le Selector
      ne doit jamais interpréter silencieusement un lien déclaré
      DEPENDENCY_PROBABLE/DEPENDENCY_UNKNOWN comme confirmé. Tant qu'un
      projecteur fidèle au relation_type déclaré n'existe pas côté
      Selector, on refuse d'enregistrer autre chose que du confirmé
      plutôt que de risquer une confirmation fabriquée.
    """
    if relation_type != "DEPENDENCY_CONFIRMED":
        return {
            "error": (
                "relation_type non supporté en V0 : "
                f"{relation_type} (seul DEPENDENCY_CONFIRMED est accepté)"
            )
        }
    entries = _load_entries(ledger_dir)
    known_ids = {e.get("ledger_entry_id") for e in entries}
    if source_entry_id not in known_ids:
        return {"error": f"source_ledger_entry_id inconnu : {source_entry_id}"}
    if dependency_entry_id not in known_ids:
        return {"error": f"dependency_ledger_entry_id inconnu : {dependency_entry_id}"}
    _append_event({
        "event_type": "DEPENDENCY_LINKED",
        "source_ledger_entry_id": source_entry_id,
        "dependency_ledger_entry_id": dependency_entry_id,
        "relation_type": relation_type,
        "evidence_type": evidence_type,
        "evidence_ref": evidence_ref,
        "timestamp": _now(),
    }, ledger_dir)
    return {
        "status": "DEPENDENCY_LINKED",
        "source_ledger_entry_id": source_entry_id,
        "dependency_ledger_entry_id": dependency_entry_id,
    }


def register_source(
    source_path: str,
    source_type: str = "REAL_SOURCE",
    target_domain: "str | None" = None,
    target_path: "str | None" = None,
    reason: "str | None" = None,
    dependency_refs: "list | None" = None,
    provenance_refs: "dict | None" = None,
    ledger_dir: "Path | None" = None,
) -> dict:
    """
    Enregistre une source réelle DÉCOUVERTE, AVANT toute session de build,
    proposal, décision KX108 ou commit.

    lifecycle_status = DISCOVERED
    proposal_id = kx108_decision = commit_sha = None (NOT YET APPLICABLE,
    pas une preuve manquante).

    Lecture seule sur la source : hash + métadonnées uniquement.
    Append-only. Idempotent (même chemin normalisé + même hash → pas de
    doublon).
    """
    p = Path(source_path)
    if not p.exists() or not p.is_file():
        return {"error": f"Source introuvable ou non-fichier : {source_path}"}

    resolved = p.resolve()

    # Vérification protégée structurelle AVANT tout hash/normalisation
    # d'affichage — indépendante du cwd, résiste aux traversées ('..'),
    # ne confond jamais un chemin similaire (proofs_backup/) avec un
    # chemin réellement protégé (proofs/).
    if _is_protected_resolved(resolved):
        return {
            "status": "REJECTED_PROTECTED",
            "reason": "protected_path",
            "source_path": _normalize_source_path(p),
        }

    normalized_path = _normalize_source_path(p)

    source_hash = _content_hash(p)  # jamais fabriqué — lecture réelle du fichier
    if source_hash is None:
        return {"error": f"Impossible de hasher la source : {source_path}"}

    identity_path = target_path or normalized_path

    existing = _load_entries(ledger_dir)
    dedup = classify_dedup(existing, identity_path, source_hash)

    entry_id = ledger_entry_id(f"DISCOVERED:{normalized_path}", source_hash)

    if any(e.get("ledger_entry_id") == entry_id for e in existing):
        return {"status": "ALREADY_REGISTERED", "ledger_entry_id": entry_id}

    if dedup == "SAME_PATH_SAME_CONTENT":
        return {"status": "SAME_PATH_SAME_CONTENT", "ledger_entry_id": entry_id}

    prev_entry_id: "str | None" = None
    if dedup == "SAME_PATH_NEW_CONTENT":
        same_path = [e for e in existing if _effective_identity_path(e) == identity_path]
        if same_path:
            prev_entry_id = same_path[-1]["ledger_entry_id"]

    entry: dict = {
        "ledger_entry_id": entry_id,
        "entry_schema_version": SCHEMA_VERSION,
        "timestamp": _now(),

        "source_type": source_type,
        "source_path": normalized_path,
        "source_hash": source_hash,

        "target_path": target_path,
        "target_domain": target_domain,

        "session_id": None,
        "branch": None,
        "worktree": None,
        "base_sha": None,

        "objective": reason,

        "proposal_id": None,
        "proposal_hash": None,

        "approved_scope": [],
        "proposal_files": [],
        "actual_modified_files": [],

        "test_evidence_ref": None,
        "gate_evidence_ref": None,

        "kx108_decision": None,
        "next_human_action": "REVIEW_SOURCE_CANDIDATE",

        "lifecycle_status": "DISCOVERED",
        "commit_sha": None,

        "provenance_refs": provenance_refs or {},
        "dependency_refs": dependency_refs or [],

        "dedup_classification": dedup,
        "prev_entry_id": prev_entry_id,

        "status": "DISCOVERED",
        "unknowns": [],
        "risk_flags": [],

        "decision_authority": DECISION_AUTHORITY,
    }

    _append_entry(entry, ledger_dir)
    _append_event({
        "event_type": "DISCOVERED",
        "ledger_entry_id": entry_id,
        "source_path": normalized_path,
        "timestamp": _now(),
        "dedup": dedup,
    }, ledger_dir)

    return {"status": "DISCOVERED", "ledger_entry_id": entry_id}


# ─── Source Git immuable (GIT_BLOB) ─────────────────────────────────────────
#
# Un blob Git est un matériau source réel et immuable. On ne le matérialise
# JAMAIS dans le dépôt pour satisfaire une API pensée pour des fichiers
# filesystem — on lit ses octets via la plomberie Git en lecture seule
# (rev-parse / ls-tree / cat-file), sans jamais checkout/switch/restore.
#
# Autorité immuable = (commit_sha exact, blob_sha, content_sha256).
# Une branche/ref (ex. "main") n'est JAMAIS l'autorité — elle est résolue en
# commit exact UNE FOIS, à l'enregistrement, puis conservée seulement comme
# indice de provenance (source_git_ref_hint). Le déplacement ultérieur de la
# branche ne peut jamais muter une source déjà enregistrée.

class GitSourceError(Exception):
    pass


def _run_git(repo_root: Path, args: "list[str]") -> "tuple[int, bytes, str]":
    result = subprocess.run(
        ["git", *args],
        cwd=str(repo_root),
        capture_output=True,
    )
    return result.returncode, result.stdout, result.stderr.decode("utf-8", errors="replace")


def _git_resolve_commit_sha(repo_root: Path, ref: str) -> Optional[str]:
    """Résout un ref (branche, tag, SHA partiel/complet) en SHA de commit exact. None si invalide."""
    code, out, _err = _run_git(repo_root, ["rev-parse", "--verify", f"{ref}^{{commit}}"])
    if code != 0:
        return None
    sha = out.decode("ascii", errors="replace").strip()
    return sha or None


def _git_blob_sha_at_commit(repo_root: Path, commit_sha: str, historical_path: str) -> Optional[str]:
    """SHA du blob à <commit_sha>:<historical_path>. None si absent ou si l'objet n'est pas un blob."""
    code, out, _err = _run_git(repo_root, ["ls-tree", commit_sha, "--", historical_path])
    if code != 0:
        return None
    line = out.decode("utf-8", errors="replace").strip()
    if not line:
        return None
    parts = line.split(None, 3)
    if len(parts) < 4:
        return None
    _mode, obj_type, obj_sha, _path_field = parts
    if obj_type != "blob":
        return None
    return obj_sha


def _git_read_blob_bytes(repo_root: Path, blob_sha: str) -> Optional[bytes]:
    """Octets bruts du blob. None si illisible. Ne fabrique jamais de contenu."""
    code, out, _err = _run_git(repo_root, ["cat-file", "-p", blob_sha])
    if code != 0:
        return None
    return out


def _validate_git_historical_path(
    historical_path: "str | None", repo_root: Path,
) -> "tuple[str | None, str | None]":
    """
    Valide historical_path SANS jamais toucher le disque (il n'a pas besoin
    d'exister dans l'arbre de travail courant — il décrit où le blob
    existait AU COMMIT). Retourne (chemin_canonique_posix, None) ou
    (None, raison_rejet).

    L'espace de noms de confinement (traversée hors dépôt) est vérifié
    contre repo_root — le MÊME dépôt que celui interrogé ensuite par
    rev-parse/ls-tree/cat-file. Jamais d'autorité scindée (valider contre
    un dépôt, lire le blob dans un autre). Le statut PROTÉGÉ reste, lui,
    toujours ancré au dépôt Obsidia canonique (_REPO_ROOT) — c'est une
    invariante globale de CE dépôt, indépendante du dépôt source lu.
    """
    if not historical_path or not str(historical_path).strip():
        return None, "GIT_SOURCE_EMPTY_PATH"
    raw = str(historical_path).strip()
    if "*" in raw or "?" in raw:
        return None, "GIT_SOURCE_WILDCARD_REJECTED"
    norm = raw.replace("\\", "/")
    if norm.startswith("/") or (len(norm) > 1 and norm[1] == ":"):
        return None, "GIT_SOURCE_ABSOLUTE_PATH_REJECTED"
    candidate = (repo_root / norm).resolve()
    try:
        rel = candidate.relative_to(repo_root.resolve())
    except ValueError:
        return None, "GIT_SOURCE_OUTSIDE_REPO_NAMESPACE"
    if _is_protected_resolved((_REPO_ROOT / rel).resolve()):
        return None, "GIT_SOURCE_PROTECTED_REJECTED"
    return rel.as_posix(), None


def _validate_git_target_path(target_path: "str | None") -> "tuple[str | None, str | None]":
    """
    Valide target_path : chemin repo-relatif canonique, toujours ancré au
    dépôt Obsidia canonique (_REPO_ROOT) — c'est là qu'une éventuelle
    écriture future se produirait, indépendamment du dépôt source d'où le
    blob Git est lu. N'exige PAS l'existence sur disque (la cible peut ne
    pas encore exister). None est valide (aucune cible connue à ce stade).
    Retourne (chemin_canonique_posix_ou_None, raison_rejet_ou_None).
    """
    if target_path is None:
        return None, None
    raw = str(target_path).strip()
    if not raw:
        return None, "GIT_TARGET_EMPTY_PATH"
    if "*" in raw or "?" in raw:
        return None, "GIT_TARGET_WILDCARD_REJECTED"
    norm = raw.replace("\\", "/")
    if norm.startswith("/") or (len(norm) > 1 and norm[1] == ":"):
        candidate = Path(raw).resolve()
    else:
        candidate = (_REPO_ROOT / norm).resolve()
    try:
        rel = candidate.relative_to(_REPO_ROOT)
    except ValueError:
        return None, "GIT_TARGET_OUTSIDE_REPO_NAMESPACE"
    if rel.as_posix() == ".":
        return None, "GIT_TARGET_REPO_ROOT_REJECTED"
    if _is_protected_resolved(candidate):
        return None, "GIT_TARGET_PROTECTED_REJECTED"
    return rel.as_posix(), None


def register_git_blob_source(
    commit_sha_or_ref: str,
    historical_path: str,
    target_path: "str | None" = None,
    target_domain: "str | None" = None,
    reason: "str | None" = None,
    provenance_refs: "dict | None" = None,
    dependency_refs: "list | None" = None,
    expected_blob_sha: "str | None" = None,
    expected_content_sha256: "str | None" = None,
    repo_root: "Path | None" = None,
    ledger_dir: "Path | None" = None,
) -> dict:
    """
    Enregistre une source Git RÉELLE et IMMUABLE (blob), AVANT toute session
    de build, proposal, décision KX108 ou commit.

    lifecycle_status = DISCOVERED. Ne checkout jamais, ne mute jamais le
    dépôt. Fail-closed sur commit inconnu, chemin absent au commit, objet
    non-blob, mismatch de hash attendu, ou cible protégée.

    Identité d'ENTRÉE = provenance immuable complète (dépôt, commit, blob,
    chemin historique, octets) + cible d'intégration (target_path, ou son
    absence) — toujours distincte de l'identité de CONTENU (source_hash).
    Deux provenances différentes, ou une même provenance vers deux cibles
    différentes, restent des entrées distinctes même si les octets sont
    identiques.
    """
    root = repo_root or _REPO_ROOT

    if not commit_sha_or_ref or not str(commit_sha_or_ref).strip():
        return {"status": "REJECTED", "reason": "GIT_SOURCE_EMPTY_COMMIT_REF"}

    canonical_path, reject_reason = _validate_git_historical_path(historical_path, root)
    if reject_reason:
        return {"status": "REJECTED", "reason": reject_reason, "historical_path": historical_path}

    commit_sha = _git_resolve_commit_sha(root, str(commit_sha_or_ref).strip())
    if not commit_sha:
        return {
            "status": "REJECTED",
            "reason": "GIT_SOURCE_UNKNOWN_COMMIT",
            "commit_ref": commit_sha_or_ref,
        }

    blob_sha = _git_blob_sha_at_commit(root, commit_sha, canonical_path)
    if not blob_sha:
        return {
            "status": "REJECTED",
            "reason": "GIT_SOURCE_PATH_NOT_FOUND_AT_COMMIT",
            "commit_sha": commit_sha,
            "historical_path": canonical_path,
        }

    if expected_blob_sha and expected_blob_sha != blob_sha:
        return {
            "status": "REJECTED",
            "reason": "GIT_SOURCE_BLOB_SHA_MISMATCH",
            "expected_blob_sha": expected_blob_sha,
            "actual_blob_sha": blob_sha,
        }

    blob_bytes = _git_read_blob_bytes(root, blob_sha)
    if blob_bytes is None:
        return {"status": "REJECTED", "reason": "GIT_SOURCE_BLOB_UNREADABLE", "blob_sha": blob_sha}

    content_sha256_full = hashlib.sha256(blob_bytes).hexdigest()
    if expected_content_sha256 and expected_content_sha256 != content_sha256_full:
        return {
            "status": "REJECTED",
            "reason": "GIT_SOURCE_CONTENT_SHA256_MISMATCH",
            "expected_content_sha256": expected_content_sha256,
            "actual_content_sha256": content_sha256_full,
        }

    source_hash = content_sha256_full[:16]  # sémantique Ledger existante préservée

    canonical_target, target_reject_reason = _validate_git_target_path(target_path)
    if target_reject_reason == "GIT_TARGET_PROTECTED_REJECTED":
        return {
            "status": "REJECTED_PROTECTED",
            "reason": "protected_target",
            "target_path": target_path,
        }
    if target_reject_reason:
        return {"status": "REJECTED", "reason": target_reject_reason, "target_path": target_path}

    identity_path = canonical_target or canonical_path

    existing = _load_entries(ledger_dir)
    dedup = classify_dedup(existing, identity_path, source_hash)

    # Identité d'entrée = provenance IMMUABLE complète + intention
    # d'intégration (cible). Même source (repo+commit+chemin+blob+octets)
    # vers deux cibles différentes DOIT rester deux entrées distinctes —
    # ce sont deux intentions d'intégration sémantiquement différentes.
    # target_path=None (aucune cible connue) reste distinct d'une cible
    # explicite ultérieure : jamais fusionné en place.
    identity_key = (
        f"DISCOVERED_GIT:{root.resolve()}:{commit_sha}:{canonical_path}:"
        f"{blob_sha}:{content_sha256_full}:{canonical_target or 'NO_TARGET'}"
    )
    entry_id = ledger_entry_id(identity_key, source_hash)

    if any(e.get("ledger_entry_id") == entry_id for e in existing):
        return {"status": "ALREADY_REGISTERED", "ledger_entry_id": entry_id}

    prev_entry_id: "str | None" = None
    if dedup == "SAME_PATH_NEW_CONTENT":
        same_path = [e for e in existing if _effective_identity_path(e) == identity_path]
        if same_path:
            prev_entry_id = same_path[-1]["ledger_entry_id"]

    entry: dict = {
        "ledger_entry_id": entry_id,
        "entry_schema_version": SCHEMA_VERSION,
        "timestamp": _now(),

        "source_kind": SOURCE_KIND_GIT_BLOB,
        "source_type": "GIT_BLOB_SOURCE",
        "source_path": canonical_path,
        "source_hash": source_hash,

        "source_git_commit_sha": commit_sha,
        "source_git_blob_sha": blob_sha,
        "source_git_historical_path": canonical_path,
        "source_git_ref_hint": str(commit_sha_or_ref).strip(),
        "source_repository_identity": str(root.resolve()),
        "source_content_sha256": content_sha256_full,

        "target_path": canonical_target,
        "target_domain": target_domain,

        "session_id": None,
        "branch": None,
        "worktree": None,
        "base_sha": None,

        "objective": reason,

        "proposal_id": None,
        "proposal_hash": None,

        "approved_scope": [],
        "proposal_files": [],
        "actual_modified_files": [],

        "test_evidence_ref": None,
        "gate_evidence_ref": None,

        "kx108_decision": None,
        "next_human_action": "REVIEW_SOURCE_CANDIDATE",

        "lifecycle_status": "DISCOVERED",
        "commit_sha": None,  # commit d'APPLICATION futur — distinct de source_git_commit_sha (provenance)

        "provenance_refs": provenance_refs or {},
        "dependency_refs": dependency_refs or [],

        "dedup_classification": dedup,
        "prev_entry_id": prev_entry_id,

        "status": "DISCOVERED",
        "unknowns": [],
        "risk_flags": [],

        "decision_authority": DECISION_AUTHORITY,
    }

    _append_entry(entry, ledger_dir)
    _append_event({
        "event_type": "DISCOVERED_GIT_BLOB",
        "ledger_entry_id": entry_id,
        "source_git_commit_sha": commit_sha,
        "source_git_blob_sha": blob_sha,
        "source_git_historical_path": canonical_path,
        "timestamp": _now(),
        "dedup": dedup,
    }, ledger_dir)

    return {
        "status": "DISCOVERED",
        "ledger_entry_id": entry_id,
        "source_git_commit_sha": commit_sha,
        "source_git_blob_sha": blob_sha,
        "source_content_sha256": content_sha256_full,
    }


# ─── Commandes lecture ───────────────────────────────────────────────────────

def cmd_ledger_list(ledger_dir: "Path | None" = None) -> int:
    d = ledger_dir or LEDGER_DIR
    entries = _load_entries(d)
    sep = "=" * 70
    print(f"\n{sep}")
    print("  OBSIDIA LEDGER -- LIST")
    print(f"  ledger_dir : {d}")
    print(f"{sep}\n")
    if not entries:
        print("  [EMPTY] Aucune entree dans le ledger.")
        return 0
    print(f"  {'ENTRY_ID':<18} {'SESSION':<28} {'DOMAIN':<12} {'KX108':<6} STATUS")
    print("  " + "-" * 80)
    for e in entries:
        print(
            f"  {e.get('ledger_entry_id','?'):<18}"
            f" {str(e.get('session_id','?')):<28}"
            f" {str(e.get('target_domain','?')):<12}"
            f" {str(e.get('kx108_decision','?')):<6}"
            f" {e.get('lifecycle_status','?')}"
        )
    print(f"\n  {len(entries)} entree(s) -- decision_authority = {DECISION_AUTHORITY}")
    return 0


def cmd_ledger_status(entry_id: str, ledger_dir: "Path | None" = None) -> int:
    entries = _load_entries(ledger_dir)
    entry = next((e for e in entries if e.get("ledger_entry_id") == entry_id), None)
    if entry is None:
        print(f"  [LEDGER_FAIL] Entree inconnue : {entry_id}")
        return 2
    sep = "=" * 70
    print(f"\n{sep}")
    print(f"  OBSIDIA LEDGER -- STATUS : {entry_id}")
    print(f"{sep}\n")
    for field in (
        "session_id", "target_path", "target_domain",
        "kx108_decision", "lifecycle_status", "commit_sha",
        "dedup_classification", "entry_schema_version",
    ):
        print(f"  {field:<30}: {entry.get(field)}")
    if entry.get("unknowns"):
        print(f"  unknowns                      : {entry['unknowns']}")
    if entry.get("risk_flags"):
        print(f"  risk_flags                    : {entry['risk_flags']}")
    return 0


def cmd_ledger_inspect(entry_id: str, ledger_dir: "Path | None" = None) -> int:
    entries = _load_entries(ledger_dir)
    entry = next((e for e in entries if e.get("ledger_entry_id") == entry_id), None)
    if entry is None:
        print(f"  [LEDGER_FAIL] Entree inconnue : {entry_id}")
        return 2
    sep = "=" * 70
    print(f"\n{sep}")
    print(f"  OBSIDIA LEDGER -- INSPECT : {entry_id}")
    print(f"{sep}\n")

    print("  [IDENTITY]")
    for f in ("ledger_entry_id", "entry_schema_version", "timestamp", "source_type", "source_hash"):
        print(f"  {f:<32}: {entry.get(f)}")

    print("\n  [SESSION]")
    for f in ("session_id", "branch", "base_sha", "objective"):
        v = str(entry.get(f, "")) [:80]
        print(f"  {f:<32}: {v}")

    print("\n  [PROVENANCE]")
    for f in ("target_path", "target_domain", "dedup_classification"):
        print(f"  {f:<32}: {entry.get(f)}")
    prov = entry.get("provenance_refs") or {}
    for k, v in prov.items():
        print(f"  provenance.{k:<22}: {v}")
    if entry.get("prev_entry_id"):
        print(f"  prev_entry_id                 : {entry['prev_entry_id']}")

    print("\n  [PROPOSAL]")
    for f in ("proposal_id", "proposal_hash"):
        print(f"  {f:<32}: {entry.get(f)}")

    print("\n  [EVIDENCE REFS]")
    te = entry.get("test_evidence_ref")
    ge = entry.get("gate_evidence_ref")
    print(f"  test_evidence_ref             : {te}")
    print(f"  gate_evidence_ref             : {ge}")

    print("\n  [KX108 / LIFECYCLE]")
    for f in ("kx108_decision", "next_human_action", "lifecycle_status", "commit_sha", "decision_authority"):
        print(f"  {f:<32}: {entry.get(f)}")

    if entry.get("unknowns"):
        print(f"\n  [UNKNOWNS] : {entry['unknowns']}")
    if entry.get("risk_flags"):
        print(f"  [RISK_FLAGS]: {entry['risk_flags']}")
    return 0


def cmd_ledger_history(entry_id: str, ledger_dir: "Path | None" = None) -> int:
    events = _load_events(ledger_dir)
    related = [ev for ev in events if ev.get("ledger_entry_id") == entry_id]
    sep = "=" * 70
    print(f"\n{sep}")
    print(f"  OBSIDIA LEDGER -- HISTORY : {entry_id}")
    print(f"{sep}\n")
    if not related:
        print("  [EMPTY] Aucun evenement pour cette entree.")
        return 0
    for ev in related:
        ts = ev.get("timestamp", "?")[:19]
        etype = ev.get("event_type", "?")
        extra = {k: v for k, v in ev.items()
                 if k not in ("event_type", "ledger_entry_id", "timestamp")}
        suffix = f" -- {extra}" if extra else ""
        print(f"  [{ts}] {etype}{suffix}")
    return 0


def cmd_ledger_find_path(path_pattern: str, ledger_dir: "Path | None" = None) -> int:
    entries = _load_entries(ledger_dir)
    found = [e for e in entries if path_pattern in str(e.get("target_path", ""))]
    print(f"\n  find --path {path_pattern!r} : {len(found)} resultat(s)")
    for e in found:
        print(
            f"  {e.get('ledger_entry_id')}  "
            f"{e.get('session_id')}  "
            f"{e.get('lifecycle_status')}"
        )
    return 0


def cmd_ledger_find_session(session_id: str, ledger_dir: "Path | None" = None) -> int:
    entries = _load_entries(ledger_dir)
    found = [e for e in entries if e.get("session_id") == session_id]
    print(f"\n  find --session {session_id!r} : {len(found)} resultat(s)")
    for e in found:
        print(
            f"  {e.get('ledger_entry_id')}  "
            f"{e.get('target_path')}  "
            f"{e.get('lifecycle_status')}"
        )
    return 0

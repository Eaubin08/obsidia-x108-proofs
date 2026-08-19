"""
obsidia_batch_selector.py
=========================
BATCH_SELECTOR_V0 — sélecteur borné et auditable de lots de changements.

Flux :
  Branching Ledger
  → découverte de candidats
  → filtrage / éligibilité / dédup
  → dépendances / conflits
  → proposition de lot (BatchProposal)
  → CLI list/status/inspect

AUTORITÉ :
  CAN_DISCOVER        = TRUE
  CAN_FILTER          = TRUE
  CAN_CLASSIFY        = TRUE
  CAN_GROUP           = TRUE
  CAN_RANK            = TRUE
  CAN_PROPOSE_BATCH   = TRUE
  CAN_EXPLAIN         = TRUE
  CAN_RECORD          = TRUE
  CAN_PROJECT         = TRUE

  CAN_APPLY           = FALSE
  CAN_MODIFY_TARGET   = FALSE
  CAN_DECIDE_KX108    = FALSE
  CAN_COMMIT          = FALSE
  CAN_PUSH            = FALSE
  CAN_MERGE           = FALSE
  CAN_DEPLOY          = FALSE

decision_authority = KX108_ONLY
human_approved     = FALSE (toujours — c'est à l'humain de valider)
"""

from __future__ import annotations

import hashlib
import json
import os
import datetime
from pathlib import Path
from typing import Optional

# ─── Constantes ──────────────────────────────────────────────────────────────

SELECTOR_VERSION       = "V0"
BATCH_SCHEMA_VERSION   = "V0"
DECISION_AUTHORITY     = "KX108_ONLY"

DEFAULT_MAX_BATCH_SIZE = 5
HARD_MAX_BATCH_SIZE    = 10

SELECTOR_DIR = Path(os.environ.get("LOCALAPPDATA", "")) / "Obsidia" / "batch_selector"

PROTECTED_PATH_PREFIXES = frozenset([
    "proofs/",
    "formal/",
    "runtime_terrain_bank_trading_gps/server.kernel.sealed.cjs",
    "merkle_seal.json",
])

# ─── Éligibilité ─────────────────────────────────────────────────────────────

ELIGIBLE             = "ELIGIBLE"
INELIGIBLE           = "INELIGIBLE"
HOLD_UNKNOWN         = "HOLD_UNKNOWN"
ALREADY_PROCESSED    = "ALREADY_PROCESSED"
DUPLICATE            = "DUPLICATE"
CONFLICT             = "CONFLICT"
MISSING_DEPENDENCY   = "MISSING_DEPENDENCY"
PROTECTED            = "PROTECTED"
UNSUPPORTED          = "UNSUPPORTED"

# ─── Dépendances ─────────────────────────────────────────────────────────────

DEPENDENCY_CONFIRMED     = "DEPENDENCY_CONFIRMED"
DEPENDENCY_PROBABLE      = "DEPENDENCY_PROBABLE"
DEPENDENCY_UNKNOWN       = "DEPENDENCY_UNKNOWN"
NO_DEPENDENCY_KNOWN      = "NO_DEPENDENCY_KNOWN"
DEPENDENCY_CYCLE         = "DEPENDENCY_CYCLE"
DEPENDENCY_UNRESOLVED    = "DEPENDENCY_UNRESOLVED"
DEPENDENCY_OUTSIDE_SCOPE = "DEPENDENCY_OUTSIDE_SCOPE"

# ─── Portée explicite de candidats ────────────────────────────────────────────

SCOPE_GLOBAL   = "GLOBAL"
SCOPE_EXPLICIT = "EXPLICIT_ENTRY_IDS"

# ─── Status batch ─────────────────────────────────────────────────────────────

BATCH_PROPOSED              = "BATCH_PROPOSED"
BATCH_HOLD                  = "BATCH_HOLD"
BATCH_BLOCKED_BY_CONSTRAINT = "BATCH_BLOCKED_BY_CONSTRAINT"

# ─── Helpers ─────────────────────────────────────────────────────────────────

def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _sha16(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _load_jsonl(path: Path) -> list:
    if not path.exists():
        return []
    result = []
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s:
            continue
        try:
            result.append(json.loads(s))
        except json.JSONDecodeError:
            pass
    return result


def _append_jsonl(path: Path, obj: dict) -> None:
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(obj, ensure_ascii=False) + "\n")


# ─── Storage batch ───────────────────────────────────────────────────────────

def _batch_path(batch_id: str, selector_dir: Optional[Path] = None) -> Path:
    d = selector_dir or SELECTOR_DIR
    return d / "batches" / batch_id / "batch_proposal.json"


def _list_batches(selector_dir: Optional[Path] = None) -> list:
    d = (selector_dir or SELECTOR_DIR) / "batches"
    if not d.exists():
        return []
    result = []
    for entry in sorted(d.iterdir()):
        if entry.is_dir():
            bp = entry / "batch_proposal.json"
            if bp.exists():
                try:
                    result.append(json.loads(bp.read_text(encoding="utf-8")))
                except (json.JSONDecodeError, OSError):
                    pass
    return result


def _save_batch(proposal: dict, selector_dir: Optional[Path] = None) -> Path:
    p = _batch_path(proposal["batch_id"], selector_dir)
    _ensure_dir(p.parent)
    p.write_text(json.dumps(proposal, ensure_ascii=False, indent=2), encoding="utf-8")
    return p


def _load_batch(batch_id: str, selector_dir: Optional[Path] = None) -> Optional[dict]:
    p = _batch_path(batch_id, selector_dir)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


# ─── Identité batch ──────────────────────────────────────────────────────────

def batch_id_from_selection(
    selected_entry_ids: list[str],
    objective: str,
    max_batch_size: int,
) -> str:
    """
    ID déterministe : sha256 des entry_ids triés + objective + max_size.
    Ne contient PAS le timestamp pour préserver le déterminisme.
    """
    payload = json.dumps({
        "selected": sorted(selected_entry_ids),
        "objective": objective,
        "max_batch_size": max_batch_size,
        "selector_version": SELECTOR_VERSION,
    }, sort_keys=True)
    return _sha16(payload)


def batch_hash_from_proposal(
    selected_entry_ids: list[str],
    source_hashes: list[str],
    dependency_edges: list[dict],
    objective: str,
    max_batch_size: int,
    execution_order: "list[str] | None" = None,
    candidate_scope_mode: "str | None" = None,
    candidate_entry_ids: "list[str] | None" = None,
    target_paths: "list[str] | None" = None,
    git_source_identities: "list[dict] | None" = None,
) -> str:
    """
    Hash couvrant la substance complète de la proposition — y compris la
    sémantique de dépendance réellement utilisée (arêtes ET ordre
    d'exécution canonique qui en résulte), pas seulement l'ensemble des
    IDs sélectionnés. Deux batchs avec le même contenu mais un graphe de
    dépendances différent (donc un ordre d'exécution différent) doivent
    produire des batch_hash différents.

    batch_hash_version : 1 (historique, formule inchangée en substance)
    si ni target_paths ni git_source_identities ne sont fournis ; 2 sinon
    — lie explicitement le chemin cible ET la provenance Git complète
    (dépôt, commit, blob, chemin historique, SHA256 complet) de chaque
    candidat GIT_BLOB sélectionné, pas seulement le source_hash tronqué
    à 16 caractères. batch_hash n'est JAMAIS recalculé pour comparaison
    contre une proposition déjà stockée ailleurs dans le code (toujours
    lu tel quel depuis l'enregistrement persistant) — étendre ce champ
    n'invalide donc aucune preuve historique déjà stockée.
    """
    has_v2_fields = target_paths is not None or git_source_identities is not None
    batch_hash_version = 2 if has_v2_fields else 1

    payload: dict = {
        "selected": sorted(selected_entry_ids),
        "source_hashes": sorted(h for h in source_hashes if h),
        "dependency_edges": sorted(
            (e.get("from", ""), e.get("to", ""), e.get("type", ""))
            for e in dependency_edges
        ),
        "execution_order": execution_order or [],
        "candidate_scope_mode": candidate_scope_mode,
        "candidate_entry_ids": sorted(candidate_entry_ids) if candidate_entry_ids else None,
        "objective": objective,
        "max_batch_size": max_batch_size,
        "selector_version": SELECTOR_VERSION,
        "batch_hash_version": batch_hash_version,
    }
    if batch_hash_version >= 2:
        payload["target_paths"] = sorted(t for t in (target_paths or []) if t)
        payload["git_source_identities"] = sorted(
            json.dumps(g, sort_keys=True) for g in (git_source_identities or [])
        )
    return _sha16(json.dumps(payload, sort_keys=True))


# ─── Éligibilité d'un candidat ───────────────────────────────────────────────

def _is_protected(path: str) -> bool:
    for prefix in PROTECTED_PATH_PREFIXES:
        if path.startswith(prefix) or path == prefix.rstrip("/"):
            return True
    return False


def _check_eligibility(entry: dict) -> tuple[str, list[str]]:
    """
    Retourne (eligibility_status, reasons[]).
    Fail-closed : UNKNOWN != ELIGIBLE.
    """
    reasons: list[str] = []

    # Schema incompatible
    schema = entry.get("entry_schema_version")
    if schema not in ("V0", None):
        reasons.append(f"unsupported_schema:{schema}")
        return UNSUPPORTED, reasons

    target_path = entry.get("target_path") or ""

    # Protected path
    if _is_protected(target_path):
        reasons.append("protected_path")
        return PROTECTED, reasons

    # Source hash manquant → HOLD (preuve de contenu insuffisante)
    source_hash = entry.get("source_hash")
    if not source_hash or source_hash == "unknown":
        reasons.append("source_hash_missing")
        return HOLD_UNKNOWN, reasons

    # Provenance insuffisante
    if not target_path or target_path == "UNKNOWN":
        reasons.append("target_path_unknown")
        return HOLD_UNKNOWN, reasons

    # Dédup UNKNOWN → HOLD si la distinction est nécessaire
    dedup = entry.get("dedup_classification")
    if dedup == "DEDUP_UNKNOWN":
        reasons.append("dedup_unknown")
        return HOLD_UNKNOWN, reasons

    # Stage-aware : une source DISCOVERED (pre-build) n'a PAS encore de
    # kx108_decision / proposal_id / commit_sha — absence attendue
    # (NOT_YET_APPLICABLE), pas une preuve manquante. Les entrées post-build
    # (tout autre lifecycle_status) gardent le comportement fail-closed strict.
    lc = entry.get("lifecycle_status") or ""
    is_discovered = lc == "DISCOVERED"

    # KX108 absent → HOLD (pas de preuve de décision), sauf stage DISCOVERED
    kx108 = entry.get("kx108_decision")
    if not kx108:
        if not is_discovered:
            reasons.append("kx108_decision_missing")
            return HOLD_UNKNOWN, reasons
    else:
        # KX108 BLOCK → non sélectionnable
        if kx108 == "BLOCK":
            reasons.append("kx108_blocked")
            return INELIGIBLE, reasons

        # KX108 HOLD → état incertain, ne pas sélectionner sans résolution humaine
        if kx108 == "HOLD":
            reasons.append("kx108_hold_status")
            return HOLD_UNKNOWN, reasons

    # Lifecycle ABORTED / CLEANED → déjà traité
    if lc in ("ABORTED", "CLEANED"):
        reasons.append(f"lifecycle_{lc.lower()}")
        return ALREADY_PROCESSED, reasons

    # Lifecycle COMMITTED → déjà dans le dépôt
    if lc == "COMMITTED":
        reasons.append("lifecycle_committed")
        return ALREADY_PROCESSED, reasons

    # Unknowns critiques (hors source_hash_missing, déjà traité)
    unknowns = [u for u in (entry.get("unknowns") or []) if u != "commit_sha_pending"]
    if is_discovered:
        unknowns = [
            u for u in unknowns
            if u not in ("proposal_id_missing", "kx108_decision_missing")
        ]
    if unknowns:
        reasons.append(f"unknowns:{unknowns}")
        return HOLD_UNKNOWN, reasons

    reasons.append("all_checks_passed")
    return ELIGIBLE, reasons


# ─── Construction des candidats ──────────────────────────────────────────────

def build_candidate(entry: dict) -> dict:
    """Construit un candidat depuis une entrée Ledger."""
    eligibility, reasons = _check_eligibility(entry)
    return {
        "candidate_id": entry.get("ledger_entry_id", "UNKNOWN"),
        "ledger_entry_id": entry.get("ledger_entry_id"),
        "normalized_path": entry.get("target_path", "UNKNOWN"),
        "source_hash": entry.get("source_hash"),
        "source_type": entry.get("source_type"),
        "source_path": entry.get("source_path"),
        "source_kind": entry.get("source_kind", "FILESYSTEM_FILE"),
        "source_git_commit_sha": entry.get("source_git_commit_sha"),
        "source_git_blob_sha": entry.get("source_git_blob_sha"),
        "source_git_historical_path": entry.get("source_git_historical_path"),
        "source_repository_identity": entry.get("source_repository_identity"),
        "source_content_sha256": entry.get("source_content_sha256"),
        "target_path": entry.get("target_path"),
        "target_domain": entry.get("target_domain"),
        "session_id": entry.get("session_id"),
        "prev_entry_id": entry.get("prev_entry_id"),
        "dedup_classification": entry.get("dedup_classification", "DEDUP_UNKNOWN"),
        "lifecycle_status": entry.get("lifecycle_status"),
        "kx108_decision": entry.get("kx108_decision"),
        "proposal_id": entry.get("proposal_id"),
        "proposal_hash": entry.get("proposal_hash"),
        "dependencies": [],
        "dependency_refs": list(entry.get("dependency_refs") or []),
        "provenance_refs": dict(entry.get("provenance_refs") or {}),
        "dependency_status": NO_DEPENDENCY_KNOWN,
        "risk_flags": list(entry.get("risk_flags") or []),
        "unknowns": list(entry.get("unknowns") or []),
        "eligibility": eligibility,
        "eligibility_reasons": reasons,
    }


def _ledger_module():
    import sys as _sys, pathlib as _pathlib
    _scripts = str(_pathlib.Path(__file__).resolve().parent)
    if _scripts not in _sys.path:
        _sys.path.insert(0, _scripts)
    import obsidia_branching_ledger as _mod
    return _mod


def _load_ledger_universe(
    ledger_dir: Optional[Path] = None,
    additional_candidates: Optional[list[dict]] = None,
) -> list[dict]:
    """Toutes les entrées Ledger connues (GLOBAL) — indépendamment de toute
    portée explicite ultérieure. Sert de référentiel pour la résolution de
    dependency_refs et pour la validation des entry_id demandés."""
    entries = _ledger_module()._load_entries(ledger_dir)
    if additional_candidates:
        entries = entries + additional_candidates
    return entries


def _load_dependency_link_events(ledger_dir: Optional[Path] = None) -> dict[str, list[str]]:
    """Projette les événements append-only DEPENDENCY_LINKED en
    {source_ledger_entry_id: [dependency_ledger_entry_id, ...]}.
    Ne modifie jamais les lignes d'entrées — lecture d'historique seule."""
    links: dict[str, list[str]] = {}
    for ev in _ledger_module()._load_events(ledger_dir):
        if ev.get("event_type") != "DEPENDENCY_LINKED":
            continue
        src = ev.get("source_ledger_entry_id")
        dep = ev.get("dependency_ledger_entry_id")
        if src and dep:
            bucket = links.setdefault(src, [])
            if dep not in bucket:
                bucket.append(dep)
    return links


def _build_entry_index(entries: list[dict]) -> dict[str, str]:
    """path/entry_id -> ledger_entry_id, depuis l'UNIVERS COMPLET (pas la
    portée). Permet de distinguer DEPENDENCY_OUTSIDE_SCOPE (résolu mais hors
    portée) de DEPENDENCY_UNRESOLVED (ne résout nulle part)."""
    index: dict[str, str] = {}
    for e in entries:
        eid = e.get("ledger_entry_id")
        if not eid:
            continue
        index.setdefault(eid, eid)
        if e.get("target_path"):
            index.setdefault(e["target_path"], eid)
        if e.get("source_path"):
            index.setdefault(e["source_path"], eid)
    return index


def build_entry_index_from_ledger(
    ledger_dir: Optional[Path] = None,
    additional_candidates: Optional[list[dict]] = None,
) -> dict[str, str]:
    return _build_entry_index(_load_ledger_universe(ledger_dir, additional_candidates))


def build_candidates_from_ledger(
    ledger_dir: Optional[Path] = None,
    additional_candidates: Optional[list[dict]] = None,
    candidate_entry_ids: Optional[list[str]] = None,
) -> list[dict]:
    """
    Charge les entrées du Ledger et construit les candidats.
    additional_candidates : liste de dicts d'entrées Ledger injectés (pour tests/E2E).
    candidate_entry_ids   : None = mode GLOBAL (historique, inchangé).
                            liste = mode EXPLICITE — seules ces entrées
                            deviennent des candidats (pas de filtrage après
                            coup : la portée contraint l'univers AVANT
                            sélection).
    """
    entries = _load_ledger_universe(ledger_dir, additional_candidates)
    dep_links = _load_dependency_link_events(ledger_dir)

    if candidate_entry_ids is not None:
        scope_set = set(candidate_entry_ids)
        entries = [e for e in entries if e.get("ledger_entry_id") in scope_set]

    candidates: list[dict] = []
    for e in entries:
        eid = e.get("ledger_entry_id")
        merged_refs = list(e.get("dependency_refs") or []) + dep_links.get(eid, [])
        e_augmented = dict(e)
        e_augmented["dependency_refs"] = merged_refs
        candidates.append(build_candidate(e_augmented))
    return candidates


# ─── Dépendances (V0 minimal) ────────────────────────────────────────────────

def detect_dependencies(
    candidates: list[dict],
    entry_index: Optional[dict[str, str]] = None,
) -> list[dict]:
    """
    Combine deux mécanismes, sans dupliquer une même relation (from,to) :
    1. relation de version prev_entry_id (V0 historique, inchangée)
    2. dependency_refs explicites (champ d'enregistrement + événements
       append-only DEPENDENCY_LINKED), résolus via entry_index — l'UNIVERS
       COMPLET du Ledger, pas seulement les candidats en portée. Permet de
       distinguer :
         - résolu ET dans la portée courante  -> DEPENDENCY_CONFIRMED
         - résolu MAIS hors portée courante    -> DEPENDENCY_OUTSIDE_SCOPE (HOLD)
         - ne résout nulle part                -> DEPENDENCY_UNRESOLVED (HOLD)
    Ne jamais inventer un ordre si les preuves ne le permettent pas.
    """
    edges: list[dict] = []
    seen: set[tuple[str, str]] = set()
    id_set = {c["candidate_id"] for c in candidates}
    idx = entry_index or {}

    def _add_edge(frm: str, to: str, etype: str, reason: str) -> None:
        key = (frm, to)
        if key in seen:
            return
        seen.add(key)
        edges.append({"from": frm, "to": to, "type": etype, "reason": reason})

    # 1. Chaîne de version (prev_entry_id)
    for c in candidates:
        prev = c.get("prev_entry_id")
        if prev:
            edge_type = DEPENDENCY_CONFIRMED if prev in id_set else DEPENDENCY_PROBABLE
            _add_edge(c["candidate_id"], prev, edge_type, "prev_entry_id_version_chain")
            if edge_type == DEPENDENCY_PROBABLE:
                c["dependency_status"] = "DEPENDENCY_OUTSIDE_BATCH"
                c["unknowns"] = list(c.get("unknowns") or []) + ["dependency_outside_batch"]
            else:
                c["dependency_status"] = DEPENDENCY_CONFIRMED

    # 2. dependency_refs explicites (champ + événements DEPENDENCY_LINKED)
    for c in candidates:
        refs = c.get("dependency_refs") or []
        for ref in refs:
            resolved = idx.get(ref)
            if resolved is None:
                _add_edge(c["candidate_id"], ref, DEPENDENCY_UNRESOLVED, "dependency_ref_unresolved")
                c["dependency_status"] = DEPENDENCY_UNRESOLVED
                c["unknowns"] = list(c.get("unknowns") or []) + ["dependency_unresolved"]
            elif resolved in id_set:
                _add_edge(c["candidate_id"], resolved, DEPENDENCY_CONFIRMED, "dependency_ref")
                if c.get("dependency_status") in (None, NO_DEPENDENCY_KNOWN):
                    c["dependency_status"] = DEPENDENCY_CONFIRMED
            else:
                _add_edge(c["candidate_id"], resolved, DEPENDENCY_OUTSIDE_SCOPE, "dependency_ref_outside_scope")
                c["dependency_status"] = DEPENDENCY_OUTSIDE_SCOPE
                c["unknowns"] = list(c.get("unknowns") or []) + ["dependency_outside_scope"]

    return edges


def detect_cycles(candidates: list[dict], edges: list[dict]) -> list[str]:
    """
    Détection COMPLÈTE des composantes cycliques (Tarjan SCC), pas
    seulement le nœud cible d'une back-edge. Tout nœud appartenant à une
    composante fortement connexe de taille > 1, ou à une boucle réflexive
    (A -> A), est retourné — déterministe (ordre d'apparition dans
    `candidates`). Les arêtes pointant hors de l'univers `candidates`
    (dépendance hors-portée/non-résolue) sont ignorées : elles ne peuvent
    pas participer à un cycle interne au batch.
    """
    graph: dict[str, list[str]] = {c["candidate_id"]: [] for c in candidates}
    for e in edges:
        if e["from"] in graph:
            graph[e["from"]].append(e["to"])

    index_counter = [0]
    stack: list[str] = []
    on_stack: set[str] = set()
    indices: dict[str, int] = {}
    lowlink: dict[str, int] = {}
    cyclic: set[str] = set()

    def strongconnect(v: str) -> None:
        indices[v] = index_counter[0]
        lowlink[v] = index_counter[0]
        index_counter[0] += 1
        stack.append(v)
        on_stack.add(v)

        for w in graph.get(v, []):
            if w not in graph:
                continue  # hors univers candidat : ne peut pas boucler ici
            if w not in indices:
                strongconnect(w)
                lowlink[v] = min(lowlink[v], lowlink[w])
            elif w in on_stack:
                lowlink[v] = min(lowlink[v], indices[w])

        if lowlink[v] == indices[v]:
            component: list[str] = []
            while True:
                w = stack.pop()
                on_stack.discard(w)
                component.append(w)
                if w == v:
                    break
            is_cyclic = len(component) > 1 or v in graph.get(v, [])
            if is_cyclic:
                cyclic.update(component)

    for c in candidates:
        node = c["candidate_id"]
        if node not in indices:
            strongconnect(node)

    return [c["candidate_id"] for c in candidates if c["candidate_id"] in cyclic]


# ─── Ordre d'exécution (dépendances d'abord) ─────────────────────────────────

def compute_execution_order(selected: list[dict], edges: list[dict]) -> list[str]:
    """
    Ordre topologique déterministe des candidats retenus : une dépendance
    DEPENDENCY_CONFIRMED précède toujours son dépendant. Les noeuds
    indépendants gardent un ordre stable (ordre d'apparition dans
    `selected` — jamais l'ordre de la requête d'entrée, cf. §6).
    N'ordonne jamais de noeuds cycliques (déjà retirés de `selected` en
    amont). Ne fabrique aucun ordre non justifié par les preuves : si un
    blocage inattendu survient (ne devrait pas arriver, cycles déjà
    retirés), le reste est placé dans l'ordre stable d'origine plutôt que
    de planter ou d'inventer une dépendance.
    """
    selected_ids = [c["candidate_id"] for c in selected]
    id_set = set(selected_ids)

    predecessors: dict[str, set[str]] = {sid: set() for sid in selected_ids}
    for e in edges:
        if e.get("type") != DEPENDENCY_CONFIRMED:
            continue
        frm, to = e.get("from"), e.get("to")
        if frm in id_set and to in id_set:
            predecessors[frm].add(to)

    order: list[str] = []
    remaining = set(selected_ids)
    placed: set[str] = set()

    while remaining:
        ready = [
            sid for sid in selected_ids
            if sid in remaining and predecessors[sid] <= placed
        ]
        if not ready:
            ready = [sid for sid in selected_ids if sid in remaining]
        for sid in ready:
            order.append(sid)
            placed.add(sid)
            remaining.discard(sid)

    return order


# ─── Déduplication dans la sélection ────────────────────────────────────────

def _dedup_candidates(candidates: list[dict]) -> tuple[list[dict], list[dict]]:
    """
    Retire les doublons exacts (même target_path + source_hash).
    Retourne (deduplicated, excluded_duplicates).
    SAME_PATH_SAME_CONTENT → exclu.
    """
    seen: dict[str, dict] = {}
    result: list[dict] = []
    excluded: list[dict] = []

    for c in candidates:
        key = f"{c.get('target_path')}::{c.get('source_hash')}"
        if c.get("dedup_classification") == "SAME_PATH_SAME_CONTENT":
            c = dict(c)
            c["exclusion_reason"] = "DUPLICATE_SAME_PATH_SAME_CONTENT"
            excluded.append(c)
        elif key in seen:
            c = dict(c)
            c["exclusion_reason"] = "DUPLICATE_KEY"
            excluded.append(c)
        else:
            seen[key] = c
            result.append(c)

    return result, excluded


# ─── Sélection principale ────────────────────────────────────────────────────

def select_batch(
    candidates: list[dict],
    max_batch_size: int = DEFAULT_MAX_BATCH_SIZE,
    objective: str = "",
    entry_index: Optional[dict[str, str]] = None,
) -> dict:
    """
    Politique déterministe V0 :
    1. Filtre protected/invalid/corrupt
    2. Retire SAME_PATH_SAME_CONTENT
    3. HOLD unknown critiques
    4. Dépendances (prev_entry_id)
    5. Cycle → DEPENDENCY_CYCLE
    6. Coupe à max_batch_size (hard max HARD_MAX_BATCH_SIZE)
    7. Priorité : ACT > HOLD_KX108 ; complet > incomplet ; petite surface

    Retourne un dict de sélection structuré.
    """
    if max_batch_size > HARD_MAX_BATCH_SIZE:
        max_batch_size = HARD_MAX_BATCH_SIZE

    selected: list[dict] = []
    hold_entries: list[dict] = []
    excluded_entries: list[dict] = []

    # Étape 1+2 : dédup + éligibilité
    deduped, dup_excluded = _dedup_candidates(candidates)
    excluded_entries.extend(dup_excluded)

    for c in deduped:
        elig = c.get("eligibility")
        if elig == ELIGIBLE:
            selected.append(c)
        elif elig in (HOLD_UNKNOWN, MISSING_DEPENDENCY):
            c = dict(c)
            c["hold_reason"] = c.get("eligibility_reasons", [])
            hold_entries.append(c)
        else:
            c = dict(c)
            c["exclusion_reason"] = c.get("exclusion_reason") or elig
            excluded_entries.append(c)

    # Étape 4 : dépendances (version chain + dependency_refs explicites)
    edges = detect_dependencies(selected + hold_entries, entry_index)

    # Étape 5 : cycles — retirer par référence originale, pas par copie
    cycle_nodes = detect_cycles(selected + hold_entries, edges)
    cycle_originals = [c for c in selected if c["candidate_id"] in cycle_nodes]
    for c_orig in cycle_originals:
        c_hold = dict(c_orig)
        c_hold["hold_reason"] = ["DEPENDENCY_CYCLE"]
        c_hold["dependency_status"] = DEPENDENCY_CYCLE
        hold_entries.append(c_hold)
        selected.remove(c_orig)

    # Étape 5bis : dépendance résolue hors-portée ou non résolue → HOLD
    # (fail-closed — ne jamais sélectionner un candidat dont la dépendance
    # déclarée ne peut être garantie dans ce même batch).
    dep_hold_originals = [
        c for c in selected
        if c.get("dependency_status") in (DEPENDENCY_OUTSIDE_SCOPE, DEPENDENCY_UNRESOLVED)
    ]
    for c_orig in dep_hold_originals:
        c_hold = dict(c_orig)
        c_hold["hold_reason"] = [c_orig["dependency_status"]]
        hold_entries.append(c_hold)
        selected.remove(c_orig)

    # Étape 5ter : ordre d'exécution topologique déterministe — les
    # dépendances CONFIRMED précèdent leur dépendant, indépendant de
    # l'ordre de la requête d'entrée (§6).
    execution_order = compute_execution_order(selected, edges)
    order_index = {sid: i for i, sid in enumerate(execution_order)}
    selected.sort(key=lambda c: order_index.get(c["candidate_id"], len(execution_order)))

    # Étape 6 : coupe à max (respecte l'ordre topologique ci-dessus)
    overflow: list[dict] = []
    if len(selected) > max_batch_size:
        overflow = selected[max_batch_size:]
        selected = selected[:max_batch_size]
        for c in overflow:
            c = dict(c)
            c["exclusion_reason"] = "EXCEEDS_MAX_BATCH_SIZE"
            excluded_entries.append(c)
    execution_order = [c["candidate_id"] for c in selected]

    return {
        "selected": selected,
        "hold_entries": hold_entries,
        "excluded_entries": excluded_entries,
        "dependency_edges": edges,
        "cycle_nodes": cycle_nodes,
        "execution_order": execution_order,
        "overflow": overflow,
    }


# ─── Métriques ───────────────────────────────────────────────────────────────

def compute_metrics(
    candidates: list[dict],
    selected: list[dict],
    hold_entries: list[dict],
    excluded_entries: list[dict],
    edges: list[dict],
    cycle_nodes: list[str],
    selection_duration_ms: float = 0.0,
) -> dict:
    n = len(candidates)
    return {
        "candidate_count": n,
        "eligible_count": sum(1 for c in candidates if c.get("eligibility") == ELIGIBLE),
        "selected_count": len(selected),
        "excluded_count": len(excluded_entries),
        "hold_count": len(hold_entries),
        "unknown_rate": round(
            sum(1 for c in candidates if c.get("eligibility") == HOLD_UNKNOWN) / n, 3
        ) if n else 0.0,
        "hold_rate": round(len(hold_entries) / n, 3) if n else 0.0,
        "duplicate_rate": round(
            sum(1 for c in excluded_entries
                if "DUPLICATE" in (c.get("exclusion_reason") or "")) / n, 3
        ) if n else 0.0,
        "dependency_count": len(edges),
        "missing_dependency_count": sum(
            1 for c in candidates
            if any(
                u in (c.get("unknowns") or [])
                for u in ("dependency_outside_batch", "dependency_outside_scope", "dependency_unresolved")
            )
        ),
        "cycle_count": len(cycle_nodes),
        "average_dependencies_per_selected": (
            round(len(edges) / len(selected), 2) if selected else 0.0
        ),
        "batch_fill_ratio": round(
            len(selected) / DEFAULT_MAX_BATCH_SIZE, 3
        ),
        "selection_duration_ms": round(selection_duration_ms, 2),
    }


# ─── Proposition de batch ────────────────────────────────────────────────────

def propose_batch(
    objective: str = "",
    max_batch_size: int = DEFAULT_MAX_BATCH_SIZE,
    ledger_dir: Optional[Path] = None,
    selector_dir: Optional[Path] = None,
    additional_candidates: Optional[list[dict]] = None,
    candidate_entry_ids: Optional[list[str]] = None,
) -> dict:
    """
    Point d'entrée principal du Selector.
    Découvre les candidats, sélectionne, produit un BatchProposal immuable.

    candidate_entry_ids : None = mode GLOBAL (historique, Ledger entier).
        list[str] = mode EXPLICITE — seuls ces entry_id peuvent devenir
        candidats. Liste vide ou entry_id inconnu -> fail-closed
        (scope_error, aucune sélection, rien sauvegardé).
    """
    import time
    t0 = time.monotonic()

    if max_batch_size > HARD_MAX_BATCH_SIZE:
        max_batch_size = HARD_MAX_BATCH_SIZE

    candidate_scope_mode = SCOPE_EXPLICIT if candidate_entry_ids is not None else SCOPE_GLOBAL
    normalized_scope_ids: Optional[list[str]] = None
    scope_error: Optional[str] = None

    if candidate_entry_ids is not None:
        seen_ids: list[str] = []
        for eid in candidate_entry_ids:
            if eid not in seen_ids:
                seen_ids.append(eid)
        normalized_scope_ids = seen_ids
        if not normalized_scope_ids:
            scope_error = "EMPTY_EXPLICIT_SCOPE"
        else:
            universe = _load_ledger_universe(ledger_dir, additional_candidates)
            known_ids = {e.get("ledger_entry_id") for e in universe}
            unknown_ids = [eid for eid in normalized_scope_ids if eid not in known_ids]
            if unknown_ids:
                scope_error = f"UNKNOWN_CANDIDATE_ENTRY_ID:{unknown_ids}"

    candidate_scope_hash = (
        _sha16(json.dumps(sorted(normalized_scope_ids)))
        if normalized_scope_ids else None
    )

    if scope_error:
        duration_ms = (time.monotonic() - t0) * 1000.0
        metrics = compute_metrics([], [], [], [], [], [], duration_ms)
        return {
            "batch_id": None,
            "batch_schema_version": BATCH_SCHEMA_VERSION,
            "created_at": _now(),
            "selector_version": SELECTOR_VERSION,
            "objective": objective,
            "requested_max_size": max_batch_size,
            "actual_size": 0,
            "candidate_count": 0,
            "eligible_count": 0,
            "selected_count": 0,
            "hold_count": 0,
            "excluded_count": 0,
            "selected_entries": [],
            "excluded_entries": [],
            "hold_entries": [],
            "dependency_edges": [],
            "dependency_groups": [],
            "cycle_nodes": [],
            "execution_order": [],
            "selection_reasons": {},
            "exclusion_reasons": {},
            "hold_reasons": {},
            "risk_flags": [],
            "unknowns": [],
            "ledger_refs": [],
            "batch_hash": None,
            "status": BATCH_HOLD,
            "human_approved": False,
            "decision_authority": DECISION_AUTHORITY,
            "metrics": metrics,
            "candidate_scope_mode": candidate_scope_mode,
            "candidate_entry_ids": normalized_scope_ids,
            "candidate_scope_hash": candidate_scope_hash,
            "scope_error": scope_error,
        }

    candidates = build_candidates_from_ledger(ledger_dir, additional_candidates, normalized_scope_ids)
    entry_index = build_entry_index_from_ledger(ledger_dir, additional_candidates)
    sel_result = select_batch(candidates, max_batch_size, objective, entry_index)

    selected        = sel_result["selected"]
    hold            = sel_result["hold_entries"]
    excluded        = sel_result["excluded_entries"]
    edges           = sel_result["dependency_edges"]
    cycles          = sel_result["cycle_nodes"]
    execution_order = sel_result["execution_order"]

    duration_ms = (time.monotonic() - t0) * 1000.0

    selected_ids   = [c["candidate_id"] for c in selected]
    source_hashes  = [c["source_hash"] for c in selected if c.get("source_hash")]
    target_paths   = [c.get("target_path") for c in selected if c.get("target_path")]
    git_source_identities = [
        {
            "source_kind": c.get("source_kind"),
            "source_repository_identity": c.get("source_repository_identity"),
            "source_git_commit_sha": c.get("source_git_commit_sha"),
            "source_git_blob_sha": c.get("source_git_blob_sha"),
            "source_git_historical_path": c.get("source_git_historical_path"),
            "source_content_sha256": c.get("source_content_sha256"),
            "target_path": c.get("target_path"),
        }
        for c in selected if c.get("source_kind") == "GIT_BLOB"
    ]

    # Persisté explicitement dans le BatchProposal (pas seulement injecté
    # dans le payload haché) — preuve durable et auto-descriptive de la
    # formule utilisée. Une proposition historique sans ce champ reste
    # interprétée comme version 1 (jamais réécrite/migrée).
    bhash_version = 2 if (target_paths or git_source_identities) else 1

    bid  = batch_id_from_selection(selected_ids, objective, max_batch_size)
    bhash = batch_hash_from_proposal(
        selected_ids, source_hashes, edges, objective, max_batch_size,
        execution_order=execution_order,
        candidate_scope_mode=candidate_scope_mode,
        candidate_entry_ids=normalized_scope_ids,
        target_paths=target_paths,
        git_source_identities=git_source_identities,
    )

    status = BATCH_PROPOSED if not (cycles or not candidates) else BATCH_HOLD
    if not candidates:
        status = BATCH_HOLD

    metrics = compute_metrics(
        candidates, selected, hold, excluded, edges, cycles, duration_ms
    )

    proposal: dict = {
        "batch_id": bid,
        "batch_schema_version": BATCH_SCHEMA_VERSION,
        "created_at": _now(),
        "selector_version": SELECTOR_VERSION,

        "objective": objective,
        "requested_max_size": max_batch_size,
        "actual_size": len(selected),

        "candidate_count": metrics["candidate_count"],
        "eligible_count": metrics["eligible_count"],
        "selected_count": metrics["selected_count"],
        "hold_count": metrics["hold_count"],
        "excluded_count": metrics["excluded_count"],

        "selected_entries": selected,
        "excluded_entries": excluded,
        "hold_entries": hold,

        "dependency_edges": edges,
        "dependency_groups": [],
        "cycle_nodes": cycles,
        "execution_order": execution_order,

        "selection_reasons": {
            c["candidate_id"]: c.get("eligibility_reasons", [])
            for c in selected
        },
        "exclusion_reasons": {
            c["candidate_id"]: c.get("exclusion_reason", "")
            for c in excluded
        },
        "hold_reasons": {
            c["candidate_id"]: c.get("hold_reason", [])
            for c in hold
        },

        "risk_flags": [
            f for c in selected for f in (c.get("risk_flags") or [])
        ],
        "unknowns": [
            u for c in selected for u in (c.get("unknowns") or [])
        ],

        "ledger_refs": selected_ids,
        "batch_hash": bhash,
        "batch_hash_version": bhash_version,

        "status": status,
        "human_approved": False,
        "decision_authority": DECISION_AUTHORITY,

        "metrics": metrics,

        "candidate_scope_mode": candidate_scope_mode,
        "candidate_entry_ids": normalized_scope_ids,
        "candidate_scope_hash": candidate_scope_hash,
        "scope_error": None,
    }

    _save_batch(proposal, selector_dir)
    return proposal


# ─── Commandes lecture ───────────────────────────────────────────────────────

def cmd_batch_list(selector_dir: Optional[Path] = None) -> int:
    batches = _list_batches(selector_dir)
    sep = "=" * 70
    print(f"\n{sep}")
    print("  OBSIDIA BATCH SELECTOR -- LIST")
    print(f"  selector_dir : {selector_dir or SELECTOR_DIR}")
    print(f"{sep}\n")
    if not batches:
        print("  [EMPTY] Aucun batch propose.")
        return 0
    print(f"  {'BATCH_ID':<18} {'STATUS':<28} {'SIZE':>4} {'HOLDS':>5} {'RISKS':>5}  created_at")
    print("  " + "-" * 80)
    for b in batches:
        risks = len(b.get("risk_flags") or [])
        holds = b.get("hold_count", 0)
        print(
            f"  {b.get('batch_id','?'):<18}"
            f" {b.get('status','?'):<28}"
            f" {b.get('actual_size',0):>4}"
            f" {holds:>5}"
            f" {risks:>5}"
            f"  {str(b.get('created_at','?'))[:19]}"
        )
    print(f"\n  {len(batches)} batch(es) -- decision_authority = {DECISION_AUTHORITY}")
    return 0


def cmd_batch_status(batch_id: str, selector_dir: Optional[Path] = None) -> int:
    proposal = _load_batch(batch_id, selector_dir)
    if proposal is None:
        print(f"  [BATCH_FAIL] Batch inconnu : {batch_id}")
        return 2
    sep = "=" * 70
    print(f"\n{sep}")
    print(f"  OBSIDIA BATCH SELECTOR -- STATUS : {batch_id}")
    print(f"{sep}\n")
    for f in (
        "objective", "status", "selected_count", "hold_count",
        "excluded_count", "candidate_count", "actual_size",
        "requested_max_size", "batch_hash", "human_approved",
        "decision_authority",
    ):
        print(f"  {f:<30}: {proposal.get(f)}")
    deps = len(proposal.get("dependency_edges") or [])
    cycles = len(proposal.get("cycle_nodes") or [])
    unk = len(proposal.get("unknowns") or [])
    risks = len(proposal.get("risk_flags") or [])
    print(f"  {'dependency_count':<30}: {deps}")
    print(f"  {'cycle_count':<30}: {cycles}")
    print(f"  {'unknowns_in_selected':<30}: {unk}")
    print(f"  {'risks_in_selected':<30}: {risks}")
    if cycles:
        print(f"  next_human_action             : RESOLVE_BATCH_HOLD")
    else:
        print(f"  next_human_action             : REVIEW_BATCH_PROPOSAL")
    return 0


def cmd_batch_inspect(batch_id: str, selector_dir: Optional[Path] = None) -> int:
    proposal = _load_batch(batch_id, selector_dir)
    if proposal is None:
        print(f"  [BATCH_FAIL] Batch inconnu : {batch_id}")
        return 2
    sep = "=" * 70
    print(f"\n{sep}")
    print(f"  OBSIDIA BATCH SELECTOR -- INSPECT : {batch_id}")
    print(f"{sep}\n")

    print("  [IDENTITY]")
    for f in ("batch_id", "batch_schema_version", "selector_version",
              "created_at", "batch_hash", "status", "human_approved", "decision_authority"):
        print(f"  {f:<32}: {proposal.get(f)}")

    print(f"\n  [SELECTED] ({proposal.get('selected_count', 0)} entrees)")
    for e in (proposal.get("selected_entries") or []):
        path  = e.get("target_path", "?")
        eid   = e.get("candidate_id", "?")
        dedup = e.get("dedup_classification", "?")
        kx    = e.get("kx108_decision", "?")
        sha   = (e.get("source_hash") or "NONE")[:12]
        print(f"  {eid}  {path}  KX108={kx}  dedup={dedup}  sha={sha}")
        reasons = e.get("eligibility_reasons") or []
        if reasons:
            print(f"    -> raisons : {reasons}")

    print(f"\n  [HOLD] ({proposal.get('hold_count', 0)} entrees)")
    for e in (proposal.get("hold_entries") or []):
        print(f"  {e.get('candidate_id','?')}  {e.get('target_path','?')}  hold={e.get('hold_reason')}")

    print(f"\n  [EXCLUDED] ({proposal.get('excluded_count', 0)} entrees)")
    for e in (proposal.get("excluded_entries") or []):
        print(f"  {e.get('candidate_id','?')}  {e.get('target_path','?')}  reason={e.get('exclusion_reason')}")

    print(f"\n  [DEPENDENCIES] ({len(proposal.get('dependency_edges') or [])} edges)")
    for edge in (proposal.get("dependency_edges") or []):
        print(f"  {edge.get('from')} -[{edge.get('type')}]-> {edge.get('to')}")

    cycles = proposal.get("cycle_nodes") or []
    if cycles:
        print(f"\n  [CYCLES DETECTES] : {cycles}")

    print(f"\n  [METRICS]")
    m = proposal.get("metrics") or {}
    for k, v in m.items():
        print(f"  {k:<34}: {v}")

    unk = proposal.get("unknowns") or []
    if unk:
        print(f"\n  [UNKNOWNS dans selected] : {unk}")
    risks = proposal.get("risk_flags") or []
    if risks:
        print(f"  [RISK_FLAGS dans selected] : {risks}")

    print(f"\n  next_human_action : {'RESOLVE_BATCH_HOLD' if cycles else 'REVIEW_BATCH_PROPOSAL'}")
    return 0


def cmd_batch_candidates(
    ledger_dir: Optional[Path] = None,
    additional_candidates: Optional[list[dict]] = None,
) -> int:
    candidates = build_candidates_from_ledger(ledger_dir, additional_candidates)
    sep = "=" * 70
    print(f"\n{sep}")
    print("  OBSIDIA BATCH SELECTOR -- CANDIDATES")
    print(f"{sep}\n")
    if not candidates:
        print("  [EMPTY] Aucun candidat disponible.")
        return 0
    for c in candidates:
        print(
            f"  {c['candidate_id']:<18}"
            f"  {str(c.get('target_path','?')):<40}"
            f"  elig={c.get('eligibility','?')}"
        )
    print(f"\n  {len(candidates)} candidat(s)")
    return 0

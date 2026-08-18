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

DEPENDENCY_CONFIRMED = "DEPENDENCY_CONFIRMED"
DEPENDENCY_PROBABLE  = "DEPENDENCY_PROBABLE"
DEPENDENCY_UNKNOWN   = "DEPENDENCY_UNKNOWN"
NO_DEPENDENCY_KNOWN  = "NO_DEPENDENCY_KNOWN"
DEPENDENCY_CYCLE     = "DEPENDENCY_CYCLE"

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
) -> str:
    """Hash couvrant la substance complète de la proposition."""
    payload = json.dumps({
        "selected": sorted(selected_entry_ids),
        "source_hashes": sorted(h for h in source_hashes if h),
        "dependency_edges": sorted(
            (e.get("from", ""), e.get("to", ""), e.get("type", ""))
            for e in dependency_edges
        ),
        "objective": objective,
        "max_batch_size": max_batch_size,
        "selector_version": SELECTOR_VERSION,
    }, sort_keys=True)
    return _sha16(payload)


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

    # KX108 absent → HOLD (pas de preuve de décision)
    kx108 = entry.get("kx108_decision")
    if not kx108:
        reasons.append("kx108_decision_missing")
        return HOLD_UNKNOWN, reasons

    # KX108 BLOCK → non sélectionnable
    if kx108 == "BLOCK":
        reasons.append("kx108_blocked")
        return INELIGIBLE, reasons

    # KX108 HOLD → état incertain, ne pas sélectionner sans résolution humaine
    if kx108 == "HOLD":
        reasons.append("kx108_hold_status")
        return HOLD_UNKNOWN, reasons

    # Lifecycle ABORTED / CLEANED → déjà traité
    lc = entry.get("lifecycle_status") or ""
    if lc in ("ABORTED", "CLEANED"):
        reasons.append(f"lifecycle_{lc.lower()}")
        return ALREADY_PROCESSED, reasons

    # Lifecycle COMMITTED → déjà dans le dépôt
    if lc == "COMMITTED":
        reasons.append("lifecycle_committed")
        return ALREADY_PROCESSED, reasons

    # Unknowns critiques (hors source_hash_missing, déjà traité)
    unknowns = [u for u in (entry.get("unknowns") or []) if u != "commit_sha_pending"]
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
        "dependency_status": NO_DEPENDENCY_KNOWN,
        "risk_flags": list(entry.get("risk_flags") or []),
        "unknowns": list(entry.get("unknowns") or []),
        "eligibility": eligibility,
        "eligibility_reasons": reasons,
    }


def build_candidates_from_ledger(
    ledger_dir: Optional[Path] = None,
    additional_candidates: Optional[list[dict]] = None,
) -> list[dict]:
    """
    Charge toutes les entrées du Ledger et construit les candidats.
    additional_candidates : liste de dicts d'entrées Ledger injectés (pour tests/E2E).
    """
    import sys as _sys, pathlib as _pathlib
    _scripts = str(_pathlib.Path(__file__).resolve().parent)
    if _scripts not in _sys.path:
        _sys.path.insert(0, _scripts)
    from obsidia_branching_ledger import _load_entries

    entries = _load_entries(ledger_dir)
    if additional_candidates:
        entries = entries + additional_candidates

    return [build_candidate(e) for e in entries]


# ─── Dépendances (V0 minimal) ────────────────────────────────────────────────

def detect_dependencies(candidates: list[dict]) -> list[dict]:
    """
    V0 : modélise uniquement la relation prev_entry_id (version chain).
    Retourne une liste d'edges {from, to, type}.
    """
    edges: list[dict] = []
    id_set = {c["candidate_id"] for c in candidates}

    for c in candidates:
        prev = c.get("prev_entry_id")
        if prev:
            edge_type = DEPENDENCY_CONFIRMED if prev in id_set else DEPENDENCY_PROBABLE
            edges.append({
                "from": c["candidate_id"],
                "to": prev,
                "type": edge_type,
                "reason": "prev_entry_id_version_chain",
            })
            if edge_type == DEPENDENCY_PROBABLE:
                c["dependency_status"] = "DEPENDENCY_OUTSIDE_BATCH"
                c["unknowns"] = list(c.get("unknowns") or []) + ["dependency_outside_batch"]
            else:
                c["dependency_status"] = DEPENDENCY_CONFIRMED

    return edges


def detect_cycles(candidates: list[dict], edges: list[dict]) -> list[str]:
    """Détection simple de cycles dans le graphe de dépendances."""
    graph: dict[str, list[str]] = {c["candidate_id"]: [] for c in candidates}
    for e in edges:
        if e["from"] in graph:
            graph[e["from"]].append(e["to"])

    visited: set = set()
    in_stack: set = set()
    cycles: list[str] = []

    def dfs(node: str) -> None:
        if node in in_stack:
            cycles.append(node)
            return
        if node in visited:
            return
        visited.add(node)
        in_stack.add(node)
        for neighbor in graph.get(node, []):
            dfs(neighbor)
        in_stack.discard(node)

    for c in candidates:
        dfs(c["candidate_id"])

    return cycles


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

    # Étape 4 : dépendances
    edges = detect_dependencies(selected + hold_entries)

    # Étape 5 : cycles — retirer par référence originale, pas par copie
    cycle_nodes = detect_cycles(selected + hold_entries, edges)
    cycle_originals = [c for c in selected if c["candidate_id"] in cycle_nodes]
    for c_orig in cycle_originals:
        c_hold = dict(c_orig)
        c_hold["hold_reason"] = ["DEPENDENCY_CYCLE"]
        c_hold["dependency_status"] = DEPENDENCY_CYCLE
        hold_entries.append(c_hold)
        selected.remove(c_orig)

    # Étape 6 : coupe à max
    overflow: list[dict] = []
    if len(selected) > max_batch_size:
        overflow = selected[max_batch_size:]
        selected = selected[:max_batch_size]
        for c in overflow:
            c = dict(c)
            c["exclusion_reason"] = "EXCEEDS_MAX_BATCH_SIZE"
            excluded_entries.append(c)

    return {
        "selected": selected,
        "hold_entries": hold_entries,
        "excluded_entries": excluded_entries,
        "dependency_edges": edges,
        "cycle_nodes": cycle_nodes,
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
            if "dependency_outside_batch" in (c.get("unknowns") or [])
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
) -> dict:
    """
    Point d'entrée principal du Selector.
    Découvre les candidats, sélectionne, produit un BatchProposal immuable.
    """
    import time
    t0 = time.monotonic()

    if max_batch_size > HARD_MAX_BATCH_SIZE:
        max_batch_size = HARD_MAX_BATCH_SIZE

    candidates = build_candidates_from_ledger(ledger_dir, additional_candidates)
    sel_result = select_batch(candidates, max_batch_size, objective)

    selected   = sel_result["selected"]
    hold       = sel_result["hold_entries"]
    excluded   = sel_result["excluded_entries"]
    edges      = sel_result["dependency_edges"]
    cycles     = sel_result["cycle_nodes"]

    duration_ms = (time.monotonic() - t0) * 1000.0

    selected_ids   = [c["candidate_id"] for c in selected]
    source_hashes  = [c["source_hash"] for c in selected if c.get("source_hash")]

    bid  = batch_id_from_selection(selected_ids, objective, max_batch_size)
    bhash = batch_hash_from_proposal(selected_ids, source_hashes, edges, objective, max_batch_size)

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

        "status": status,
        "human_approved": False,
        "decision_authority": DECISION_AUTHORITY,

        "metrics": metrics,
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

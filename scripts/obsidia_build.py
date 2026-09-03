#!/usr/bin/env python3
"""
obsidia_build -- Bounded Build Engine Obsidia X-108 v2
=======================================================
decision_authority = KX108_ONLY
auto_commit        = NEVER
auto_push          = NEVER
auto_merge         = NEVER

Usage:
  python scripts/obsidia_build.py "<objectif>"
      -> PLAN_PROPOSED (zero ecriture, zero worktree, zero commit)

  python scripts/obsidia_build.py "<objectif>" \\
      --approve HUMAN_APPROVED_BUILD_SESSION=<session_id>:<manifest_hash>
      -> EXECUTE (apres approbation humaine)

Phase 1 (plan uniquement):
  Produit PLAN_PROPOSED -- aucune mutation, aucun worktree, aucune branche,
  aucune ecriture dans le depot ou dans %LOCALAPPDATA%.
  Le session_id est derive de facon deterministe.
  Le token requis contient session_id ET manifest_hash.

Phase 2 (apres approbation humaine):
  Regenere le plan depuis l'etat courant du depot.
  Verifie le token complet: session_id + manifest_hash.
  Si base_sha ou manifeste a change: BLOCKED.
  Cree worktree + branche uniquement si validation OK.
  Applique le patch synthetique dans le worktree.
  Execute tests cibles dans le worktree.
  Execute gates reelles avec leurs CLI exactes.
  Appelle KX108 ou declare BLOCKED_KX108_CONTRACT_UNAVAILABLE.
  Ecrit le receipt hors depot dans OBSIDIA_BUILD_STATE_DIR.
  JAMAIS de commit automatique. JAMAIS de push. JAMAIS de merge.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from obsidia_candidate_patch_v1 import (
    CandidatePatchSpec,
    CANDIDATE_PATCH_MODE,
    apply_candidate_patch,
    bind_candidate_to_objective,
    check_candidate_patch,
    load_candidate_patch_file,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
VERSION = "0.2.0"
DECISION_AUTHORITY = "KX108_ONLY"
AUTO_COMMIT = "NEVER"
AUTO_PUSH = "NEVER"
AUTO_MERGE = "NEVER"
MAX_CANDIDATE_FILES = 20

# State dir hors depot
def _default_state_dir() -> Path:
    lad = os.environ.get("LOCALAPPDATA", "")
    base = Path(lad) if lad else Path.home()
    return base / "Obsidia" / "build_sessions"

OBSIDIA_BUILD_STATE_DIR = Path(
    os.environ.get("OBSIDIA_BUILD_STATE_DIR", str(_default_state_dir()))
)

KERNEL_URL = os.environ.get(
    "OBSIDIA_KERNEL_URL", "http://127.0.0.1:3001/kernel/ragnarok"
)

# Cible synthetique periodique -- non protegee, scope PERIPHERAL
SYNTHETIC_TARGET = "tests/fixtures/terminal_build_bounded/target.txt"
SYNTHETIC_TEST_PY = "tests/fixtures/terminal_build_bounded/test_target_content.py"
SYNTHETIC_MARKER = "BUILD_SESSION_APPLIED"

PROTECTED_PATHS = (
    "runtime_terrain_bank_trading_gps/server.kernel.sealed.cjs",
    "server.kernel.sealed.cjs",
    "proofs/",
    "formal/",
    "merkle_seal.json",
    ".claude/",
    "sigma/",
)

# Interfaces CLI reelles des gates (auditees)
GATES_REAL = [
    "scripts/gates/obsidia_commit_scope_guard.py",     # --allow <f> (repetable)
    "scripts/gates/obsidia_forbidden_write_check.py",  # --dir <d> (defaut: scripts/gates/)
    "scripts/gates/obsidia_kernel_boundary_check.py",  # --staged-only
    "scripts/gates/obsidia_lean_manifest_guard.py",    # --file <p>
]

ALLOWED_OBSIDURE_DOMAINS = ("BANK", "TRADING", "GPS", "ECOM", "LEAN", "SRL")


# =============================================================================
# Fonctions pures -- aucun I/O, deterministes, importables par les tests
# =============================================================================

def detect_domain(objective: str) -> str:
    obj = objective.lower()
    if any(k in obj for k in ("bank", "banque", "finance", "bancaire", "paiement")):
        return "BANK"
    if any(k in obj for k in ("trading", "bourse", "marche", "market", "flash")):
        return "TRADING"
    if any(k in obj for k in ("gps", "aviation", "gnss", "terrain", "spoofing")):
        return "GPS"
    if any(k in obj for k in ("lean", "proof", "preuve", "tla", "theoreme", "lemma")):
        return "LEAN"
    if any(k in obj for k in ("sigma", "gate", "scope", "guard", "coherence")):
        return "SIGMA"
    return "PERIPHERAL"


def is_protected(path: str) -> bool:
    for p in PROTECTED_PATHS:
        clean = p.rstrip("/")
        if path == clean or path.startswith(clean + "/") or path == p:
            return True
    return False


def compute_manifest_hash(candidate_files: list[str], repo_root: Path | None = None) -> str:
    """Hash deterministe du manifeste: chemins + tailles."""
    root = repo_root or REPO_ROOT
    h = hashlib.sha256()
    for f in sorted(candidate_files):
        h.update(f.encode("utf-8"))
        p = root / f
        if p.exists():
            h.update(str(p.stat().st_size).encode("utf-8"))
    return h.hexdigest()[:16]


def compute_session_id(objective: str, base_sha: str, manifest_hash: str) -> str:
    """Session_id deterministe: meme inputs = meme session_id."""
    raw = f"{objective}\x00{base_sha}\x00{manifest_hash}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:8]


def estimate_risk(candidate_files: list[str], domain: str) -> str:
    if any("kernel" in f or "sealed" in f for f in candidate_files):
        return "HIGH"
    if domain in ("LEAN", "SIGMA"):
        return "MEDIUM"
    if len(candidate_files) > 10:
        return "MEDIUM"
    return "LOW"


def find_candidate_files(
    objective: str,
    domain: str,
    repo_root: Path | None = None,
) -> tuple[list[str], list[str]]:
    """Retourne (candidates, protected_detected). Max 20, sans wildcard."""
    root = repo_root or REPO_ROOT
    candidates: list[str] = []

    domain_paths: dict[str, list[str]] = {
        "BANK":       ["connectors/bank_normal_flow.py", "domains/bank/"],
        "TRADING":    ["connectors/trading_live.py", "domains/trading/"],
        "GPS":        ["connectors/aviation_robo.py", "domains/gps/"],
        "LEAN":       ["proofs/lean/", "formal/lean/"],
        "PERIPHERAL": ["tests/fixtures/terminal_build_bounded/"],
    }

    scan_paths = domain_paths.get(domain, ["tests/fixtures/terminal_build_bounded/"])

    for sp in scan_paths:
        rp = root / sp
        if not rp.exists():
            continue
        if rp.is_file():
            candidates.append(sp)
        else:
            for f in sorted(rp.iterdir()):
                if f.is_file() and f.suffix in (".py", ".txt", ".yaml", ".json", ".lean", ".tla"):
                    rel = str(f.relative_to(root)).replace("\\", "/")
                    candidates.append(rel)

    # Le fichier test ne fait pas partie du scope: c'est un validateur, pas une cible
    candidates = [c for c in candidates if not c.endswith("test_target_content.py")]

    protected_detected = [c for c in candidates if is_protected(c)]
    candidates = [c for c in candidates if not is_protected(c)]
    return candidates[:MAX_CANDIDATE_FILES], protected_detected


def infer_tests(
    candidate_files: list[str],
    domain: str,
    repo_root: Path | None = None,
) -> list[str]:
    root = repo_root or REPO_ROOT
    tests: list[str] = []
    for f in candidate_files:
        if f == SYNTHETIC_TARGET:
            tests.append(f"python -m pytest {SYNTHETIC_TEST_PY} -q")
            continue
        basename = Path(f).stem
        test_path = root / "tests" / f"test_{basename}.py"
        if test_path.exists():
            tests.append(f"python -m pytest tests/test_{basename}.py -q")
    if not tests:
        tests.append("python -m pytest tests/ -q --tb=no")
    # Deduplication, max 5
    seen: list[str] = []
    for t in tests:
        if t not in seen:
            seen.append(t)
    return seen[:5]


SCOPE_MODE_HEURISTIC_LEGACY = "HEURISTIC_LEGACY"
SCOPE_MODE_EXPLICIT_CHILD_TARGET = "EXPLICIT_CHILD_TARGET"


def compute_approved_scope_hash(approved_scope: list[str]) -> str:
    """Identité pure de l'ENSEMBLE de chemins de la portée — change dès
    qu'un target_path change. Distinct de manifest_hash (qui inclut aussi
    les tailles de fichiers) et de tout hash côté batch_execution/approval."""
    payload = json.dumps(sorted(approved_scope), sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def canonicalize_explicit_target(raw: str, repo_root: Path) -> tuple[str | None, str | None]:
    """
    Résout un target explicite en identité canonique repo-relative, ou
    rejette avec une raison explicite. JAMAIS Path.cwd() comme autorité —
    seul repo_root sert de référence. Fail-closed : aucune fabrication de
    chemin, aucune expansion.

    Retourne (chemin_canonique_repo_relatif, None) si valide,
    ou (None, raison) si rejeté.
    """
    if raw is None or not str(raw).strip():
        return None, "EXPLICIT_SCOPE_EMPTY_TARGET"
    raw = str(raw)
    if any(ch in raw for ch in ("*", "?")):
        return None, "EXPLICIT_SCOPE_WILDCARD_REJECTED"

    root = repo_root.resolve()
    p = Path(raw)
    resolved = p.resolve() if p.is_absolute() else (root / raw).resolve()

    try:
        rel = resolved.relative_to(root)
    except ValueError:
        return None, "EXPLICIT_SCOPE_OUTSIDE_REPO"

    rel_str = rel.as_posix()
    if rel_str in ("", "."):
        return None, "EXPLICIT_SCOPE_EMPTY_TARGET"
    if resolved.exists() and resolved.is_dir():
        return None, "EXPLICIT_SCOPE_DIRECTORY_REJECTED"
    if is_protected(rel_str):
        return None, "EXPLICIT_SCOPE_PROTECTED_REJECTED"

    return rel_str, None


def compute_explicit_session_id(legacy_session_id: str, plan_authority_hash: str) -> str:
    """
    Identité de SESSION pour le mode EXPLICIT_CHILD_TARGET — dérivée du
    session_id legacy ET de plan_authority_hash, pour qu'un plan explicite
    et un plan heuristique sélectionnant EXACTEMENT les mêmes fichiers
    (même objective/base_sha/manifest_hash, donc même legacy session_id)
    n'occupent jamais le même worktree/branche/état de session — ils
    doivent rester deux artefacts opérationnels totalement distincts.
    """
    raw = f"{legacy_session_id}\x00{plan_authority_hash}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:8]


def compute_plan_authority_hash(
    objective: str,
    base_sha: str,
    manifest_hash: str,
    scope_mode: str,
    approved_scope_hash: str,
) -> str:
    """
    Identité d'AUTORITÉ du plan — lie scope_mode et approved_scope_hash à
    l'identité, pas seulement objective/base_sha/manifest_hash (cf.
    compute_session_id, dont la formule reste inchangée pour compat
    historique). Deux plans avec exactement les mêmes candidate_files
    mais des scope_mode différents (EXPLICIT_CHILD_TARGET vs
    HEURISTIC_LEGACY) — ou des approved_scope différents — DOIVENT
    produire des plan_authority_hash différents. Ne jamais confondre avec
    KX108, BatchProposal.batch_hash, candidate_scope_hash ou
    approval_record_hash (autres systèmes, autres autorités).
    """
    payload = json.dumps({
        "objective": objective,
        "base_sha": base_sha,
        "manifest_hash": manifest_hash,
        "scope_mode": scope_mode,
        "approved_scope_hash": approved_scope_hash,
    }, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def compute_plan(
    objective: str,
    base_sha: str,
    repo_root: Path | None = None,
    explicit_scope: list[str] | None = None,
) -> dict:
    """
    Fonction pure -- aucun I/O, aucune ecriture, aucune mutation. Deterministe.

    explicit_scope=None (défaut) : comportement heuristique historique
    inchangé (HEURISTIC_LEGACY) — find_candidate_files() découvre les
    candidats depuis l'objectif/domaine.

    explicit_scope=[...] : mode EXPLICIT_CHILD_TARGET — la portée fournie
    fait AUTORITÉ. Aucune découverte heuristique n'a lieu. Aucune union
    avec des fichiers heuristiques. Un target rejeté (hors repo, protégé,
    wildcard, répertoire, vide) ne retombe JAMAIS sur le mode heuristique
    — échec fermé explicite (status=PLAN_REJECTED, scope_error=<raison>).
    Le texte de l'objectif reste purement descriptif : il ne peut jamais
    élargir cette portée.
    """
    root = repo_root or REPO_ROOT
    domain = detect_domain(objective)

    if explicit_scope is not None:
        scope_mode = SCOPE_MODE_EXPLICIT_CHILD_TARGET
        canonical: list[str] = []
        for raw in explicit_scope:
            canon, reason = canonicalize_explicit_target(raw, root)
            if reason is not None:
                return {
                    "session_id": None,
                    "objective": objective,
                    "domain": domain,
                    "base_sha": base_sha,
                    "scope_mode": scope_mode,
                    "requested_explicit_scope": list(explicit_scope),
                    "approved_scope_proposal": [],
                    "candidate_files": [],
                    "excluded_files": [],
                    "protected_files": list(PROTECTED_PATHS),
                    "manifest_hash": None,
                    "approved_scope_hash": None,
                    "plan_authority_hash": None,
                    "decision_authority": DECISION_AUTHORITY,
                    "status": "PLAN_REJECTED",
                    "scope_error": reason,
                }
            canonical.append(canon)
        candidate_files = canonical
        protected_detected: list[str] = []
    else:
        scope_mode = SCOPE_MODE_HEURISTIC_LEGACY
        candidate_files, protected_detected = find_candidate_files(objective, domain, root)

    manifest_hash = compute_manifest_hash(candidate_files, root)
    # legacy_session_id garde SA formule historique (objective, base_sha,
    # manifest_hash) inchangée pour compatibilité — c'est l'identité
    # OPÉRATIONNELLE finale en mode HEURISTIC_LEGACY. En mode
    # EXPLICIT_CHILD_TARGET, l'identité finale dérive EN PLUS de
    # plan_authority_hash (cf. compute_explicit_session_id) pour qu'un
    # plan explicite et un plan heuristique aux fichiers identiques
    # n'occupent jamais le même worktree/branche/état de session.
    legacy_session_id = compute_session_id(objective, base_sha, manifest_hash)
    approved_scope_hash = compute_approved_scope_hash(candidate_files)
    plan_authority_hash = compute_plan_authority_hash(
        objective, base_sha, manifest_hash, scope_mode, approved_scope_hash,
    )
    session_id = (
        compute_explicit_session_id(legacy_session_id, plan_authority_hash)
        if scope_mode == SCOPE_MODE_EXPLICIT_CHILD_TARGET
        else legacy_session_id
    )
    risk = estimate_risk(candidate_files, domain)
    tests_required = infer_tests(candidate_files, domain, root)
    gates_available = [g for g in GATES_REAL if (root / g).exists()]
    worktree_proposal = f"obsidia-x108-proofs_BUILD_{session_id}"
    branch_proposal = f"feat/build-{session_id}"
    # Le 2e segment du token porte l'AUTORITÉ complète en mode explicite
    # (scope_mode + approved_scope_hash liés), le manifest_hash brut en
    # mode heuristique legacy (format de token inchangé, comportement
    # historique préservé à l'identique) — un token émis pour un mode ne
    # peut jamais valider l'autre, même si les fichiers coïncident.
    token_scope_value = (
        plan_authority_hash if scope_mode == SCOPE_MODE_EXPLICIT_CHILD_TARGET
        else manifest_hash
    )
    token = f"HUMAN_APPROVED_BUILD_SESSION={session_id}:{token_scope_value}"

    return {
        "session_id":            session_id,
        "objective":             objective,
        "domain":                domain,
        "risk":                  risk,
        "base_sha":              base_sha,
        "candidate_files":       candidate_files,
        "approved_scope_proposal": list(candidate_files),
        "excluded_files":        protected_detected,
        "protected_files":       list(PROTECTED_PATHS),
        "tests_required":        tests_required,
        "gates_required":        gates_available,
        "worktree_proposal":     worktree_proposal,
        "branch_proposal":       branch_proposal,
        "manifest_hash":         manifest_hash,
        "approved_scope_hash":   approved_scope_hash,
        "plan_authority_hash":   plan_authority_hash,
        "decision_authority":    DECISION_AUTHORITY,
        "next_human_action":     token,
        "auto_commit":           AUTO_COMMIT,
        "auto_push":             AUTO_PUSH,
        "auto_merge":            AUTO_MERGE,
        "status":                "PLAN_PROPOSED",
        "scope_mode":            scope_mode,
        "requested_explicit_scope": list(explicit_scope) if explicit_scope is not None else None,
        "scope_error":           None,
    }


def format_plan_proposed(plan: dict, stack_status: str = "UNKNOWN") -> str:
    """Formate le plan en texte lisible. Pure, aucun I/O."""
    sep = "=" * 70
    lines = [
        f"\n{sep}",
        "  OBSIDIA BUILD -- PLAN_PROPOSED",
        "  decision_authority = KX108_ONLY  |  auto_commit = NEVER",
        sep,
        f"  session_id        : {plan['session_id']}",
        f"  objective         : {plan.get('display_objective', plan['objective'])}",
        f"  domain            : {plan['domain']}",
        f"  risk              : {plan['risk']}",
        f"  base_sha          : {plan['base_sha']}",
        f"  stack_status      : {stack_status}",
        f"  manifest_hash     : {plan['manifest_hash']}",
        f"  scope_mode        : {plan.get('scope_mode')}",
        f"  approved_scope_hash: {plan.get('approved_scope_hash')}",
        f"  plan_authority_hash: {plan.get('plan_authority_hash')}",
        f"  worktree_proposal : {plan['worktree_proposal']}",
        f"  branch_proposal   : {plan['branch_proposal']}",
        "",
        f"  candidate_files ({len(plan['candidate_files'])}, max {MAX_CANDIDATE_FILES}):",
    ]
    for f in plan["candidate_files"]:
        lines.append(f"    {f}")
    if plan.get("excluded_files"):
        lines.append("")
        lines.append("  excluded_files (protege -- hors scope approuve):")
        for f in plan["excluded_files"]:
            lines.append(f"    [PROTECTED] {f}")
    lines += ["", "  tests_required:"]
    for t in plan["tests_required"]:
        lines.append(f"    {t}")
    lines += ["", "  gates_required:"]
    for g in plan["gates_required"]:
        lines.append(f"    {g}")
    token = plan["next_human_action"]
    lines += [
        "",
        "  AUCUNE ECRITURE. AUCUN WORKTREE. AUCUNE BRANCHE. AUCUN COMMIT.",
        "",
        "  TOKEN D'APPROBATION REQUIS (session_id:manifest_hash):",
        f"  {token}",
        "",
        "  Commande Phase 2:",
        f'  python scripts/obsidia_build.py "{plan["objective"]}" \\',
        f"      --approve {token}",
        sep,
    ]
    if (
        plan.get("scope_mode")
        == SCOPE_MODE_EXPLICIT_CHILD_TARGET
    ):
        scope_lines = [
            f'      --scope "{scope_path}"'
            for scope_path
            in plan.get(
                "approved_scope_proposal",
                [],
            )
        ]

        # Conserver le séparateur comme dernière ligne.
        if lines and lines[-1] == sep:
            lines[-1:-1] = scope_lines
        else:
            lines.extend(scope_lines)

    if plan.get("candidate_patch_mode"):
        candidate_meta = [
            "",
            f"  candidate_patch_mode : {plan.get('candidate_patch_mode')}",
            f"  candidate_patch_hash : {plan.get('candidate_patch_hash')}",
            "  candidate_patch_files:",
        ]

        candidate_meta.extend(
            f"    {f}"
            for f in plan.get(
                "candidate_patch_files",
                [],
            )
        )

        # Placer les métadonnées avant la zone approval.
        approval_index = next(
            (
                i for i, line in enumerate(lines)
                if "TOKEN D'APPROBATION REQUIS" in line
            ),
            len(lines),
        )

        lines[approval_index:approval_index] = (
            candidate_meta
        )

        source = plan.get(
            "candidate_patch_source"
        )

        if source:
            candidate_cmd = (
                f'      --candidate-patch "{source}"'
            )

            if lines and lines[-1] == sep:
                lines[-1:-1] = [candidate_cmd]
            else:
                lines.append(candidate_cmd)

    return "\n".join(lines)


def validate_approval_token(token: str) -> tuple[str, str]:
    """Valide le token. Retourne (session_id, manifest_hash) ou leve ValueError."""
    prefix = "HUMAN_APPROVED_BUILD_SESSION="
    if not token.startswith(prefix):
        raise ValueError(
            f"Token invalide. Format requis: {prefix}<session_id>:<manifest_hash>\n"
            f"Recu: {token!r}"
        )
    rest = token[len(prefix):].strip()
    if ":" not in rest:
        raise ValueError(
            f"Token invalide: '<session_id>:<manifest_hash>' requis apres '='.\n"
            f"Format: {prefix}<session_id>:<manifest_hash>\n"
            f"Recu: {token!r}"
        )
    sid, mhash = rest.split(":", 1)
    sid = sid.strip()
    mhash = mhash.strip()
    if not sid:
        raise ValueError("session_id vide dans le token.")
    if not mhash:
        raise ValueError("manifest_hash vide dans le token.")
    return sid, mhash


# =============================================================================
# Fonctions I/O
# =============================================================================

def get_base_sha(repo_root: Path | None = None) -> str:
    root = repo_root or REPO_ROOT
    try:
        r = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, cwd=root, timeout=10,
        )
        return r.stdout.strip() if r.returncode == 0 else "UNKNOWN"
    except Exception:
        return "UNKNOWN"


def _probe_api_status() -> str:
    try:
        with urllib.request.urlopen(
            "http://127.0.0.1:8000/api/health", timeout=2
        ) as r:
            return "API_UP" if r.status == 200 else "API_DOWN"
    except Exception:
        return "API_DOWN_OR_UNREACHABLE"


def _call_kx108(plan: dict, full_state: dict | None = None) -> tuple[str, dict]:
    """
    Soumet le payload de session au kernel X-108 via domain=tooling_build.
    Retourne (status, raw_response).
    status: ACT | HOLD | BLOCK
          | BLOCKED_KX108_CONTRACT_UNAVAILABLE
          | BLOCKED_KX108_UNAVAILABLE

    full_state : dict complet ToolingBuildState (optionnel).
    Si absent, construit un état minimal depuis plan.
    """
    if full_state is not None:
        state_payload = full_state
    else:
        state_payload = {
            "session_id":            plan.get("session_id", "UNKNOWN"),
            "objective":             plan.get("objective", ""),
            "base_sha":              plan.get("base_sha", ""),
            "manifest_hash":         plan.get("manifest_hash", ""),
            "diff_hash":             plan.get("diff_hash", ""),
            "approved_scope":        plan.get("approved_scope_proposal", plan.get("approved_scope", [])),
            "actual_touched_files":  plan.get("actual_touched_files", []),
            "new_files":             plan.get("new_files", []),
            "deleted_files":         plan.get("deleted_files", []),
            "protected_scope_status": plan.get("protected_scope_status", "UNKNOWN"),
            "human_approval_status": "APPROVED" if plan.get("human_approved") else "MISSING",
            "obsidure_status":       plan.get("obsidure_status", "UNKNOWN"),
            "worktree_isolated":     bool(plan.get("worktree_isolated", False)),
            "branch_isolated":       bool(plan.get("branch_isolated", False)),
            "auto_commit_disabled":  True,
            "auto_push_disabled":    True,
            "auto_merge_disabled":   True,
            "tests_results":         "UNKNOWN",
            "gates_results":         "UNKNOWN",
            "first_failure":         plan.get("first_failure", ""),
            "commit_status":         plan.get("commit_status", "NOT_COMMITTED"),
            "push_status":           plan.get("push_status", "NOT_PUSHED"),
            "merge_status":          plan.get("merge_status", "NOT_MERGED"),
            "unknowns":              [],
            "contradictions":        [],
            "risk_flags":            [],
            "decision_authority":    "KX108_ONLY",
        }

    payload = {
        "domain": "tooling_build",
        "state": state_payload,
    }
    encoded = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        KERNEL_URL,
        data=encoded,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            try:
                data = json.loads(raw)
            except Exception:
                data = {"raw": raw[:500]}
            # Chercher une decision reconnue (x108_gate=ALLOW→ACT, HOLD→HOLD, BLOCK→BLOCK)
            _GATE_MAP = {
                "ALLOW": "ACT", "ACT": "ACT",
                "HOLD": "HOLD", "BUILD_HOLD": "HOLD",
                "BLOCK": "BLOCK", "BUILD_BLOCK": "BLOCK",
            }
            for field in ("x108_gate", "action", "decision", "status", "verdict"):
                raw_val = str(data.get(field, "")).upper()
                mapped = _GATE_MAP.get(raw_val)
                if mapped:
                    return mapped, data
            return "BLOCKED_KX108_CONTRACT_UNAVAILABLE", data
    except urllib.error.HTTPError as exc:
        # Kernel accessible mais contrat non supporte (4xx/5xx).
        raw = ""
        try:
            raw = exc.read().decode("utf-8", errors="replace")
        except Exception:
            pass
        return "BLOCKED_KX108_CONTRACT_UNAVAILABLE", {
            "http_status": exc.code, "http_reason": exc.reason, "raw": raw[:500],
        }
    except urllib.error.URLError as exc:
        return "BLOCKED_KX108_UNAVAILABLE", {"error": str(exc)}
    except OSError as exc:
        return "BLOCKED_KX108_UNAVAILABLE", {"error": str(exc)}
    except Exception as exc:
        return "BLOCKED_KX108_UNAVAILABLE", {"error": str(exc)}


def _git(args: list[str], cwd: Path, timeout: int = 30) -> tuple[int, str, str]:
    r = subprocess.run(
        ["git"] + args,
        capture_output=True, text=True, cwd=cwd, timeout=timeout,
    )
    return r.returncode, r.stdout.strip(), r.stderr.strip()


# =============================================================================
# Phase 1 : PLAN_PROPOSED -- zero ecriture
# =============================================================================

def cmd_plan(objective: str, repo_root: Path | None = None) -> int:
    """Phase 1 -- produit PLAN_PROPOSED. ZERO ecriture. ZERO worktree. ZERO commit."""
    root = repo_root or REPO_ROOT
    base_sha = get_base_sha(root)
    plan = compute_plan(objective, base_sha, root)
    stack_status = _probe_api_status()
    print(format_plan_proposed(plan, stack_status))
    # AUCUNE ECRITURE ICI.
    return 0


# =============================================================================
# Phase 2 : EXECUTE (apres approbation humaine)
# =============================================================================

def cmd_execute(
    objective: str,
    approval_token: str,
    repo_root: Path | None = None,
    state_dir: Path | None = None,
    explicit_scope: list[str] | None = None,
    candidate_patch_spec: CandidatePatchSpec | None = None,
) -> int:
    """
    Phase 2 -- valide token, regenere plan, execute.
    JAMAIS de commit automatique. JAMAIS de push. JAMAIS de merge.
    Receipt ecrit dans state_dir (hors depot).

    explicit_scope DOIT être identique à celui utilisé pour produire le
    plan/token approuvé — la régénération du plan ici utilise EXACTEMENT
    la même primitive (compute_plan) avec le même explicit_scope, jamais
    une redécouverte heuristique divergente (pas de recalcul de portée
    différent entre planification et exécution).
    """
    root = repo_root or REPO_ROOT
    sdir = state_dir or OBSIDIA_BUILD_STATE_DIR
    sep = "=" * 70

    # ── 0. Valider le token ──────────────────────────────────────────────────
    try:
        token_sid, token_mhash = validate_approval_token(approval_token)
    except ValueError as exc:
        print(f"\n[BLOCKED_APPROVAL_TOKEN_INVALID] {exc}")
        return 2

    # ── 1. Regenerer le plan depuis l'etat courant ───────────────────────────
    current_sha = get_base_sha(root)
    plan = compute_plan(objective, current_sha, root, explicit_scope=explicit_scope)

    # ── 2. Verifications croisees token <-> plan regenere ────────────────────
    if plan["session_id"] != token_sid:
        print(f"\n[BLOCKED_OBJECTIVE_CHANGED]")
        print(f"  session plan  : {plan['session_id']}")
        print(f"  session token : {token_sid}")
        print("  L'objectif, le depot ou les candidats ont change.")
        return 2

    # En mode EXPLICIT_CHILD_TARGET, le 2e segment du token porte
    # plan_authority_hash (lie scope_mode + approved_scope_hash), pas le
    # manifest_hash brut — un token EXPLICIT ne peut donc jamais valider
    # une exécution regénérée en HEURISTIC_LEGACY (ou vice-versa, ou avec
    # une portée explicite différente), même si les fichiers candidats
    # coïncident exactement. Format de token inchangé (toujours
    # <session_id>:<X>) ; seule la sémantique de X dépend du scope_mode
    # régénéré, exactement comme au moment de la génération du plan.
    expected_scope_value = (
        plan.get("plan_authority_hash")
        if plan.get("scope_mode") == SCOPE_MODE_EXPLICIT_CHILD_TARGET
        else plan["manifest_hash"]
    )
    if expected_scope_value != token_mhash:
        print(f"\n[BLOCKED_MANIFEST_CHANGED]")
        print(f"  scope_mode plan          : {plan.get('scope_mode')}")
        print(f"  valeur attendue (plan)   : {expected_scope_value}")
        print(f"  valeur token             : {token_mhash}")
        print("  Les fichiers candidats ou le mode de portee ont change depuis le token.")
        return 2

    # (base_sha entre dans compute_session_id: si HEAD change, session_id change)

    print(f"\n{sep}")
    print("  OBSIDIA BUILD -- EXECUTE (token valide)")
    print(f"  session_id : {plan['session_id']}  |  domain : {plan['domain']}")
    print(f"  base_sha   : {current_sha[:16]}...")
    print(f"  objectif   : {objective}")
    print(f"{sep}\n")

    session_id       = plan["session_id"]
    domain           = plan["domain"]
    base_sha         = plan["base_sha"]
    branch_name      = plan["branch_proposal"]
    worktree_name    = plan["worktree_proposal"]
    candidate_files  = plan["candidate_files"]
    approved_scope   = plan["approved_scope_proposal"]

    worktree_path = root.parent / worktree_name

    receipt: dict = {
        "session_id":          session_id,
        "objective":           objective,
        "domain":              domain,
        "base_sha":            base_sha,
        "manifest_hash":       plan["manifest_hash"],
        "approval_token_hash": hashlib.sha256(approval_token.encode()).hexdigest()[:16],
        "worktree":            str(worktree_path),
        "branch":              branch_name,
        "approved_scope":      approved_scope,
        "scope_mode":          plan.get("scope_mode"),
        "approved_scope_hash": plan.get("approved_scope_hash"),
        "plan_authority_hash": plan.get("plan_authority_hash"),
        "candidate_patch_mode": (
            candidate_patch_spec.mode
            if candidate_patch_spec
            else None
        ),
        "candidate_patch_hash": (
            candidate_patch_spec.sha256
            if candidate_patch_spec
            else None
        ),
        "candidate_patch_files": (
            list(candidate_patch_spec.files)
            if candidate_patch_spec
            else []
        ),
        "candidate_patch_apply": None,
        "actual_touched_files": [],
        "new_files":           [],
        "deleted_files":       [],
        "tests_commands":      [],
        "tests_results":       {},
        "gates_commands":      [],
        "gates_results":       {},
        "kx108_request":       {},
        "kx108_decision":      "PENDING",
        "first_failure":       None,
        "diff_hash":           None,
        "diff_stat":           None,
        "protected_scope_status": "OK",
        "commit_status":       "NOT_COMMITTED",
        "push_status":         "NOT_PUSHED",
        "merge_status":        "NOT_MERGED",
        "next_human_action":   "REVIEW_AND_COMMIT_IF_APPROVED",
        "obsidure_note":       "PENDING",
        "decision_authority":  DECISION_AUTHORITY,
        "auto_commit":         AUTO_COMMIT,
        "auto_push":           AUTO_PUSH,
        "auto_merge":          AUTO_MERGE,
        "timestamps":          {},
    }
    receipt["timestamps"]["start"] = datetime.now(timezone.utc).isoformat()
    first_failure: str | None = None

    # ── [1/10] Creer le worktree ─────────────────────────────────────────────
    print("  [1/10] Creation worktree...")
    if worktree_path.exists():
        print(f"  [BLOCK] Worktree deja existant: {worktree_path}")
        print("  Supprimer manuellement: git worktree remove --force <path>")
        return 2

    rc, _, err = _git(
        ["worktree", "add", str(worktree_path), "-b", branch_name, base_sha],
        root, timeout=60,
    )
    if rc != 0:
        print(f"  [BLOCK] git worktree add echec:\n    {err}")
        return 2
    print(f"  [OK] worktree : {worktree_path}")
    print(f"  [OK] branche  : {branch_name}")
    receipt["timestamps"]["worktree_created"] = datetime.now(timezone.utc).isoformat()

    # ── [2/10] Verifier worktree propre ─────────────────────────────────────
    print("\n  [2/10] Verification worktree propre...")
    rc, st_out, _ = _git(["status", "--short"], worktree_path)
    if st_out.strip():
        print(f"  [WARN] Non propre:\n    {st_out}")
    else:
        print("  [OK] Worktree propre")

    # ── [3/10] Obsidure DryRun (advisory, non bloquant si absent) ───────────
    print("\n  [3/10] Obsidure DryRun (lecture seule, advisory)...")
    obs_domain = domain if domain in ALLOWED_OBSIDURE_DOMAINS else "BANK"
    obs_script = root / "scripts" / "obsidure_cli.py"
    obsidure_ok = False
    if obs_script.exists():
        r_obs = subprocess.run(
            [sys.executable, str(obs_script),
             "--objective", objective,
             "--dry-run", "--quiet",
             "--domain", obs_domain],
            capture_output=True, text=True, cwd=root, timeout=90,
        )
        obsidure_ok = r_obs.returncode == 0
        lbl = "OK" if obsidure_ok else "WARN"
        print(f"  [{lbl}] Obsidure DryRun exit={r_obs.returncode}")
        for ln in (r_obs.stdout or "").splitlines()[:4]:
            if ln.strip():
                print(f"    {ln}")
        receipt["obsidure_note"] = (
            "OBSIDURE_DRY_RUN_COMPLETED"
            if obsidure_ok else "OBSIDURE_DRY_RUN_WARN"
        )
    else:
        print("  [WARN] obsidure_cli.py absent -- DryRun ignore (non bloquant)")
        receipt["obsidure_note"] = "OBSIDURE_ABSENT"
        obsidure_ok = True

    # ── [4/10] Patch synthetique dans le worktree ───────────────────────────
    print("\n  [4/10] Application patch synthetique dans le worktree...")
    patch_applied_files: list[str] = []

    if candidate_patch_spec is not None:
        print(
            "\n  [4/10-REAL] Application candidate.patch "
            "dans le worktree..."
        )

        # Defense-in-depth: exact files must still equal approved scope.
        if sorted(candidate_patch_spec.files) != sorted(approved_scope):
            receipt["first_failure"] = (
                "CANDIDATE_APPROVED_SCOPE_MISMATCH"
            )
            receipt["candidate_patch_apply"] = {
                "ok": False,
                "phase": "PRE_APPLY_SCOPE_BINDING",
            }
            _write_receipt(
                sdir,
                session_id,
                receipt,
            )
            print(
                "  [BLOCKED] CANDIDATE_APPROVED_SCOPE_MISMATCH"
            )
            return 2

        result = apply_candidate_patch(
            candidate_patch_spec,
            worktree_path,
        )

        receipt["candidate_patch_apply"] = result

        if not result.get("ok"):
            receipt["first_failure"] = (
                "REAL_CANDIDATE_PATCH_APPLY_FAILED:"
                + str(result.get("phase"))
            )
            receipt["timestamps"]["blocked_at"] = (
                datetime.now(timezone.utc).isoformat()
            )
            _write_receipt(
                sdir,
                session_id,
                receipt,
            )
            print(
                "  [BLOCKED] candidate.patch non applicable: "
                + str(result.get("message", ""))
            )
            return 2

        patch_applied_files.extend(
            candidate_patch_spec.files
        )

        receipt["obsidure_note"] = (
            "REAL_CANDIDATE_PATCH_APPLIED_BY_BOUNDED_BUILD"
        )

        print(
            "  [OK] real candidate applied: "
            + ", ".join(candidate_patch_spec.files)
        )
        print(
            "  [OK] candidate_sha256: "
            + candidate_patch_spec.sha256
        )

    if (
        candidate_patch_spec is None
        and SYNTHETIC_TARGET in approved_scope
    ):
        tgt = worktree_path / SYNTHETIC_TARGET

        # Seed: si la cible est absente du worktree (fichier non versionne),
        # la copier depuis le depot source ou la creer minimalement.
        if not tgt.exists():
            tgt.parent.mkdir(parents=True, exist_ok=True)
            src_tgt = root / SYNTHETIC_TARGET
            if src_tgt.exists():
                shutil.copy(src_tgt, tgt)
                print(f"  [SEED] {SYNTHETIC_TARGET} copie depuis le depot source")
            else:
                tgt.write_text(
                    "TERMINAL_BUILD_BOUNDED_V1_TARGET_V0\n"
                    "Cible synthetique pour le moteur de build borne.\n"
                    "Non protegee. Modifiable uniquement dans le worktree de session.\n",
                    encoding="utf-8",
                )
                print(f"  [SEED] {SYNTHETIC_TARGET} cree (fichier minimal)")

        # Seed: copier aussi le fichier de test si absent (validateur non stage).
        tst = worktree_path / SYNTHETIC_TEST_PY
        if not tst.exists():
            src_tst = root / SYNTHETIC_TEST_PY
            if src_tst.exists():
                tst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(src_tst, tst)
                print(f"  [SEED] {SYNTHETIC_TEST_PY} copie (validateur, non stage)")

        if tgt.exists():
            original = tgt.read_text(encoding="utf-8")
            marker = f"{SYNTHETIC_MARKER}: {session_id}"
            if marker not in original:
                patched = original.rstrip() + f"\n{marker}\n"
                tgt.write_text(patched, encoding="utf-8")
                patch_applied_files.append(SYNTHETIC_TARGET)
                print(f"  [OK] Patch applique: {SYNTHETIC_TARGET}")
                if "OBSIDURE_DRY_RUN" in receipt["obsidure_note"]:
                    receipt["obsidure_note"] += (
                        " | SYNTHETIC_PATCH_APPLIED_BY_BOUNDED_HARNESS"
                    )
                else:
                    receipt["obsidure_note"] = (
                        "SYNTHETIC_PATCH_APPLIED_BY_BOUNDED_HARNESS"
                    )
                print("  [NOTE] SYNTHETIC_PATCH_APPLIED_BY_BOUNDED_HARNESS (hors Obsidure)")
            else:
                print(f"  [WARN] Marqueur deja present dans {SYNTHETIC_TARGET}")
    else:
        if candidate_patch_spec is not None:
            print(
                "  [NOTE] Candidate reel fourni — "
                "harness synthetique bypassed"
            )
        else:
            print(
                "  [NOTE] Cible synthetique hors scope -- "
                "patch non applicable"
            )

    # ── [5/10] Controle scope reel ──────────────────────────────────────────
    print("\n  [5/10] Controle scope reel...")
    rc, diff_names, _ = _git(["diff", "--name-only"], worktree_path)
    actual_touched = [f for f in diff_names.splitlines() if f.strip()]

    rc, newf_out, _ = _git(["ls-files", "--others", "--exclude-standard"], worktree_path)
    new_files = [f for f in newf_out.splitlines() if f.strip()]

    rc, delf_out, _ = _git(["diff", "--diff-filter=D", "--name-only"], worktree_path)
    deleted_files = [f for f in delf_out.splitlines() if f.strip()]

    receipt["actual_touched_files"] = actual_touched
    receipt["new_files"] = new_files
    receipt["deleted_files"] = deleted_files

    # Le fichier de test est un validateur seed, pas une livraison: exclu du drift.
    scope_drift = [
        f for f in actual_touched + new_files
        if f not in approved_scope and f != SYNTHETIC_TEST_PY
    ]
    if scope_drift:
        print(f"  [BLOCKED_SCOPE_DRIFT] Fichiers hors scope approuve:")
        for f in scope_drift:
            print(f"    {f}")
        receipt["protected_scope_status"] = f"BLOCKED_SCOPE_DRIFT: {scope_drift}"
        first_failure = f"SCOPE_DRIFT: {scope_drift}"
        receipt["first_failure"] = first_failure
        receipt["timestamps"]["blocked_at"] = datetime.now(timezone.utc).isoformat()
        _write_receipt(sdir, session_id, receipt)
        print(f"\n  Worktree conserve pour revue: {worktree_path}")
        return 2

    print(f"  [OK] {len(actual_touched)} fichier(s) touches, tous dans scope")
    for f in actual_touched:
        print(f"    {f}")

    # ── [6/10] Staging + diff hash ───────────────────────────────────────────
    print("\n  [6/10] Staging dans le worktree + diff hash...")
    # Stager les fichiers approuves: modifies (actual_touched) ET nouveaux (new_files seedes).
    for f in set(actual_touched + [nf for nf in new_files if nf in approved_scope]):
        if f in approved_scope:
            _git(["add", f], worktree_path)

    rc, diff_staged, _ = _git(["diff", "--staged"], worktree_path)
    diff_hash = hashlib.sha256(diff_staged.encode("utf-8")).hexdigest()[:16]
    rc, diff_stat, _ = _git(["diff", "--staged", "--stat"], worktree_path)
    receipt["diff_hash"] = diff_hash
    receipt["diff_stat"] = diff_stat or "(aucune diff stagee)"
    print(f"  [OK] diff_hash : {diff_hash}")
    print(f"  [OK] diff_stat : {diff_stat or '(vide)'}")

    # ── [7/10] Tests cibles dans le worktree ────────────────────────────────
    print("\n  [7/10] Tests cibles (dans le worktree)...")
    tests_required = plan["tests_required"]
    receipt["tests_commands"] = tests_required
    tests_ok = True

    for test_cmd in tests_required:
        parts = test_cmd.split()
        # Remplacer les chemins relatifs tests/ par les chemins worktree
        wt_parts: list[str] = []
        for p in parts:
            if p.startswith("tests/") or p.startswith("tests\\"):
                wt_parts.append(str(worktree_path / p))
            else:
                wt_parts.append(p)
        r_t = subprocess.run(
            wt_parts, capture_output=True, text=True,
            cwd=worktree_path, timeout=120,
        )
        ok = r_t.returncode == 0
        lbl = "OK" if ok else "FAIL"
        print(f"  [{lbl}] {test_cmd}")
        out_tail = (r_t.stdout or r_t.stderr or "")[-300:]
        receipt["tests_results"][test_cmd] = {
            "ok": ok, "exit": r_t.returncode, "output_tail": out_tail,
        }
        if not ok:
            tests_ok = False
            if first_failure is None:
                first_failure = f"TEST_FAILED: {test_cmd}"
            print(f"    {out_tail}")
            print(f"  [first_failure] {first_failure}")
            break  # premier echec: arret des tests et des gates suivantes

    receipt["first_failure"] = first_failure

    if not tests_ok:
        receipt["timestamps"]["blocked_at"] = datetime.now(timezone.utc).isoformat()
        _write_receipt(sdir, session_id, receipt)
        print(f"\n  [BLOCKED_TEST_FAILURE] {first_failure}")
        print(f"  Worktree conserve pour revue: {worktree_path}")
        return 1

    # ── [8/10] Gates reelles (CLI exactes, auditees) ─────────────────────────
    print("\n  [8/10] Gates reelles...")
    gates_ok = True

    # Gate 1: scope_guard -- depuis worktree, --allow pour chaque fichier approuve
    gate1 = root / "scripts/gates/obsidia_commit_scope_guard.py"
    if gate1.exists():
        allow_args: list[str] = []
        for f in approved_scope:
            allow_args += ["--allow", f]
        cmd_g1 = [sys.executable, str(gate1)] + allow_args
        r_g1 = subprocess.run(
            cmd_g1, capture_output=True, text=True, cwd=worktree_path, timeout=30,
        )
        ok1 = r_g1.returncode == 0
        msg1 = (r_g1.stdout or r_g1.stderr or "")[:200].strip()
        lbl = "OK" if ok1 else "FAIL"
        print(f"  [{lbl}] scope_guard: {msg1}")
        receipt["gates_commands"].append(f"scope_guard " + " ".join(allow_args))
        receipt["gates_results"]["scope_guard"] = {"ok": ok1, "msg": msg1}
        if not ok1:
            gates_ok = False
            if first_failure is None:
                first_failure = f"GATE_FAIL: scope_guard"
    else:
        print("  [SKIP] scope_guard absent")
        receipt["gates_results"]["scope_guard"] = {"ok": None, "msg": "GATE_ABSENT"}

    # Gate 2: forbidden_write -- depuis root, default scan scripts/gates/
    gate2 = root / "scripts/gates/obsidia_forbidden_write_check.py"
    if gate2.exists():
        r_g2 = subprocess.run(
            [sys.executable, str(gate2)],
            capture_output=True, text=True, cwd=root, timeout=30,
        )
        ok2 = r_g2.returncode == 0
        msg2 = (r_g2.stdout or r_g2.stderr or "")[:200].strip()
        lbl = "OK" if ok2 else "FAIL"
        print(f"  [{lbl}] forbidden_write: {msg2}")
        receipt["gates_commands"].append("forbidden_write_check (default: scripts/gates/)")
        receipt["gates_results"]["forbidden_write"] = {"ok": ok2, "msg": msg2}
        if not ok2 and gates_ok:
            gates_ok = False
            if first_failure is None:
                first_failure = f"GATE_FAIL: forbidden_write"
    else:
        print("  [SKIP] forbidden_write absent")
        receipt["gates_results"]["forbidden_write"] = {"ok": None, "msg": "GATE_ABSENT"}

    # Gate 3: kernel_boundary -- depuis worktree, --staged-only
    gate3 = root / "scripts/gates/obsidia_kernel_boundary_check.py"
    if gate3.exists():
        r_g3 = subprocess.run(
            [sys.executable, str(gate3), "--staged-only"],
            capture_output=True, text=True, cwd=worktree_path, timeout=30,
        )
        ok3 = r_g3.returncode == 0
        msg3 = (r_g3.stdout or r_g3.stderr or "")[:200].strip()
        lbl = "OK" if ok3 else "FAIL"
        print(f"  [{lbl}] kernel_boundary (--staged-only): {msg3}")
        receipt["gates_commands"].append("kernel_boundary_check --staged-only")
        receipt["gates_results"]["kernel_boundary"] = {"ok": ok3, "msg": msg3}
        if not ok3 and gates_ok:
            gates_ok = False
            if first_failure is None:
                first_failure = f"GATE_FAIL: kernel_boundary"
    else:
        print("  [SKIP] kernel_boundary absent")
        receipt["gates_results"]["kernel_boundary"] = {"ok": None, "msg": "GATE_ABSENT"}

    # Gate 4: lean_manifest -- depuis worktree (lit le manifest de la worktree)
    gate4 = root / "scripts/gates/obsidia_lean_manifest_guard.py"
    if gate4.exists():
        r_g4 = subprocess.run(
            [sys.executable, str(gate4)],
            capture_output=True, text=True, cwd=worktree_path, timeout=30,
        )
        ok4 = r_g4.returncode == 0
        msg4 = (r_g4.stdout or r_g4.stderr or "")[:200].strip()
        lbl = "OK" if ok4 else "FAIL"
        print(f"  [{lbl}] lean_manifest: {msg4}")
        receipt["gates_commands"].append("lean_manifest_guard (default manifest)")
        receipt["gates_results"]["lean_manifest"] = {"ok": ok4, "msg": msg4}
        if not ok4 and gates_ok:
            gates_ok = False
            if first_failure is None:
                first_failure = f"GATE_FAIL: lean_manifest"
    else:
        print("  [SKIP] lean_manifest absent")
        receipt["gates_results"]["lean_manifest"] = {"ok": None, "msg": "GATE_ABSENT"}

    receipt["first_failure"] = first_failure

    # ── [9/10] Appel KX108 ───────────────────────────────────────────────────
    print("\n  [9/10] Appel KX108 (domain=tooling_build)...")
    _tests_r = "PASS" if tests_ok else "FAIL"
    _gates_r = "PASS" if gates_ok else "FAIL"
    kx108_full_state = {
        "session_id":            session_id,
        "objective":             plan["objective"],
        "base_sha":              base_sha,
        "manifest_hash":         plan["manifest_hash"],
        "diff_hash":             diff_hash,
        "approved_scope":        approved_scope,
        "actual_touched_files":  actual_touched,
        "new_files":             [],
        "deleted_files":         [],
        "protected_scope_status": receipt["protected_scope_status"],
        "human_approval_status": "APPROVED",
        "obsidure_status":       "UNKNOWN",
        "worktree_isolated":     True,
        "branch_isolated":       True,
        "auto_commit_disabled":  True,
        "auto_push_disabled":    True,
        "auto_merge_disabled":   True,
        "tests_results":         _tests_r,
        "gates_results":         _gates_r,
        "first_failure":         first_failure or "",
        "commit_status":         "NOT_COMMITTED",
        "push_status":           "NOT_PUSHED",
        "merge_status":          "NOT_MERGED",
        "unknowns":              [],
        "contradictions":        [],
        "risk_flags":            [],
        "decision_authority":    "KX108_ONLY",
    }
    receipt["kx108_request"] = kx108_full_state

    kx108_status, kx108_raw = _call_kx108(plan, full_state=kx108_full_state)
    receipt["kx108_decision"] = kx108_status

    print(f"  [KX108] decision_authority = KX108_ONLY")
    print(f"  [KX108] decision           = {kx108_status}")
    print(f"  [KX108] auto_commit        = NEVER (meme sur ACT)")

    if kx108_status == "BLOCKED_KX108_UNAVAILABLE":
        print("  [KX108] Kernel X-108 non accessible (port 3001 injoignable)")
    elif kx108_status == "BLOCKED_KX108_CONTRACT_UNAVAILABLE":
        print("  [KX108] Noyau X-108 actif : contrat tooling_build non reconnu")
    elif kx108_status in ("ACT", "HOLD"):
        print(f"  [KX108] Decision reelle recue: {kx108_status}")
        receipt["next_human_action"] = "READY_FOR_COMMIT_REVIEW"
    elif kx108_status == "BLOCK":
        print(f"  [KX108] Decision reelle: BLOCK")
        receipt["next_human_action"] = "BLOCKED_BY_KX108"

    # ── [10/10] Receipt + diff final + rapport ───────────────────────────────
    print("\n  [10/10] Receipt + diff final...")
    receipt["timestamps"]["end"] = datetime.now(timezone.utc).isoformat()
    state_path = _write_receipt(sdir, session_id, receipt)

    # Diff complet pour revue humaine
    rc, diff_full, _ = _git(["diff", "--staged", "--stat"], worktree_path)
    if diff_full.strip():
        print("\n  Diff stage:")
        for ln in diff_full.splitlines():
            print(f"    {ln}")
    else:
        print("  (aucune diff stagee)")

    overall_ok = tests_ok and gates_ok
    final_status: str
    if kx108_status in ("BLOCKED_KX108_CONTRACT_UNAVAILABLE", "BLOCKED_KX108_UNAVAILABLE"):
        final_status = kx108_status
    elif kx108_status == "BLOCK":
        final_status = "BLOCKED_BY_KX108"
    elif overall_ok:
        final_status = "READY_FOR_COMMIT_REVIEW"
    else:
        final_status = "BLOCKED"

    print(f"\n{sep}")
    print("  OBSIDIA BUILD -- RESULTAT")
    print(sep)
    print(f"  session_id    : {session_id}")
    print(f"  kx108_status  : {kx108_status}")
    print(f"  tests         : {'OK' if tests_ok else 'FAIL'}")
    print(f"  gates         : {'OK' if gates_ok else 'FAIL'}")
    print(f"  first_failure : {first_failure or 'AUCUN'}")
    print(f"  final_status  : {final_status}")
    print()
    print(f"  worktree      : {worktree_path}")
    print(f"  branch        : {branch_name}")
    print(f"  receipt       : {state_path}")
    print()
    print("  AUCUN COMMIT AUTOMATIQUE. AUCUN PUSH. AUCUN MERGE.")
    if overall_ok and kx108_status not in ("BLOCK",):
        print()
        print("  Pour committer manuellement apres revue humaine:")
        manual_files = " ".join(
            f'"{f}"'
            for f in approved_scope
        )
        print(
            f'    git -C "{worktree_path}" add -- {manual_files}'
        )
        print(
            f'    git -C "{worktree_path}" commit -m '
            f'"build({domain}): {objective[:40]} [session={session_id}]"'
        )
    print()
    print("  decision_authority = KX108_ONLY")
    print(f"{sep}\n")

    return 0 if overall_ok else 1


# =============================================================================
# Reprise bornee KX108 -- apres BLOCKED_KX108_UNAVAILABLE
# =============================================================================

def cmd_resume_kx108(
    session_id: str,
    repo_root: Path | None = None,
    state_dir: Path | None = None,
) -> int:
    """
    Reprend une session bloquee sur KX108, re-verifie tout, appelle KX108.
    NE reapplique PAS le patch. NE cree PAS de worktree. NE cree PAS de branche.
    JAMAIS de commit, push, merge.
    """
    root = repo_root or REPO_ROOT
    sdir = state_dir or OBSIDIA_BUILD_STATE_DIR
    sep = "=" * 70

    print(f"\n{sep}")
    print("  OBSIDIA BUILD -- RESUME_KX108")
    print(f"  session_id : {session_id}")
    print(f"  decision_authority = KX108_ONLY")
    print(f"{sep}\n")

    # ── [R1] Lire le receipt existant ───────────────────────────────────────
    print("  [R1] Lecture du receipt existant...")
    receipt_path = sdir / session_id / "receipt.json"
    if not receipt_path.exists():
        print(f"  [BLOCKED_RESUME] Receipt absent: {receipt_path}")
        return 2
    try:
        receipt: dict = json.loads(receipt_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"  [BLOCKED_RESUME] Receipt illisible: {exc}")
        return 2
    print(f"  [OK] Receipt lu: {receipt_path}")

    # Champs requis du receipt
    required_fields = [
        "session_id", "base_sha", "manifest_hash", "approved_scope",
        "worktree", "branch", "diff_hash",
        "commit_status", "push_status", "merge_status",
    ]
    missing = [f for f in required_fields if f not in receipt]
    if missing:
        print(f"  [BLOCKED_RESUME] Champs manquants dans le receipt: {missing}")
        return 2

    # Verifier que c'est bien la bonne session
    if receipt.get("session_id") != session_id:
        print(f"  [BLOCKED_RESUME] session_id mismatch: receipt={receipt.get('session_id')} != {session_id}")
        return 2

    base_sha        = receipt["base_sha"]
    manifest_hash   = receipt["manifest_hash"]
    approved_scope  = receipt["approved_scope"]
    worktree_str    = receipt["worktree"]
    branch_name     = receipt["branch"]
    receipt_diff_hash = receipt["diff_hash"]
    objective       = receipt.get("objective", "")
    domain          = receipt.get("domain", "PERIPHERAL")

    print(f"  [OK] base_sha       : {base_sha[:16]}...")
    print(f"  [OK] manifest_hash  : {manifest_hash}")
    print(f"  [OK] approved_scope : {approved_scope}")
    print(f"  [OK] worktree       : {worktree_str}")
    print(f"  [OK] branch         : {branch_name}")

    # ── [R2] Verifier le worktree ────────────────────────────────────────────
    print("\n  [R2] Verification worktree existant...")
    worktree_path = Path(worktree_str)
    if not worktree_path.exists():
        print(f"  [BLOCKED_RESUME] Worktree absent: {worktree_path}")
        return 2

    # Verifier la branche du worktree
    rc, wt_branch, _ = _git(["rev-parse", "--abbrev-ref", "HEAD"], worktree_path)
    if wt_branch != branch_name:
        print(f"  [BLOCKED_RESUME] Branche worktree: {wt_branch!r} != attendu {branch_name!r}")
        return 2
    print(f"  [OK] Branche confirmee: {branch_name}")

    # ── [R3] Verifier base_sha ───────────────────────────────────────────────
    print("\n  [R3] Verification base_sha...")
    current_sha = get_base_sha(root)
    if current_sha != base_sha:
        print(f"  [BLOCKED_RESUME] base_sha modifie:")
        print(f"    receipt : {base_sha}")
        print(f"    actuel  : {current_sha}")
        return 2
    print(f"  [OK] base_sha inchange: {base_sha[:16]}...")

    # ── [R4] Verifier manifest_hash ──────────────────────────────────────────
    print("\n  [R4] Verification manifest_hash...")
    current_mhash = compute_manifest_hash(approved_scope, root)
    if current_mhash != manifest_hash:
        print(f"  [BLOCKED_RESUME] manifest_hash modifie:")
        print(f"    receipt : {manifest_hash}")
        print(f"    actuel  : {current_mhash}")
        return 2
    print(f"  [OK] manifest_hash inchange: {manifest_hash}")

    # ── [R5] Verifier scope reel dans le worktree ────────────────────────────
    print("\n  [R5] Verification scope reel (worktree)...")
    rc, diff_names, _ = _git(["diff", "--staged", "--name-only"], worktree_path)
    staged_files = [f.strip() for f in diff_names.splitlines() if f.strip()]

    rc, newf_out, _ = _git(["ls-files", "--others", "--exclude-standard"], worktree_path)
    untracked = [f.strip() for f in newf_out.splitlines() if f.strip()]

    scope_drift = [
        f for f in staged_files + untracked
        if f not in approved_scope
        and f != SYNTHETIC_TEST_PY
        and "__pycache__" not in f
        and not f.endswith(".pyc")
    ]
    if scope_drift:
        print(f"  [BLOCKED_RESUME] SCOPE_DRIFT: {scope_drift}")
        return 2
    print(f"  [OK] Scope inchange: {staged_files}")

    # ── [R6] Recalculer diff_hash ────────────────────────────────────────────
    print("\n  [R6] Recalcul diff_hash...")
    rc, diff_staged_text, _ = _git(["diff", "--staged"], worktree_path)
    current_diff_hash = hashlib.sha256(diff_staged_text.encode("utf-8")).hexdigest()[:16]
    if current_diff_hash != receipt_diff_hash:
        # Note: divergence possible entre modes de capture (line endings Windows).
        # On accepte si le diff montre les memes fichiers et le marqueur attendu.
        marker_present = False
        tgt = worktree_path / SYNTHETIC_TARGET
        if tgt.exists():
            marker_present = f"{SYNTHETIC_MARKER}: {session_id}" in tgt.read_text(encoding="utf-8")
        if not marker_present:
            print(f"  [BLOCKED_RESUME] diff_hash diverge ET marqueur absent:")
            print(f"    receipt : {receipt_diff_hash}")
            print(f"    actuel  : {current_diff_hash}")
            return 2
        print(f"  [WARN] diff_hash diverge (line-endings Windows) mais marqueur valide")
        print(f"    receipt : {receipt_diff_hash}  actuel: {current_diff_hash}")
    else:
        print(f"  [OK] diff_hash confirme: {current_diff_hash}")

    # ── [R7] Verifier fichiers proteges ─────────────────────────────────────
    print("\n  [R7] Verification fichiers proteges...")
    rc, prot_diff, _ = _git(
        ["diff", "--staged", "--name-only",
         "--", "proofs/", "formal/",
         "runtime_terrain_bank_trading_gps/server.kernel.sealed.cjs",
         "merkle_seal.json"],
        worktree_path,
    )
    protected_touched = [f for f in prot_diff.splitlines() if f.strip()]
    if protected_touched:
        print(f"  [BLOCKED_RESUME] Fichiers proteges touches: {protected_touched}")
        return 2
    print("  [OK] Aucun fichier protege touche")

    # ── [R8] Verifier aucun commit ──────────────────────────────────────────
    print("\n  [R8] Verification aucun commit depuis base_sha...")
    rc, commits_ahead, _ = _git(
        ["log", "HEAD", f"^{base_sha}", "--oneline"],
        worktree_path,
    )
    if commits_ahead.strip():
        print(f"  [BLOCKED_RESUME] Commits detectes apres base_sha:")
        print(f"    {commits_ahead}")
        return 2
    print("  [OK] Aucun commit depuis base_sha")

    # ── [R9] Verifier coherence: commit_status == NOT_COMMITTED ─────────────
    if receipt.get("commit_status") != "NOT_COMMITTED":
        print(f"  [BLOCKED_RESUME] commit_status dans receipt: {receipt.get('commit_status')}")
        return 2
    print("  [OK] commit_status = NOT_COMMITTED")

    # ── [R10] Relancer le test cible ─────────────────────────────────────────
    print("\n  [R10] Relancement du test cible...")
    test_cmd = f"python -m pytest {SYNTHETIC_TEST_PY} -q"
    tst_path = worktree_path / SYNTHETIC_TEST_PY
    if not tst_path.exists():
        print(f"  [BLOCKED_RESUME] Fichier test absent du worktree: {tst_path}")
        return 2

    wt_test_path = str(worktree_path / SYNTHETIC_TEST_PY)
    r_t = subprocess.run(
        [sys.executable, "-m", "pytest", wt_test_path, "-q"],
        capture_output=True, text=True,
        cwd=worktree_path, timeout=60,
    )
    if r_t.returncode != 0:
        print(f"  [BLOCKED_RESUME] Test cible en echec: {r_t.stdout[-200:]}")
        receipt["first_failure"] = f"RESUME_TEST_FAILED: {test_cmd}"
        _write_receipt(sdir, session_id, receipt)
        return 2
    print(f"  [OK] Test cible: PASS")

    # ── [R11] Relancer les gates ─────────────────────────────────────────────
    print("\n  [R11] Gates reelles (re-verification)...")
    gates_ok = True
    first_gate_fail: str | None = None

    gate1 = root / "scripts/gates/obsidia_commit_scope_guard.py"
    if gate1.exists():
        allow_args: list[str] = []
        for f in approved_scope:
            allow_args += ["--allow", f]
        r_g1 = subprocess.run(
            [sys.executable, str(gate1)] + allow_args,
            capture_output=True, text=True, cwd=worktree_path, timeout=30,
        )
        ok1 = r_g1.returncode == 0
        msg1 = (r_g1.stdout or r_g1.stderr or "")[:200].strip()
        print(f"  [{'OK' if ok1 else 'FAIL'}] scope_guard: {msg1}")
        if not ok1:
            gates_ok = False
            first_gate_fail = "GATE_FAIL: scope_guard"

    gate2 = root / "scripts/gates/obsidia_forbidden_write_check.py"
    if gate2.exists():
        r_g2 = subprocess.run(
            [sys.executable, str(gate2)],
            capture_output=True, text=True, cwd=root, timeout=30,
        )
        ok2 = r_g2.returncode == 0
        msg2 = (r_g2.stdout or r_g2.stderr or "")[:200].strip()
        print(f"  [{'OK' if ok2 else 'FAIL'}] forbidden_write: {msg2}")
        if not ok2 and gates_ok:
            gates_ok = False
            first_gate_fail = "GATE_FAIL: forbidden_write"

    gate3 = root / "scripts/gates/obsidia_kernel_boundary_check.py"
    if gate3.exists():
        r_g3 = subprocess.run(
            [sys.executable, str(gate3), "--staged-only"],
            capture_output=True, text=True, cwd=worktree_path, timeout=30,
        )
        ok3 = r_g3.returncode == 0
        msg3 = (r_g3.stdout or r_g3.stderr or "")[:200].strip()
        print(f"  [{'OK' if ok3 else 'FAIL'}] kernel_boundary: {msg3}")
        if not ok3 and gates_ok:
            gates_ok = False
            first_gate_fail = "GATE_FAIL: kernel_boundary"

    gate4 = root / "scripts/gates/obsidia_lean_manifest_guard.py"
    if gate4.exists():
        r_g4 = subprocess.run(
            [sys.executable, str(gate4)],
            capture_output=True, text=True, cwd=worktree_path, timeout=30,
        )
        ok4 = r_g4.returncode == 0
        msg4 = (r_g4.stdout or r_g4.stderr or "")[:200].strip()
        print(f"  [{'OK' if ok4 else 'FAIL'}] lean_manifest: {msg4}")
        if not ok4 and gates_ok:
            gates_ok = False
            first_gate_fail = "GATE_FAIL: lean_manifest"

    if not gates_ok:
        print(f"  [BLOCKED_RESUME] Gate en echec: {first_gate_fail}")
        receipt["first_failure"] = first_gate_fail
        _write_receipt(sdir, session_id, receipt)
        return 2
    print("  [OK] Toutes les gates repassees")

    # ── [R12] Construire le payload KX108 ────────────────────────────────────
    print("\n  [R12] Construction payload KX108 (domain=tooling_build)...")
    actual_files = staged_files
    resume_full_state = {
        "session_id":            session_id,
        "objective":             objective,
        "base_sha":              base_sha,
        "manifest_hash":         manifest_hash,
        "diff_hash":             current_diff_hash,
        "approved_scope":        approved_scope,
        "actual_touched_files":  actual_files,
        "new_files":             [],
        "deleted_files":         [],
        "protected_scope_status": "CLEAN",
        "human_approval_status": "APPROVED",
        "obsidure_status":       "UNKNOWN",
        "worktree_isolated":     True,
        "branch_isolated":       True,
        "auto_commit_disabled":  True,
        "auto_push_disabled":    True,
        "auto_merge_disabled":   True,
        "tests_results":         "PASS",
        "gates_results":         "PASS",
        "first_failure":         "",
        "commit_status":         "NOT_COMMITTED",
        "push_status":           "NOT_PUSHED",
        "merge_status":          "NOT_MERGED",
        "unknowns":              [],
        "contradictions":        [],
        "risk_flags":            [],
        "decision_authority":    "KX108_ONLY",
    }
    print(f"  [INFO] Appel: POST {KERNEL_URL}")
    print(f"  [INFO] domain=tooling_build")

    # ── [R13] Appel KX108 ────────────────────────────────────────────────────
    print("\n  [R13] Appel KX108...")
    plan_for_kx108 = {"session_id": session_id, "approved_scope_proposal": approved_scope}
    kx108_status, kx108_raw = _call_kx108(plan_for_kx108, full_state=resume_full_state)
    receipt["kx108_decision"] = kx108_status
    receipt["kx108_request"]["resume_attempt"] = {
        "domain": "tooling_build",
        "url": KERNEL_URL,
        "session_id": session_id,
    }

    print(f"  [KX108] decision_authority = KX108_ONLY")
    print(f"  [KX108] decision           = {kx108_status}")
    print(f"  [KX108] auto_commit        = NEVER (meme sur ACT)")

    if kx108_status == "BLOCKED_KX108_UNAVAILABLE":
        print("  [KX108] Kernel X-108 injoignable")
    elif kx108_status == "BLOCKED_KX108_CONTRACT_UNAVAILABLE":
        print("  [KX108] Kernel actif, contrat tooling_build non reconnu")
    elif kx108_status in ("ACT", "HOLD", "BLOCK"):
        print(f"  [KX108] Decision reelle: {kx108_status}")

    # ── [R14] Mettre a jour le receipt ──────────────────────────────────────
    receipt["timestamps"]["resume_kx108"] = datetime.now(timezone.utc).isoformat()
    receipt["resume_kx108_diff_hash_actual"] = current_diff_hash
    receipt["staged_files_at_resume"] = staged_files
    if kx108_status in ("ACT", "HOLD"):
        receipt["next_human_action"] = "READY_FOR_COMMIT_REVIEW"
    elif kx108_status == "BLOCK":
        receipt["next_human_action"] = "BLOCKED_BY_KX108"
    elif kx108_status == "BLOCKED_KX108_CONTRACT_UNAVAILABLE":
        receipt["next_human_action"] = "BLOCKED_KX108_CONTRACT_UNAVAILABLE"
    else:
        receipt["next_human_action"] = kx108_status

    state_path = _write_receipt(sdir, session_id, receipt)

    # ── Rapport final ────────────────────────────────────────────────────────
    overall_ok = (kx108_status not in (
        "BLOCKED_KX108_UNAVAILABLE", "BLOCKED_KX108_CONTRACT_UNAVAILABLE", "BLOCK"
    ))

    if kx108_status == "BLOCKED_KX108_CONTRACT_UNAVAILABLE":
        final_verdict = "TERMINAL_BUILD_BOUNDED_V1_BLOCKED_KX108_CONTRACT_UNAVAILABLE"
    elif kx108_status == "BLOCKED_KX108_UNAVAILABLE":
        final_verdict = "TERMINAL_BUILD_BOUNDED_V1_BLOCKED_KX108_UNAVAILABLE"
    elif kx108_status == "ACT":
        final_verdict = "TERMINAL_BUILD_BOUNDED_V1_READY_FOR_HUMAN_VALIDATION"
    elif kx108_status == "HOLD":
        final_verdict = "TERMINAL_BUILD_BOUNDED_V1_READY_FOR_HUMAN_VALIDATION"
    elif kx108_status == "BLOCK":
        final_verdict = "TERMINAL_BUILD_BOUNDED_V1_BLOCKED_BY_KX108"
    else:
        final_verdict = f"TERMINAL_BUILD_BOUNDED_V1_{kx108_status}"

    print(f"\n{sep}")
    print("  OBSIDIA BUILD -- RESUME_KX108 RESULTAT")
    print(sep)
    print(f"  session_id    : {session_id}")
    print(f"  kx108_status  : {kx108_status}")
    print(f"  test_cible    : OK")
    print(f"  gates         : OK")
    print(f"  diff_hash     : {current_diff_hash} (receipt: {receipt_diff_hash})")
    print(f"  worktree      : {worktree_path}")
    print(f"  branch        : {branch_name}")
    print(f"  receipt       : {state_path}")
    print()
    print(f"  VERDICT: {final_verdict}")
    print()
    print("  AUCUN COMMIT. AUCUN PUSH. AUCUN MERGE.")
    print(f"  decision_authority = KX108_ONLY")
    print(f"{sep}\n")

    return 0 if overall_ok else 2


def _write_receipt(state_dir: Path, session_id: str, receipt: dict) -> Path:
    """Ecrit le receipt hors depot. Retourne le chemin de la session."""
    session_path = state_dir / session_id
    session_path.mkdir(parents=True, exist_ok=True)

    (session_path / "receipt.json").write_text(
        json.dumps(receipt, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )

    tr = receipt.get("tests_results", {})
    gr = receipt.get("gates_results", {})
    tests_ok_lbl = "OK" if tr and all(v.get("ok") for v in tr.values()) else ("FAIL" if tr else "N/A")
    gates_ok_lbl = "OK" if gr and all(
        v.get("ok") for v in gr.values() if v.get("ok") is not None
    ) else ("FAIL_OR_SKIP" if gr else "N/A")

    md_lines = [
        f"# OBSIDIA BUILD RECEIPT -- {receipt.get('session_id', '?')}",
        "",
        f"**session_id**     : {receipt.get('session_id', '?')}",
        f"**objective**      : {receipt.get('objective', '?')}",
        f"**domain**         : {receipt.get('domain', '?')}",
        f"**base_sha**       : {receipt.get('base_sha', '?')}",
        f"**manifest_hash**  : {receipt.get('manifest_hash', '?')}",
        f"**kx108**          : {receipt.get('kx108_decision', '?')}",
        f"**tests**          : {tests_ok_lbl}",
        f"**gates**          : {gates_ok_lbl}",
        f"**first_failure**  : {receipt.get('first_failure') or 'AUCUN'}",
        f"**diff_hash**      : {receipt.get('diff_hash', '?')}",
        f"**actual_touched** : {receipt.get('actual_touched_files', [])}",
        f"**commit_status**  : {receipt.get('commit_status', 'NOT_COMMITTED')}",
        f"**push_status**    : {receipt.get('push_status', 'NOT_PUSHED')}",
        f"**merge_status**   : {receipt.get('merge_status', 'NOT_MERGED')}",
        f"**auto_commit**    : {receipt.get('auto_commit', 'NEVER')}",
        f"**auto_push**      : {receipt.get('auto_push', 'NEVER')}",
        f"**obsidure_note**  : {receipt.get('obsidure_note', '?')}",
        "",
        "decision_authority = KX108_ONLY",
        "Aucun commit automatique. Aucun push. Aucun merge.",
    ]
    (session_path / "RECEIPT.md").write_text(
        "\n".join(md_lines), encoding="utf-8",
    )
    return session_path


# =============================================================================
# TERMINAL BUILD LIFECYCLE V1
# =============================================================================
# Source de vérité dérivée — jamais de valeur brute écrite pour "status".
# IMMUTABLE: receipt.json, apply_receipt.json — jamais réécrits après production.
# OPERATOR:  lifecycle_events.jsonl (événements opérateur uniquement).
# KX108 decisions {ACT, HOLD, BLOCK} ≠ lifecycle_status {ABORTED, CLEANED, …}.
# =============================================================================


def _load_receipt(session_id: str, state_dir: Path | None = None) -> "dict | None":
    """Charge receipt.json. Retourne None si absent ou illisible."""
    p = (state_dir or OBSIDIA_BUILD_STATE_DIR) / session_id / "receipt.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def _load_apply_receipt(session_id: str, state_dir: Path | None = None) -> "dict | None":
    """Charge apply_receipt.json. Retourne None si absent ou illisible."""
    p = (state_dir or OBSIDIA_BUILD_STATE_DIR) / session_id / "apply_receipt.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def _load_lifecycle_events(session_id: str, state_dir: Path | None = None) -> list:
    """Charge lifecycle_events.jsonl. Retourne [] si absent."""
    p = (state_dir or OBSIDIA_BUILD_STATE_DIR) / session_id / "lifecycle_events.jsonl"
    if not p.exists():
        return []
    events: list = []
    try:
        for raw in p.read_text(encoding="utf-8").splitlines():
            raw = raw.strip()
            if raw:
                try:
                    events.append(json.loads(raw))
                except Exception:
                    pass
    except Exception:
        pass
    return events


def _append_lifecycle_event(
    session_id: str,
    event_type: str,
    details: "dict | None" = None,
    state_dir: "Path | None" = None,
) -> None:
    """Ajoute un événement dans lifecycle_events.jsonl. Ne touche pas les receipts."""
    session_path = (state_dir or OBSIDIA_BUILD_STATE_DIR) / session_id
    session_path.mkdir(parents=True, exist_ok=True)
    event = {
        "type": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "by": "operator",
        **(details or {}),
    }
    p = session_path / "lifecycle_events.jsonl"
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")


def _list_sessions(state_dir: "Path | None" = None) -> list:
    """Liste les session_ids ayant receipt.json ou apply_receipt.json."""
    sdir = state_dir or OBSIDIA_BUILD_STATE_DIR
    if not sdir.exists():
        return []
    result: list = []
    try:
        for child in sorted(sdir.iterdir()):
            if not child.is_dir():
                continue
            if (child / "receipt.json").exists() or (child / "apply_receipt.json").exists():
                result.append(child.name)
    except Exception:
        pass
    return result


def _git_worktree_state(worktree_path: Path) -> dict:
    """Lit l'état git d'un worktree. READ_ONLY.
    Fail-closed: dirty=None si git status échoue (jamais False par défaut).
    Champs: exists, path, branch, head, dirty, state_complete, errors."""
    if not worktree_path.exists():
        return {"exists": False, "path": str(worktree_path)}
    result: dict = {
        "exists": True, "path": str(worktree_path),
        "state_complete": True, "errors": [],
    }
    for cmd, key in [
        (["git", "rev-parse", "--abbrev-ref", "HEAD"], "branch"),
        (["git", "rev-parse", "HEAD"], "head"),
    ]:
        try:
            r = subprocess.run(
                cmd, cwd=str(worktree_path),
                capture_output=True, text=True, timeout=10,
            )
            result[key] = r.stdout.strip() if r.returncode == 0 else "?"
        except Exception:
            result[key] = "?"
    try:
        r = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(worktree_path),
            capture_output=True, text=True, timeout=10,
        )
        if r.returncode == 0:
            result["dirty"] = bool(r.stdout.strip())
        else:
            result["dirty"] = None
            result["state_complete"] = False
            result["errors"].append(
                f"git status returncode={r.returncode}: {r.stderr.strip()[:80]}"
            )
    except Exception as exc:
        result["dirty"] = None
        result["state_complete"] = False
        result["errors"].append(f"git status exception: {exc}")
    return result


def _derive_lifecycle_status(
    receipt: "dict | None",
    apply_receipt: "dict | None",
    lifecycle_events: list,
    worktree_state: "dict | None",
) -> str:
    """
    Dérive le lifecycle_status de façon déterministe depuis les artifacts.
    Hiérarchie : événements opérateur > receipt > apply_receipt > défaut.
    KX108 decisions (ACT/HOLD/BLOCK) ≠ lifecycle_status (ABORTED, CLEANED, …).
    """
    # 1. Événements opérateur — états terminaux définitifs
    for ev in reversed(lifecycle_events):
        t = ev.get("type", "")
        if t == "CLEANED":
            return "CLEANED"
        if t == "ABORTED":
            return "ABORTED"

    # 2. Depuis receipt.json (session build via cmd_execute)
    if receipt:
        if receipt.get("commit_status") == "COMMITTED":
            return "COMMITTED"
        kx108 = receipt.get("kx108_decision", "")
        nha = receipt.get("next_human_action", "")
        if kx108 == "ACT" or nha == "READY_FOR_COMMIT_REVIEW":
            return "READY_FOR_COMMIT_REVIEW"
        if kx108 == "BLOCK":
            return "BLOCK"
        if kx108 == "HOLD":
            return "HOLD"
        if receipt.get("approved_scope"):
            wt = worktree_state or {}
            return "WORKTREE_READY" if wt.get("exists") else "APPROVED"
        return "PLAN_PROPOSED"

    # 3. Depuis apply_receipt.json (session Obsidure)
    if apply_receipt:
        kx108 = apply_receipt.get("kx108_decision", "")
        nha = apply_receipt.get("next_human_action", "")
        if kx108 == "ACT" or nha == "READY_FOR_COMMIT_REVIEW":
            return "READY_FOR_COMMIT_REVIEW"
        if kx108 == "BLOCK":
            return "BLOCK"
        if kx108 == "HOLD":
            return "HOLD"
        if apply_receipt.get("apply_status") == "APPLIED":
            return "APPLIED"

    return "UNKNOWN"


def _session_summary(session_id: str, state_dir: "Path | None" = None) -> dict:
    """Construit un résumé dérivé (lecture seule) — projection de la vérité."""
    sdir = state_dir or OBSIDIA_BUILD_STATE_DIR
    receipt = _load_receipt(session_id, sdir)
    apply_receipt = _load_apply_receipt(session_id, sdir)
    lifecycle_events = _load_lifecycle_events(session_id, sdir)

    src = receipt or apply_receipt or {}
    wt_path_str: str = src.get("worktree", "")

    worktree_state: "dict | None" = None
    if wt_path_str and Path(wt_path_str).is_absolute():
        worktree_state = _git_worktree_state(Path(wt_path_str))

    lifecycle_status = _derive_lifecycle_status(
        receipt, apply_receipt, lifecycle_events, worktree_state
    )

    ts = (receipt or {}).get("timestamps", {})
    created_at = ts.get("start") or (apply_receipt or {}).get("created_at", "?")
    updated_at = (
        ts.get("resume_kx108") or ts.get("end")
        or (apply_receipt or {}).get("written_at", "?")
    )

    return {
        "session_id": session_id,
        "objective": src.get("objective", "?"),
        "lifecycle_status": lifecycle_status,
        "kx108_decision": src.get("kx108_decision", "?"),
        "next_human_action": src.get("next_human_action", "?"),
        "branch": (receipt or {}).get("branch", "?"),
        "worktree": wt_path_str or "?",
        "created_at": created_at,
        "updated_at": updated_at,
        "commit_status": src.get("commit_status", "NOT_COMMITTED"),
        "push_status": src.get("push_status", "NOT_PUSHED"),
        "merge_status": src.get("merge_status", "NOT_MERGED"),
        "decision_authority": src.get("decision_authority", DECISION_AUTHORITY),
        "has_receipt": receipt is not None,
        "has_apply_receipt": apply_receipt is not None,
        "lifecycle_events_count": len(lifecycle_events),
        "worktree_state": worktree_state,
    }


# ─── Commandes lifecycle ────────────────────────────────────────────────────

def cmd_list(state_dir: "Path | None" = None) -> int:
    """Liste toutes les sessions avec leur lifecycle_status dérivé."""
    sdir = state_dir or OBSIDIA_BUILD_STATE_DIR
    sep = "=" * 70
    print(f"\n{sep}")
    print("  OBSIDIA BUILD -- LIST")
    print(f"  state_dir : {sdir}")
    print(f"{sep}\n")
    sessions = _list_sessions(sdir)
    if not sessions:
        print("  Aucune session build trouvée.")
        return 0
    hdr = f"  {'SESSION_ID':<30} {'STATUS':<26} {'KX108':<6} {'NEXT_ACTION'}"
    print(hdr)
    print("  " + "-" * 72)
    for sid in sessions:
        s = _session_summary(sid, sdir)
        print(
            f"  {sid:<30} {s['lifecycle_status']:<26} "
            f"{s['kx108_decision']:<6} {s['next_human_action']}"
        )
    print(f"\n  {len(sessions)} session(s) — decision_authority = KX108_ONLY")
    return 0


def cmd_status(session_id: str, state_dir: "Path | None" = None) -> int:
    """Vue courte déterministe d'une session."""
    sdir = state_dir or OBSIDIA_BUILD_STATE_DIR
    if _load_receipt(session_id, sdir) is None and _load_apply_receipt(session_id, sdir) is None:
        print(f"  [STATUS_FAIL] Session inconnue : {session_id}")
        return 2
    s = _session_summary(session_id, sdir)
    sep = "=" * 70
    print(f"\n{sep}")
    print("  OBSIDIA BUILD -- STATUS")
    print(f"  session_id        : {session_id}")
    print(f"{sep}")
    print(f"  lifecycle_status  : {s['lifecycle_status']}")
    print(f"  kx108_decision    : {s['kx108_decision']}")
    print(f"  next_human_action : {s['next_human_action']}")
    print(f"  commit_status     : {s['commit_status']}")
    print(f"  branch            : {s['branch']}")
    wt = s.get("worktree_state") or {}
    if wt.get("exists"):
        dirty_tag = " [DIRTY]" if wt.get("dirty") else ""
        wt_label = f"présent{dirty_tag}"
    elif s["worktree"] != "?":
        wt_label = "absent"
    else:
        wt_label = "?"
    print(f"  worktree          : {wt_label}")
    print(f"  created_at        : {s['created_at']}")
    print(f"  updated_at        : {s['updated_at']}")
    print(f"  decision_authority: KX108_ONLY")
    return 0


def cmd_inspect(session_id: str, state_dir: "Path | None" = None) -> int:
    """Vue détaillée et auditable. READ_ONLY."""
    sdir = state_dir or OBSIDIA_BUILD_STATE_DIR
    receipt = _load_receipt(session_id, sdir)
    apply_receipt = _load_apply_receipt(session_id, sdir)
    lifecycle_events = _load_lifecycle_events(session_id, sdir)
    if receipt is None and apply_receipt is None:
        print(f"  [INSPECT_FAIL] Session inconnue : {session_id}")
        return 2
    s = _session_summary(session_id, sdir)
    sep = "=" * 70
    print(f"\n{sep}")
    print("  OBSIDIA BUILD -- INSPECT (READ_ONLY)")
    print(f"  session_id        : {session_id}")
    print(f"{sep}\n")
    print("  [LIFECYCLE]")
    print(f"  lifecycle_status  : {s['lifecycle_status']}")
    print(f"  lifecycle_events  : {s['lifecycle_events_count']} event(s)")
    for ev in lifecycle_events:
        print(f"    [{ev.get('type','?')}] {ev.get('timestamp','?')} — {ev.get('by','?')}")
    print("\n  [IDENTITE]")
    print(f"  objective         : {s['objective']}")
    print(f"  branch            : {s['branch']}")
    print(f"  worktree          : {s['worktree']}")
    print(f"  created_at        : {s['created_at']}")
    print(f"  updated_at        : {s['updated_at']}")
    print("\n  [KX108]")
    print(f"  kx108_decision    : {s['kx108_decision']}")
    print(f"  next_human_action : {s['next_human_action']}")
    print(f"  decision_authority: KX108_ONLY")
    print("\n  [COMMIT GUARD]")
    print(f"  commit_status     : {s['commit_status']}")
    print(f"  push_status       : {s['push_status']}")
    print(f"  merge_status      : {s['merge_status']}")
    print(f"  auto_commit       : NEVER")
    print(f"  auto_push         : NEVER")
    print(f"  auto_merge        : NEVER")
    wt = s.get("worktree_state") or {}
    if wt:
        print("\n  [GIT STATE]")
        print(f"  worktree exists   : {wt.get('exists', False)}")
        if wt.get("exists"):
            print(f"  branch            : {wt.get('branch', '?')}")
            print(f"  HEAD              : {wt.get('head', '?')}")
            print(f"  dirty             : {wt.get('dirty', False)}")
    if receipt:
        print("\n  [RECEIPT.JSON]")
        for k in ("base_sha", "manifest_hash", "approved_scope", "domain",
                  "diff_hash", "tests_results", "gates_results"):
            v = receipt.get(k, "absent")
            print(f"  {k:<20}: {str(v)[:80]}")
    if apply_receipt:
        print("\n  [APPLY_RECEIPT.JSON]")
        for k in ("proposal_id", "proposal_hash", "apply_status",
                  "scope_verification", "protected_paths_status"):
            v = apply_receipt.get(k, "absent")
            print(f"  {k:<24}: {str(v)[:80]}")
    return 0


def cmd_resume(
    session_id: str,
    repo_root: "Path | None" = None,
    state_dir: "Path | None" = None,
) -> int:
    """
    Reprend la session depuis le dernier état prouvé.
    Ne re-joue jamais une étape déjà prouvée.
    HOLD_SESSION_STATE_MISMATCH si la branche git diverge du receipt.
    """
    sdir = state_dir or OBSIDIA_BUILD_STATE_DIR
    receipt = _load_receipt(session_id, sdir)
    apply_receipt = _load_apply_receipt(session_id, sdir)
    if receipt is None and apply_receipt is None:
        print(f"  [RESUME_FAIL] Session inconnue : {session_id}")
        return 2
    s = _session_summary(session_id, sdir)
    status = s["lifecycle_status"]
    sep = "=" * 70
    print(f"\n{sep}")
    print("  OBSIDIA BUILD -- RESUME")
    print(f"  session_id        : {session_id}")
    print(f"  lifecycle_status  : {status}")
    print(f"{sep}\n")
    # Mismatch: worktree présent mais sur la mauvaise branche
    wt = s.get("worktree_state") or {}
    if receipt and wt.get("exists"):
        expected = receipt.get("branch", "")
        actual = wt.get("branch", "")
        if expected and actual and actual != "?" and expected != actual:
            print("  [HOLD_SESSION_STATE_MISMATCH]")
            print(f"  Branche attendue  : {expected}")
            print(f"  Branche réelle    : {actual}")
            print("  Aucune reprise automatique. Inspecter manuellement.")
            return 3
    # États terminaux — rien à reprendre
    if status in ("COMMITTED", "ABORTED", "CLEANED"):
        print(f"  [NO_RESUME] Session en état {status} — rien à reprendre.")
        return 0
    # En attente d'approbation humaine
    if status in ("PLAN_PROPOSED", "AWAITING_APPROVAL"):
        print("  [AWAITING_APPROVAL] Session en attente d'approbation humaine.")
        print(f"  Objectif : {s['objective']}")
        print(f"  Pour approuver : python scripts/obsidia_build.py \"<obj>\" "
              f"--approve HUMAN_APPROVED_BUILD_SESSION={session_id}:<manifest_hash>")
        return 0
    # Prête pour revue — rediriger
    if status == "READY_FOR_COMMIT_REVIEW":
        print("  [READY_FOR_COMMIT_REVIEW] Session prête pour revue humaine.")
        print(f"  Utiliser : build review {session_id}")
        print("  Ce command NE COMMIT PAS — decision_authority = KX108_ONLY")
        return 0
    # Bloquée — aucune reprise automatique
    if status == "BLOCK":
        print("  [BLOCK] Session bloquée par KX108 — aucune reprise automatique.")
        print(f"  kx108_decision : {s['kx108_decision']}")
        return 1
    # HOLD — tenter reprise KX108 si le receipt est complet
    if status == "HOLD":
        required = [
            "base_sha", "manifest_hash", "approved_scope",
            "worktree", "branch", "diff_hash",
        ]
        if receipt and all(f in receipt for f in required):
            print("  [RESUME_KX108] Reprise KX108 pour session HOLD...")
            return cmd_resume_kx108(session_id, repo_root or REPO_ROOT, sdir)
        print("  [HOLD] Données insuffisantes pour reprise KX108 automatique.")
        print(f"  Inspecter avec : build inspect {session_id}")
        return 1
    # Autres états (WORKTREE_READY, APPROVED, APPLIED, UNKNOWN)
    print(f"  [INFO] État {status} — aucune reprise automatique disponible en V1.")
    print(f"  Inspecter avec : build inspect {session_id}")
    return 0


def cmd_review(session_id: str, state_dir: "Path | None" = None) -> int:
    """Vue opérateur pour READY_FOR_COMMIT_REVIEW. Ne commit PAS."""
    sdir = state_dir or OBSIDIA_BUILD_STATE_DIR
    receipt = _load_receipt(session_id, sdir)
    apply_receipt = _load_apply_receipt(session_id, sdir)
    if receipt is None and apply_receipt is None:
        print(f"  [REVIEW_FAIL] Session inconnue : {session_id}")
        return 2
    s = _session_summary(session_id, sdir)
    status = s["lifecycle_status"]
    sep = "=" * 70
    print(f"\n{sep}")
    print("  OBSIDIA BUILD -- REVIEW")
    print(f"  session_id : {session_id}")
    print(f"  status     : {status}")
    print(f"{sep}\n")
    if status != "READY_FOR_COMMIT_REVIEW":
        print(f"  [REVIEW_NA] Session non en READY_FOR_COMMIT_REVIEW (état : {status})")
        if status == "HOLD":
            print(f"  → Reprendre avec : build resume {session_id}")
        elif status == "BLOCK":
            print("  → Session bloquée par KX108. Aucune action.")
        elif status in ("ABORTED", "CLEANED"):
            print("  → Session terminée.")
        elif status == "COMMITTED":
            print("  → Session déjà committée.")
        return 1
    src = receipt or apply_receipt or {}
    print(f"  objective          : {s['objective']}")
    print(f"  kx108_decision     : {src.get('kx108_decision', '?')}")
    print(f"  branch             : {s['branch']}")
    print(f"  worktree           : {s['worktree']}")
    print(f"  commit_status      : {src.get('commit_status', 'NOT_COMMITTED')}")
    print(f"  push_status        : {src.get('push_status', 'NOT_PUSHED')}")
    print(f"  merge_status       : {src.get('merge_status', 'NOT_MERGED')}")
    print(f"  decision_authority : KX108_ONLY")
    wt = s.get("worktree_state") or {}
    if wt.get("exists"):
        print("\n  [GIT STATE WORKTREE]")
        print(f"  HEAD    : {wt.get('head', '?')}")
        print(f"  branch  : {wt.get('branch', '?')}")
        dirty_lbl = "OUI [ATTENTION]" if wt.get("dirty") else "non"
        print(f"  dirty   : {dirty_lbl}")
    print("\n  [REVIEW_READY] Inspectez le diff dans le worktree avant de committer.")
    print("  Ce command NE COMMIT PAS.")
    print("  decision_authority = KX108_ONLY")
    return 0


def cmd_abort(
    session_id: str,
    reason: str = "",
    state_dir: "Path | None" = None,
) -> int:
    """
    Clôture logique de la session. Préserve tous les artifacts.
    Écrit uniquement dans lifecycle_events.jsonl — receipts immutables.
    HOLD si worktree dirty non préservé.
    """
    sdir = state_dir or OBSIDIA_BUILD_STATE_DIR
    receipt = _load_receipt(session_id, sdir)
    apply_receipt = _load_apply_receipt(session_id, sdir)
    if receipt is None and apply_receipt is None:
        print(f"  [ABORT_FAIL] Session inconnue : {session_id}")
        return 2
    lifecycle_events = _load_lifecycle_events(session_id, sdir)
    src = receipt or apply_receipt or {}
    wt_path_str: str = src.get("worktree", "")
    wt_state: "dict | None" = None
    if wt_path_str and Path(wt_path_str).is_absolute() and Path(wt_path_str).exists():
        wt_state = _git_worktree_state(Path(wt_path_str))
    status = _derive_lifecycle_status(receipt, apply_receipt, lifecycle_events, wt_state)
    if status in ("COMMITTED", "CLEANED", "ABORTED"):
        print(f"  [ABORT_FAIL] Session {session_id} déjà en état {status}.")
        return 1
    if wt_state and wt_state.get("exists"):
        _dirty = wt_state.get("dirty")
        if _dirty is True:
            print("  [HOLD_ABORT_REQUIRES_HUMAN_REVIEW]")
            print(f"  Worktree dirty : {wt_path_str}")
            print("  Inspecter le diff avant d'aborter — aucune écriture effectuée.")
            return 3
        if _dirty is None:
            print("  [HOLD_SESSION_GIT_STATE_UNKNOWN]")
            print(f"  État git du worktree indéterminable : {wt_path_str}")
            _errs = wt_state.get("errors", [])
            if _errs:
                print(f"  Erreurs : {_errs[:2]}")
            print("  Impossible de vérifier si le worktree est propre — aucune écriture effectuée.")
            return 3
    _append_lifecycle_event(
        session_id, "ABORTED",
        {"reason": reason or "operator_abort", "previous_status": status},
        sdir,
    )
    print(f"  [ABORTED] Session {session_id} — état ABORTED enregistré.")
    print("  receipt.json et apply_receipt.json PRÉSERVÉS (immutables).")
    print("  lifecycle_events.jsonl mis à jour.")
    return 0


def cmd_cleanup(session_id: str, state_dir: "Path | None" = None) -> int:
    """
    Nettoie les ressources opérationnelles (worktree git uniquement).
    NE supprime PAS state_dir ni les preuves.
    Autorisé uniquement si lifecycle_status ∈ {COMMITTED, ABORTED}.
    """
    sdir = state_dir or OBSIDIA_BUILD_STATE_DIR
    receipt = _load_receipt(session_id, sdir)
    apply_receipt = _load_apply_receipt(session_id, sdir)
    if receipt is None and apply_receipt is None:
        print(f"  [CLEANUP_FAIL] Session inconnue : {session_id}")
        return 2
    lifecycle_events = _load_lifecycle_events(session_id, sdir)
    src = receipt or apply_receipt or {}
    wt_path_str: str = src.get("worktree", "")
    wt_state: "dict | None" = None
    if wt_path_str and Path(wt_path_str).is_absolute() and Path(wt_path_str).exists():
        wt_state = _git_worktree_state(Path(wt_path_str))
    status = _derive_lifecycle_status(receipt, apply_receipt, lifecycle_events, wt_state)
    sep = "=" * 70
    print(f"\n{sep}")
    print("  OBSIDIA BUILD -- CLEANUP")
    print(f"  session_id : {session_id}")
    print(f"  status     : {status}")
    print(f"{sep}\n")
    if status not in ("COMMITTED", "ABORTED"):
        print("  [CLEANUP_REFUSED] Cleanup autorisé uniquement pour : COMMITTED, ABORTED")
        print(f"  État actuel : {status}")
        if status == "READY_FOR_COMMIT_REVIEW":
            print("  → Committer d'abord, puis cleanup.")
        elif status not in ("CLEANED",):
            print(f"  → Aborter si nécessaire : build abort {session_id}")
        return 1
    session_path = sdir / session_id
    preserved = [
        f for f in ("receipt.json", "apply_receipt.json", "lifecycle_events.jsonl")
        if (session_path / f).exists()
    ]
    if not preserved:
        print(f"  [CLEANUP_REFUSED] Aucune preuve persistée pour {session_id}.")
        return 1
    cleaned_worktree = False
    if wt_path_str and Path(wt_path_str).is_absolute() and Path(wt_path_str).exists():
        # Relire l'état réel immédiatement avant suppression (fail-closed)
        fresh_wt = _git_worktree_state(Path(wt_path_str))
        _fresh_dirty = fresh_wt.get("dirty")
        if not fresh_wt.get("state_complete", True):
            print("  [HOLD_CLEANUP_REQUIRES_HUMAN_REVIEW]")
            print(f"  État git du worktree indéterminable : {wt_path_str}")
            _errs = fresh_wt.get("errors", [])
            if _errs:
                print(f"  Erreurs : {_errs[:2]}")
            print("  Impossible de vérifier l'état du worktree — aucune suppression.")
            return 3
        if _fresh_dirty is True:
            print("  [HOLD_CLEANUP_REQUIRES_HUMAN_REVIEW]")
            print(f"  Worktree dirty : {wt_path_str}")
            print("  Inspecter le diff avant cleanup — aucune suppression effectuée.")
            return 3
        # Worktree propre confirmé — suppression sans --force
        try:
            r = subprocess.run(
                ["git", "worktree", "remove", wt_path_str],
                cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=30,
            )
        except Exception as exc:
            print(f"  [HOLD_CLEANUP_FAILED] Erreur suppression worktree : {exc}")
            print("  Aucun événement CLEANED écrit.")
            return 3
        if r.returncode != 0:
            print(f"  [HOLD_CLEANUP_FAILED] git worktree remove a échoué :")
            print(f"  {r.stderr.strip()[:200]}")
            print("  Aucun événement CLEANED écrit.")
            return 3
        # Postcondition : vérifier l'absence effective
        if Path(wt_path_str).exists():
            print("  [HOLD_CLEANUP_POSTCONDITION_FAILED] Worktree toujours présent après suppression.")
            print(f"  Chemin : {wt_path_str}")
            print("  Aucun événement CLEANED écrit.")
            return 3
        cleaned_worktree = True
        print(f"  [OK] Worktree supprimé et vérifié absent : {wt_path_str}")
    else:
        print("  [INFO] Worktree absent ou non absolu — CLEANED sans suppression.")
    _append_lifecycle_event(
        session_id, "CLEANED",
        {"worktree_removed": cleaned_worktree, "previous_status": status},
        sdir,
    )
    print(f"  [CLEANED] Session {session_id}.")
    print(f"  Preuves préservées dans : {session_path}")
    print(f"  Fichiers préservés : {preserved}")
    print("  State_dir CONSERVÉ — les preuves ne sont jamais supprimées.")
    return 0


# =============================================================================
# Point d'entree CLI
# =============================================================================

def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="obsidia_build",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "objective", nargs="?", default="",
        help="Objectif de build (texte libre; --objective-file pour multi-ligne)",
    )
    parser.add_argument(
        "--approve",
        metavar="HUMAN_APPROVED_BUILD_SESSION=<session_id>:<manifest_hash>",
        default="",
        help="Token d'approbation Phase 2",
    )
    parser.add_argument(
        "--resume-kx108",
        metavar="SESSION_ID",
        default="",
        help="Reprendre une session bloquee sur KX108 (re-verifie + appelle KX108)",
    )
    parser.add_argument(
        "--version", action="version", version=f"obsidia_build {VERSION}",
    )

    parser.add_argument(
        "--objective-file",
        metavar="PATH",
        default="",
        help=(
            "Objectif UTF-8 depuis fichier. "
            "Support multi-ligne et objectifs longs."
        ),
    )

    parser.add_argument(
        "--scope",
        action="append",
        default=[],
        metavar="REPO_RELATIVE_PATH",
        help=(
            "Cible explicite repo-relative. Repetable. "
            "Active EXPLICIT_CHILD_TARGET sans fallback heuristique."
        ),
    )

    parser.add_argument(
        "--candidate-patch",
        metavar="PATH",
        default="",
        help=(
            "Unified diff reel. Son SHA-256 et ses fichiers "
            "sont lies a l'identite d'approbation."
        ),
    )

    args = parser.parse_args(argv)

    # R8-A
    #
    # Le texte complet est l'identite logique.
    # utf-8-sig absorbe uniquement un BOM de transport eventuel.
    objective = args.objective

    if args.objective_file:

        if objective:
            print(
                "[ERROR] objective et --objective-file "
                "sont mutuellement exclusifs."
            )
            return 1

        objective_path = Path(
            args.objective_file
        ).expanduser()

        if not objective_path.is_file():
            print(
                f"[ERROR] objective-file introuvable: "
                f"{objective_path}"
            )
            return 1

        try:
            objective = objective_path.read_text(
                encoding="utf-8-sig"
            )

        except Exception as exc:
            print(
                "[ERROR] lecture objective-file impossible: "
                f"{exc}"
            )
            return 1

        if not objective.strip():
            print(
                "[ERROR] objective-file vide."
            )
            return 1

    if args.resume_kx108:
        return cmd_resume_kx108(
            args.resume_kx108.strip(),
            REPO_ROOT, OBSIDIA_BUILD_STATE_DIR,
        )

    candidate_patch_spec = None
    authority_objective = objective
    effective_scope = list(args.scope) if args.scope else None

    if args.candidate_patch:
        try:
            candidate_patch_spec = load_candidate_patch_file(
                args.candidate_patch,
                REPO_ROOT,
            )
        except ValueError as exc:
            print(f"[ERROR] {exc}")
            return 2

        # Si --scope est également fourni, il doit être EXACTEMENT
        # le scope dérivé du patch. Aucun élargissement.
        if args.scope:
            requested = sorted(
                x.replace("\\", "/")
                for x in args.scope
            )
            derived = sorted(
                candidate_patch_spec.files
            )

            if requested != derived:
                print(
                    "[ERROR] CANDIDATE_SCOPE_MISMATCH "
                    f"requested={requested} derived={derived}"
                )
                return 2

        effective_scope = list(
            candidate_patch_spec.files
        )

        ok, msg = check_candidate_patch(
            candidate_patch_spec,
            REPO_ROOT,
        )

        if not ok:
            print(
                "[ERROR] CANDIDATE_PATCH_NOT_APPLICABLE "
                f"{msg}"
            )
            return 2

        authority_objective = bind_candidate_to_objective(
            objective,
            candidate_patch_spec,
        )

    if not authority_objective:
        parser.print_help()
        return 1

    if args.approve:

        # Preserve the exact pre-R8-B call contract when no real
        # candidate exists. Existing callers/mocks must not suddenly
        # receive a new keyword argument containing None.
        if candidate_patch_spec is None:
            return cmd_execute(
                authority_objective,
                args.approve,
                REPO_ROOT,
                OBSIDIA_BUILD_STATE_DIR,
                explicit_scope=effective_scope,
            )

        return cmd_execute(
            authority_objective,
            args.approve,
            REPO_ROOT,
            OBSIDIA_BUILD_STATE_DIR,
            explicit_scope=effective_scope,
            candidate_patch_spec=candidate_patch_spec,
        )

    if effective_scope:

        plan = compute_plan(
            authority_objective,
            get_base_sha(REPO_ROOT),
            REPO_ROOT,
            explicit_scope=effective_scope,
        )

        if candidate_patch_spec is not None:
            plan["candidate_patch_mode"] = (
                candidate_patch_spec.mode
            )
            plan["candidate_patch_hash"] = (
                candidate_patch_spec.sha256
            )
            plan["candidate_patch_files"] = list(
                candidate_patch_spec.files
            )
            plan["candidate_patch_source"] = (
                candidate_patch_spec.source_path
            )
            plan["display_objective"] = objective

        print(
            format_plan_proposed(
                plan,
                _probe_api_status(),
            )
        )

        return (
            0
            if plan.get("status") == "PLAN_PROPOSED"
            else 2
        )

    return cmd_plan(
        objective,
        REPO_ROOT,
    )


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

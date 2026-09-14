"""
periphery/agents/obsidure_repair_bridge.py
==========================================
PONT DE RÉPARATION EXTERNE — Obsidure ↔ moteur de raisonnement externe.

Cycle complet :

    1.  Obsidure tente (phase D).
    2.  Échec ou absence d'artefact → build_repair_request_from_cycle()
        produit un RepairRequest à partir des ErrorContext RÉELS.
    3.  persist_repair_request() dépose le JSON. Un moteur externe (Claude,
        autre agent, humain) lit et dépose un RepairProposal.
    4.  test_repair_proposal() écrit les candidats en SANDBOX ÉPHÉMÈRE,
        les compile, les passe au contrôle de conformité Obsidure, exécute
        les tests déclarés, et retourne un RepairVerdict.
    5.  resume_objective_from_verdict() rend l'objectif initial pour relance.

CE MODULE N'APPLIQUE RIEN.
    - écriture limitée à _EPHEMERAL_REPAIR_SANDBOX_* et _PATCH_PROPOSALS/
    - aucun git, aucun commit, aucun push
    - aucune écriture dans kernel / proofs / sealed / merkle / rfc3161
    - decision_authority = KX108_ONLY

LIMITE CONNUE ET DÉCLARÉE — isolation des tests :
    Les tests déclarés dans `tests_to_run` s'exécutent avec la sandbox en
    préfixe de PYTHONPATH. Ce masquage ne couvre PAS les modules déjà
    importés ni les packages sans __init__.py dans la sandbox. Chaque entrée
    de `tests_executed` porte donc `isolation` = FULL | PARTIAL, et un statut
    global PASS n'est jamais émis sur une isolation PARTIAL en échec.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from periphery.agents.obsidure_repair_contract import (
    REPAIR_BOUNDARY,
    FailureMode,
    ErrorContextRecord,
    RepairCandidateFile,
    RepairRequest,
    RepairProposal,
    RepairVerdict,
    is_protected_repair_path,
    repair_proposal_from_dict,
    repair_request_to_json,
    validate_repair_proposal,
)

__all__ = [
    "REPAIR_SANDBOX_PREFIX",
    "build_repair_request_from_cycle",
    "persist_repair_request",
    "load_repair_proposal",
    "test_repair_proposal",
    "resume_objective_from_verdict",
    "cleanup_repair_sandbox",
]

REPO_ROOT: Path = Path(__file__).resolve().parents[2]
REPAIR_SANDBOX_PREFIX = "_EPHEMERAL_REPAIR_SANDBOX_"
PROPOSALS_DIR: Path = REPO_ROOT / "_PATCH_PROPOSALS"

# Extrait de fichier joint au RepairRequest — borné pour rester lisible.
_EXCERPT_MAX_CHARS = 20000

# Types d'erreur qui signifient « la route interne ne peut pas y arriver ».
_ESCALATION_ERROR_TYPES = frozenset({
    "EMPTY_PATCH_PROPOSAL",
    "LEAN_EMPTY_PATCH_PROPOSAL",
    "SEMANTIC_REPAIR_REQUIRED",
})


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def _sha256_file(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except Exception:
        return ""


# ===========================================================================
# 1.  OBSIDURE → RepairRequest
# ===========================================================================


def _infer_failure_mode(
    error_contexts: List[Any],
    patches: List[Dict[str, Any]],
    stabilization: Optional[Any],
) -> str:
    """Déduit le mode d'échec général à partir des ErrorContext réels."""
    types = {str(getattr(c, "error_type", "")) for c in error_contexts}

    if "SEMANTIC_REPAIR_REQUIRED" in types:
        return FailureMode.SEMANTIC_REPAIR_REQUIRED
    if types & {"EMPTY_PATCH_PROPOSAL", "LEAN_EMPTY_PATCH_PROPOSAL"}:
        return FailureMode.NO_ARTIFACT_PRODUCED
    if not patches:
        return FailureMode.NO_ARTIFACT_PRODUCED
    if any(t.endswith("BUILD_ERROR") for t in types):
        return FailureMode.BUILD_ERROR
    if types:
        return FailureMode.CONFORMITY_VIOLATION
    if stabilization is not None and not getattr(stabilization, "passed", False):
        return FailureMode.MAX_ATTEMPTS_REACHED
    return FailureMode.UNKNOWN


def _collect_repo_targets(
    error_contexts: List[Any],
    patches: List[Dict[str, Any]],
) -> List[str]:
    """Chemins repo réels concernés par l'échec, dédupliqués, ordre stable."""
    targets: List[str] = []

    def _add(raw: Any) -> None:
        p = str(raw or "").replace("\\", "/").strip()
        if p and p not in targets and not is_protected_repair_path(p):
            targets.append(p)

    for ctx in error_contexts:
        _add(getattr(ctx, "target_hint", ""))
        _add(getattr(ctx, "protected_path", ""))
    for patch in patches:
        _add(patch.get("path", ""))

    return targets[:20]


def build_repair_request_from_cycle(
    objective: str,
    os_trad: Any = None,
    stabilization: Any = None,
    error_contexts: Optional[List[Any]] = None,
    patches: Optional[List[Dict[str, Any]]] = None,
    sandbox_dir: str = "",
    origin: str = "OBSIDURE",
    repo_root: Optional[Path] = None,
) -> RepairRequest:
    """
    Construit un RepairRequest à partir d'un cycle Obsidure réel.

    Ne fabrique aucune erreur : si le cycle n'a produit aucun ErrorContext mais
    aucun artefact non plus, le failure_mode reste NO_ARTIFACT_PRODUCED — car
    l'absence d'artefact est en soi l'échec.
    """
    ctxs = list(error_contexts or [])
    pchs = list(patches or [])

    root = Path(repo_root) if repo_root else REPO_ROOT
    records = [ErrorContextRecord.from_obj(c) for c in ctxs]
    failure_mode = _infer_failure_mode(ctxs, pchs, stabilization)
    repo_targets = _collect_repo_targets(ctxs, pchs)

    # Extraits réels des fichiers cibles — le moteur externe doit raisonner
    # sur le code existant, pas sur un résumé.
    excerpts: Dict[str, str] = {}
    for rel in repo_targets:
        candidate = root / rel
        if candidate.is_file():
            try:
                excerpts[rel] = candidate.read_text(
                    encoding="utf-8", errors="replace"
                )[:_EXCERPT_MAX_CHARS]
            except Exception:
                continue

    attempts = int(getattr(stabilization, "attempts", 0) or 0)
    final_status = str(getattr(stabilization, "final_status", "") or "")

    summary_bits = [
        f"failure_mode={failure_mode}",
        f"patches_count={len(pchs)}",
        f"error_contexts={len(records)}",
    ]
    if final_status:
        summary_bits.append(f"stabilization={final_status}")
    if failure_mode == FailureMode.NO_ARTIFACT_PRODUCED:
        summary_bits.append(
            "Aucun artefact produit alors que l'objectif en exige un — "
            "zero erreur n'est PAS un succes."
        )

    return RepairRequest(
        origin=origin,
        objective=objective,
        failure_mode=failure_mode,
        summary=" | ".join(summary_bits),
        error_contexts=records,
        repo_targets=repo_targets,
        target_excerpts=excerpts,
        attempts_spent=attempts,
        sandbox_dir=str(sandbox_dir or ""),
        tests_hint=_suggest_tests(repo_targets, root),
    )


def _suggest_tests(repo_targets: List[str], repo_root: Optional[Path] = None) -> List[str]:
    """
    Propose des chemins de tests plausibles pour les cibles — sans inventer :
    seuls les fichiers de test qui EXISTENT réellement sont retournés.
    """
    root = Path(repo_root) if repo_root else REPO_ROOT
    found: List[str] = []
    for rel in repo_targets:
        stem = Path(rel).stem
        for base in ("periphery/tests", "tests", "tests/periphery", "tests/api"):
            for name in (f"test_{stem}.py", f"{stem}_test.py"):
                cand = root / base / name
                if cand.is_file():
                    p = f"{base}/{name}"
                    if p not in found:
                        found.append(p)
    return found


def persist_repair_request(
    request: RepairRequest,
    out_dir: Optional[Path] = None,
) -> Path:
    """
    Dépose le RepairRequest en JSON. Écriture confinée à _PATCH_PROPOSALS/.
    Aucun git. Retourne le chemin du fichier écrit.
    """
    target_dir = Path(out_dir) if out_dir else (PROPOSALS_DIR / "_repair_requests")
    target_dir.mkdir(parents=True, exist_ok=True)
    out = target_dir / f"{request.request_id}.json"
    out.write_text(repair_request_to_json(request), encoding="utf-8")
    return out


def load_repair_proposal(path: Path) -> RepairProposal:
    """Lit un RepairProposal déposé par le moteur externe."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return repair_proposal_from_dict(data)


# ===========================================================================
# 2.  RepairProposal → test SANDBOX → RepairVerdict
# ===========================================================================


def _compile_candidate(sandbox_file: Path, rel: str) -> Optional[Dict[str, Any]]:
    """Compile / parse un candidat. Retourne une erreur ou None."""
    suffix = Path(rel).suffix.lower()

    if suffix == ".py":
        # compile() builtin plutôt que py_compile : même contrôle de syntaxe,
        # zéro écriture de bytecode (py_compile+os.devnull échoue sur Windows,
        # où 'nul' n'est pas un fichier régulier).
        try:
            source = sandbox_file.read_text(encoding="utf-8")
            compile(source, str(sandbox_file), "exec", dont_inherit=True)
        except SyntaxError as exc:
            return {
                "type": "REPAIR_PY_COMPILE_ERROR",
                "path": rel,
                "details": f"SyntaxError line {exc.lineno}: {exc.msg}"[:800],
            }
        except Exception as exc:
            return {
                "type": "REPAIR_PY_COMPILE_ERROR",
                "path": rel,
                "details": f"{type(exc).__name__}: {exc}"[:800],
            }
        return None

    if suffix == ".json":
        try:
            json.loads(sandbox_file.read_text(encoding="utf-8"))
        except Exception as exc:
            return {
                "type": "REPAIR_JSON_PARSE_ERROR",
                "path": rel,
                "details": f"{type(exc).__name__}: {exc}"[:800],
            }
        return None

    # .md / .yaml / .toml : pas de compilation — lisibilité UTF-8 seulement.
    try:
        sandbox_file.read_text(encoding="utf-8")
    except Exception as exc:
        return {
            "type": "REPAIR_DECODE_ERROR",
            "path": rel,
            "details": f"{type(exc).__name__}: {exc}"[:400],
        }
    return None


def _run_declared_tests(
    tests: List[str],
    sandbox_root: Path,
    timeout: int,
    repo_root: Optional[Path] = None,
) -> List[Dict[str, Any]]:
    """
    Exécute les tests déclarés avec la sandbox en préfixe de PYTHONPATH.

    L'isolation est déclarée honnêtement :
      FULL     le module candidat est effectivement résolu depuis la sandbox
      PARTIAL  le masquage n'est pas garanti (package sans __init__.py, etc.)
    """
    results: List[Dict[str, Any]] = []
    if not tests:
        return results

    root = Path(repo_root) if repo_root else REPO_ROOT
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(
        [str(sandbox_root), str(root), env.get("PYTHONPATH", "")]
    ).strip(os.pathsep)
    env["PYTHONDONTWRITEBYTECODE"] = "1"

    # Isolation FULL seulement si la sandbox porte une arborescence de packages
    # importable (au moins un __init__.py au niveau du premier segment).
    isolation = "PARTIAL"
    for child in sandbox_root.iterdir() if sandbox_root.is_dir() else []:
        if child.is_dir() and (child / "__init__.py").is_file():
            isolation = "FULL"
            break

    for test_path in tests[:10]:
        rel = str(test_path).replace("\\", "/")
        if is_protected_repair_path(rel):
            results.append({
                "test": rel,
                "status": "SKIPPED_PROTECTED",
                "isolation": isolation,
                "details": "Chemin protégé — non exécuté.",
            })
            continue
        if not (root / rel).exists():
            results.append({
                "test": rel,
                "status": "NOT_FOUND",
                "isolation": isolation,
                "details": "Le test déclaré n'existe pas dans le repo.",
            })
            continue

        try:
            proc = subprocess.run(
                [sys.executable, "-m", "pytest", rel, "-q", "--no-header", "-p", "no:cacheprovider"],
                cwd=str(root),
                env=env,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            tail = ((proc.stdout or "") + (proc.stderr or "")).strip().splitlines()
            results.append({
                "test": rel,
                "status": "PASS" if proc.returncode == 0 else "FAIL",
                "returncode": proc.returncode,
                "isolation": isolation,
                "details": "\n".join(tail[-15:])[:2000],
            })
        except subprocess.TimeoutExpired:
            results.append({
                "test": rel,
                "status": "TIMEOUT",
                "isolation": isolation,
                "details": f"Dépassement de {timeout}s.",
            })
        except Exception as exc:
            results.append({
                "test": rel,
                "status": "ERROR",
                "isolation": isolation,
                "details": f"{type(exc).__name__}: {exc}"[:400],
            })

    return results


def test_repair_proposal(
    proposal: RepairProposal,
    request: Optional[RepairRequest] = None,
    sandbox_root: Optional[Path] = None,
    run_tests: bool = True,
    test_timeout: int = 180,
    repo_root: Optional[Path] = None,
) -> RepairVerdict:
    """
    Teste un RepairProposal EN SANDBOX. N'applique jamais rien au repo.

    Séquence :
      1. validation statique (frontières, chemins, extensions, contenu non vide)
      2. écriture des candidats dans une sandbox éphémère
      3. compilation / parsing de chaque candidat
      4. contrôle de conformité Obsidure (mots interdits, réplication kernel…)
      5. exécution des tests déclarés

    Statut :
      NO_CANDIDATE  proposition vide — jamais un succès
      BLOCKED       frontière, chemin protégé, ou compilation en échec
      PARTIAL       compile et conforme, mais tests absents / non concluants
      PASS          compile, conforme, et tous les tests déclarés passent
    """
    root = Path(repo_root) if repo_root else REPO_ROOT
    req_id = request.request_id if request else str(getattr(proposal, "request_id", ""))
    verdict = RepairVerdict(
        request_id=req_id,
        proposal_id=proposal.proposal_id,
        resume_objective=(request.objective if request else ""),
    )

    # ── 1. Validation statique ────────────────────────────────────────────
    static_errors = validate_repair_proposal(proposal)
    verdict.errors.extend(static_errors)

    if any(e["type"] == "REPAIR_NO_CANDIDATE" for e in static_errors):
        verdict.status = "NO_CANDIDATE"
        return verdict

    blocking = {
        "REPAIR_BOUNDARY_VIOLATION",
        "REPAIR_PROTECTED_PATH",
        "REPAIR_PATH_ESCAPE",
        "REPAIR_PATH_OUT_OF_SCOPE",
        "REPAIR_INVALID_EXTENSION",
        "REPAIR_EMPTY_CONTENT",
        "REPAIR_EMPTY_PATH",
        "REPAIR_INVALID_CHANGE_KIND",
    }
    if any(e["type"] in blocking for e in static_errors):
        verdict.status = "BLOCKED"
        return verdict

    # ── 2. Sandbox éphémère ───────────────────────────────────────────────
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    sb = Path(sandbox_root) if sandbox_root else (
        root / f"{REPAIR_SANDBOX_PREFIX}{ts}_{uuid.uuid4().hex[:6]}"
    )
    sb.mkdir(parents=True, exist_ok=True)
    verdict.sandbox_dir = str(sb)

    written: List[Tuple[str, Path]] = []
    for cand in proposal.candidate_files:
        rel = str(cand.path).replace("\\", "/").lstrip("./")
        out = sb / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(cand.full_content, encoding="utf-8")
        written.append((rel, out))

        # Dérive : le fichier de base a changé depuis l'émission du request.
        base = root / rel
        if cand.base_sha256 and base.is_file():
            actual = _sha256_file(base)
            if actual and actual != cand.base_sha256:
                verdict.errors.append({
                    "type": "REPAIR_BASE_DRIFT",
                    "path": rel,
                    "details": (
                        "Le fichier de référence a changé depuis l'émission du "
                        f"RepairRequest (attendu {cand.base_sha256[:12]}, "
                        f"actuel {actual[:12]})."
                    ),
                })

        # MODIFY sur un fichier inexistant / CREATE sur un fichier existant.
        if cand.change_kind == "MODIFY" and not base.is_file():
            verdict.errors.append({
                "type": "REPAIR_MODIFY_MISSING_TARGET",
                "path": rel,
                "details": "change_kind=MODIFY mais le fichier n'existe pas dans le repo.",
            })
        elif cand.change_kind == "CREATE" and base.is_file():
            verdict.errors.append({
                "type": "REPAIR_CREATE_OVERWRITES_EXISTING",
                "path": rel,
                "details": "change_kind=CREATE mais le fichier existe déjà — écrasement refusé.",
            })

    # ── 3. Compilation ────────────────────────────────────────────────────
    for rel, out in written:
        err = _compile_candidate(out, rel)
        if err:
            verdict.errors.append(err)
        else:
            verdict.compiled_files.append(rel)

    # ── 4. Conformité Obsidure (import tardif — évite le cycle) ───────────
    try:
        from periphery.agents.agent_obsidure import _test_patches_conformity

        conformity_patches = [
            {
                "path": rel,
                "action": "REPAIR_CANDIDATE",
                "sandbox_path": str(out),
            }
            for rel, out in written
        ]
        verdict.errors.extend(_test_patches_conformity(conformity_patches, None, sb))
    except Exception as exc:
        verdict.errors.append({
            "type": "REPAIR_CONFORMITY_UNAVAILABLE",
            "path": "",
            "details": f"{type(exc).__name__}: {exc}"[:400],
        })

    if verdict.errors:
        verdict.status = "BLOCKED"
        return verdict

    # ── 5. Tests déclarés ─────────────────────────────────────────────────
    declared = list(proposal.tests_to_run) or (list(request.tests_hint) if request else [])
    if run_tests and declared:
        verdict.tests_executed = _run_declared_tests(declared, sb, test_timeout, root)
        statuses = {t["status"] for t in verdict.tests_executed}
        if statuses and statuses <= {"PASS"}:
            verdict.status = "PASS"
        elif "FAIL" in statuses or "ERROR" in statuses or "TIMEOUT" in statuses:
            verdict.status = "BLOCKED"
            verdict.errors.append({
                "type": "REPAIR_DECLARED_TESTS_FAILED",
                "path": "",
                "details": f"Statuts observés : {sorted(statuses)}",
            })
        else:
            verdict.status = "PARTIAL"
    else:
        # Compile et conforme, mais rien ne prouve que l'objectif est atteint.
        verdict.status = "PARTIAL"

    return verdict


def resume_objective_from_verdict(
    verdict: RepairVerdict,
    request: Optional[RepairRequest] = None,
) -> Optional[str]:
    """
    Retourne l'objectif INITIAL à reprendre si la réparation est exploitable.

    None si le verdict ne permet pas de reprendre — la reprise n'est jamais
    automatique côté décision : c'est l'opérateur qui relance le cycle.
    """
    if verdict.status not in ("PASS", "PARTIAL"):
        return None
    objective = verdict.resume_objective or (request.objective if request else "")
    return objective or None


def cleanup_repair_sandbox(
    verdict: RepairVerdict,
    repo_root: Optional[Path] = None,
) -> bool:
    """
    Supprime la sandbox éphémère d'un verdict. Refuse tout chemin qui ne porte
    pas le préfixe attendu et ne se trouve pas sous REPO_ROOT — fail-closed.
    """
    raw = str(verdict.sandbox_dir or "")
    if not raw:
        return False
    root = Path(repo_root).resolve() if repo_root else REPO_ROOT.resolve()
    path = Path(raw).resolve()
    if not path.name.startswith(REPAIR_SANDBOX_PREFIX):
        return False
    try:
        path.relative_to(root)
    except ValueError:
        return False
    if not path.is_dir():
        return False
    shutil.rmtree(path, ignore_errors=True)
    return not path.exists()

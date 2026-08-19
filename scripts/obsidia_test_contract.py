"""
obsidia_test_contract.py
==========================
ACD01_EXECUTION_TEST_CONTRACT_V0 — contrat de test immuable, borné,
non-souverain, lié à l'autorité d'exécution humaine.

Un TestContract décrit EXACTEMENT quelles vérifications doivent être
exécutées après une application de contenu — argv réel (jamais
shell=True), code de sortie attendu, obligatoire ou non. Le runner qui
l'exécute ne décide RIEN : TEST_RUNNER_EMITS_ACT = FALSE. Le résultat
(TestContractResult) est une PREUVE destinée à KX108, jamais une
décision. PASSING TESTS != ACT.

decision_authority = KX108_ONLY
"""

from __future__ import annotations

import datetime
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Optional

SCHEMA_VERSION = 1
DECISION_AUTHORITY = "KX108_ONLY"

CHECK_TYPE_SUBPROCESS = "SUBPROCESS_ARGV"
CHECK_TYPE_TARGET_SHA256 = "TARGET_POSTCONDITION_SHA256"
CHECK_TYPE_DIFF_SCOPE = "DIFF_SCOPE_EXACT"

RESULT_PASS = "PASS"
RESULT_FAIL = "FAIL"
RESULT_ERROR = "ERROR"

AGGREGATE_ALL_REQUIRED_PASS = "ALL_REQUIRED_PASS"
AGGREGATE_REQUIRED_TEST_FAILED = "REQUIRED_TEST_FAILED"
AGGREGATE_TEST_EXECUTION_ERROR = "TEST_EXECUTION_ERROR"


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


_CONTRACT_BOUND_FIELDS = (
    "test_contract_schema_version", "contract_id", "candidate_entry_id",
    "batch_id", "target_path",
)

_CHECK_BOUND_FIELDS = (
    "check_id", "check_type", "argv", "cwd_policy",
    "expected_exit_code", "required", "timeout_seconds",
    "target_path", "expected_target_sha256", "expected_diff_paths",
)


def compute_test_contract_hash(contract: dict) -> str:
    """
    SHA256 COMPLET (64 hex), jamais tronqué. Sérialisation canonique.
    L'ORDRE des checks est préservé tel quel (liste, pas un ensemble
    trié) — sémantiquement pertinent, certains checks dépendent de
    l'état laissé par les précédents (ex. le scan après l'application
    de contenu). Toute modification d'argv, de code de sortie attendu,
    de `required`, de cwd_policy, de timeout, ou d'ordre change ce hash.
    """
    checks_payload = [
        {k: c.get(k) for k in _CHECK_BOUND_FIELDS}
        for c in (contract.get("checks") or [])
    ]
    payload = json.dumps(
        {
            **{k: contract.get(k) for k in _CONTRACT_BOUND_FIELDS},
            "checks": checks_payload,
        },
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def build_check(
    check_id: str,
    check_type: str,
    argv: "list[str] | None" = None,
    cwd_policy: str = "REPO_ROOT",
    expected_exit_code: "int | None" = 0,
    required: bool = True,
    timeout_seconds: int = 60,
    target_path: "str | None" = None,
    expected_target_sha256: "str | None" = None,
    expected_diff_paths: "list[str] | None" = None,
) -> dict:
    """Construit un check déterministe — argv en LISTE, jamais une chaîne shell."""
    return {
        "check_id": check_id,
        "check_type": check_type,
        "argv": list(argv) if argv else None,
        "cwd_policy": cwd_policy,
        "expected_exit_code": expected_exit_code,
        "required": required,
        "timeout_seconds": timeout_seconds,
        "target_path": target_path,
        "expected_target_sha256": expected_target_sha256,
        "expected_diff_paths": list(expected_diff_paths) if expected_diff_paths is not None else None,
    }


def build_test_contract(
    contract_id: str,
    candidate_entry_id: str,
    batch_id: str,
    target_path: str,
    checks: "list[dict]",
) -> dict:
    return {
        "test_contract_schema_version": SCHEMA_VERSION,
        "contract_id": contract_id,
        "candidate_entry_id": candidate_entry_id,
        "batch_id": batch_id,
        "target_path": target_path,
        "checks": list(checks),
        "decision_authority": DECISION_AUTHORITY,
    }


def _resolve_cwd(cwd_policy: str, repo_root: Path) -> Path:
    if cwd_policy == "REPO_ROOT":
        return repo_root
    raise ValueError(f"UNSUPPORTED_CWD_POLICY:{cwd_policy}")


def _run_subprocess_check(check: dict, repo_root: Path) -> dict:
    argv = check.get("argv")
    started = _now()
    if not argv or not isinstance(argv, list):
        return {
            "check_id": check.get("check_id"), "result": RESULT_ERROR,
            "reason": "MISSING_ARGV", "started_at": started, "finished_at": _now(),
        }
    try:
        cwd = _resolve_cwd(check.get("cwd_policy") or "REPO_ROOT", repo_root)
    except ValueError as exc:
        return {
            "check_id": check.get("check_id"), "result": RESULT_ERROR,
            "reason": str(exc), "started_at": started, "finished_at": _now(),
        }
    try:
        proc = subprocess.run(
            argv, cwd=str(cwd), capture_output=True, text=True,
            timeout=check.get("timeout_seconds") or 60,
        )
    except subprocess.TimeoutExpired:
        return {
            "check_id": check.get("check_id"), "result": RESULT_ERROR,
            "reason": "TIMEOUT", "started_at": started, "finished_at": _now(),
        }
    except OSError as exc:
        return {
            "check_id": check.get("check_id"), "result": RESULT_ERROR,
            "reason": f"SPAWN_FAILED:{exc}", "started_at": started, "finished_at": _now(),
        }
    finished = _now()
    expected = check.get("expected_exit_code")
    result = RESULT_PASS if (expected is None or proc.returncode == expected) else RESULT_FAIL
    return {
        "check_id": check.get("check_id"), "result": result,
        "exit_code": proc.returncode, "expected_exit_code": expected,
        "stdout": proc.stdout[-4000:], "stderr": proc.stderr[-4000:],
        "started_at": started, "finished_at": finished,
    }


def _run_target_sha256_check(check: dict, repo_root: Path) -> dict:
    started = _now()
    target_path = check.get("target_path")
    p = (repo_root / target_path) if target_path else None
    if p is None or not p.exists() or not p.is_file():
        return {
            "check_id": check.get("check_id"), "result": RESULT_ERROR,
            "reason": "TARGET_MISSING", "started_at": started, "finished_at": _now(),
        }
    actual = hashlib.sha256(p.read_bytes()).hexdigest()
    expected = check.get("expected_target_sha256")
    result = RESULT_PASS if actual == expected else RESULT_FAIL
    return {
        "check_id": check.get("check_id"), "result": result,
        "actual_target_sha256": actual, "expected_target_sha256": expected,
        "started_at": started, "finished_at": _now(),
    }


def _run_diff_scope_check(check: dict, repo_root: Path) -> dict:
    started = _now()
    try:
        proc = subprocess.run(
            ["git", "diff", "--name-only"], cwd=str(repo_root),
            capture_output=True, text=True, timeout=check.get("timeout_seconds") or 30,
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        return {
            "check_id": check.get("check_id"), "result": RESULT_ERROR,
            "reason": str(exc), "started_at": started, "finished_at": _now(),
        }
    actual_paths = sorted(p for p in proc.stdout.splitlines() if p.strip())
    expected_paths = sorted(check.get("expected_diff_paths") or [])
    result = RESULT_PASS if actual_paths == expected_paths else RESULT_FAIL
    return {
        "check_id": check.get("check_id"), "result": result,
        "actual_diff_paths": actual_paths, "expected_diff_paths": expected_paths,
        "started_at": started, "finished_at": _now(),
    }


_CHECK_RUNNERS = {
    CHECK_TYPE_SUBPROCESS: _run_subprocess_check,
    CHECK_TYPE_TARGET_SHA256: _run_target_sha256_check,
    CHECK_TYPE_DIFF_SCOPE: _run_diff_scope_check,
}


def run_test_contract(contract: dict, repo_root: Path) -> dict:
    """
    Exécute chaque check du contrat, dans l'ordre. Ne décide RIEN — ne
    fabrique jamais kx108_decision (toujours None). Le résultat agrégé
    est une projection PURE des résultats individuels, jamais une
    autorité.
    """
    results = []
    for check in contract.get("checks", []):
        runner = _CHECK_RUNNERS.get(check.get("check_type"))
        if runner is None:
            r = {
                "check_id": check.get("check_id"), "result": RESULT_ERROR,
                "reason": f"UNSUPPORTED_CHECK_TYPE:{check.get('check_type')}",
                "started_at": _now(), "finished_at": _now(),
            }
        else:
            r = runner(check, repo_root)
        r["required"] = check.get("required", True)
        results.append(r)

    required_results = [r for r in results if r["required"]]
    if any(r["result"] == RESULT_ERROR for r in required_results):
        aggregate = AGGREGATE_TEST_EXECUTION_ERROR
    elif any(r["result"] != RESULT_PASS for r in required_results):
        aggregate = AGGREGATE_REQUIRED_TEST_FAILED
    else:
        aggregate = AGGREGATE_ALL_REQUIRED_PASS

    return {
        "test_contract_hash": compute_test_contract_hash(contract),
        "contract_id": contract.get("contract_id"),
        "checks": results,
        "aggregate_status": aggregate,
        "decision_authority": DECISION_AUTHORITY,
        "kx108_decision": None,
    }

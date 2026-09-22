"""obsidia_session_simulate_cli — TERMINAL_SESSION_SIMULATE_V0.

STATUS: IMPLEMENTATION
CANONICAL_NAME: TERMINAL_SESSION_SIMULATE_V0
SCOPE: PUBLIC_BOUNDED_SESSION_SIMULATION_ONLY
PUBLIC_COMMAND: OBSIDIA_SESSION_SIMULATE
SIMULATED: TRUE
REAL_EXECUTION: FORBIDDEN
REPOSITORY_MUTATION: FORBIDDEN
TEMP_LOCK_MUTATION: ALLOWED_BOUNDED
PERSISTENT_LOCK: FORBIDDEN
OBSIDURE_WIRING: FORBIDDEN
BRODY_WIRING: FORBIDDEN
KX108_INTEGRATION: DEFERRED
RECLAIM: FORBIDDEN

Usage:
    python -B scripts/obsidia_session_simulate_cli.py
        --lock-path "<chemin absolu>"
        --session-id "<identifiant>"
        --heartbeat-interval-seconds "<nombre>"
        --max-steps "<entier>"
        --control "<none|stop|abort>"
        --ack-temp-lock-mutation

Codes de retour :
    0  result.ok=true, postconditions cohérentes, JSON émis
    1  INTERNAL_ERROR, POSTCONDITION_FAILED ou canal stdout défaillant
    2  invocation/validation invalide, JSON émis
    3  simulation exécutée avec result.ok=false cohérent, JSON émis

Invariants :
    - aucun subprocess, thread, asyncio, réseau, signal handler ;
    - aucune écriture directe, suppression, renommage de fichier ;
    - seule mutation autorisée : lock temporaire via adapter (TEMP_LOCK_ONLY) ;
    - aucun reclaim, aucun classify_lock, aucune exécution réelle ;
    - aucune lecture de variable d'environnement, aucun accès Git ;
    - stderr toujours vide ;
    - stdout = exactement un objet JSON UTF-8.

authority: NONE | sovereign: false | decision_authority: KX108_ONLY
kx108_decision_present: false | simulated: true | isolated: true | wired: true
"""
from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import decimal
import json
import os
import re
import stat
from pathlib import Path
from typing import Optional, Sequence

_SCRIPT_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _SCRIPT_DIR.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from periphery.session_lock.terminal_session_adapter import (  # noqa: E402
    TerminalSessionAdapter,
    TerminalSessionAdapterResult,
)
from periphery.session_lock.heartbeat_lock_manager import (  # noqa: E402
    ControlRequest,
    HeartbeatConfig,
)

# ---------------------------------------------------------------------------
# Constantes publiques
# ---------------------------------------------------------------------------
_COMMAND = "obsidia session simulate"
_AUTHORITY = "NONE"
_SOVEREIGN = False
_DECISION_AUTHORITY = "KX108_ONLY"
_KX108_DECISION_PRESENT = False
_OPERATION = "SIMULATE_BOUNDED_SESSION"
_SIMULATED = True
_ISOLATED = True
_WIRED = True
_MUTATION_SCOPE = "TEMP_LOCK_ONLY"

# ---------------------------------------------------------------------------
# Grammaires
# ---------------------------------------------------------------------------
_SESSION_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_HEARTBEAT_INTERVAL_RE = re.compile(r"^(?:0|[1-9][0-9]*)(?:\.[0-9]+)?$")
_MAX_STEPS_RE = re.compile(r"^(?:[1-9]|[1-9][0-9]|100)$")

# ---------------------------------------------------------------------------
# Racine du dépôt (sans Git, sans environnement)
# ---------------------------------------------------------------------------
SCRIPT_PATH = Path(__file__).resolve(strict=True)
REPO_ROOT = SCRIPT_PATH.parent.parent
RESOLVED_REPO_ROOT = REPO_ROOT.resolve(strict=True)


# ---------------------------------------------------------------------------
# Émission JSON déterministe — OUTPUT_CHANNEL_FAILURE_FAIL_CLOSED
# ---------------------------------------------------------------------------
def _try_emit(envelope: dict) -> bool:
    try:
        payload = json.dumps(
            envelope,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        sys.stdout.write(payload + "\n")
        sys.stdout.flush()
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Construction d'envelopes normatives
# ---------------------------------------------------------------------------
def _make_envelope(
    *,
    ok: bool,
    adapter_code: str,
    lock_path: Optional[str],
    session_id: Optional[str],
    heartbeat_interval_seconds: Optional[float],
    max_steps: Optional[int],
    control_request: Optional[str],
    sequence_ok: Optional[bool],
    cleanup_ok: Optional[bool],
    first_failure: Optional[dict],
    steps_executed: int,
    terminated: bool,
    released: bool,
    lock_exists_after: Optional[bool],
    detail: str,
) -> dict:
    return {
        "command": _COMMAND,
        "ok": ok,
        "authority": _AUTHORITY,
        "sovereign": _SOVEREIGN,
        "decision_authority": _DECISION_AUTHORITY,
        "kx108_decision_present": _KX108_DECISION_PRESENT,
        "operation": _OPERATION,
        "adapter_code": adapter_code,
        "lock_path": lock_path,
        "session_id": session_id,
        "heartbeat_interval_seconds": heartbeat_interval_seconds,
        "max_steps": max_steps,
        "control_request": control_request,
        "sequence_ok": sequence_ok,
        "cleanup_ok": cleanup_ok,
        "first_failure": first_failure,
        "steps_executed": steps_executed,
        "terminated": terminated,
        "released": released,
        "simulated": _SIMULATED,
        "isolated": _ISOLATED,
        "wired": _WIRED,
        "mutation_scope": _MUTATION_SCOPE,
        "lock_exists_after": lock_exists_after,
        "detail": detail,
    }


def _invocation_invalid(
    lock_path: Optional[str] = None,
    session_id: Optional[str] = None,
    heartbeat_interval_seconds: Optional[float] = None,
    max_steps: Optional[int] = None,
    control_request: Optional[str] = None,
) -> dict:
    return _make_envelope(
        ok=False,
        adapter_code="INVOCATION_INVALID",
        lock_path=lock_path,
        session_id=session_id,
        heartbeat_interval_seconds=heartbeat_interval_seconds,
        max_steps=max_steps,
        control_request=control_request,
        sequence_ok=None,
        cleanup_ok=None,
        first_failure=None,
        steps_executed=0,
        terminated=False,
        released=False,
        lock_exists_after=None,
        detail="INVOCATION_INVALID",
    )


def _internal_error(
    lock_path: Optional[str] = None,
    session_id: Optional[str] = None,
    heartbeat_interval_seconds: Optional[float] = None,
    max_steps: Optional[int] = None,
    control_request: Optional[str] = None,
) -> dict:
    return _make_envelope(
        ok=False,
        adapter_code="INTERNAL_ERROR",
        lock_path=lock_path,
        session_id=session_id,
        heartbeat_interval_seconds=heartbeat_interval_seconds,
        max_steps=max_steps,
        control_request=control_request,
        sequence_ok=None,
        cleanup_ok=None,
        first_failure=None,
        steps_executed=0,
        terminated=False,
        released=False,
        lock_exists_after=None,
        detail="INTERNAL_ERROR",
    )


# ---------------------------------------------------------------------------
# Projection first_failure (OperationResult → dict public)
# ---------------------------------------------------------------------------
def _project_first_failure(ff: object) -> Optional[dict]:
    if ff is None:
        return None
    code_val = ff.code.value if ff.code is not None else None
    return {
        "ok": ff.ok,
        "code": code_val,
        "fail_closed": ff.fail_closed,
        "human_recovery_required": ff.human_recovery_required,
        "detail": ff.detail,
    }


# ---------------------------------------------------------------------------
# Parser strict — 11 tokens exacts
# ---------------------------------------------------------------------------
_EXPECTED_OPTIONS = (
    "--lock-path",
    "--session-id",
    "--heartbeat-interval-seconds",
    "--max-steps",
    "--control",
    "--ack-temp-lock-mutation",
)


def _parse_argv(argv: Sequence[str]) -> tuple[Optional[dict], Optional[str]]:
    """Retourne (parsed, None) ou (None, erreur)."""
    if len(argv) != 11:
        return None, f"11 tokens attendus, reçu {len(argv)}"
    if argv[0] != "--lock-path":
        return None, f"token[0] invalide : {argv[0]!r}"
    if argv[2] != "--session-id":
        return None, f"token[2] invalide : {argv[2]!r}"
    if argv[4] != "--heartbeat-interval-seconds":
        return None, f"token[4] invalide : {argv[4]!r}"
    if argv[6] != "--max-steps":
        return None, f"token[6] invalide : {argv[6]!r}"
    if argv[8] != "--control":
        return None, f"token[8] invalide : {argv[8]!r}"
    if argv[10] != "--ack-temp-lock-mutation":
        return None, f"token[10] invalide : {argv[10]!r}"
    for i in (1, 3, 5, 7, 9):
        if argv[i].startswith("--"):
            return None, f"token[{i}] ressemble à une option : {argv[i]!r}"
    return {
        "lock_path": argv[1],
        "session_id": argv[3],
        "heartbeat_interval": argv[5],
        "max_steps": argv[7],
        "control": argv[9],
    }, None


# ---------------------------------------------------------------------------
# Validation lock path
# ---------------------------------------------------------------------------

def _validate_lock_path_string(raw: str) -> Optional[str]:
    """Validation brute de la chaîne. Retourne un message d'erreur ou None."""
    if not raw:
        return "lock_path vide"
    if raw != raw.strip():
        return "lock_path ne doit pas comporter d'espace initial ou final"
    if not Path(raw).is_absolute():
        return "lock_path doit être absolu"
    if raw.startswith("\\\\?\\") or raw.startswith("\\\\.\\"):
        return "lock_path : préfixe étendu Windows interdit"
    if raw.startswith("\\\\"):
        return "lock_path : chemin UNC interdit"
    # Alternate data stream : colon supplémentaire après le colon du lecteur
    ads_check = raw[2:] if (len(raw) >= 2 and raw[1] == ":") else raw
    if ":" in ads_check:
        return "lock_path : alternate data stream interdit"
    # Segments courts Windows (~<chiffres>)
    for seg in Path(raw).parts:
        if re.search(r"~[0-9]+", seg):
            return f"lock_path : segment court Windows détecté : {seg!r}"
    return None


def _validate_parent(raw: str) -> Optional[str]:
    parent = Path(raw).parent
    if not parent.exists():
        return f"répertoire parent inexistant : {parent}"
    if not parent.is_dir():
        return f"parent n'est pas un répertoire : {parent}"
    return None


def _validate_components(raw: str) -> Optional[str]:
    """Vérifie que chaque composant existant du parent n'est pas un symlink/reparse."""
    parent = Path(raw).parent
    parts = parent.parts
    if not parts:
        return None
    current = Path(parts[0])
    for part in parts[1:]:
        current = current / part
        if not os.path.lexists(str(current)):
            break
        try:
            st = os.lstat(str(current))
        except OSError as exc:
            return f"lstat échoué sur {current} : {exc}"
        if current.is_symlink():
            return f"composant symlink interdit : {current}"
        attr = (
            getattr(st, "st_file_attributes", 0)
            & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
        )
        if attr:
            return f"composant reparse point interdit : {current}"
    return None


def _check_confinement(raw: str) -> Optional[str]:
    """Retourne un message d'erreur si la cible est dans le dépôt."""
    resolved = Path(raw).resolve(strict=False)
    try:
        common = os.path.commonpath([
            os.path.normcase(os.path.normpath(str(resolved))),
            os.path.normcase(os.path.normpath(str(RESOLVED_REPO_ROOT))),
        ])
        repo_norm = os.path.normcase(os.path.normpath(str(RESOLVED_REPO_ROOT)))
        if common == repo_norm:
            return "lock_path confiné dans le dépôt : interdit"
    except ValueError:
        pass
    return None


# ---------------------------------------------------------------------------
# Point d'entrée public
# ---------------------------------------------------------------------------

def main(argv: Optional[Sequence[str]] = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="strict")
        except Exception:
            return 1

    # Phase 3 — Parser strict
    parsed, parse_err = _parse_argv(argv)
    if parsed is None:
        if not _try_emit(_invocation_invalid()):
            return 1
        return 2

    raw_lock_path: str = parsed["lock_path"]
    raw_session_id: str = parsed["session_id"]
    raw_interval: str = parsed["heartbeat_interval"]
    raw_max_steps: str = parsed["max_steps"]
    raw_control: str = parsed["control"]

    # Phase 4 — Session ID
    if not _SESSION_ID_RE.match(raw_session_id):
        if not _try_emit(_invocation_invalid(lock_path=raw_lock_path)):
            return 1
        return 2

    # Phase 5 — Heartbeat interval
    if not _HEARTBEAT_INTERVAL_RE.match(raw_interval):
        if not _try_emit(_invocation_invalid(
            lock_path=raw_lock_path, session_id=raw_session_id,
        )):
            return 1
        return 2
    try:
        d_val = decimal.Decimal(raw_interval)
        if not d_val.is_finite():
            raise ValueError("non fini")
        if not (decimal.Decimal("0.01") <= d_val <= decimal.Decimal("5.0")):
            raise ValueError("hors borne")
        validated_interval = float(d_val)
    except Exception:
        if not _try_emit(_invocation_invalid(
            lock_path=raw_lock_path, session_id=raw_session_id,
        )):
            return 1
        return 2

    # Phase 6 — Max steps
    if not _MAX_STEPS_RE.match(raw_max_steps):
        if not _try_emit(_invocation_invalid(
            lock_path=raw_lock_path,
            session_id=raw_session_id,
            heartbeat_interval_seconds=validated_interval,
        )):
            return 1
        return 2
    validated_max_steps = int(raw_max_steps)

    # Phase 7 — Control
    _ctrl_map = {
        "none": None,
        "stop": ControlRequest.STOP,
        "abort": ControlRequest.ABORT,
    }
    if raw_control not in _ctrl_map:
        if not _try_emit(_invocation_invalid(
            lock_path=raw_lock_path,
            session_id=raw_session_id,
            heartbeat_interval_seconds=validated_interval,
            max_steps=validated_max_steps,
        )):
            return 1
        return 2
    control_request: Optional[ControlRequest] = _ctrl_map[raw_control]

    # Phase 8 — Validation lock path (brute)
    str_err = _validate_lock_path_string(raw_lock_path)
    if str_err is not None:
        if not _try_emit(_invocation_invalid(
            lock_path=raw_lock_path,
            session_id=raw_session_id,
            heartbeat_interval_seconds=validated_interval,
            max_steps=validated_max_steps,
            control_request=raw_control,
        )):
            return 1
        return 2

    # Phase 8 — Existence (rejeter si cible existe déjà)
    try:
        target_exists = os.path.lexists(raw_lock_path)
    except Exception:
        if not _try_emit(_internal_error(
            lock_path=raw_lock_path,
            session_id=raw_session_id,
            heartbeat_interval_seconds=validated_interval,
            max_steps=validated_max_steps,
            control_request=raw_control,
        )):
            return 1
        return 1
    if target_exists:
        if not _try_emit(_invocation_invalid(
            lock_path=raw_lock_path,
            session_id=raw_session_id,
            heartbeat_interval_seconds=validated_interval,
            max_steps=validated_max_steps,
            control_request=raw_control,
        )):
            return 1
        return 2

    # Phase 8 — Parent
    parent_err = _validate_parent(raw_lock_path)
    if parent_err is not None:
        if not _try_emit(_invocation_invalid(
            lock_path=raw_lock_path,
            session_id=raw_session_id,
            heartbeat_interval_seconds=validated_interval,
            max_steps=validated_max_steps,
            control_request=raw_control,
        )):
            return 1
        return 2

    # Phase 8 — Composants (symlinks / reparse points)
    try:
        comp_err = _validate_components(raw_lock_path)
    except Exception:
        if not _try_emit(_invocation_invalid(
            lock_path=raw_lock_path,
            session_id=raw_session_id,
            heartbeat_interval_seconds=validated_interval,
            max_steps=validated_max_steps,
            control_request=raw_control,
        )):
            return 1
        return 2
    if comp_err is not None:
        if not _try_emit(_invocation_invalid(
            lock_path=raw_lock_path,
            session_id=raw_session_id,
            heartbeat_interval_seconds=validated_interval,
            max_steps=validated_max_steps,
            control_request=raw_control,
        )):
            return 1
        return 2

    # Phase 8 — Confinement
    try:
        conf_err = _check_confinement(raw_lock_path)
    except Exception:
        if not _try_emit(_internal_error(
            lock_path=raw_lock_path,
            session_id=raw_session_id,
            heartbeat_interval_seconds=validated_interval,
            max_steps=validated_max_steps,
            control_request=raw_control,
        )):
            return 1
        return 1
    if conf_err is not None:
        if not _try_emit(_invocation_invalid(
            lock_path=raw_lock_path,
            session_id=raw_session_id,
            heartbeat_interval_seconds=validated_interval,
            max_steps=validated_max_steps,
            control_request=raw_control,
        )):
            return 1
        return 2

    # Phase 10 — HeartbeatConfig
    heartbeat_config = HeartbeatConfig(
        enabled=True,
        heartbeat_interval_seconds=validated_interval,
        max_v2_future_clock_skew_seconds=None,
        human_approved_corrected_gf_r01_sha256=None,
    )

    # Phase 11 — Appel unique à l'adapter
    try:
        result: TerminalSessionAdapterResult = TerminalSessionAdapter().simulate_bounded_session(
            lock_path=raw_lock_path,
            session_id=raw_session_id,
            heartbeat_config=heartbeat_config,
            max_steps=validated_max_steps,
            control_request=control_request,
        )
    except Exception:
        if not _try_emit(_internal_error(
            lock_path=raw_lock_path,
            session_id=raw_session_id,
            heartbeat_interval_seconds=validated_interval,
            max_steps=validated_max_steps,
            control_request=raw_control,
        )):
            return 1
        return 1

    # Phase 12 — lock_exists_after
    try:
        lock_exists_after: Optional[bool] = bool(os.path.lexists(raw_lock_path))
    except Exception:
        if not _try_emit(_internal_error(
            lock_path=raw_lock_path,
            session_id=raw_session_id,
            heartbeat_interval_seconds=validated_interval,
            max_steps=validated_max_steps,
            control_request=raw_control,
        )):
            return 1
        return 1

    # Observations depuis le résultat adapter
    adapter_ok: bool = result.ok
    adapter_code_str: str = result.adapter_code.value
    sequence_ok: Optional[bool] = result.sequence_ok
    cleanup_ok: Optional[bool] = result.cleanup_ok
    first_failure_raw = result.first_failure

    cr = result.caller_result
    if cr is not None:
        steps_executed: int = cr.steps_executed
        terminated: bool = cr.terminated
        released: bool = cr.released
    else:
        steps_executed = 0
        terminated = False
        released = False

    # Détection bootstrap failure
    is_bootstrap = (
        adapter_code_str == "CALLER_FAILED"
        and sequence_ok is None
        and cleanup_ok is None
        and first_failure_raw is None
    )

    # Phase 13 — Postconditions
    postcond_msg: Optional[str] = None
    if cleanup_ok is True and not released:
        postcond_msg = "cleanup_ok=true mais released=false"
    elif released and lock_exists_after:
        postcond_msg = "released=true mais lock_exists_after=true"
    elif adapter_ok and cleanup_ok is not True:
        postcond_msg = "result.ok=true mais cleanup_ok != true"
    elif adapter_ok and not released:
        postcond_msg = "result.ok=true mais released=false"
    elif adapter_ok and lock_exists_after:
        postcond_msg = "result.ok=true mais lock_exists_after=true"
    elif is_bootstrap and lock_exists_after:
        postcond_msg = "bootstrap failure mais lock_exists_after=true"

    if postcond_msg is not None:
        env = _make_envelope(
            ok=False,
            adapter_code="POSTCONDITION_FAILED",
            lock_path=raw_lock_path,
            session_id=raw_session_id,
            heartbeat_interval_seconds=validated_interval,
            max_steps=validated_max_steps,
            control_request=raw_control,
            sequence_ok=sequence_ok,
            cleanup_ok=cleanup_ok,
            first_failure=_project_first_failure(first_failure_raw),
            steps_executed=steps_executed,
            terminated=terminated,
            released=released,
            lock_exists_after=lock_exists_after,
            detail="POSTCONDITION_FAILED",
        )
        if not _try_emit(env):
            return 1
        return 1

    # Phase 14-15 — Envelope finale
    env = _make_envelope(
        ok=adapter_ok,
        adapter_code=adapter_code_str,
        lock_path=raw_lock_path,
        session_id=raw_session_id,
        heartbeat_interval_seconds=validated_interval,
        max_steps=validated_max_steps,
        control_request=raw_control,
        sequence_ok=sequence_ok,
        cleanup_ok=cleanup_ok,
        first_failure=_project_first_failure(first_failure_raw),
        steps_executed=steps_executed,
        terminated=terminated,
        released=released,
        lock_exists_after=lock_exists_after,
        detail=result.detail,
    )

    # Phase 16 — Émission
    if not _try_emit(env):
        return 1

    return 0 if adapter_ok else 3


if __name__ == "__main__":
    raise SystemExit(main())

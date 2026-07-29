"""obsidia_session_inspect_cli — TERMINAL_SESSION_INSPECT_V0.

STATUS: IMPLEMENTATION
CANONICAL_NAME: TERMINAL_SESSION_INSPECT_V0
SCOPE: PUBLIC_READONLY_INSPECT_COMMAND_ONLY
PUBLIC_COMMAND: OBSIDIA_SESSION_INSPECT
LOCK_MUTATION: FORBIDDEN
REAL_EXECUTION: FORBIDDEN
OBSIDURE_WIRING: FORBIDDEN
KX108_INTEGRATION: DEFERRED
RECLAIM: FORBIDDEN

Usage:
    python scripts/obsidia_session_inspect_cli.py --lock-path "<chemin>"

Codes de retour :
    0  inspection réussie (result.ok=true), émission réussie
    1  erreur interne, ou canal stdout défaillant (OUTPUT_CHANNEL_FAILURE_FAIL_CLOSED)
    2  invocation invalide, émission réussie
    3  inspection exécutée mais result.ok=false, émission réussie

Invariants :
    - aucun subprocess, thread, asyncio, réseau, signal handler ;
    - aucune écriture, suppression, renommage de fichier ;
    - aucun reclaim, aucun classify_lock, aucune simulation ;
    - aucune lecture d'environnement, aucun accès Git ;
    - le seul accès fichier est celui de TerminalSessionAdapter.inspect_lock() ;
    - stderr toujours vide ;
    - stdout = exactement un objet JSON UTF-8.

authority: NONE | sovereign: false | decision_authority: KX108_ONLY
kx108_decision_present: false | simulated: false | isolated: true | wired: true
"""
from __future__ import annotations

import json
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Sequence

# ---------------------------------------------------------------------------
# Initialisation du chemin d'import
# Transforme uniquement l'emplacement interne du script, jamais lock_path.
# Ne lit aucune variable d'environnement. Ne dépend pas du répertoire courant.
# ---------------------------------------------------------------------------
_SCRIPT_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _SCRIPT_DIR.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from periphery.session_lock.terminal_session_adapter import (  # noqa: E402
    AdapterCode,
    TerminalSessionAdapter,
)

# ---------------------------------------------------------------------------
# Constantes publiques de la commande
# ---------------------------------------------------------------------------
_COMMAND = "obsidia session inspect"
_OPERATION = "INSPECT_LOCK"
_AUTHORITY = "NONE"
_SOVEREIGN = False
_DECISION_AUTHORITY = "KX108_ONLY"
_KX108_DECISION_PRESENT = False
_SIMULATED = False
_ISOLATED = True
_WIRED = True        # commande publique raccordée à l'adapter (documentaire)
_MUTATION_SCOPE = "NONE"


# ---------------------------------------------------------------------------
# Conversion JSON read-only (sans mutation de la source)
# dict/MappingProxyType → dict, tuple/list → list, scalaires inchangés.
# ---------------------------------------------------------------------------
def _to_json(value: object) -> object:
    if isinstance(value, Mapping):
        return {k: _to_json(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [_to_json(item) for item in value]
    return value


# ---------------------------------------------------------------------------
# Construction des envelopes publiques
# ---------------------------------------------------------------------------
def _envelope(
    ok: bool,
    adapter_code: str,
    lock_path: object,
    session_id: object,
    lock_record: object,
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
        "lock_record": lock_record,
        "simulated": _SIMULATED,
        "isolated": _ISOLATED,
        "wired": _WIRED,
        "mutation_scope": _MUTATION_SCOPE,
        "detail": detail,
    }


def _invocation_invalid_envelope(lock_path: object) -> dict:
    return _envelope(
        ok=False,
        adapter_code="INVOCATION_INVALID",
        lock_path=lock_path,
        session_id=None,
        lock_record=None,
        detail="INVOCATION_INVALID",
    )


def _internal_error_envelope(lock_path: object) -> dict:
    return _envelope(
        ok=False,
        adapter_code="INTERNAL_ERROR",
        lock_path=lock_path,
        session_id=None,
        lock_record=None,
        detail="INTERNAL_ERROR",
    )


# ---------------------------------------------------------------------------
# Émission JSON déterministe (stdout uniquement, stderr vide)
# OUTPUT_CHANNEL_FAILURE_FAIL_CLOSED : quand stdout est fermé ou défaillant,
# il est impossible de garantir un JSON sur stdout. L'exigence se réduit à :
# aucune exception échappée, aucun traceback, stderr vide, code retour 1.
# ---------------------------------------------------------------------------
def _try_emit(envelope: dict) -> bool:
    try:
        payload = json.dumps(
            envelope, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        )
        sys.stdout.write(payload + "\n")
        sys.stdout.flush()
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Parser manuel — forme canonique unique : --lock-path <valeur>
# Retourne (lock_path, None) ou (None, detail_erreur).
# ---------------------------------------------------------------------------
def _parse(argv: list[str]) -> tuple[str | None, str | None]:
    if not argv:
        return None, "INVOCATION_INVALID: no arguments"

    lock_path_val: str | None = None
    lock_path_count = 0
    i = 0
    while i < len(argv):
        token = argv[i]
        if token == "--lock-path":
            lock_path_count += 1
            if lock_path_count > 1:
                return None, "INVOCATION_INVALID: --lock-path dupliqué"
            i += 1
            if i >= len(argv):
                return None, "INVOCATION_INVALID: valeur manquante"
            val = argv[i]
            if val.startswith("--"):
                return None, "INVOCATION_INVALID: valeur manquante (option suivante détectée)"
            if not val:
                return None, "INVOCATION_INVALID: valeur vide"
            lock_path_val = val
            i += 1
        elif token.startswith("--lock-path="):
            return None, "INVOCATION_INVALID: forme --lock-path= non reconnue"
        elif token.startswith("--"):
            return None, "INVOCATION_INVALID: option inconnue"
        else:
            return None, "INVOCATION_INVALID: argument positionnel non autorisé"

    if lock_path_count == 0:
        return None, "INVOCATION_INVALID: --lock-path absent"

    return lock_path_val, None


# ---------------------------------------------------------------------------
# Point d'entrée
# ---------------------------------------------------------------------------
def main(argv: Sequence[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    argv_list = list(argv)

    # --- Parsing ---
    lock_path, parse_err = _parse(argv_list)
    if parse_err is not None:
        emitted = _try_emit(_invocation_invalid_envelope(None))
        return 2 if emitted else 1

    # --- Inspection (opération unique) ---
    try:
        result = TerminalSessionAdapter().inspect_lock(lock_path)
    except Exception:
        _try_emit(_internal_error_envelope(lock_path))  # OUTPUT_CHANNEL_FAILURE_FAIL_CLOSED
        return 1

    # --- Construction et émission de l'envelope ---
    try:
        lock_record_json = (
            _to_json(result.lock_record) if result.lock_record is not None else None
        )
        envelope = _envelope(
            ok=result.ok,
            adapter_code=result.adapter_code.value,
            lock_path=lock_path,
            session_id=result.session_id,
            lock_record=lock_record_json,
            detail=result.detail,
        )
    except Exception:
        _try_emit(_internal_error_envelope(lock_path))  # OUTPUT_CHANNEL_FAILURE_FAIL_CLOSED
        return 1

    emitted = _try_emit(envelope)
    if not emitted:
        return 1
    return 0 if result.ok else 3


if __name__ == "__main__":
    raise SystemExit(main())

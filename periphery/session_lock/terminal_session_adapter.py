"""terminal_session_adapter — TERMINAL_SESSION_ADAPTER_V0 APPROVED_AND_CLOSED.

STATUS: APPROVED_AND_CLOSED
CANONICAL_NAME: TERMINAL_SESSION_ADAPTER_V0
SCOPE: INTERNAL_ADAPTER_ONLY
PUBLIC_COMMANDS: NONE
REAL_EXECUTION: FORBIDDEN
OBSIDURE_WIRING: FORBIDDEN
KX108_INTEGRATION: DEFERRED
RECLAIM: FORBIDDEN

Adaptateur interne borné. Deux opérations uniquement :
    inspect_lock(lock_path)
    simulate_bounded_session(...)

Invariants absolus :
- aucun thread, processus, daemon, scheduler ;
- aucun réseau, subprocess, socket ;
- aucun appel à classify_lock, prepare_reclaim_proposal ou execute_reclaim ;
- configuration injectée explicitement — aucune valeur de production inventée ;
- mutation limitée à TEMP_LOCK_ONLY (lock_path injecté par l'appelant) ;
- aucune écriture JSONL — résultat structuré en mémoire uniquement ;
- aucun import de apps/, scripts/, sigma/, kernel/, Obsidure, Brody.

authority: NONE | sovereign: false | decision_authority: KX108_ONLY
kx108_decision_present: false | simulated: true | isolated: true | wired: false
No IO except the lock_path explicitly injected by the caller.
No network. No subprocess. No ACT. DECISION_AUTHORITY=KX108_ONLY.
"""
from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from types import MappingProxyType
from typing import Mapping, Optional

from periphery.session_lock.heartbeat_caller import (
    CallerResult,
    SynchronousHeartbeatCaller,
)
from periphery.session_lock.heartbeat_lock_manager import (
    ControlRequest,
    HeartbeatConfig,
    HeartbeatLockManager,
    OperationResult,
)

# ---------------------------------------------------------------------------
# Valeurs normatives documentaires (DECISION_AUTHORITY=KX108_ONLY)
# Ces constantes ne constituent aucune décision KX108 réelle.
# ---------------------------------------------------------------------------
_AUTHORITY = "NONE"
_SOVEREIGN = False
_DECISION_AUTHORITY = "KX108_ONLY"
_KX108_DECISION_PRESENT = False
_ISOLATED = True
_WIRED = False

_LOCK_REQUIRED_FIELDS = ("session_id", "lock_version", "created_at", "heartbeat_at")


class AdapterOperation(str, Enum):
    INSPECT_LOCK = "INSPECT_LOCK"
    SIMULATE_BOUNDED_SESSION = "SIMULATE_BOUNDED_SESSION"


class AdapterCode(str, Enum):
    OK = "OK"
    LOCK_NOT_FOUND = "LOCK_NOT_FOUND"
    LOCK_NOT_FILE = "LOCK_NOT_FILE"
    LOCK_READ_FAILED = "LOCK_READ_FAILED"
    LOCK_JSON_INVALID = "LOCK_JSON_INVALID"
    LOCK_SCHEMA_INVALID = "LOCK_SCHEMA_INVALID"
    INPUT_INVALID = "INPUT_INVALID"
    CALLER_FAILED = "CALLER_FAILED"


@dataclass(frozen=True)
class TerminalSessionAdapterResult:
    """Résultat immuable d'une opération de l'adaptateur.

    Les champs authority / sovereign / decision_authority / kx108_decision_present
    sont documentaires. Ils ne constituent aucune autorisation KX108 réelle.
    """
    operation: AdapterOperation
    ok: bool
    authority: str
    sovereign: bool
    decision_authority: str
    kx108_decision_present: bool
    session_id: Optional[str]
    lock_path: str
    caller_result: Optional[CallerResult]
    sequence_ok: Optional[bool]
    cleanup_ok: Optional[bool]
    first_failure: Optional[OperationResult]
    simulated: bool
    isolated: bool
    wired: bool
    mutation_scope: str
    lock_record: Optional[Mapping[str, object]]
    detail: str
    adapter_code: AdapterCode


# ---------------------------------------------------------------------------
# Helpers privés
# ---------------------------------------------------------------------------

def _coerce_lock_path(
    value: object,
) -> "tuple[Path, None] | tuple[None, str]":
    """Convertit lock_path en Path, fail-closed pour tout type invalide.

    Retourne (Path, None) en cas de succès, (None, message_erreur) sinon.
    N'accepte que str ou os.PathLike retournant str.
    Ne résout aucun symlink, ne crée aucun fichier, ne rend aucun chemin absolu.
    """
    if isinstance(value, str):
        if not value:
            return None, "lock_path vide"
        return Path(value), None
    if isinstance(value, os.PathLike):
        try:
            s = os.fspath(value)
        except TypeError as exc:
            return None, f"lock_path non convertible : {exc}"
        if not isinstance(s, str):
            return None, "lock_path.__fspath__ doit retourner str"
        if not s:
            return None, "lock_path vide"
        return Path(s), None
    return None, (
        f"lock_path doit être str ou os.PathLike, reçu : {type(value).__name__}"
    )


def _deep_freeze_json(value: object) -> object:
    """Gèle récursivement une valeur JSON en structures immuables.

    dict  → MappingProxyType (clés et valeurs gelées récursivement)
    list  → tuple (éléments gelés récursivement)
    other → inchangé (scalaires JSON : str, int, float, bool, None)
    """
    if isinstance(value, dict):
        return MappingProxyType(
            {k: _deep_freeze_json(v) for k, v in value.items()}
        )
    if isinstance(value, list):
        return tuple(_deep_freeze_json(item) for item in value)
    return value


class TerminalSessionAdapter:
    """Adaptateur interne borné — TERMINAL_SESSION_ADAPTER_V0.

    Constructeur sans argument et sans effet de bord.
    Ne lit aucun fichier, ne crée aucun lock, n'instancie aucun manager,
    ne démarre aucune opération, ne lit aucune variable d'environnement,
    n'inspecte aucun dépôt Git.

    Deux opérations internes :
        inspect_lock        — lecture seule, mutation_scope: NONE
        simulate_bounded_session — simulation bornée, mutation_scope: TEMP_LOCK_ONLY
    """

    # -----------------------------------------------------------------------
    # inspect_lock
    # -----------------------------------------------------------------------

    def inspect_lock(
        self,
        lock_path: "os.PathLike[str] | str",
    ) -> TerminalSessionAdapterResult:
        """Lecture seule du fichier JSON désigné par lock_path.

        Garanties :
        - aucune création, modification, suppression ou réparation de fichier ;
        - aucune instanciation de HeartbeatLockManager ou SynchronousHeartbeatCaller ;
        - aucun appel à classify_lock, prepare_reclaim_proposal ou execute_reclaim ;
        - mutation_scope: NONE.
        """
        path_obj, path_err = _coerce_lock_path(lock_path)
        path_str = str(path_obj) if path_obj is not None else ""

        def _fail(code: AdapterCode, detail: str) -> TerminalSessionAdapterResult:
            return TerminalSessionAdapterResult(
                operation=AdapterOperation.INSPECT_LOCK,
                ok=False,
                authority=_AUTHORITY,
                sovereign=_SOVEREIGN,
                decision_authority=_DECISION_AUTHORITY,
                kx108_decision_present=_KX108_DECISION_PRESENT,
                session_id=None,
                lock_path=path_str,
                caller_result=None,
                sequence_ok=None,
                cleanup_ok=None,
                first_failure=None,
                simulated=False,
                isolated=_ISOLATED,
                wired=_WIRED,
                mutation_scope="NONE",
                lock_record=None,
                detail=detail,
                adapter_code=code,
            )

        if path_obj is None:
            return _fail(AdapterCode.INPUT_INVALID, path_err)

        if not path_obj.exists():
            return _fail(AdapterCode.LOCK_NOT_FOUND, f"absent : {path_str}")

        if not path_obj.is_file():
            return _fail(AdapterCode.LOCK_NOT_FILE, f"non fichier : {path_str}")

        try:
            raw = path_obj.read_bytes()
        except OSError as exc:
            return _fail(AdapterCode.LOCK_READ_FAILED, f"lecture échouée : {exc}")

        try:
            data = json.loads(raw)
        except (json.JSONDecodeError, ValueError) as exc:
            return _fail(AdapterCode.LOCK_JSON_INVALID, f"JSON invalide : {exc}")

        if not isinstance(data, dict):
            return _fail(AdapterCode.LOCK_JSON_INVALID, "JSON racine non objet")

        for fname in _LOCK_REQUIRED_FIELDS:
            if fname not in data:
                return _fail(
                    AdapterCode.LOCK_SCHEMA_INVALID,
                    f"champ manquant : {fname}",
                )

        sid = data.get("session_id")
        if not isinstance(sid, str) or not sid:
            return _fail(AdapterCode.LOCK_SCHEMA_INVALID, "session_id invalide")

        lv = data.get("lock_version")
        if not isinstance(lv, str) or not lv:
            return _fail(AdapterCode.LOCK_SCHEMA_INVALID, "lock_version invalide")

        for num_f in ("created_at", "heartbeat_at"):
            val = data.get(num_f)
            if isinstance(val, bool) or not isinstance(val, (int, float)):
                return _fail(
                    AdapterCode.LOCK_SCHEMA_INVALID,
                    f"{num_f} doit être int ou float non booléen",
                )
            if not math.isfinite(val):
                return _fail(
                    AdapterCode.LOCK_SCHEMA_INVALID,
                    f"{num_f} doit être fini (reçu : {val})",
                )

        return TerminalSessionAdapterResult(
            operation=AdapterOperation.INSPECT_LOCK,
            ok=True,
            authority=_AUTHORITY,
            sovereign=_SOVEREIGN,
            decision_authority=_DECISION_AUTHORITY,
            kx108_decision_present=_KX108_DECISION_PRESENT,
            session_id=sid,
            lock_path=path_str,
            caller_result=None,
            sequence_ok=None,
            cleanup_ok=None,
            first_failure=None,
            simulated=False,
            isolated=_ISOLATED,
            wired=_WIRED,
            mutation_scope="NONE",
            lock_record=_deep_freeze_json(data),
            detail="INSPECT_OK",
            adapter_code=AdapterCode.OK,
        )

    # -----------------------------------------------------------------------
    # simulate_bounded_session
    # -----------------------------------------------------------------------

    def simulate_bounded_session(
        self,
        *,
        lock_path: "os.PathLike[str] | str",
        session_id: str,
        heartbeat_config: HeartbeatConfig,
        max_steps: int,
        control_request: Optional[ControlRequest] = None,
    ) -> TerminalSessionAdapterResult:
        """Simulation bornée d'une session.

        Toutes les valeurs sont injectées explicitement.
        Aucune valeur de production inventée.
        N'appelle jamais classify_lock, prepare_reclaim_proposal ou execute_reclaim.
        mutation_scope: TEMP_LOCK_ONLY représente le périmètre de mutation autorisé.
        """
        path_obj, path_err = _coerce_lock_path(lock_path)
        path_str = str(path_obj) if path_obj is not None else ""

        def _input_fail(detail: str) -> TerminalSessionAdapterResult:
            return TerminalSessionAdapterResult(
                operation=AdapterOperation.SIMULATE_BOUNDED_SESSION,
                ok=False,
                authority=_AUTHORITY,
                sovereign=_SOVEREIGN,
                decision_authority=_DECISION_AUTHORITY,
                kx108_decision_present=_KX108_DECISION_PRESENT,
                session_id=None,
                lock_path=path_str,
                caller_result=None,
                sequence_ok=None,
                cleanup_ok=None,
                first_failure=None,
                simulated=True,
                isolated=_ISOLATED,
                wired=_WIRED,
                mutation_scope="NONE",
                lock_record=None,
                detail=detail,
                adapter_code=AdapterCode.INPUT_INVALID,
            )

        if path_obj is None:
            return _input_fail(path_err)

        if not isinstance(session_id, str) or not session_id:
            return _input_fail("session_id doit être une chaîne non vide")

        if not isinstance(heartbeat_config, HeartbeatConfig):
            return _input_fail("heartbeat_config doit être HeartbeatConfig")

        # Validation de la config avant toute construction du manager
        if heartbeat_config.enabled is not True:
            return _input_fail("heartbeat_config.enabled doit être True")

        interval = heartbeat_config.heartbeat_interval_seconds
        if isinstance(interval, bool) or not isinstance(interval, (int, float)):
            return _input_fail(
                "heartbeat_interval_seconds doit être int ou float non booléen"
            )
        if interval <= 0 or not math.isfinite(interval):
            return _input_fail(
                "heartbeat_interval_seconds doit être strictement positif et fini"
            )

        if isinstance(max_steps, bool) or not isinstance(max_steps, int) or max_steps <= 0:
            return _input_fail("max_steps doit être un entier strictement positif")

        if control_request is not None and not isinstance(control_request, ControlRequest):
            return _input_fail(
                "control_request doit être ControlRequest.STOP, ABORT ou None"
            )

        manager = HeartbeatLockManager(
            config=heartbeat_config,
            lock_path=path_obj,
            session_id=session_id,
        )
        caller = SynchronousHeartbeatCaller(manager)
        caller_result = caller.run_bounded(
            max_steps=max_steps,
            control_request=control_request,
        )

        return TerminalSessionAdapterResult(
            operation=AdapterOperation.SIMULATE_BOUNDED_SESSION,
            ok=caller_result.ok,
            authority=_AUTHORITY,
            sovereign=_SOVEREIGN,
            decision_authority=_DECISION_AUTHORITY,
            kx108_decision_present=_KX108_DECISION_PRESENT,
            session_id=session_id,
            lock_path=path_str,
            caller_result=caller_result,
            sequence_ok=caller_result.sequence_ok,
            cleanup_ok=caller_result.cleanup_ok,
            first_failure=caller_result.first_failure,
            simulated=True,
            isolated=_ISOLATED,
            wired=_WIRED,
            mutation_scope="TEMP_LOCK_ONLY",
            lock_record=None,
            detail=caller_result.detail,
            adapter_code=(
                AdapterCode.OK if caller_result.ok else AdapterCode.CALLER_FAILED
            ),
        )

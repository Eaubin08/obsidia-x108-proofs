"""heartbeat_lock_manager — PALIER_PROPOSAL_GUARD_RECLAIM_FIX_V17 PART_A_REV10.

Composant isolé periphery/session_lock. Implémente les machines d'états et
transactions normatives des SECTION_12 (boucle heartbeat), SECTION_13
(release de session) et SECTION_14 (reclaim d'un lock stale) de la
spécification PART_A_REV10 approuvée humainement (APPROVED_AND_CLOSED).

Invariants absolus (spécification + mandat IMPLEMENT_BOUNDED) :
- disabled by default : sans configuration explicitement activée, toute
  opération retourne un résultat fail-closed sans mutation ;
- aucun wiring runtime : aucun thread lancé ici, aucun import de apps/,
  scripts/, sigma/, kernel ; la boucle est pilotée explicitement par un
  appelant futur (PART_B, non autorisé) ;
- aucun reclaim réel : la SECTION_14 est implémentée jusqu'à la porte
  d'autorisation et la préparation d'une proposition ; toute mutation
  réelle (suppression du lock JSON par reclaim) est structurellement
  refusée (real_stale_lock_reclaim: NOT_AUTHORIZED) ;
- paramètres non inventables : HEARTBEAT_INTERVAL_SECONDS,
  MAX_V2_FUTURE_CLOCK_SKEW_SECONDS et
  HUMAN_APPROVED_CORRECTED_GF_R01_SHA256 n'ont AUCUNE valeur par défaut ;
  leur absence produit un comportement désactivé / fail-closed ;
- toute ambiguïté produit FAIL_CLOSED + HUMAN_RECOVERY_DECISION_REQUIRED.

No IO except the session lock JSON explicitly owned by this component.
No network. No subprocess. No ACT. DECISION_AUTHORITY=KX108_ONLY.
"""
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Optional


# ---------------------------------------------------------------------------
# États et codes normatifs
# ---------------------------------------------------------------------------

class HeartbeatRuntimeState(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    ACTIVE_WAITING = "ACTIVE_WAITING"
    CONTROL_PENDING = "CONTROL_PENDING"
    ACTIVE_TICK = "ACTIVE_TICK"
    STOPPING = "STOPPING"
    ABORTING = "ABORTING"
    FAULTED = "FAULTED"


class TickAdmissionState(str, Enum):
    IDLE = "IDLE"
    ADMITTED = "ADMITTED"


class HandoffAction(str, Enum):
    CONSUME_CONTROL = "CONSUME_CONTROL"
    RESUME_WAIT = "RESUME_WAIT"


class ControlRequest(str, Enum):
    STOP = "STOP"
    ABORT = "ABORT"


class LockClassification(str, Enum):
    ACTIVE = "ACTIVE"
    STALE_CANDIDATE = "STALE_CANDIDATE"
    FUTURE_TIMESTAMP_BEYOND_SKEW = "FUTURE_TIMESTAMP_BEYOND_SKEW"
    ABSENT = "ABSENT"
    CORRUPTED = "CORRUPTED"
    INCOMPLETE = "INCOMPLETE"
    UNCLASSIFIABLE_FAIL_CLOSED = "UNCLASSIFIABLE_FAIL_CLOSED"


class FailureCode(str, Enum):
    # composant / configuration
    MANAGER_DISABLED = "MANAGER_DISABLED"
    HEARTBEAT_CONFIG_MISSING = "HEARTBEAT_CONFIG_MISSING"
    # SECTION_12
    HEARTBEAT_RUNTIME_CONTROL_CONSUMPTION_STATE_INVALID = (
        "HEARTBEAT_RUNTIME_CONTROL_CONSUMPTION_STATE_INVALID"
    )
    HEARTBEAT_RUNTIME_TERMINATION_STATE_INVALID = (
        "HEARTBEAT_RUNTIME_TERMINATION_STATE_INVALID"
    )
    POST_ACTIVATION_HEARTBEAT_FAULT = "POST_ACTIVATION_HEARTBEAT_FAULT"
    HEARTBEAT_LOCK_IDENTITY_MISMATCH = "HEARTBEAT_LOCK_IDENTITY_MISMATCH"
    # SECTION_13
    RELEASE_SESSION_STATE_INVALID = "RELEASE_SESSION_STATE_INVALID"
    RELEASE_HEARTBEAT_NOT_QUIESCENT = "RELEASE_HEARTBEAT_NOT_QUIESCENT"
    RELEASE_LOCK_STATE_MISMATCH = "RELEASE_LOCK_STATE_MISMATCH"
    RELEASE_LOCK_DELETE_FAILED = "RELEASE_LOCK_DELETE_FAILED"
    RELEASE_TARGET_HANDLE_CLOSE_FAILED = "RELEASE_TARGET_HANDLE_CLOSE_FAILED"
    RELEASE_ARBITRATION_LOCK_RELEASE_FAILED = (
        "RELEASE_ARBITRATION_LOCK_RELEASE_FAILED"
    )
    # SECTION_14
    RECLAIM_AUTHORIZATION_INVALID = "RECLAIM_AUTHORIZATION_INVALID"
    RECLAIM_LOCK_STATE_MISMATCH = "RECLAIM_LOCK_STATE_MISMATCH"
    RECLAIM_VERSION_POLICY_FAILED = "RECLAIM_VERSION_POLICY_FAILED"
    RECLAIM_REAL_EXECUTION_NOT_AUTHORIZED = (
        "RECLAIM_REAL_EXECUTION_NOT_AUTHORIZED"
    )


RELEASE_ALLOWED_STATES = frozenset({
    HeartbeatRuntimeState.ACTIVE_WAITING,
    HeartbeatRuntimeState.CONTROL_PENDING,
    HeartbeatRuntimeState.STOPPING,
    HeartbeatRuntimeState.ABORTING,
    HeartbeatRuntimeState.FAULTED,
})

CONSUMPTION_ALLOWED_STATES = frozenset({
    HeartbeatRuntimeState.ACTIVE_WAITING,
    HeartbeatRuntimeState.CONTROL_PENDING,
})

TERMINAL_DRAIN_ALLOWED_STATES = frozenset({
    HeartbeatRuntimeState.STOPPING,
    HeartbeatRuntimeState.ABORTING,
})

# Champs obligatoires du lock JSON (identité + heartbeat).
LOCK_REQUIRED_FIELDS = ("session_id", "lock_version", "created_at", "heartbeat_at")

# real_stale_lock_reclaim: NOT_AUTHORIZED (PART_A_REV10, statut final).
# Aucune configuration ne peut activer l'exécution réelle du reclaim :
# ce verrou est structurel et relève d'un futur palier (PART_B, non autorisé).
REAL_RECLAIM_EXECUTION_AUTHORIZED = False


@dataclass(frozen=True)
class HeartbeatConfig:
    """Configuration du manager. Tous les paramètres normatifs sont sans
    valeur par défaut : None signifie « non fourni par décision humaine »."""
    enabled: bool = False
    heartbeat_interval_seconds: Optional[float] = None
    max_v2_future_clock_skew_seconds: Optional[float] = None
    human_approved_corrected_gf_r01_sha256: Optional[str] = None


@dataclass(frozen=True)
class OperationResult:
    """Résultat déterministe d'une opération. Jamais d'exception silencieuse :
    tout refus est un résultat fail-closed explicite."""
    ok: bool
    code: Optional[FailureCode] = None
    fail_closed: bool = False
    human_recovery_required: bool = False
    detail: str = ""
    payload: dict = field(default_factory=dict)

    @staticmethod
    def success(detail: str = "", **payload: Any) -> "OperationResult":
        return OperationResult(ok=True, detail=detail, payload=dict(payload))

    @staticmethod
    def failure(code: FailureCode, detail: str = "",
                human: bool = True, **payload: Any) -> "OperationResult":
        return OperationResult(
            ok=False, code=code, fail_closed=True,
            human_recovery_required=human, detail=detail, payload=dict(payload),
        )


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class HeartbeatLockManager:
    """Gestionnaire heartbeat / session lock — PART_A isolée.

    Pilotage explicite (aucun thread) : l'appelant invoque les transitions.
    Le lock JSON est le seul fichier que ce composant possède ; son identité
    (bytes exacts) est validée avant toute mutation (SECTION_12/13).
    """

    def __init__(
        self,
        config: HeartbeatConfig,
        lock_path: os.PathLike,
        session_id: str,
        clock: Optional[Callable[[], float]] = None,
    ) -> None:
        self._config = config
        self._lock_path = Path(lock_path)
        self._session_id = session_id
        self._clock = clock if clock is not None else _default_clock
        # SECTION_12 — état runtime
        self.runtime_state = HeartbeatRuntimeState.NOT_STARTED
        self.tick_admission_state = TickAdmissionState.IDLE
        self.tick_in_progress = False
        self.level1_locked = False
        self.level2_locked = False
        # requête de contrôle (STOP/ABORT)
        self.control_request: Optional[ControlRequest] = None
        self.control_request_pending = False
        self.control_consumed: Optional[ControlRequest] = None
        self.control_consumed_sequence = 0
        # terminaison
        self.termination_committed = False
        self.termination_reason: Optional[str] = None
        self.terminal_event = False
        self.periodic_loop_terminated = False
        # faute
        self.runtime_fault: Optional[str] = None
        self.secondary_faults: list = []
        # identité attendue du lock (SECTION_12 bootstrap)
        self.expected_lock_bytes: Optional[bytes] = None
        self.heartbeat_last_committed_at: Optional[float] = None
        # SECTION_13 — session / Level 3
        self.session_level3_owned = False
        self.session_target_handle_resource: Optional[object] = None
        self.session_target_handle_resource_owner = "NONE"
        self.session_target_handle_resource_closed = False
        self.session_level3_release_confirmed = False
        self.session_release_state = "NOT_RELEASED"
        self.session_release_completed = False

    # -- garde de désactivation ---------------------------------------------

    def _gate(self) -> Optional[OperationResult]:
        if not self._config.enabled:
            return OperationResult.failure(
                FailureCode.MANAGER_DISABLED,
                "manager disabled by default — activation humaine requise",
                human=False,
            )
        if self._config.heartbeat_interval_seconds is None:
            return OperationResult.failure(
                FailureCode.HEARTBEAT_CONFIG_MISSING,
                "HEARTBEAT_INTERVAL_SECONDS absent — manager non activable",
                human=False,
            )
        return None

    # -- SECTION_12 : bootstrap, tick, contrôle, terminaison, faute ----------

    def acquire_session_lock(self) -> OperationResult:
        """Bootstrap : crée le lock JSON de la session et prend possession du
        Level 3 session-scoped. Refuse si un lock existe déjà (pas d'écrasement)."""
        gated = self._gate()
        if gated:
            return gated
        if self.runtime_state is not HeartbeatRuntimeState.NOT_STARTED:
            return OperationResult.failure(
                FailureCode.HEARTBEAT_RUNTIME_TERMINATION_STATE_INVALID,
                f"acquire refusé depuis {self.runtime_state.value}",
            )
        if self._lock_path.exists():
            return OperationResult.failure(
                FailureCode.HEARTBEAT_LOCK_IDENTITY_MISMATCH,
                "lock JSON déjà présent — aucun écrasement",
            )
        now = self._clock()
        record = {
            "session_id": self._session_id,
            "lock_version": "V2",
            "created_at": now,
            "heartbeat_at": now,
        }
        data = json.dumps(record, sort_keys=True).encode("utf-8")
        self._lock_path.write_bytes(data)
        self.expected_lock_bytes = data
        self.heartbeat_last_committed_at = now
        self.session_level3_owned = True
        self.session_target_handle_resource = object()
        self.session_target_handle_resource_owner = "SESSION"
        self.runtime_state = HeartbeatRuntimeState.ACTIVE_WAITING
        return OperationResult.success("session lock acquired", heartbeat_at=now)

    def _validate_lock_identity(self) -> Optional[OperationResult]:
        """Identité du lock validée avant toute mutation (bytes exacts)."""
        if not self._lock_path.exists():
            return OperationResult.failure(
                FailureCode.HEARTBEAT_LOCK_IDENTITY_MISMATCH,
                "lock JSON absent",
            )
        current = self._lock_path.read_bytes()
        if current != self.expected_lock_bytes:
            return OperationResult.failure(
                FailureCode.HEARTBEAT_LOCK_IDENTITY_MISMATCH,
                "bytes du lock JSON différents de l'identité attendue",
            )
        return None

    def heartbeat_tick(self) -> OperationResult:
        """Un tick explicite : admission, validation d'identité, commit du
        heartbeat_at, handoff post-tick (PART_B1_LOCK_SCOPE_FIX)."""
        gated = self._gate()
        if gated:
            return gated
        if self.runtime_state not in (
            HeartbeatRuntimeState.ACTIVE_WAITING,
            HeartbeatRuntimeState.CONTROL_PENDING,
        ):
            return OperationResult.failure(
                FailureCode.HEARTBEAT_RUNTIME_TERMINATION_STATE_INVALID,
                f"tick refusé depuis {self.runtime_state.value}",
            )
        mism = self._validate_lock_identity()
        if mism:
            return self._enter_fault(mism)
        # admission
        self.tick_admission_state = TickAdmissionState.ADMITTED
        self.tick_in_progress = True
        self.runtime_state = HeartbeatRuntimeState.ACTIVE_TICK
        # commit heartbeat
        now = self._clock()
        record = json.loads(self.expected_lock_bytes.decode("utf-8"))
        record["heartbeat_at"] = now
        data = json.dumps(record, sort_keys=True).encode("utf-8")
        self._lock_path.write_bytes(data)
        self.expected_lock_bytes = data
        self.heartbeat_last_committed_at = now
        # HEARTBEAT_POST_TICK_HANDOFF (PART_B1 + LOCK_SCOPE_FIX) —
        # décision et transition sous la même section critique logique.
        assert self.tick_admission_state is TickAdmissionState.ADMITTED
        assert self.tick_in_progress is True
        assert self.level1_locked is False
        assert self.level2_locked is False
        self.tick_admission_state = TickAdmissionState.IDLE
        self.tick_in_progress = False
        if self.control_request_pending:
            self.runtime_state = HeartbeatRuntimeState.CONTROL_PENDING
            handoff = HandoffAction.CONSUME_CONTROL
        else:
            self.runtime_state = HeartbeatRuntimeState.ACTIVE_WAITING
            handoff = HandoffAction.RESUME_WAIT
        return OperationResult.success(
            "tick committed", heartbeat_at=now, handoff_action=handoff.value,
        )

    def request_control(self, request: ControlRequest) -> OperationResult:
        """Publie une requête STOP/ABORT. En ACTIVE_TICK la consommation est
        FORBIDDEN : la requête demeure pendante (routage post-tick)."""
        gated = self._gate()
        if gated:
            return gated
        self.control_request = request
        self.control_request_pending = True
        return OperationResult.success("control request published",
                                       request=request.value)

    def consume_control(self) -> OperationResult:
        """RUNTIME_CONTROL_CONSUMPTION_STATE_DOMAIN_CORRECTION :
        consommation uniquement en ACTIVE_WAITING / CONTROL_PENDING ;
        ACTIVE_TICK → FORBIDDEN (requête préservée) ;
        tout autre état → CONSUMPTION_STATE_INVALID, FAIL_CLOSED sans mutation."""
        gated = self._gate()
        if gated:
            return gated
        if self.runtime_state is HeartbeatRuntimeState.ACTIVE_TICK:
            # consommation FORBIDDEN — requête et pending inchangés
            return OperationResult.failure(
                FailureCode.HEARTBEAT_RUNTIME_CONTROL_CONSUMPTION_STATE_INVALID,
                "consommation interdite en ACTIVE_TICK — routage post-tick",
                human=False, routed_to="HEARTBEAT_POST_TICK_CONTROL_HANDOFF",
            )
        if self.runtime_state not in CONSUMPTION_ALLOWED_STATES:
            # aucun des cinq champs de contrôle n'est modifié
            return OperationResult.failure(
                FailureCode.HEARTBEAT_RUNTIME_CONTROL_CONSUMPTION_STATE_INVALID,
                f"consommation invalide depuis {self.runtime_state.value}",
            )
        if not self.control_request_pending or self.control_request is None:
            return OperationResult.failure(
                FailureCode.HEARTBEAT_RUNTIME_CONTROL_CONSUMPTION_STATE_INVALID,
                "aucune requête pendante",
            )
        consumed = self.control_request
        self.control_consumed = consumed
        self.control_consumed_sequence += 1
        self.control_request = None
        self.control_request_pending = False
        self.runtime_state = (
            HeartbeatRuntimeState.STOPPING
            if consumed is ControlRequest.STOP
            else HeartbeatRuntimeState.ABORTING
        )
        return OperationResult.success("control consumed", consumed=consumed.value)

    def commit_termination(self) -> OperationResult:
        """RUNTIME_TERMINATION_DRAIN_STATE_DOMAIN + FAIL_CLOSED_NO_FALLTHROUGH :
        drain terminal et commit uniquement depuis STOPPING/ABORTING."""
        gated = self._gate()
        if gated:
            return gated
        if self.runtime_state not in TERMINAL_DRAIN_ALLOWED_STATES:
            # termination_committed demeure false ; aucune requête modifiée ;
            # aucun terminal_event positionné
            return OperationResult.failure(
                FailureCode.HEARTBEAT_RUNTIME_TERMINATION_STATE_INVALID,
                f"drain refusé depuis {self.runtime_state.value}",
            )
        runtime_state_valid = True
        control_state_consistent = (
            (self.control_request is None) == (not self.control_request_pending)
        )
        visible_request_classified = self.control_consumed is not None
        terminal_drain_failure = None
        if not (runtime_state_valid and control_state_consistent
                and visible_request_classified
                and terminal_drain_failure is None):
            return OperationResult.failure(
                FailureCode.HEARTBEAT_RUNTIME_TERMINATION_STATE_INVALID,
                "conditions de commit terminal non réunies",
            )
        self.termination_committed = True
        # HEARTBEAT_NORMAL_RUNTIME_TERMINATION
        if self.tick_in_progress or self.level1_locked or self.level2_locked:
            self.termination_committed = False
            return OperationResult.failure(
                FailureCode.HEARTBEAT_RUNTIME_TERMINATION_STATE_INVALID,
                "tick en cours ou verrou d'arbitrage détenu",
            )
        self.periodic_loop_terminated = True
        self.terminal_event = True
        # jamais : suppression du lock JSON, auto-reclaim, toucher au Level 3
        return OperationResult.success("normal termination committed")

    def _enter_fault(self, cause: OperationResult) -> OperationResult:
        """HEARTBEAT_POST_ACTIVATION_FAULT_STATE + FAULT_CLEANUP."""
        if self.runtime_fault is None:
            self.runtime_fault = f"{cause.code.value}: {cause.detail}"
        else:
            self.secondary_faults.append(f"{cause.code.value}: {cause.detail}")
        self.runtime_state = HeartbeatRuntimeState.FAULTED
        self.termination_reason = "POST_ACTIVATION_HEARTBEAT_FAULT"
        self.periodic_loop_terminated = True
        # cleanup : Level 1 / Level 2 (jamais le Level 3 session-scoped,
        # jamais le lock JSON, jamais session_target_handle_resource)
        self.level2_locked = False
        self.level1_locked = False
        self.terminal_event = True
        return OperationResult.failure(
            FailureCode.POST_ACTIVATION_HEARTBEAT_FAULT,
            self.runtime_fault,
        )

    # -- classification du lock (support SECTION_14, lecture seule) ----------

    def classify_lock(self) -> OperationResult:
        """Classification READ-ONLY du lock JSON. Aucune mutation, jamais.
        L'absence de MAX_V2_FUTURE_CLOCK_SKEW_SECONDS rend la branche
        « horodatage futur » inclassifiable → fail-closed."""
        gated = self._gate()
        if gated:
            return gated
        if not self._lock_path.exists():
            return OperationResult.success(
                "lock absent", classification=LockClassification.ABSENT.value)
        raw = self._lock_path.read_bytes()
        try:
            record = json.loads(raw.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return OperationResult.success(
                "lock corrompu",
                classification=LockClassification.CORRUPTED.value)
        if not isinstance(record, dict) or any(
                k not in record for k in LOCK_REQUIRED_FIELDS):
            return OperationResult.success(
                "lock incomplet",
                classification=LockClassification.INCOMPLETE.value)
        now = self._clock()
        interval = self._config.heartbeat_interval_seconds
        heartbeat_at = record["heartbeat_at"]
        if not isinstance(heartbeat_at, (int, float)):
            return OperationResult.success(
                "heartbeat_at non numérique",
                classification=LockClassification.CORRUPTED.value)
        if heartbeat_at > now:
            skew = self._config.max_v2_future_clock_skew_seconds
            if skew is None:
                # paramètre humain absent : classification impossible → fail-closed
                return OperationResult.failure(
                    FailureCode.RECLAIM_AUTHORIZATION_INVALID,
                    "MAX_V2_FUTURE_CLOCK_SKEW_SECONDS absent — "
                    "horodatage futur inclassifiable",
                    classification=LockClassification
                    .UNCLASSIFIABLE_FAIL_CLOSED.value,
                )
            if heartbeat_at - now > skew:
                return OperationResult.success(
                    "horodatage futur au-delà du skew",
                    classification=LockClassification
                    .FUTURE_TIMESTAMP_BEYOND_SKEW.value)
            return OperationResult.success(
                "horodatage futur dans le skew",
                classification=LockClassification.ACTIVE.value)
        if now - heartbeat_at <= 2 * interval:
            return OperationResult.success(
                "heartbeat valide",
                classification=LockClassification.ACTIVE.value)
        return OperationResult.success(
            "candidat stale",
            classification=LockClassification.STALE_CANDIDATE.value,
            age_seconds=now - heartbeat_at)

    # -- SECTION_13 : release de session (A → H) ------------------------------

    def release_session(self) -> OperationResult:
        gated = self._gate()
        if gated:
            return gated
        # PART_A — RELEASE_SESSION_ENTRY_GUARD
        if self.runtime_state not in RELEASE_ALLOWED_STATES:
            return OperationResult.failure(
                FailureCode.RELEASE_SESSION_STATE_INVALID,
                f"release refusé depuis {self.runtime_state.value}")
        if not (self.session_target_handle_resource is not None
                and self.session_target_handle_resource_owner == "SESSION"
                and self.session_level3_owned):
            return OperationResult.failure(
                FailureCode.RELEASE_SESSION_STATE_INVALID,
                "préconditions de session non réunies")
        # PART_B — RELEASE_HEARTBEAT_QUIESCENCE_GATE
        if self.tick_in_progress or self.level1_locked or self.level2_locked:
            return OperationResult.failure(
                FailureCode.RELEASE_HEARTBEAT_NOT_QUIESCENT,
                "heartbeat non quiescent")
        # PART_C — RELEASE_LOCK_ACQUISITION_ORDER (Level 1 puis Level 2 borné ;
        # le Level 3 déjà détenu par la session est consommé, jamais réacquis)
        self.level1_locked = True
        self.level2_locked = True
        try:
            # PART_D — RELEASE_LOCK_STATE_VALIDATION
            if not self._lock_path.exists():
                return self._release_mismatch("lock JSON absent")
            current = self._lock_path.read_bytes()
            if current != self.expected_lock_bytes:
                return self._release_mismatch("bytes courants != attendus")
            record = json.loads(current.decode("utf-8"))
            if record.get("session_id") != self._session_id:
                return self._release_mismatch("session_id différent")
            if record.get("heartbeat_at") != self.heartbeat_last_committed_at:
                return self._release_mismatch(
                    "heartbeat_at != heartbeat_last_committed_at")
            # PART_E — RELEASE_LOCK_JSON_DELETE_TRANSACTION
            # revalidation immédiatement avant unlink (pas de prévalidation
            # suivie d'un unlink permissif)
            if self._lock_path.read_bytes() != self.expected_lock_bytes:
                return self._release_mismatch("objet remplacé avant suppression")
            try:
                self._lock_path.unlink()
            except OSError as exc:
                return OperationResult.failure(
                    FailureCode.RELEASE_LOCK_DELETE_FAILED, str(exc))
            # durabilité du répertoire parent (best effort portable) +
            # vérification d'absence prouvée
            _fsync_dir(self._lock_path.parent)
            if self._lock_path.exists():
                return OperationResult.failure(
                    FailureCode.RELEASE_LOCK_DELETE_FAILED,
                    "le chemin du lock JSON est encore présent")
            # PART_F — RELEASE_SESSION_TARGET_HANDLE_CLOSE
            self.session_target_handle_resource = None
            self.session_target_handle_resource_owner = "NONE"
            self.session_target_handle_resource_closed = True
            self.session_level3_owned = False
            self.session_level3_release_confirmed = True
        finally:
            # PART_G — RELEASE_ARBITRATION_LOCKS (Level 2 puis Level 1 ;
            # tentés même en cas de faute, fautes secondaires préservées)
            self.level2_locked = False
            self.level1_locked = False
        # PART_H — RELEASE_SESSION_FINALIZATION
        if (self.level1_locked or self.level2_locked
                or self.session_level3_owned
                or self.session_target_handle_resource is not None
                or self._lock_path.exists()):
            return OperationResult.failure(
                FailureCode.RELEASE_SESSION_STATE_INVALID,
                "postconditions de RELEASED non réunies")
        self.session_release_state = "RELEASED"
        self.session_release_completed = True
        return OperationResult.success("RELEASED")

    def _release_mismatch(self, detail: str) -> OperationResult:
        # aucune suppression, aucune fermeture du target handle,
        # aucune libération du Level 3
        return OperationResult.failure(
            FailureCode.RELEASE_LOCK_STATE_MISMATCH, detail)

    # -- SECTION_14 : reclaim (porte d'autorisation + proposition seulement) --

    def prepare_reclaim_proposal(
        self,
        authorization_proof: Optional[dict] = None,
    ) -> OperationResult:
        """RECLAIM_AUTHORIZATION_ENTRY_GATE (PART_A de SECTION_14).

        Vérifie la porte d'autorisation et, si elle est satisfaite, prépare
        une PROPOSITION de reclaim (readonly). N'exécute JAMAIS le reclaim
        réel : real_stale_lock_reclaim est NOT_AUTHORIZED au niveau du
        palier — voir execute_reclaim()."""
        gated = self._gate()
        if gated:
            return gated
        if not self._lock_path.exists():
            return OperationResult.failure(
                FailureCode.RECLAIM_AUTHORIZATION_INVALID,
                "lock JSON absent — rien à réclamer")
        raw = self._lock_path.read_bytes()
        try:
            record = json.loads(raw.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return OperationResult.failure(
                FailureCode.RECLAIM_AUTHORIZATION_INVALID,
                "lock JSON corrompu — classification humaine requise")
        version = record.get("lock_version")
        if version not in ("V1", "V2"):
            return OperationResult.failure(
                FailureCode.RECLAIM_AUTHORIZATION_INVALID,
                f"version de lock non reconnue: {version!r}")
        # exigences communes : GF_R01 approuvé humainement
        gf = self._config.human_approved_corrected_gf_r01_sha256
        if not gf:
            return OperationResult.failure(
                FailureCode.RECLAIM_AUTHORIZATION_INVALID,
                "HUMAN_APPROVED_CORRECTED_GF_R01_SHA256 indisponible — "
                "tout reclaim réel interdit")
        # V2 exige le skew ; V1 exige la référence de quiescence legacy
        if version == "V2" and self._config.max_v2_future_clock_skew_seconds is None:
            return OperationResult.failure(
                FailureCode.RECLAIM_AUTHORIZATION_INVALID,
                "MAX_V2_FUTURE_CLOCK_SKEW_SECONDS indisponible — reclaim V2 interdit")
        proof = authorization_proof or {}
        required_proof_fields = (
            "approval_id", "repository_path_hash", "orphan_session_id",
            "authorized_reason", "issued_at", "expires_at",
        )
        missing = [f for f in required_proof_fields if f not in proof]
        if missing:
            return OperationResult.failure(
                FailureCode.RECLAIM_AUTHORIZATION_INVALID,
                f"preuve d'autorisation incomplète: {missing}")
        if version == "V1" and proof.get("legacy_quiescence_decision_ref") != \
                "CONFIRMER_QUIESCENCE_GUARD_LEGACY":
            return OperationResult.failure(
                FailureCode.RECLAIM_AUTHORIZATION_INVALID,
                "legacy_quiescence_decision_ref invalide pour V1")
        now = self._clock()
        if not (isinstance(proof.get("expires_at"), (int, float))
                and proof["expires_at"] >= now):
            return OperationResult.failure(
                FailureCode.RECLAIM_AUTHORIZATION_INVALID,
                "preuve expirée ou expires_at invalide")
        if proof.get("orphan_session_id") != record.get("session_id"):
            return OperationResult.failure(
                FailureCode.RECLAIM_LOCK_STATE_MISMATCH,
                "orphan_session_id ne correspond pas au lock")
        # Porte satisfaite : proposition readonly, aucune mutation.
        proposal = {
            "lock_version": version,
            "orphan_session_id": record.get("session_id"),
            "lock_bytes_sha256": _sha256_bytes(raw),
            "approval_id": proof["approval_id"],
            "real_execution_authorized": REAL_RECLAIM_EXECUTION_AUTHORIZED,
        }
        return OperationResult.success(
            "reclaim proposal prepared — real execution NOT authorized",
            proposal=proposal)

    def execute_reclaim(self, *_args: Any, **_kwargs: Any) -> OperationResult:
        """Le reclaim réel (PART_B..H de SECTION_14 avec mutation) est
        structurellement refusé dans PART_A : real_stale_lock_reclaim est
        NOT_AUTHORIZED. Aucun paramètre ne peut lever ce refus."""
        return OperationResult.failure(
            FailureCode.RECLAIM_REAL_EXECUTION_NOT_AUTHORIZED,
            "real_stale_lock_reclaim: NOT_AUTHORIZED (PART_A_REV10)",
        )


def _default_clock() -> float:
    import time
    return time.time()


def _fsync_dir(directory: Path) -> None:
    """Durabilité du répertoire parent — best effort portable (no-op si
    l'OS ne permet pas d'ouvrir un répertoire, ex. Windows)."""
    try:
        fd = os.open(str(directory), os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(fd)
    except OSError:
        pass
    finally:
        os.close(fd)

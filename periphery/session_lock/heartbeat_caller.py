"""heartbeat_caller — PALIER_PROPOSAL_GUARD_RECLAIM_FIX_V17 PART_B_REV01.

Caller heartbeat synchrone isolé.
Sous-périmètre approuvé : HEARTBEAT_CALLER_AND_BOUNDED_ACTIVATION_ONLY.

Invariants absolus (PART_B_REV01, MUST_REMAIN_FALSE_UNDER_PART_B_REV01) :
- aucun thread, processus, daemon ou scheduler ;
- aucune boucle autonome démarrée au constructeur ;
- configuration injectée explicitement — aucune lecture d'env, de fichier ou
  de secret manager ;
- résultats structurés uniquement — aucun callback, logger externe ou bus ;
- reclaim réel interdit — execute_reclaim() n'est jamais appelée ;
- REAL_RECLAIM_EXECUTION_AUTHORIZED = False maintenu sans exception ;
- aucun import de apps/, scripts/, sigma/, kernel/ ou runtime actif ;
- aucune valeur de production inventée pour H/I/J ;
- composant isolé, non câblé au runtime.

DECISION_AUTHORITY=KX108_ONLY — mécanisme reporté (DECISION_D).
No IO except via HeartbeatLockManager. No network. No subprocess. No ACT.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from periphery.session_lock.heartbeat_lock_manager import (
    ControlRequest,
    HandoffAction,
    HeartbeatLockManager,
    HeartbeatRuntimeState,
    OperationResult,
)


class CallerPhase(str, Enum):
    """Phase de la séquence bornée du caller."""
    IDLE = "IDLE"
    BOOTSTRAPPED = "BOOTSTRAPPED"
    TICKING = "TICKING"
    CONTROL_REQUESTED = "CONTROL_REQUESTED"
    TERMINATED = "TERMINATED"
    RELEASED = "RELEASED"
    FAULTED = "FAULTED"


@dataclass(frozen=True)
class CallerResult:
    """Résultat immuable d'une opération bornée du caller.

    Champs :
    - ok            : opération réussie (séquence entière + cleanup pour run_bounded)
    - phase         : phase du caller au moment du résultat
    - part_a_result : OperationResult retourné par PART_A (ou première erreur)
    - runtime_state : état runtime observé après l'opération
    - handoff       : valeur de handoff_action si applicable, sinon None
    - steps_executed: nombre de ticks réussis dans cette invocation
    - terminated    : True si commit_termination() a réussi
    - released      : True si release_session() a réussi
    - detail        : description lisible de la phase/résultat

    Champs run_bounded (None pour les appels d'opération unique) :
    - sequence_ok   : True si aucune erreur avant le cleanup (ticks + termination)
    - cleanup_ok    : True si release_session() a réussi
    - first_failure : OperationResult de la première opération en échec
    """
    ok: bool
    phase: CallerPhase
    part_a_result: OperationResult
    runtime_state: HeartbeatRuntimeState
    handoff: Optional[str]
    steps_executed: int
    terminated: bool
    released: bool
    detail: str
    sequence_ok: Optional[bool] = None
    cleanup_ok: Optional[bool] = None
    first_failure: Optional[OperationResult] = None

    ISOLATED_UNWIRED: str = field(
        default="PART_B_REV01_ISOLATED_UNWIRED",
        init=False,
        compare=False,
    )


class SynchronousHeartbeatCaller:
    """Caller heartbeat synchrone isolé — PART_B_REV01.

    Pilote explicitement un HeartbeatLockManager (PART_A) sans boucle
    autonome, sans thread et sans activation implicite.

    L'appelant contrôle intégralement le rythme des ticks et la durée
    de vie de la session. Ce composant n'introduit aucune temporisation,
    aucune décision de contrôle automatique et aucune mutation hors du
    périmètre de HeartbeatLockManager.

    Utilisation minimale :
        caller = SynchronousHeartbeatCaller(mgr)
        r = caller.bootstrap()          # acquire_session_lock
        r = caller.tick()               # un heartbeat_tick
        r = caller.request_stop()       # STOP — optionnel selon signal
        r = caller.run_bounded(n)       # n ticks maximum
        r = caller.release()            # release_session
    """

    def __init__(self, manager: HeartbeatLockManager) -> None:
        if not isinstance(manager, HeartbeatLockManager):
            raise TypeError(
                "SynchronousHeartbeatCaller requiert un HeartbeatLockManager"
            )
        self._mgr = manager
        self._phase: CallerPhase = CallerPhase.IDLE
        self._steps: int = 0
        self._terminated: bool = False
        self._released: bool = False

    # ------------------------------------------------------------------
    # Accesseurs d'état (lecture seule)
    # ------------------------------------------------------------------

    @property
    def phase(self) -> CallerPhase:
        return self._phase

    @property
    def steps_executed(self) -> int:
        return self._steps

    @property
    def terminated(self) -> bool:
        return self._terminated

    @property
    def released(self) -> bool:
        return self._released

    # ------------------------------------------------------------------
    # Opérations bornées
    # ------------------------------------------------------------------

    def bootstrap(self) -> CallerResult:
        """Étape 1 — acquire_session_lock().

        Doit être appelée avant tout tick. N'active pas le manager : la
        configuration enabled=True doit avoir été injectée explicitement
        avant la construction du HeartbeatLockManager.
        """
        result = self._mgr.acquire_session_lock()
        if result.ok:
            self._phase = CallerPhase.BOOTSTRAPPED
        else:
            self._phase = CallerPhase.FAULTED
        return self._make_result(result, handoff=None)

    def tick(self) -> CallerResult:
        """Étape 2 — un heartbeat_tick() unique.

        Retourne le résultat sans dormir. L'appelant est responsable de
        toute temporisation entre deux ticks.

        Handoffs possibles :
        - CONSUME_CONTROL : phase passe à CONTROL_REQUESTED ;
        - RESUME_WAIT     : retour immédiat, phase reste TICKING ;
        - absent ou inconnu : résultat fail-closed (ok=False, FAULTED).

        Si le handoff est CONSUME_CONTROL, l'appelant doit appeler
        consume_and_terminate() avant le prochain tick ou release().
        """
        result = self._mgr.heartbeat_tick()
        if result.ok:
            self._steps += 1
            raw_handoff = result.payload.get("handoff_action")
            try:
                action = HandoffAction(raw_handoff)
            except (ValueError, TypeError):
                # handoff absent ou inconnu — fail-closed, aucune continuation
                self._phase = CallerPhase.FAULTED
                return self._make_result(result, handoff=raw_handoff, ok_override=False)
            handoff: Optional[str] = action.value
            if action is HandoffAction.CONSUME_CONTROL:
                self._phase = CallerPhase.CONTROL_REQUESTED
            else:
                # RESUME_WAIT
                self._phase = CallerPhase.TICKING
        else:
            self._phase = CallerPhase.FAULTED
            handoff = None
        return self._make_result(result, handoff=handoff)

    def request_stop(self) -> CallerResult:
        """Transmet ControlRequest.STOP à PART_A."""
        return self._request_control(ControlRequest.STOP)

    def request_abort(self) -> CallerResult:
        """Transmet ControlRequest.ABORT à PART_A."""
        return self._request_control(ControlRequest.ABORT)

    def consume_and_terminate(self) -> CallerResult:
        """Étapes consume_control() puis commit_termination().

        Doit être appelée uniquement après un tick ayant retourné
        handoff_action == CONSUME_CONTROL.

        Si consume_control() échoue, commit_termination() n'est pas appelé.
        Aucune mutation hors de la séquence autorisée par PART_A.
        """
        consume = self._mgr.consume_control()
        if not consume.ok:
            self._phase = CallerPhase.FAULTED
            return self._make_result(consume, handoff=None)

        terminate = self._mgr.commit_termination()
        if terminate.ok:
            self._phase = CallerPhase.TERMINATED
            self._terminated = True
        else:
            self._phase = CallerPhase.FAULTED
        return self._make_result(terminate, handoff=None)

    def release(self) -> CallerResult:
        """Étape finale — release_session().

        Peut être appelée depuis BOOTSTRAPPED, TICKING, CONTROL_REQUESTED,
        TERMINATED ou FAULTED selon les états admis par PART_A.

        En cas d'échec, le résultat d'erreur est retourné sans suppression
        manuelle du lock et sans tentative de reclaim.
        """
        result = self._mgr.release_session()
        if result.ok:
            self._phase = CallerPhase.RELEASED
            self._released = True
        else:
            self._phase = CallerPhase.FAULTED
        return self._make_result(result, handoff=None)

    def run_bounded(
        self,
        max_steps: int,
        control_request: Optional[ControlRequest] = None,
    ) -> CallerResult:
        """Exécution bornée : bootstrap + au plus max_steps ticks + release.

        Paramètres :
        - max_steps       : nombre maximal de ticks (doit être > 0)
        - control_request : STOP ou ABORT optionnel injecté avant la boucle

        La boucle s'arrête dès que :
        - max_steps ticks ont été exécutés ;
        - un handoff CONSUME_CONTROL est reçu (consume + terminate exécutés) ;
        - une opération PART_A échoue.

        Sémantique du résultat :
        - ok=False si la séquence a rencontré une erreur OU si le cleanup
          (release) a échoué ;
        - sequence_ok distingue les erreurs de séquence de celles du cleanup ;
        - first_failure conserve la première OperationResult en échec ;
        - le succès du release ne masque jamais une erreur de séquence ;
        - si le bootstrap échoue, la méthode retourne immédiatement sans
          tenter de release : sequence_ok=None, cleanup_ok=None (jamais
          démarré, distinct de sequence_ok=False = démarré puis échoué).

        Aucun sleep, aucun thread, aucun while True.
        L'appelant est responsable de toute temporisation entre les ticks.
        """
        if max_steps <= 0:
            raise ValueError("max_steps doit être strictement positif")

        r = self.bootstrap()
        if not r.ok:
            return r

        first_error: Optional[CallerResult] = None

        if control_request is not None:
            r = self._request_control(control_request)
            if not r.ok:
                first_error = r

        if first_error is None:
            for _ in range(max_steps):
                r = self.tick()
                if not r.ok:
                    first_error = r
                    break
                if r.handoff == HandoffAction.CONSUME_CONTROL.value:
                    r = self.consume_and_terminate()
                    if not r.ok:
                        first_error = r
                    break

        release_r = self.release()
        return self._make_bounded_result(
            first_error=first_error,
            release_result=release_r,
        )

    # ------------------------------------------------------------------
    # Interne
    # ------------------------------------------------------------------

    def _request_control(self, request: ControlRequest) -> CallerResult:
        result = self._mgr.request_control(request)
        if not result.ok:
            self._phase = CallerPhase.FAULTED
        return self._make_result(result, handoff=None)

    def _make_result(
        self,
        part_a_result: OperationResult,
        handoff: Optional[str],
        ok_override: Optional[bool] = None,
    ) -> CallerResult:
        ok = ok_override if ok_override is not None else part_a_result.ok
        return CallerResult(
            ok=ok,
            phase=self._phase,
            part_a_result=part_a_result,
            runtime_state=self._mgr.runtime_state,
            handoff=handoff,
            steps_executed=self._steps,
            terminated=self._terminated,
            released=self._released,
            detail=f"PART_B_REV01_ISOLATED_UNWIRED | phase={self._phase.value}",
        )

    def _make_bounded_result(
        self,
        first_error: Optional[CallerResult],
        release_result: CallerResult,
    ) -> CallerResult:
        """Construit le CallerResult final de run_bounded.

        Si une erreur de séquence est présente, elle devient le résultat
        principal (ok=False) même si le cleanup a réussi.
        """
        cleanup_ok = release_result.ok
        if first_error is not None:
            return CallerResult(
                ok=False,
                phase=self._phase,
                part_a_result=first_error.part_a_result,
                runtime_state=self._mgr.runtime_state,
                handoff=None,
                steps_executed=self._steps,
                terminated=self._terminated,
                released=self._released,
                detail=(
                    f"PART_B_REV01_ISOLATED_UNWIRED | phase={self._phase.value}"
                    " | SEQUENCE_FAILED"
                ),
                sequence_ok=False,
                cleanup_ok=cleanup_ok,
                first_failure=first_error.part_a_result,
            )
        return CallerResult(
            ok=cleanup_ok,
            phase=self._phase,
            part_a_result=release_result.part_a_result,
            runtime_state=self._mgr.runtime_state,
            handoff=release_result.handoff,
            steps_executed=self._steps,
            terminated=self._terminated,
            released=self._released,
            detail=f"PART_B_REV01_ISOLATED_UNWIRED | phase={self._phase.value}",
            sequence_ok=True,
            cleanup_ok=cleanup_ok,
            first_failure=None,
        )

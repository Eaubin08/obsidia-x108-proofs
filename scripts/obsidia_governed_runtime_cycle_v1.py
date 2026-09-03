"""
obsidia_governed_runtime_cycle_v1.py
====================================
GOVERNED_INTERNAL_RUNTIME_CYCLE_V1 — couche d'ORCHESTRATION / TRANSPORT
reliant le chemin agent -> contexte (R4) au rail d'exécution canonique
(CanonicalExecutionFlow / CanonicalRuntimeReceiptFlow) A TRAVERS une
décision KX108 souveraine réelle.

INVARIANT FONDATEUR :

    runtime coordinator coordinates authority;
    runtime coordinator does not possess authority.

Ce module :
  * ne DÉCIDE rien — le seul producteur de x108_gate est
    sigma.guard.GuardX108.decide(), atteint par le pont canonique
    periphery.sigma_bridge.run_<domaine>_with_periphery() ;
  * ne synthétise JAMAIS un ALLOW, ni une approbation humaine, ni un
    consentement, ni un SovereignTicket réel ;
  * ne traite JAMAIS ALLOW_CONTEXT_ONLY (stub dry-run) comme une
    autorisation d'exécution — ce stub n'est pas consulté ici ;
  * n'écrit AUCUNE mémoire, ne mute AUCUN kernel, n'émet AUCUN ACT ;
  * ne modifie PAS runtime_allowed_now sur le ContextPacket (invariant
    de la couche contexte dry-run) ;
  * n'active AUCUNE world action (le monde extérieur reste dry-run).

Chaîne réellement traversée :

    run_registered_agent()                        -> AgentResult réel
    agent_result_to_context_packet()              -> ContextPacket réel (binder R4)
    validate_context_packet() / check_x108_context_boundary()
    sigma_bridge.run_<domaine>_with_periphery()   -> GuardX108.decide() réel
                                                  -> CanonicalDecisionEnvelope
    build_os3_ticket()                            -> input/output/trace/merkle
    ticket_is_valid() + run_replay()              -> vérification cryptographique
    [GATE] ALLOW + ticket valide + replay PASS    -> et SEULEMENT alors
    CanonicalRuntimeReceiptFlow.run()             -> CanonicalExecutionFlow
                                                  -> CanonicalExecutionOrchestrator
                                                  -> MissionExecutionRouter
                                                  -> handler borné
                                                  -> CanonicalExecutionEnvelope.seal()
                                                  -> ProviderRuntimeReceipt terminal
    build_memory_candidate()                      -> feedback READONLY

BLOCKER FACTUEL CONNU — persistance canonique du decision record :
obsidia_kx108_decision_store.run_and_persist_kx108_pre_execution_decision()
n'est PAS applicable à un cycle agent. Son contrat de liaison
(_PRE_BINDING_CONTEXT_FIELDS) exige des artefacts propres au rail de
remédiation de contenu : batch_execution_id, child_execution_id,
execution_authority_hash d'un contenu de fichier, approval_id d'une
HumanApproval liée à cet EAH, pre_execution_context_id d'une isolation
Git, test_contract_hash. Un cycle agent -> provider n'en possède aucun,
et les fabriquer reviendrait à détourner une autorisation humaine
accordée pour autre chose. Ce module NE LES FABRIQUE DONC PAS : il
expose le blocker nommé et laisse decision_record_persisted=False.
La vérification cryptographique effectivement réalisée ici est celle du
rail OS3 (ticket + replay), pas verify_kx108_decision_record().

decision_authority = KX108_ONLY.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from periphery.agent_registry import run_registered_agent
from periphery.common import ActionCandidate
from periphery.context.agent_result_context_adapter import (
    agent_result_to_context_packet,
    context_packet_validation_projection,
)
from periphery.context.context_packet_validator import validate_context_packet
from periphery.x108_ingress.x108_context_boundary import check_x108_context_boundary
from periphery.feedback_memory_bridge_brody_readonly import build_memory_candidate
from periphery.os3_replay_runner import run_replay
from periphery.os3_ticket import build_os3_ticket, ticket_is_valid
from periphery.sigma_bridge import (
    run_bank_with_periphery,
    run_ecom_with_periphery,
    run_gps_with_periphery,
    run_trading_with_periphery,
)

DECISION_AUTHORITY = "KX108_ONLY"
CYCLE_BOUNDARY = "GOVERNED_INTERNAL_RUNTIME_CYCLE_V1"

VALID_X108_GATES = ("ALLOW", "HOLD", "BLOCK")

# Le seul motif qui ouvre la couche d'exécution.
EXECUTION_AUTHORIZED = "EXECUTION_AUTHORIZED_BY_VERIFIED_KX108_ALLOW"

# Motifs de refus — tous fail-closed, provider jamais invoqué.
REFUSED_GATE_NOT_ALLOW = "KX108_GATE_NOT_ALLOW"
REFUSED_GATE_INVALID = "KX108_GATE_OUTSIDE_VALID_ENUM"
REFUSED_AUTHORITY = "DECISION_AUTHORITY_NOT_KX108_ONLY"
REFUSED_TICKET_INVALID = "OS3_TICKET_INVALID"
REFUSED_TICKET_GATE_MISMATCH = "OS3_TICKET_GATE_MISMATCH"
REFUSED_REPLAY_NOT_PASS = "OS3_REPLAY_NOT_PASS"
REFUSED_NO_EXECUTION_SURFACE = "NO_BOUND_EXECUTION_SURFACE_PROVIDED"
REFUSED_CONTEXT_INVALID = "CONTEXT_PRE_GATE_FAIL_CLOSED"

# Blocker nommé — jamais contourné.
DECISION_RECORD_PERSISTENCE_BLOCKER = (
    "KX108_PRE_EXECUTION_RECORD_BINDING_NOT_APPLICABLE_TO_AGENT_CYCLE"
)

_DOMAIN_PIPELINES: dict[str, Callable[[Any, Any], Any]] = {
    "bank": run_bank_with_periphery,
    "trading": run_trading_with_periphery,
    "ecom": run_ecom_with_periphery,
    "gps": run_gps_with_periphery,
    "gps_defense_aviation": run_gps_with_periphery,
}


class GovernedRuntimeCycleError(Exception):
    """Erreur de transport / de contrat. Jamais un refus de gouvernance."""


@dataclass
class GovernedRuntimeCycleResult:
    """Preuve observable et bornée d'un cycle gouverné interne."""

    # Phase agent / contexte
    agent_id: str
    agent_layer: str
    action_id: str
    domain: str
    context_id: str
    context_validation: dict[str, Any] = field(default_factory=dict)
    context_boundary: dict[str, Any] = field(default_factory=dict)

    # Phase décision KX108 souveraine
    x108_gate: str = "BLOCK"
    decision_id: str = ""
    trace_id: str = ""
    reason_code: str = ""
    severity: str = ""
    decision_engine: str = "sigma.guard.GuardX108.decide"

    # Vérification cryptographique OS3
    os3_ticket_id: str = ""
    input_hash: str = ""
    output_hash: str = ""
    trace_hash: str = ""
    merkle_root: str = ""
    replay_status: str = "NOT_RUN"

    # Gate d'exécution
    execution_authorized: bool = False
    execution_authorization_reason: str = REFUSED_GATE_NOT_ALLOW
    provider_invoked: bool = False

    # Phase exécution réelle (uniquement si autorisée)
    flow_status: str = ""
    envelope_status: str = ""
    runtime_id: str = ""
    receipt: Optional[dict[str, Any]] = None

    # Feedback readonly
    feedback: Optional[dict[str, Any]] = None

    # Persistance canonique — blocker factuel
    decision_record_persisted: bool = False
    decision_record_persistence_blocker: str = DECISION_RECORD_PERSISTENCE_BLOCKER

    # Invariants verrouillés
    decision_authority: str = DECISION_AUTHORITY
    emits_act: bool = False
    memory_write: bool = False
    kernel_mutation: bool = False
    context_runtime_allowed_now: bool = False
    world_action_allowed: bool = False
    world_action_dry_run_only: bool = True
    boundary: str = CYCLE_BOUNDARY

    def assert_non_sovereign(self) -> None:
        if self.emits_act:
            raise AssertionError("CYCLE_VIOLATION: emits_act must be False")
        if self.memory_write:
            raise AssertionError("CYCLE_VIOLATION: memory_write must be False")
        if self.kernel_mutation:
            raise AssertionError("CYCLE_VIOLATION: kernel_mutation must be False")
        if self.context_runtime_allowed_now:
            raise AssertionError("CYCLE_VIOLATION: context runtime_allowed_now must stay False")
        if self.world_action_allowed:
            raise AssertionError("CYCLE_VIOLATION: world_action_allowed must be False")
        if not self.world_action_dry_run_only:
            raise AssertionError("CYCLE_VIOLATION: world action must stay dry-run only")
        if self.decision_authority != DECISION_AUTHORITY:
            raise AssertionError("CYCLE_VIOLATION: decision_authority must be KX108_ONLY")
        if self.x108_gate not in VALID_X108_GATES:
            raise AssertionError(f"CYCLE_VIOLATION: gate outside enum: {self.x108_gate}")
        if self.provider_invoked and not self.execution_authorized:
            raise AssertionError("CYCLE_VIOLATION: provider invoked without authorization")
        if self.execution_authorized and self.x108_gate != "ALLOW":
            raise AssertionError("CYCLE_VIOLATION: authorization without a KX108 ALLOW")

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "agent_layer": self.agent_layer,
            "action_id": self.action_id,
            "domain": self.domain,
            "context_id": self.context_id,
            "context_validation": self.context_validation,
            "context_boundary": self.context_boundary,
            "x108_gate": self.x108_gate,
            "decision_id": self.decision_id,
            "trace_id": self.trace_id,
            "reason_code": self.reason_code,
            "severity": self.severity,
            "decision_engine": self.decision_engine,
            "os3_ticket_id": self.os3_ticket_id,
            "input_hash": self.input_hash,
            "output_hash": self.output_hash,
            "trace_hash": self.trace_hash,
            "merkle_root": self.merkle_root,
            "replay_status": self.replay_status,
            "execution_authorized": self.execution_authorized,
            "execution_authorization_reason": self.execution_authorization_reason,
            "provider_invoked": self.provider_invoked,
            "flow_status": self.flow_status,
            "envelope_status": self.envelope_status,
            "runtime_id": self.runtime_id,
            "receipt": self.receipt,
            "feedback": self.feedback,
            "decision_record_persisted": self.decision_record_persisted,
            "decision_record_persistence_blocker": self.decision_record_persistence_blocker,
            "decision_authority": self.decision_authority,
            "emits_act": self.emits_act,
            "memory_write": self.memory_write,
            "kernel_mutation": self.kernel_mutation,
            "context_runtime_allowed_now": self.context_runtime_allowed_now,
            "world_action_allowed": self.world_action_allowed,
            "world_action_dry_run_only": self.world_action_dry_run_only,
            "boundary": self.boundary,
        }


def resolve_domain_pipeline(domain: str) -> Callable[[Any, Any], Any]:
    """Pont canonique du domaine. Aucun domaine inventé, aucun repli."""
    pipeline = _DOMAIN_PIPELINES.get(domain)
    if pipeline is None:
        raise GovernedRuntimeCycleError(f"NO_CANONICAL_DOMAIN_PIPELINE:{domain}")
    return pipeline


def authorize_execution_from_verified_kx108(
    envelope: Any,
    ticket: Any,
    replay: Any,
) -> tuple[bool, str]:
    """
    Dérive une autorisation d'exécution UNIQUEMENT d'une décision KX108
    souveraine ALLOW dont l'évidence OS3 est vérifiée et rejouable.

    Fonction PURE : ne décide pas, ne rejoue pas, n'exécute rien. Elle
    lit un verdict déjà rendu et refuse par défaut. Tout écart -> refus.
    """
    gate = getattr(envelope, "x108_gate", None)

    if gate not in VALID_X108_GATES:
        return False, REFUSED_GATE_INVALID
    if gate != "ALLOW":
        return False, REFUSED_GATE_NOT_ALLOW
    if not ticket_is_valid(ticket):
        return False, REFUSED_TICKET_INVALID
    if getattr(ticket, "x108_gate", None) != gate:
        return False, REFUSED_TICKET_GATE_MISMATCH
    if getattr(replay, "replay_status", None) != "PASS":
        return False, REFUSED_REPLAY_NOT_PASS

    return True, EXECUTION_AUTHORIZED


def run_governed_runtime_cycle(
    agent_id: str,
    action: ActionCandidate,
    domain_state: Any,
    *,
    execution_surface: Any = None,
    mission_id: str = "",
    provider_id: str = "",
    capability: str = "",
    execution_payload: Optional[dict[str, Any]] = None,
) -> GovernedRuntimeCycleResult:
    """
    Exécute un cycle gouverné interne complet.

    `execution_surface` est un CanonicalRuntimeReceiptFlow déjà pourvu de
    son provider borné. Il n'est JAMAIS invoqué avant qu'une décision
    KX108 ALLOW vérifiée n'ait été obtenue. Absent, le cycle s'arrête
    proprement au gate sans jamais dégrader la décision.
    """
    # ── 1. Agent réel -> AgentResult réel ────────────────────────────────
    agent_result = run_registered_agent(agent_id, action)
    agent_result.assert_non_sovereign()
    packet = agent_result.packet

    # ── 2. Binder R4 : ContextPacket canonique issu de CE AgentResult ────
    context = agent_result_to_context_packet(agent_result)
    projection = context_packet_validation_projection(context)
    validation = validate_context_packet(projection)
    boundary = check_x108_context_boundary(projection)

    result = GovernedRuntimeCycleResult(
        agent_id=agent_result.agent_id,
        agent_layer=agent_result.layer.value,
        action_id=packet.action_id,
        domain=packet.domain,
        context_id=context.context_id,
        context_validation=validation.to_dict(),
        context_boundary=boundary.to_dict(),
        context_runtime_allowed_now=context.runtime_allowed_now,
    )

    if not validation.valid or not boundary.passed:
        result.execution_authorization_reason = REFUSED_CONTEXT_INVALID
        result.assert_non_sovereign()
        return result

    # ── 3. Décision KX108 SOUVERAINE réelle (GuardX108) ──────────────────
    pipeline = resolve_domain_pipeline(packet.domain)
    envelope = pipeline(domain_state, packet)

    result.x108_gate = getattr(envelope, "x108_gate", "BLOCK")
    result.decision_id = getattr(envelope, "decision_id", "")
    result.trace_id = getattr(envelope, "trace_id", "")
    result.reason_code = getattr(envelope, "reason_code", "")
    result.severity = getattr(envelope, "severity", "")

    # ── 4. Évidence OS3 + vérification cryptographique par rejeu ─────────
    ticket = build_os3_ticket(action, packet, envelope)
    replay = run_replay(ticket, action, packet, envelope)

    result.os3_ticket_id = ticket.ticket_id
    result.input_hash = ticket.input_hash
    result.output_hash = ticket.output_hash
    result.trace_hash = ticket.trace_hash
    result.merkle_root = ticket.merkle_root
    result.replay_status = replay.replay_status

    # ── 5. Gate d'exécution — dérivé UNIQUEMENT du verdict vérifié ───────
    authorized, reason = authorize_execution_from_verified_kx108(
        envelope, ticket, replay
    )
    result.execution_authorized = authorized
    result.execution_authorization_reason = reason

    # ── 6. Exécution réelle bornée — jamais atteinte sans ALLOW vérifié ──
    if authorized:
        if execution_surface is None:
            result.execution_authorized = False
            result.execution_authorization_reason = REFUSED_NO_EXECUTION_SURFACE
        else:
            output = execution_surface.run(
                mission_id=mission_id,
                provider_id=provider_id,
                capability=capability,
                payload=dict(execution_payload or {}),
            )
            execution = output["execution"]
            exec_envelope = execution["execution"]["envelope"]

            result.provider_invoked = True
            result.flow_status = execution.get("flow_status", "")
            result.envelope_status = exec_envelope.get("status", "")
            result.runtime_id = exec_envelope.get("runtime_id", "")
            result.receipt = output["receipt"]

    # ── 7. Feedback READONLY via la primitive canonique ──────────────────
    feedback = build_memory_candidate(ticket, packet, action)
    feedback.assert_no_write()
    result.feedback = feedback.to_dict()

    result.assert_non_sovereign()
    return result

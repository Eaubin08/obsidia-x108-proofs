from __future__ import annotations

from dataclasses import asdict

from ..constants import DECISION_AUTHORITY, READONLY_FLAGS
from ..models import ContextPacket, X108ReadonlyIngressEnvelope, stable_id

SKILL_SPEC = {
    "skill_id": "SKILL_X108_INGRESS_ENVELOPE_READONLY",
    "contract": "build X108 ingress candidate envelope without direct runtime call or merge",
}


def build_x108_readonly_ingress_envelope(packet: ContextPacket) -> X108ReadonlyIngressEnvelope:
    """Wrap packet for X108 readonly ingress.

    This is a handoff object, not a runtime invocation.
    """
    envelope_id = stable_id("X108_RO_INGRESS", {"packet_id": packet.packet_id, "trace": packet.trace_chain})
    return X108ReadonlyIngressEnvelope(
        envelope_id=envelope_id,
        source_packet_id=packet.packet_id,
        ingress_kind="x108_readonly_context_candidate",
        purpose="provide structured workflow context to X108 boundary without decision, mutation, or runtime call",
        context_packet=asdict(packet),
        ingress_contract={
            "decision_authority": DECISION_AUTHORITY,
            "expected_consumer": "KX108_READONLY_INGRESS_OR_EXTERNAL_REVIEW",
            "allowed_use": ["context_review", "evidence_check", "replay_inspection", "operator_handoff"],
            "forbidden_use": ["runtime_execution", "kernel_patch", "x108_patch", "workflow_authorization"],
            "x108_runtime_binding": False,
            "x108_merge": False,
            "kernel_binding": False,
            "boundary": {"decision_authority": DECISION_AUTHORITY, **READONLY_FLAGS},
        },
        x108_merge=False,
        x108_runtime_binding=False,
        kernel_binding=False,
        direct_runtime_call=False,
        candidate_only=True,
    )

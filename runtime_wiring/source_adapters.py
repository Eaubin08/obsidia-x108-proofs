# runtime_wiring/source_adapters.py
# Source adapters: dict[metadata] → ContextPacket (dry-run)
# stdlib only — no import from apps/, periphery/, connectors/, sigma/
# Each adapter FORCES correct boundary and labels per contract

from __future__ import annotations
import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict

from .packet_types import ContextPacket


def _make_context_id(prefix: str, metadata: Dict[str, Any]) -> str:
    content = json.dumps(metadata, sort_keys=True, default=str)
    digest = hashlib.sha256(f"{prefix}:{content}".encode()).hexdigest()[:16]
    return f"cp-dryrun-{prefix}-{digest}"


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def cognitive_to_context_packet(metadata: Dict[str, Any]) -> ContextPacket:
    """
    Cognitive Reintegration → ContextPacket dry-run.
    Boundary: COGNITIVE_REINTEGRATION_ADVISORY_ONLY
    Source pack: COPIED_READONLY (F07 pending)
    """
    packet = ContextPacket(
        context_id=_make_context_id("cognitive", metadata),
        source="cognitive",
        source_status="COPIED_READONLY",
        claim_scope="CLAIMABLE_SPEC_ONLY",
        boundary="COGNITIVE_REINTEGRATION_ADVISORY_ONLY",
        timestamp_or_tick=metadata.get("timestamp", _utcnow()),
        advisory_only=True,
        readonly=True,
        runtime_allowed_now=False,
        emits_act=False,
        emits_decision=False,
        decision_authority="KX108_ONLY",
        labels=["COGNITIVE_ADVISORY_FUTURE"],
        payload={
            **{k: v for k, v in metadata.items() if k != "timestamp"},
            "_cognitive_can_decide": False,
            "_boundary": "COGNITIVE_REINTEGRATION_ADVISORY_ONLY",
            "_dry_run": True,
        },
        notes="Cognitive pack COPIED_READONLY — import pending F07",
    )
    packet.validate_invariants()
    return packet


def rssi_rgpd_to_context_packet(metadata: Dict[str, Any]) -> ContextPacket:
    """
    RSSI + RGPD → ContextPacket dry-run.
    Boundaries: RSSI_EVIDENCE_ONLY + RGPD_COMPLIANCE_SCOPE_GUARD
    Source pack: COPIED_READONLY (F03 pending)
    """
    packet = ContextPacket(
        context_id=_make_context_id("rssi_rgpd", metadata),
        source="rssi_rgpd",
        source_status="COPIED_READONLY",
        claim_scope="CLAIMABLE_SPEC_ONLY",
        boundary="RSSI_EVIDENCE_ONLY|RGPD_COMPLIANCE_SCOPE_GUARD",
        timestamp_or_tick=metadata.get("timestamp", _utcnow()),
        advisory_only=True,
        readonly=True,
        runtime_allowed_now=False,
        emits_act=False,
        emits_decision=False,
        decision_authority="KX108_ONLY",
        labels=["RSSI_EVIDENCE_ONLY_FUTURE", "RGPD_SCOPE_GUARD_FUTURE"],
        payload={
            **{k: v for k, v in metadata.items() if k != "timestamp"},
            "_rssi_can_decide": False,
            "_rgpd_is_certified": False,
            "_boundary": "RSSI_EVIDENCE_ONLY|RGPD_COMPLIANCE_SCOPE_GUARD",
            "_dry_run": True,
        },
        notes="RSSI COPIED_READONLY F03 pending. RGPD readiness ≠ legal compliance.",
    )
    packet.validate_invariants()
    return packet


def atlas_to_context_packet(metadata: Dict[str, Any]) -> ContextPacket:
    """
    Branchable Atlas → ContextPacket dry-run.
    Boundary: ATLAS_READONLY_ADVISORY_ONLY
    Source pack: COPIED_READONLY (1738 files, 92 duplicates — F06 pending)
    """
    packet = ContextPacket(
        context_id=_make_context_id("atlas", metadata),
        source="atlas",
        source_status="COPIED_READONLY",
        claim_scope="CLAIMABLE_SPEC_ONLY",
        boundary="ATLAS_READONLY_ADVISORY_ONLY",
        timestamp_or_tick=metadata.get("timestamp", _utcnow()),
        advisory_only=True,
        readonly=True,
        runtime_allowed_now=False,
        emits_act=False,
        emits_decision=False,
        decision_authority="KX108_ONLY",
        labels=["ATLAS_READONLY_FUTURE"],
        payload={
            **{k: v for k, v in metadata.items() if k != "timestamp"},
            "_atlas_can_execute": False,
            "_atlas_agents_executable": False,
            "_boundary": "ATLAS_READONLY_ADVISORY_ONLY",
            "_dry_run": True,
        },
        notes="Branchable Atlas COPIED_READONLY — 1738 files, 92 duplicates — import F06 pending",
    )
    packet.validate_invariants()
    return packet


def compliance_to_context_packet(metadata: Dict[str, Any]) -> ContextPacket:
    """
    Compliance / RGPD-primary → ContextPacket dry-run.
    Boundaries: RGPD_COMPLIANCE_SCOPE_GUARD + RSSI_EVIDENCE_ONLY
    Source pack: COPIED_READONLY (F10 pending)
    """
    packet = ContextPacket(
        context_id=_make_context_id("compliance", metadata),
        source="compliance_rgpd",
        source_status="COPIED_READONLY",
        claim_scope="CLAIMABLE_SPEC_ONLY",
        boundary="RGPD_COMPLIANCE_SCOPE_GUARD|RSSI_EVIDENCE_ONLY",
        timestamp_or_tick=metadata.get("timestamp", _utcnow()),
        advisory_only=True,
        readonly=True,
        runtime_allowed_now=False,
        emits_act=False,
        emits_decision=False,
        decision_authority="KX108_ONLY",
        labels=["RGPD_SCOPE_GUARD_FUTURE", "RSSI_EVIDENCE_ONLY_FUTURE"],
        payload={
            **{k: v for k, v in metadata.items() if k != "timestamp"},
            "_rgpd_compliant": False,
            "_iso_certified": False,
            "_secnumcloud_certified": False,
            "_boundary": "RGPD_COMPLIANCE_SCOPE_GUARD|RSSI_EVIDENCE_ONLY",
            "_dry_run": True,
        },
        notes="RGPD ISO readiness ≠ legal compliance. SecNumCloud target ≠ label actif.",
    )
    packet.validate_invariants()
    return packet

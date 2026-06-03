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


# ── P24 — New adapters for coverage gap families ──────────────────────────────

def rssi_security_to_context_packet(metadata: Dict[str, Any]) -> ContextPacket:
    """
    RSSI Security Presentation → ContextPacket dry-run.
    Boundary: RSSI_EVIDENCE_ONLY
    Source pack: COPIED_READONLY (F11/P24 — 835 files, 80 .py DO_NOT_IMPORT_RUNTIME)
    """
    packet = ContextPacket(
        context_id=_make_context_id("rssi_security", metadata),
        source="rssi_security",
        source_status="COPIED_READONLY",
        claim_scope="CLAIMABLE_SPEC_ONLY",
        boundary="RSSI_EVIDENCE_ONLY",
        timestamp_or_tick=metadata.get("timestamp", _utcnow()),
        advisory_only=True,
        readonly=True,
        runtime_allowed_now=False,
        emits_act=False,
        emits_decision=False,
        decision_authority="KX108_ONLY",
        labels=["RSSI_SECURITY_EVIDENCE_FUTURE"],
        payload={
            **{k: v for k, v in metadata.items() if k != "timestamp"},
            "_rssi_security_can_decide": False,
            "_py_files_excluded": True,
            "_boundary": "RSSI_EVIDENCE_ONLY",
            "_dry_run": True,
        },
        notes="RSSI Security pack COPIED_READONLY F11 pending. 80 .py DO_NOT_IMPORT_RUNTIME.",
    )
    packet.validate_invariants()
    return packet


def external_signals_to_context_packet(metadata: Dict[str, Any]) -> ContextPacket:
    """
    External Signals (incl. Timeverse C459 temporal sidecar) → ContextPacket dry-run.
    Boundary: EXTERNAL_SIGNALS_SIGNAL_ONLY
    Source pack: COPIED_READONLY (F04 already extracted in specs/external_signals/, 0 .py)
    """
    packet = ContextPacket(
        context_id=_make_context_id("external_signals", metadata),
        source="external_signals",
        source_status="COPIED_READONLY",
        claim_scope="CLAIMABLE_SPEC_ONLY",
        boundary="EXTERNAL_SIGNALS_SIGNAL_ONLY",
        timestamp_or_tick=metadata.get("timestamp", _utcnow()),
        advisory_only=True,
        readonly=True,
        runtime_allowed_now=False,
        emits_act=False,
        emits_decision=False,
        decision_authority="KX108_ONLY",
        labels=["EXTERNAL_SIGNALS_FUTURE"],
        payload={
            **{k: v for k, v in metadata.items() if k != "timestamp"},
            "_timeverse_included": True,
            "_timeverse_advisory_only": True,
            "_can_emit_act": False,
            "_boundary": "EXTERNAL_SIGNALS_SIGNAL_ONLY",
            "_dry_run": True,
        },
        notes="External Signals F04 extracted specs/external_signals/. Timeverse C459 temporal sidecar included. 0 .py.",
    )
    packet.validate_invariants()
    return packet


def npl_to_context_packet(metadata: Dict[str, Any]) -> ContextPacket:
    """
    Narrative Provenance Layer → ContextPacket dry-run.
    Boundary: NPL_ADVISORY_ONLY
    Source pack: COPIED_READONLY (F12/P24 — 103 files, all .md/.json, 0 .py)
    """
    packet = ContextPacket(
        context_id=_make_context_id("npl", metadata),
        source="narrative_provenance_layer",
        source_status="COPIED_READONLY",
        claim_scope="CLAIMABLE_SPEC_ONLY",
        boundary="NPL_ADVISORY_ONLY",
        timestamp_or_tick=metadata.get("timestamp", _utcnow()),
        advisory_only=True,
        readonly=True,
        runtime_allowed_now=False,
        emits_act=False,
        emits_decision=False,
        decision_authority="KX108_ONLY",
        labels=["NPL_ADVISORY_FUTURE"],
        payload={
            **{k: v for k, v in metadata.items() if k != "timestamp"},
            "_npl_can_decide": False,
            "_npl_exposes_chain": True,
            "_npl_narrative_not_truth": True,
            "_boundary": "NPL_ADVISORY_ONLY",
            "_dry_run": True,
        },
        notes="NPL spec pack F12 pending. NPL expose la chaine narrative, ne decide pas du recit vrai. 0 .py.",
    )
    packet.validate_invariants()
    return packet


# ── P32 — OS Trad / Reverse OS 8th family ────────────────────────────────────

def os_trad_reverse_to_context_packet(metadata: Dict[str, Any]) -> ContextPacket:
    """
    OS Trad / Reverse OS / 34 Arbres / Agents 52 → ContextPacket dry-run.
    Boundary: OS_TRAD_REVERSE_OS_ADVISORY_ONLY
    Source pack: COPIED_READONLY (P32 — 629 files, 546 safe .md/.json, 63 .py DO_NOT_IMPORT_RUNTIME)
    """
    packet = ContextPacket(
        context_id=_make_context_id("os_trad_reverse", metadata),
        source="os_trad_reverse_os",
        source_status="COPIED_READONLY",
        claim_scope="CLAIMABLE_SPEC_ONLY",
        boundary="OS_TRAD_REVERSE_OS_ADVISORY_ONLY",
        timestamp_or_tick=metadata.get("timestamp", _utcnow()),
        advisory_only=True,
        readonly=True,
        runtime_allowed_now=False,
        emits_act=False,
        emits_decision=False,
        decision_authority="KX108_ONLY",
        labels=["OS_TRAD_ADVISORY_FUTURE", "REVERSE_OS_ADVISORY_FUTURE"],
        payload={
            **{k: v for k, v in metadata.items() if k != "timestamp"},
            "_os_trad_can_act": False,
            "_reverse_os_can_decide": False,
            "_34_arbres_advisory_only": True,
            "_agents_52_registry_readonly": True,
            "_py_files_excluded": True,
            "_boundary": "OS_TRAD_REVERSE_OS_ADVISORY_ONLY",
            "_dry_run": True,
        },
        notes=(
            "OS Trad/Reverse OS pack P32. 546 safe .md/.json entries. "
            "63 .py DO_NOT_IMPORT_RUNTIME excluded from registry. "
            "34 arbres advisory specs. 52 agents registry readonly."
        ),
    )
    packet.validate_invariants()
    return packet

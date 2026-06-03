# runtime_wiring/source_registry/adapter_target_map.py
# Mapping: source_family → adapter_target / packet_target / boundary / claim_scope
# stdlib only — no runtime imports, no zip extraction

from __future__ import annotations
from typing import Any, Dict

# Master adapter target map — one entry per source family
ADAPTER_TARGET_MAP: Dict[str, Dict[str, Any]] = {
    "COGNITIVE_REINTEGRATION": {
        "source_family": "COGNITIVE_REINTEGRATION",
        "adapter_target": "cognitive_to_context_packet",
        "packet_target": "ContextPacket",
        "boundary": "COGNITIVE_REINTEGRATION_ADVISORY_ONLY",
        "claim_scope": "ADVISORY_ONLY",
        "decision_authority": "KX108_ONLY",
        "runtime_allowed_now": False,
        "emits_act": False,
        "label": "COGNITIVE_ADVISORY_FUTURE",
        "source_status": "COPIED_READONLY",
        "notes": "F07 — Cognitive reintegration spec pack, advisory only, import pending",
    },
    "RSSI_RGPD": {
        "source_family": "RSSI_RGPD",
        "adapter_target": "rssi_rgpd_to_context_packet",
        "packet_target": "ContextPacket|OS3EvidenceTicketDryRun_ref",
        "boundary": "RSSI_EVIDENCE_ONLY|RGPD_COMPLIANCE_SCOPE_GUARD",
        "claim_scope": "EVIDENCE_ONLY|COMPLIANCE_SCOPE_GUARD_ONLY",
        "decision_authority": "KX108_ONLY",
        "runtime_allowed_now": False,
        "emits_act": False,
        "label": "RSSI_EVIDENCE_ONLY_FUTURE",
        "source_status": "COPIED_READONLY",
        "notes": "F03 — RSSI/RGPD compliance pack, evidence only, RGPD readiness != certification",
    },
    "ATLAS": {
        "source_family": "ATLAS",
        "adapter_target": "atlas_to_context_packet",
        "packet_target": "ContextPacket",
        "boundary": "ATLAS_READONLY_ADVISORY_ONLY",
        "claim_scope": "READONLY_ADVISORY_ONLY",
        "decision_authority": "KX108_ONLY",
        "runtime_allowed_now": False,
        "emits_act": False,
        "label": "ATLAS_READONLY_FUTURE",
        "source_status": "COPIED_READONLY",
        "notes": "F06 — Branchable Atlas pack, readonly advisory, 1738 files 92 duplicates",
    },
    "COMPLIANCE_DATA_GOVERNANCE": {
        "source_family": "COMPLIANCE_DATA_GOVERNANCE",
        "adapter_target": "compliance_to_context_packet",
        "packet_target": "ContextPacket|OS3EvidenceTicketDryRun_ref",
        "boundary": "RGPD_COMPLIANCE_SCOPE_GUARD|RSSI_EVIDENCE_ONLY",
        "claim_scope": "SCOPE_GUARD_ONLY|EVIDENCE_ONLY",
        "decision_authority": "KX108_ONLY",
        "runtime_allowed_now": False,
        "emits_act": False,
        "label": "RGPD_SCOPE_GUARD_FUTURE",
        "source_status": "COPIED_READONLY",
        "notes": "F10 — RGPD/ISO Data Governance pack, scope guard only, legal certification != readiness",
    },
}

# Detect source family from CSV source_zip filename
_ZIP_NAME_TO_FAMILY: Dict[str, str] = {
    "COGNITIVE": "COGNITIVE_REINTEGRATION",
    "RSSI_EXTERNAL": "RSSI_RGPD",
    "RSSI_RGPD": "RSSI_RGPD",
    "BRANCHABLE_ATLAS": "ATLAS",
    "ATLAS": "ATLAS",
    "RSSI_RGPD_ISO": "COMPLIANCE_DATA_GOVERNANCE",
    "COMPLIANCE": "COMPLIANCE_DATA_GOVERNANCE",
    "DATA_GOVERNANCE": "COMPLIANCE_DATA_GOVERNANCE",
}


def detect_family_from_zip(source_zip: str) -> str:
    """Detect source_family from source_zip filename (case-insensitive prefix match)."""
    name = source_zip.upper()
    for key, family in _ZIP_NAME_TO_FAMILY.items():
        if key in name:
            return family
    return "UNKNOWN"


def get_adapter_map(source_family: str) -> Dict[str, Any]:
    """Return adapter map for a source family, or a safe fallback."""
    return ADAPTER_TARGET_MAP.get(source_family, {
        "source_family": source_family,
        "adapter_target": "UNKNOWN_NO_ADAPTER",
        "packet_target": "NONE",
        "boundary": "UNKNOWN",
        "claim_scope": "UNKNOWN",
        "decision_authority": "KX108_ONLY",
        "runtime_allowed_now": False,
        "emits_act": False,
        "label": "UNKNOWN_FUTURE",
        "source_status": "UNKNOWN",
        "notes": f"Unknown family: {source_family} — no adapter mapped",
    })

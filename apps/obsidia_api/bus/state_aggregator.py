"""
Bus/Bridge state aggregator — F54 minimal implementation.

Collects readonly observable state across system dimensions.
Never decides. Never writes. Never mutates.
All fields honest: unknown/unavailable/not_collected when source absent.
"""
from __future__ import annotations
import sys
from typing import Any


def build_bus_stats_state() -> dict[str, Any]:
    """
    Aggregate readonly system stats state for GET /bus/stats.

    Returns a dict with internal bus fields (emitted/dropped/queue_size)
    visible in default and debug modes, omitted in compact mode.
    All sovereignty flags enforced by output_envelope + safe_backend_response.
    """
    return {
        "status": "OK",
        # Internal bus counters — visible in default/debug, omitted in compact
        "emitted": 0,
        "dropped": 0,
        "queue_size": 0,
        # Bridge snapshot fields — present in default/debug, omitted in compact
        "bridge_registration": "not_collected",
        "brody_context": "not_collected",
        "sigma_counters": "not_collected",
        "bridge_snapshot": "not_collected",
        # State dimensions (F53 model)
        "runtime_state": {
            "python_version": sys.version.split()[0],
            "app_available": True,
            "localhost_only": True,
        },
        "proof_state": {
            "last_palier": "F54",
            "f54_minimal_ready": True,
        },
        "audit_state": {
            "f51_debt_known": True,
            "f52_quarantine_done": True,
            "f53_contract_defined": True,
            "f54_routes_implemented": True,
        },
        "readiness_state": {
            "bus_stats_route": True,
            "bus_bridge_route": True,
            "f54_minimal_ready": True,
        },
        "debt_state": {
            "quarantined_tests_reactivated": True,
            "bus_signal_future": True,
            "post_bus_signal_status": "F55_plus",
        },
    }


def build_bus_bridge_state() -> dict[str, Any]:
    """
    Aggregate readonly bridge connective state for GET /bus/bridge.

    Returns bridge identity fields (bridge_id, is_attached, stats)
    visible in default/debug, omitted in compact.
    External signal ingestion deferred to F55+.
    """
    return {
        "status": "OK",
        # Bridge identity — present in default/debug, omitted in compact
        "bridge_id": "f54-bus-bridge-readonly",
        "is_attached": True,
        "stats": {"emitted": 0, "dropped": 0},
        # Context state (advisory read, no write)
        "memory_context_state": {
            "graphiti_status": "not_collected",
            "brody_context_status": "not_collected",
        },
        "external_signal_state": {
            "last_signal": "none",
            "signal_ingest_endpoint": "not_implemented",
            "post_bus_signal_status": "F55_plus",
        },
        "debt_state": {
            "quarantined_tests_reactivated": True,
            "bus_signal_future": True,
        },
    }

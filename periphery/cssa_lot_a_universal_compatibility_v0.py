"""CSSA Lot A — prove compatibility with existing Universal office sandbox rail.

This integration runs both *real existing implementations* on an isolated
pytest workspace, and explicitly does not mislabel enterprise input as CSSA
native work or grant CSSA approval/ACT.
"""
from __future__ import annotations

from pathlib import Path

from periphery.cssa_season_campaign_lot_a_v0 import (
    run_cssa_season_campaign, verify_cssa_season_campaign,
)
from periphery.native_sources.enterprise_office_full_loop_e2e_v0 import (
    run_enterprise_office_full_loop_e2e_v0,
)
from periphery.native_sources.enterprise_source_sandbox_v0 import (
    materialize_enterprise_source_sandbox_v0,
)


def run_cssa_lot_a_compatibility(root: Path, events: list[dict]) -> dict:
    """Execute baseline Universal Digital Twin separately from CSSA fixture review.

    No CSSA event is fed into native committed CASE/TASK/FOLLOW-UP here:
    that translation requires a proven CSSA intake/domain mapping.
    """
    root = Path(root)
    if root.exists() and any(root.iterdir()):
        raise ValueError("CSSA_LOT_A_ROOT_MUST_BE_EMPTY")
    root.mkdir(parents=True, exist_ok=True)
    cssa = run_cssa_season_campaign(events)
    if not verify_cssa_season_campaign(cssa):
        raise ValueError("CSSA_LOT_A_RECEIPT_INVALID")
    paths = materialize_enterprise_source_sandbox_v0(root / "enterprise")
    universal = run_enterprise_office_full_loop_e2e_v0(
        paths=paths,
        runtime_root=root / "runtime",
        native_store_root=root / "native",
        governance_root=root / "governance",
        execution_root=root / "execution",
    )
    if (universal["status"] != "ENTERPRISE_OFFICE_FULL_LOOP_E2E_V0_PROVEN"
            or universal["network_call_performed"] is not False
            or universal["real_external_effect"] is not False
            or universal["decision_authority"] != "KX108_ONLY"
            or universal["execution_receipt_count"] != universal["sandbox_execution_count"]
            or universal["execution_replay_ok_count"] != universal["sandbox_execution_count"]):
        raise ValueError("CSSA_LOT_A_UNIVERSAL_BASELINE_INVALID")
    return {
        "schema": "CSSA_LOT_A_COMPATIBILITY_V0",
        "status": "COMPATIBLE_COMPONENTS_BRIDGE_UNPROVEN",
        "cssa_case_count": cssa["report"]["totals"]["events"],
        "cssa_blocked": cssa["report"]["totals"]["blocked"],
        "cssa_receipt_sha256": cssa["receipt_sha256"],
        "cssa_to_native_work_bound": False,
        "universal_enterprise_sandbox_executions": universal["sandbox_execution_count"],
        "universal_receipts_replayed": universal["execution_replay_ok_count"],
        "universal_stable_intent_hash": universal["stable_intent_hash"],
        "decision_authority": "KX108_ONLY",
        "cssa_kx108_decision": None,
        "cssa_external_actions": [],
        "network_call_performed": False,
        "real_external_effect": False,
    }

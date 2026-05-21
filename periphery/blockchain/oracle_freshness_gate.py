"""
Oracle Freshness Gate.
ORACLE_STALE_DATA -> HOLD. Oracle-dependent actions require fresh data confirmation.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

_FRESHNESS_THRESHOLD_SECONDS = 300  # 5 minutes


@dataclass
class OracleFreshnessDecision:
    oracle_id: str
    data_age_seconds: float
    gate: str
    reason: str
    is_fresh: bool
    stale_risk_flag: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "oracle_id": self.oracle_id,
            "data_age_seconds": self.data_age_seconds,
            "gate": self.gate,
            "reason": self.reason,
            "is_fresh": self.is_fresh,
            "stale_risk_flag": self.stale_risk_flag,
        }


def evaluate_oracle_freshness(
    oracle_id: str,
    last_update_iso: str | None,
    threshold_seconds: float = _FRESHNESS_THRESHOLD_SECONDS,
) -> OracleFreshnessDecision:
    if last_update_iso is None:
        return OracleFreshnessDecision(
            oracle_id=oracle_id,
            data_age_seconds=float("inf"),
            gate="HOLD",
            reason="ORACLE_STALE_DATA_NO_TIMESTAMP",
            is_fresh=False,
            stale_risk_flag=True,
        )

    try:
        last_update = datetime.fromisoformat(last_update_iso)
        if last_update.tzinfo is None:
            last_update = last_update.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        age = (now - last_update).total_seconds()
    except (ValueError, TypeError):
        return OracleFreshnessDecision(
            oracle_id=oracle_id,
            data_age_seconds=float("inf"),
            gate="HOLD",
            reason="ORACLE_STALE_DATA_INVALID_TIMESTAMP",
            is_fresh=False,
            stale_risk_flag=True,
        )

    if age > threshold_seconds:
        return OracleFreshnessDecision(
            oracle_id=oracle_id,
            data_age_seconds=age,
            gate="HOLD",
            reason=f"ORACLE_STALE_DATA:{age:.0f}s>{threshold_seconds}s",
            is_fresh=False,
            stale_risk_flag=True,
        )

    return OracleFreshnessDecision(
        oracle_id=oracle_id,
        data_age_seconds=age,
        gate="ALLOW",
        reason="ORACLE_DATA_FRESH",
        is_fresh=True,
        stale_risk_flag=False,
    )

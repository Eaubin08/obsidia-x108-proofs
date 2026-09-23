"""OIE V0.1 — Meter: converts a raw Obsidia measurement into a CostReceipt."""
from __future__ import annotations

from typing import List, Optional

from .cost_receipt import CostReceipt, DomainMetrics
from .baselines import BASELINE_LABELS


def create_cost_receipt(
    *,
    layer: str,
    route: str,
    domain: str,
    action_type: str,
    elapsed_ms: float,
    internal_units: float,
    obsidia_cost_eur_per_1m: float,
    baseline_label: str,
    modules_activated: List[str] | None = None,
    modules_skipped: List[str] | None = None,
    kernel_status: str = "ACTIVE",
    proof_or_replay_available: bool = False,
    domain_metrics: Optional[DomainMetrics] = None,
) -> CostReceipt:
    """Return a CostReceipt for one Obsidia measurement vs. one Big Tech baseline.

    savings_ratio      = baseline_cost / obsidia_cost  (higher is better)
    avoided_cost       = baseline_cost - obsidia_cost
    domain_metrics     = optional per-domain business breakdown (V0.1)
    """
    if baseline_label not in BASELINE_LABELS:
        raise ValueError(
            f"Unknown baseline '{baseline_label}'. "
            f"Valid values: {list(BASELINE_LABELS)}"
        )
    if obsidia_cost_eur_per_1m <= 0:
        raise ValueError("obsidia_cost_eur_per_1m must be > 0")

    baseline_cost = BASELINE_LABELS[baseline_label]
    savings_ratio = baseline_cost / obsidia_cost_eur_per_1m
    avoided_cost = baseline_cost - obsidia_cost_eur_per_1m

    return CostReceipt(
        layer=layer,
        route=route,
        domain=domain,
        action_type=action_type,
        elapsed_ms=elapsed_ms,
        internal_units=internal_units,
        modules_activated=modules_activated or [],
        modules_skipped=modules_skipped or [],
        obsidia_cost_eur_per_1m=obsidia_cost_eur_per_1m,
        baseline_label=baseline_label,
        baseline_cost_eur_per_1m=baseline_cost,
        savings_ratio=savings_ratio,
        avoided_cost_eur_per_1m=avoided_cost,
        kernel_status=kernel_status,
        proof_or_replay_available=proof_or_replay_available,
        domain_metrics=domain_metrics,
    )

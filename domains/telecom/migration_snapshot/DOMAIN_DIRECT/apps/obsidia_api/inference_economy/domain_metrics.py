"""OIE V0.1 — Domain Metrics aggregation and DCA (Domain Cost Advantage).

Non-sovereign: read-only, no ACT, no kernel mutation, no memory write.
"""
from __future__ import annotations

from typing import List

from .cost_receipt import CostReceipt, DomainMetrics
from .baselines import BT_API_NORMAL, BT_AGENTIC


def compute_dca(obsidia_cost_eur_per_1m: float) -> dict:
    """Domain Cost Advantage vs the two standard baselines.

    DCA_API_NORMAL = BT_API_NORMAL / obsidia_cost
    DCA_AGENTIC    = BT_AGENTIC    / obsidia_cost
    """
    if obsidia_cost_eur_per_1m <= 0:
        raise ValueError("obsidia_cost_eur_per_1m must be > 0")
    return {
        "DCA_API_NORMAL": BT_API_NORMAL / obsidia_cost_eur_per_1m,
        "DCA_AGENTIC": BT_AGENTIC / obsidia_cost_eur_per_1m,
        "baseline_api_normal": BT_API_NORMAL,
        "baseline_agentic": BT_AGENTIC,
    }


def summarize_domain_metrics(receipts: List[CostReceipt]) -> dict:
    """Aggregate DomainMetrics by domain_name across a list of CostReceipts.

    Receipts without domain_metrics are skipped.
    Returns a dict keyed by domain_name.
    """
    aggregated: dict[str, dict] = {}

    for receipt in receipts:
        dm = receipt.domain_metrics
        if dm is None:
            continue

        name = dm.domain_name or receipt.domain
        if name not in aggregated:
            aggregated[name] = {
                "domain_name": name,
                "total_receipts": 0,
                "obsidia_total_cost_eur_per_1m": 0.0,
                "baseline_api_normal_cost_eur_per_1m": BT_API_NORMAL,
                "baseline_agentic_cost_eur_per_1m": BT_AGENTIC,
                "dca_api_normal": 0.0,
                "dca_agentic": 0.0,
                "avg_latency_ms": 0.0,
                "_latency_sum": 0.0,
                "avg_internal_units": 0.0,
                "_units_sum": 0.0,
                "tools_used": set(),
                "tools_skipped": set(),
                "llm_calls_avoided": 0,
                "external_api_calls_avoided": 0,
                "proof_or_replay_count": 0,
                "hold_count": 0,
                "block_count": 0,
                "act_count": 0,
                "unknowns_count": 0,
                "contradictions_count": 0,
            }

        agg = aggregated[name]
        agg["total_receipts"] += 1
        agg["obsidia_total_cost_eur_per_1m"] += receipt.obsidia_cost_eur_per_1m
        agg["_latency_sum"] += dm.domain_latency_ms
        agg["_units_sum"] += dm.domain_internal_units
        agg["tools_used"].update(dm.domain_tools_used)
        agg["tools_skipped"].update(dm.domain_tools_skipped)
        agg["llm_calls_avoided"] += dm.llm_calls_avoided
        agg["external_api_calls_avoided"] += dm.external_api_calls_avoided
        agg["hold_count"] += dm.hold_count
        agg["block_count"] += dm.block_count
        agg["act_count"] += dm.act_count
        agg["unknowns_count"] += dm.unknowns_count
        agg["contradictions_count"] += dm.contradictions_count
        if dm.proof_available or dm.replay_available:
            agg["proof_or_replay_count"] += 1

    # Post-aggregate: compute averages, DCA, serialise sets
    result = {}
    for name, agg in aggregated.items():
        n = agg["total_receipts"]
        avg_cost = agg["obsidia_total_cost_eur_per_1m"] / n if n > 0 else 0.0
        dca = compute_dca(avg_cost) if avg_cost > 0 else {"DCA_API_NORMAL": 0.0, "DCA_AGENTIC": 0.0}

        result[name] = {
            "domain_name": name,
            "total_receipts": n,
            "obsidia_total_cost_eur_per_1m": round(agg["obsidia_total_cost_eur_per_1m"], 6),
            "obsidia_avg_cost_eur_per_1m": round(avg_cost, 6),
            "baseline_api_normal_cost_eur_per_1m": BT_API_NORMAL,
            "baseline_agentic_cost_eur_per_1m": BT_AGENTIC,
            "dca_api_normal": round(dca["DCA_API_NORMAL"], 4),
            "dca_agentic": round(dca["DCA_AGENTIC"], 4),
            "avg_latency_ms": round(agg["_latency_sum"] / n, 4) if n > 0 else 0.0,
            "avg_internal_units": round(agg["_units_sum"] / n, 4) if n > 0 else 0.0,
            "tools_used": sorted(agg["tools_used"]),
            "tools_skipped": sorted(agg["tools_skipped"]),
            "llm_calls_avoided": agg["llm_calls_avoided"],
            "external_api_calls_avoided": agg["external_api_calls_avoided"],
            "proof_or_replay_rate": round(agg["proof_or_replay_count"] / n, 4) if n > 0 else 0.0,
            "hold_count": agg["hold_count"],
            "block_count": agg["block_count"],
            "act_count": agg["act_count"],
            "unknowns_count": agg["unknowns_count"],
            "contradictions_count": agg["contradictions_count"],
        }

    return result

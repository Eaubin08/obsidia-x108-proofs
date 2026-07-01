#!/usr/bin/env python3
"""OIE V0.1 -- Portfolio benchmark.

Rejoue les couts figes dans OBSIDIA_INFERENCE_ECONOMY_AUDIT_V0 (commit 73444cd),
produit un JSON de receipts, un resume console, calcule OSCA / OAPI / ODPI,
domain metrics summary et DCA par domaine.

Non-souverain : aucun ACT, aucune mutation kernel, aucune ecriture memoire.
Console : ASCII uniquement (compatible Windows cp1252).
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

# Allow running from repo root without install
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from apps.obsidia_api.inference_economy.meter import create_cost_receipt
from apps.obsidia_api.inference_economy.baselines import BT_API_NORMAL, BT_AGENTIC
from apps.obsidia_api.inference_economy.cost_receipt import DomainMetrics
from apps.obsidia_api.inference_economy.domain_metrics import (
    summarize_domain_metrics,
    compute_dca,
)

# ── Frozen audit portfolio (EUR / 1M actions) ────────────────────────────────
PORTFOLIO = [
    dict(
        label="Fast Path",
        layer="FAST_PATH",
        route="fast_path",
        domain="core",
        action_type="fast_dispatch",
        obsidia_cost=0.0015,
        baseline_label="BT_API_NORMAL",
        proof_or_replay_available=True,
        modules_activated=["router"],
        modules_skipped=["brody", "lean_checker"],
        category="api",
        domain_metrics=None,
    ),
    dict(
        label="Brody chat",
        layer="AGENTIC",
        route="brody_chat",
        domain="chat",
        action_type="conversational",
        obsidia_cost=0.20,
        baseline_label="BT_API_NORMAL",
        proof_or_replay_available=False,
        modules_activated=["brody", "router"],
        modules_skipped=["lean_checker"],
        category="api",
        domain_metrics=DomainMetrics(
            domain_name="brody",
            domain_action_type="conversational",
            domain_risk_level="LOW",
            domain_reversibility="HIGH",
            domain_cost_eur_per_1m=0.20,
            domain_latency_ms=85.0,
            domain_internal_units=1.2,
            domain_tools_used=["brody_chat", "router"],
            domain_tools_skipped=["lean_checker", "sigma"],
            external_api_calls_avoided=1,
            llm_calls_avoided=1,
            human_review_avoided_estimate=0.0,
            hold_count=0,
            block_count=0,
            act_count=0,
            unknowns_count=0,
            contradictions_count=0,
            proof_available=False,
            replay_available=False,
            business_cost_avoided_label="assistant_llm_api",
            business_cost_avoided_estimate_eur=24999.80,
            domain_savings_ratio=BT_API_NORMAL / 0.20,
        ),
    ),
    dict(
        label="Bank",
        layer="CONNECTORS",
        route="bank_connector",
        domain="bank",
        action_type="domain_query",
        obsidia_cost=0.70,
        baseline_label="BT_API_NORMAL",
        proof_or_replay_available=True,
        modules_activated=["bank_connector", "sigma", "router"],
        modules_skipped=["lean_checker"],
        category="domain",
        domain_metrics=DomainMetrics(
            domain_name="bank",
            domain_action_type="virement_decision",
            domain_risk_level="HIGH",
            domain_reversibility="LOW",
            domain_cost_eur_per_1m=0.70,
            domain_latency_ms=42.0,
            domain_internal_units=2.1,
            domain_tools_used=["bank_connector", "sigma", "router"],
            domain_tools_skipped=["lean_checker", "obsidure"],
            external_api_calls_avoided=3,
            llm_calls_avoided=2,
            human_review_avoided_estimate=0.15,
            hold_count=12,
            block_count=3,
            act_count=0,
            unknowns_count=1,
            contradictions_count=0,
            proof_available=True,
            replay_available=True,
            business_cost_avoided_label="bank_llm_domain_analysis",
            business_cost_avoided_estimate_eur=24999.30,
            domain_savings_ratio=BT_API_NORMAL / 0.70,
        ),
    ),
    dict(
        label="Trading",
        layer="CONNECTORS",
        route="trading_connector",
        domain="trading",
        action_type="domain_query",
        obsidia_cost=0.84,
        baseline_label="BT_API_NORMAL",
        proof_or_replay_available=True,
        modules_activated=["trading_connector", "sigma", "router"],
        modules_skipped=["lean_checker"],
        category="domain",
        domain_metrics=DomainMetrics(
            domain_name="trading",
            domain_action_type="signal_processing",
            domain_risk_level="HIGH",
            domain_reversibility="NONE",
            domain_cost_eur_per_1m=0.84,
            domain_latency_ms=18.0,
            domain_internal_units=1.8,
            domain_tools_used=["trading_connector", "sigma", "router"],
            domain_tools_skipped=["lean_checker", "obsidure"],
            external_api_calls_avoided=4,
            llm_calls_avoided=2,
            human_review_avoided_estimate=0.05,
            hold_count=8,
            block_count=5,
            act_count=0,
            unknowns_count=2,
            contradictions_count=1,
            proof_available=True,
            replay_available=True,
            business_cost_avoided_label="trading_llm_domain_analysis",
            business_cost_avoided_estimate_eur=24999.16,
            domain_savings_ratio=BT_API_NORMAL / 0.84,
        ),
    ),
    dict(
        label="GPS/Aviation",
        layer="CONNECTORS",
        route="aviation_connector",
        domain="aviation",
        action_type="domain_query",
        obsidia_cost=0.91,
        baseline_label="BT_API_NORMAL",
        proof_or_replay_available=True,
        modules_activated=["aviation_connector", "sigma", "router"],
        modules_skipped=["lean_checker"],
        category="domain",
        domain_metrics=DomainMetrics(
            domain_name="aviation",
            domain_action_type="terrain_signal",
            domain_risk_level="CRITICAL",
            domain_reversibility="NONE",
            domain_cost_eur_per_1m=0.91,
            domain_latency_ms=9.5,
            domain_internal_units=1.5,
            domain_tools_used=["aviation_connector", "sigma", "router"],
            domain_tools_skipped=["lean_checker", "obsidure"],
            external_api_calls_avoided=5,
            llm_calls_avoided=3,
            human_review_avoided_estimate=0.02,
            hold_count=4,
            block_count=7,
            act_count=0,
            unknowns_count=0,
            contradictions_count=2,
            proof_available=True,
            replay_available=True,
            business_cost_avoided_label="gps_llm_terrain_analysis",
            business_cost_avoided_estimate_eur=24999.09,
            domain_savings_ratio=BT_API_NORMAL / 0.91,
        ),
    ),
    dict(
        label="Lean canon check",
        layer="KERNEL",
        route="lean_canon_check",
        domain="proof",
        action_type="proof_verification",
        obsidia_cost=13.29,
        baseline_label="BT_API_NORMAL",
        proof_or_replay_available=True,
        modules_activated=["lean_checker", "router"],
        modules_skipped=[],
        category="kernel",
        domain_metrics=None,
    ),
    dict(
        label="Obsidure Lean cible",
        layer="KERNEL",
        route="obsidure_lean_targeted",
        domain="obsidure",
        action_type="targeted_proof",
        obsidia_cost=23.92,
        baseline_label="BT_API_NORMAL",
        proof_or_replay_available=True,
        modules_activated=["lean_checker", "obsidure", "router"],
        modules_skipped=[],
        category="kernel",
        domain_metrics=DomainMetrics(
            domain_name="obsidure",
            domain_action_type="lean_patch",
            domain_risk_level="MEDIUM",
            domain_reversibility="MEDIUM",
            domain_cost_eur_per_1m=23.92,
            domain_latency_ms=1200.0,
            domain_internal_units=8.0,
            domain_tools_used=["lean_checker", "obsidure", "router"],
            domain_tools_skipped=[],
            external_api_calls_avoided=2,
            llm_calls_avoided=5,
            human_review_avoided_estimate=0.30,
            hold_count=0,
            block_count=0,
            act_count=0,
            unknowns_count=1,
            contradictions_count=0,
            proof_available=True,
            replay_available=True,
            business_cost_avoided_label="external_code_agent",
            business_cost_avoided_estimate_eur=24976.08,
            domain_savings_ratio=BT_API_NORMAL / 23.92,
        ),
    ),
]


# ── Build receipts ────────────────────────────────────────────────────────────

def build_receipts() -> list:
    receipts = []
    for item in PORTFOLIO:
        r = create_cost_receipt(
            layer=item["layer"],
            route=item["route"],
            domain=item["domain"],
            action_type=item["action_type"],
            elapsed_ms=0.0,
            internal_units=0.0,
            obsidia_cost_eur_per_1m=item["obsidia_cost"],
            baseline_label=item["baseline_label"],
            modules_activated=item.get("modules_activated", []),
            modules_skipped=item.get("modules_skipped", []),
            proof_or_replay_available=item.get("proof_or_replay_available", False),
            domain_metrics=item.get("domain_metrics"),
        )
        receipts.append((item["label"], item["category"], r))
    return receipts


# ── Index computation ─────────────────────────────────────────────────────────

def osca(receipts: list) -> float:
    """OSCA -- moyenne geometrique des savings_ratio sur toutes les couches."""
    ratios = [r.savings_ratio for _, _, r in receipts]
    return math.exp(sum(math.log(x) for x in ratios) / len(ratios))


def oapi(receipts: list) -> float:
    """OAPI -- portefeuille Fast Path + Brody + Bank + Trading + GPS vs BT_API_NORMAL."""
    api_labels = {"Fast Path", "Brody chat", "Bank", "Trading", "GPS/Aviation"}
    selected = [r for label, _, r in receipts if label in api_labels]
    obsidia_avg = sum(r.obsidia_cost_eur_per_1m for r in selected) / len(selected)
    return BT_API_NORMAL / obsidia_avg


def odpi(receipts: list) -> float:
    """ODPI -- portefeuille domaines Bank + Trading + GPS vs BT_API_NORMAL."""
    domain_labels = {"Bank", "Trading", "GPS/Aviation"}
    selected = [r for label, _, r in receipts if label in domain_labels]
    obsidia_avg = sum(r.obsidia_cost_eur_per_1m for r in selected) / len(selected)
    return BT_API_NORMAL / obsidia_avg


# ── DCA per domain ────────────────────────────────────────────────────────────

DCA_TARGETS = {
    "Bank":                ("bank",     0.70),
    "Trading":             ("trading",  0.84),
    "GPS/Aviation":        ("aviation", 0.91),
    "Brody chat":          ("brody",    0.20),
    "Obsidure Lean cible": ("obsidure", 23.92),
}


def compute_all_dca() -> dict:
    result = {}
    for label, (domain, cost) in DCA_TARGETS.items():
        dca = compute_dca(cost)
        result[label] = {
            "domain": domain,
            "obsidia_cost_eur_per_1m": cost,
            "DCA_API_NORMAL": round(dca["DCA_API_NORMAL"], 2),
            "DCA_AGENTIC": round(dca["DCA_AGENTIC"], 2),
        }
    return result


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    receipts = build_receipts()

    print("\n=== OIE V0.1 -- Portfolio Benchmark ===\n")
    print(f"{'Route':<28} {'Obsidia EUR/1M':>16} {'Baseline EUR/1M':>16} {'Ratio':>12} {'Avoided EUR/1M':>16}")
    print("-" * 92)
    for label, _, r in receipts:
        print(
            f"{label:<28} "
            f"{r.obsidia_cost_eur_per_1m:>14.4f}   "
            f"{r.baseline_cost_eur_per_1m:>14.0f}   "
            f"{r.savings_ratio:>10.1f}x "
            f"{r.avoided_cost_eur_per_1m:>14.2f}"
        )

    osca_val = osca(receipts)
    oapi_val = oapi(receipts)
    odpi_val = odpi(receipts)

    print("\n--- Indices ---")
    print(f"  OSCA (geo-moyenne toutes couches) : {osca_val:>12.2f}x")
    print(f"  OAPI (portefeuille API)            : {oapi_val:>12.2f}x")
    print(f"  ODPI (portefeuille domaines)       : {odpi_val:>12.2f}x")

    # DCA per domain
    dca_all = compute_all_dca()
    print("\n--- DCA par domaine (vs BT_API_NORMAL / BT_AGENTIC) ---")
    print(f"{'Domaine':<24} {'Cout EUR/1M':>14} {'DCA_API_NORMAL':>16} {'DCA_AGENTIC':>14}")
    print("-" * 72)
    for label, d in dca_all.items():
        print(
            f"{label:<24} "
            f"{d['obsidia_cost_eur_per_1m']:>12.4f}   "
            f"{d['DCA_API_NORMAL']:>14.1f}x "
            f"{d['DCA_AGENTIC']:>12.1f}x"
        )

    # Domain metrics summary
    all_receipts = [r for _, _, r in receipts]
    domain_summary = summarize_domain_metrics(all_receipts)

    print("\n--- Domain Metrics Summary ---")
    for domain_name, summary in domain_summary.items():
        print(f"\n  [{domain_name.upper()}]")
        print(f"    receipts           : {summary['total_receipts']}")
        print(f"    avg cost EUR/1M    : {summary['obsidia_avg_cost_eur_per_1m']}")
        print(f"    DCA_API_NORMAL     : {summary['dca_api_normal']:.1f}x")
        print(f"    DCA_AGENTIC        : {summary['dca_agentic']:.1f}x")
        print(f"    llm_avoided        : {summary['llm_calls_avoided']}")
        print(f"    api_avoided        : {summary['external_api_calls_avoided']}")
        print(f"    hold/block/act     : {summary['hold_count']}/{summary['block_count']}/{summary['act_count']}")
        print(f"    proof_replay_rate  : {summary['proof_or_replay_rate']:.0%}")

    print()

    # JSON output
    output = {
        "benchmark": "OIE_V0.1_PORTFOLIO",
        "baseline": "BT_API_NORMAL",
        "indices": {
            "OSCA": round(osca_val, 4),
            "OAPI": round(oapi_val, 4),
            "ODPI": round(odpi_val, 4),
        },
        "dca_by_domain": dca_all,
        "domain_summary": domain_summary,
        "receipts": [r.to_dict() for _, _, r in receipts],
    }

    out_path = Path(__file__).parent / "oie_v0_portfolio_receipts.json"
    out_path.write_text(
        json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"Receipts JSON -> {out_path}")
    print("\nGovernance: readonly=True | emits_act=False | kernel_mutation=False\n")


if __name__ == "__main__":
    main()

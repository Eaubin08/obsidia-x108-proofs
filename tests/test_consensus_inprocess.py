#!/usr/bin/env python3
"""
OBSIDIA Phase 9 — Consensus Multi-Nœuds IN-PROCESS
Version sans HTTP / sans Docker : 4 nœuds simulés en threads Python.

Propriété démontrée : fail-closed
  - Si aucune supermajorité (3/4) n'est atteinte → décision = BLOCK
  - Si un nœud est en erreur → il contribue ERROR → pousse vers BLOCK
  - Seul un accord 3/4 sur ALLOW peut produire une décision positive

Usage :
  python3 distributed/test_consensus_inprocess.py
"""
import sys, os, json, threading, uuid

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from agents.run_pipeline import run_trading_pipeline
from agents.contracts import TradingState


# ─────────────────────────────────────────────────────────────────────────────
# Nœud Obsidia — appel direct au pipeline (pas de HTTP)
# ─────────────────────────────────────────────────────────────────────────────

def node_decide(node_id: str, state: TradingState, results: dict):
    """Un nœud = un appel au pipeline complet (agents + Guard X-108)."""
    try:
        envelope = run_trading_pipeline(state)
        results[node_id] = {
            "node_id": node_id,
            "decision": envelope.x108_gate,
            "market_verdict": envelope.market_verdict,
            "confidence": round(envelope.confidence, 4),
            "risk_flags": envelope.risk_flags,
            "contradictions": envelope.contradictions,
            "reason_code": envelope.reason_code,
            "severity": envelope.severity,
            "trace_id": str(uuid.uuid4())[:8]
        }
    except Exception as e:
        results[node_id] = {"node_id": node_id, "decision": "ERROR", "error": str(e)}


# ─────────────────────────────────────────────────────────────────────────────
# Agrégateur — règle supermajorité 3/4 (fail-closed)
# ─────────────────────────────────────────────────────────────────────────────

def aggregate_consensus(node_results: dict) -> dict:
    """
    Règle fail-closed :
    - 3/4 sur ALLOW → ALLOW
    - 3/4 sur HOLD  → HOLD
    - Sinon          → BLOCK (fail-closed)
    """
    counts = {}
    for r in node_results.values():
        d = r.get("decision", "ERROR")
        counts[d] = counts.get(d, 0) + 1

    best_decision, best_count = max(counts.items(), key=lambda x: x[1])

    if best_count >= 3 and best_decision not in ("ERROR", "BLOCK"):
        return {
            "final_decision": best_decision,
            "votes": counts,
            "supermajority": True,
            "threshold": "3/4",
            "fail_closed": False
        }
    else:
        return {
            "final_decision": "BLOCK",
            "votes": counts,
            "supermajority": False,
            "threshold": "3/4",
            "fail_closed": True,
            "reason": "No 3/4 supermajority — fail-closed applies"
        }


# ─────────────────────────────────────────────────────────────────────────────
# Scénarios
# ─────────────────────────────────────────────────────────────────────────────

def make_bullish_state():
    # Données identiques à examples/trading_bullish.json → produit ALLOW
    p = [100,101,102,103,104,106,108,110,111,113,115,117,118,119,121,123,124,126,127,129,131]
    h = [101,102,103,104,105,107,109,111,112,114,116,118,119,120,122,124,125,127,128,130,132]
    l = [99,100,101,102,103,105,107,109,110,112,114,116,117,118,120,122,123,125,126,128,130]
    v = [1000,1050,1100,1150,1200,1250,1300,1350,1400,1450,1500,1550,1600,1650,1700,1750,1800,1850,1900,1950,2000]
    n = len(p)
    return TradingState(
        symbol="BTCUSDT",
        prices=[float(x) for x in p],
        highs=[float(x) for x in h],
        lows=[float(x) for x in l],
        volumes=[float(x) for x in v],
        spreads_bps=[4.0] * n,
        sentiment_scores=[0.2] * n,
        event_risk_scores=[0.15] * n,
        btc_reference_prices=[float(x) for x in p],
        exposure=0.3,
        drawdown=0.02,
        order_book_imbalance=0.1,
        order_book_depth=5000.0,
        slippage_bps=3.0
    )

def make_crash_state():
    return TradingState(
        symbol="BTCUSDT",
        prices=[100.0, 98.0, 95.0, 90.0, 85.0, 80.0],
        highs=[101.0, 99.0, 96.0, 91.0, 86.0, 81.0],
        lows=[97.0, 95.0, 92.0, 87.0, 82.0, 77.0],
        volumes=[500.0, 400.0, 300.0, 200.0, 100.0, 50.0],
        spreads_bps=[50.0, 60.0, 70.0, 80.0, 90.0, 100.0],
        sentiment_scores=[-0.5, -0.6, -0.7, -0.75, -0.8, -0.85],
        event_risk_scores=[0.7, 0.75, 0.8, 0.85, 0.9, 0.95],
        btc_reference_prices=[100.0, 98.0, 95.0, 90.0, 85.0, 80.0],
        exposure=0.9,
        drawdown=0.25,
        order_book_imbalance=0.8,
        order_book_depth=100.0,
        slippage_bps=50.0
    )


SCENARIOS = [
    {
        "name": "Consensus normal — signal haussier fort",
        "state_fn": make_bullish_state,
        "expected_fail_closed": False,
        "expected_decision": "ALLOW"
    },
    {
        "name": "Fail-closed — signal crash (FRAUD_PATTERN attendu)",
        "state_fn": make_crash_state,
        "expected_fail_closed": True,
        "expected_decision": "BLOCK"
    }
]


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def run_scenario(scenario: dict) -> dict:
    print(f"\n{'='*60}")
    print(f"SCÉNARIO : {scenario['name']}")
    print(f"{'='*60}")

    NODE_IDS = ["node1", "node2", "node3", "node4"]
    results = {}
    threads = []
    state = scenario["state_fn"]()

    for node_id in NODE_IDS:
        t = threading.Thread(target=node_decide, args=(node_id, state, results))
        threads.append(t)
        t.start()

    for t in threads:
        t.join(timeout=15)

    print("\nVotes individuels :")
    for node_id in NODE_IDS:
        r = results.get(node_id, {"decision": "TIMEOUT"})
        print(f"  [{node_id}] decision={r.get('decision'):8s}  "
              f"confidence={r.get('confidence', 'N/A')}  "
              f"risk_flags={r.get('risk_flags', [])}")

    consensus = aggregate_consensus(results)
    print(f"\nCONSENSUS FINAL :")
    print(json.dumps(consensus, indent=2))

    return {"scenario": scenario["name"], "node_results": results,
            "consensus": consensus, "expected": scenario}


def main():
    print("=" * 60)
    print("OBSIDIA Phase 9 — Consensus Multi-Nœuds IN-PROCESS")
    print("4 nœuds Python en threads — sans HTTP, sans Docker")
    print("Propriété testée : fail-closed (3/4 supermajorité)")
    print("=" * 60)

    all_results = []
    for scenario in SCENARIOS:
        result = run_scenario(scenario)
        all_results.append(result)

    print(f"\n{'='*60}")
    print("RÉSUMÉ")
    print(f"{'='*60}")

    all_pass = True
    for r in all_results:
        c = r["consensus"]
        exp = r["expected"]
        decision_ok = c["final_decision"] == exp["expected_decision"]
        fail_closed_ok = c["fail_closed"] == exp["expected_fail_closed"]
        ok = decision_ok and fail_closed_ok
        if not ok:
            all_pass = False
        status = "✓ PASS" if ok else "✗ FAIL"
        print(f"  {status}  {r['scenario'][:55]}")
        print(f"         → decision={c['final_decision']} (attendu={exp['expected_decision']}) | "
              f"fail_closed={c['fail_closed']} (attendu={exp['expected_fail_closed']})")

    print(f"\nPropriété fail-closed : {'VERIFIED' if all_pass else 'PARTIAL'}")
    print(f"\nRÉSULTAT GLOBAL : {'PASS' if all_pass else 'PARTIAL'}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())

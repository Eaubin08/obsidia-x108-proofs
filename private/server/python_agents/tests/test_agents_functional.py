from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from obsidia_canonical_agents import TradingState, BankState, EcomState
from obsidia_canonical_agents.protocols import run_trading_pipeline, run_bank_pipeline, run_ecom_pipeline, build_agent_registry


def make_trading_state():
    return TradingState(
        symbol="BTCUSDT",
        prices=[100,101,102,103,104,106,108,110,111,113,115,117,118,119,121,123,124,126,127,129,131],
        highs=[101,102,103,104,105,107,109,111,112,114,116,118,119,120,122,124,125,127,128,130,132],
        lows=[99,100,101,102,103,105,107,109,110,112,114,116,117,118,120,122,123,125,126,128,130],
        volumes=[1000 + i*50 for i in range(21)],
        spreads_bps=[4]*21,
        sentiment_scores=[0.2]*21,
        event_risk_scores=[0.15]*21,
        btc_reference_prices=[100,101,102,103,104,106,108,110,111,113,115,117,118,119,121,123,124,126,127,129,131],
        exposure=0.2,
        drawdown=0.01,
        order_book_imbalance=0.15,
        order_book_depth=1.2,
        slippage_bps=2,
    )


def make_bank_state():
    return BankState(
        transaction_type="TRANSFER",
        amount=1200,
        channel="mobile",
        counterparty_known=True,
        counterparty_age_days=120,
        account_balance=10000,
        available_cash=8500,
        historical_avg_amount=300,
        behavior_shift_score=0.25,
        fraud_score=0.10,
        policy_limit=5000,
        affordability_score=0.9,
        urgency_score=0.2,
        identity_mismatch_score=0.1,
        narrative_conflict_score=0.1,
        device_trust_score=0.95,
        recent_failed_attempts=0,
        elapsed_s=140,
        min_required_elapsed_s=108,
    )


def make_ecom_state():
    return EcomState(
        session_id="sess-1",
        traffic_quality=0.8,
        basket_intent_score=0.76,
        stock_ok=True,
        margin_rate=0.22,
        roas=2.4,
        conversion_readiness=0.77,
        fulfillment_risk=0.22,
        customer_trust=0.85,
        intent_conflict_score=0.1,
        checkout_friction_score=0.2,
        merchant_policy_score=0.9,
        basket_value=140,
        ad_spend=20,
        order_value=140,
        x108_compliance_rate=0.95,
    )


def test_registry_builds_all_domains():
    reg = build_agent_registry()
    assert "trading" in reg and "bank" in reg and "ecom" in reg and "meta" in reg
    assert len(reg["trading"]) >= 17
    assert len(reg["bank"]) >= 12
    assert len(reg["ecom"]) >= 12
    assert len(reg["meta"]) >= 10


def test_trading_pipeline_outputs_canonical_envelope():
    env = run_trading_pipeline(make_trading_state())
    assert env.domain == "trading"
    assert env.x108_gate in {"ALLOW", "HOLD", "BLOCK"}
    assert env.market_verdict in {"EXECUTE_LONG", "EXECUTE_SHORT", "REVIEW"}


def test_bank_pipeline_outputs_canonical_envelope():
    env = run_bank_pipeline(make_bank_state())
    assert env.domain == "bank"
    assert env.x108_gate in {"ALLOW", "HOLD", "BLOCK"}
    assert env.market_verdict in {"AUTHORIZE", "ANALYZE", "BLOCK"}


def test_ecom_pipeline_outputs_canonical_envelope():
    env = run_ecom_pipeline(make_ecom_state())
    assert env.domain == "ecom"
    assert env.x108_gate in {"ALLOW", "HOLD", "BLOCK"}
    assert env.market_verdict in {"PAY", "WAIT", "REFUSE"}


def test_ticket_is_emitted_only_on_allow():
    env = run_bank_pipeline(make_bank_state())
    if env.x108_gate == "ALLOW":
        assert env.ticket_required is True
        assert env.ticket_id is not None
    else:
        assert env.ticket_id is None


def test_guard_is_unique_contract_style():
    t = run_trading_pipeline(make_trading_state())
    b = run_bank_pipeline(make_bank_state())
    e = run_ecom_pipeline(make_ecom_state())
    assert {t.x108_gate, b.x108_gate, e.x108_gate}.issubset({"ALLOW", "HOLD", "BLOCK"})

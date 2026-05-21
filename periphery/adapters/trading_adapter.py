from __future__ import annotations

from periphery.common import ActionCandidate
from sigma.contracts import TradingState

DEFAULT_PRICES = [100 + i * 0.05 for i in range(80)]
DEFAULT_TRADING_STATE = {
    "symbol": "BTC/USDT",
    "prices": DEFAULT_PRICES,
    "highs": [p * 1.002 for p in DEFAULT_PRICES],
    "lows": [p * 0.998 for p in DEFAULT_PRICES],
    "volumes": [1000.0 for _ in DEFAULT_PRICES],
    "spreads_bps": [5.0 for _ in DEFAULT_PRICES],
    "sentiment_scores": [0.05 for _ in DEFAULT_PRICES],
    "event_risk_scores": [0.1 for _ in DEFAULT_PRICES],
    "btc_reference_prices": DEFAULT_PRICES,
    "drawdown": 0.01,
    "exposure": 0.25,
    "slippage_bps": 1.0,
    "order_book_imbalance": 0.0,
}

def build_trading_action(payload: dict) -> ActionCandidate:
    return ActionCandidate(
        action_id=payload.get("action_id", "trading-action"),
        domain="trading",
        actor_id=payload.get("actor_id", "trading-agent"),
        intent=payload.get("intent", "trade_execution_review"),
        action_type=payload.get("action_type", "trade"),
        irreversible=bool(payload.get("irreversible", True)),
        timestamp_plan=payload.get("timestamp_plan", ""),
        timestamp_exec=payload.get("timestamp_exec"),
        payload=payload,
    )

def build_trading_state(payload: dict) -> TradingState:
    data = dict(DEFAULT_TRADING_STATE)
    for k, v in payload.items():
        if k in data or k in {"symbol", "prices", "highs", "lows", "volumes", "spreads_bps", "sentiment_scores", "event_risk_scores", "btc_reference_prices", "drawdown", "exposure", "slippage_bps", "order_book_imbalance"}:
            data[k] = v
    return TradingState(**data)

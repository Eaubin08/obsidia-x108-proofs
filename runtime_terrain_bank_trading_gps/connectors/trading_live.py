from __future__ import annotations

import os
import time
from typing import Any

import requests


DEFAULT_API_BASE = os.environ.get("OBSIDIA_API_BASE", "http://127.0.0.1:8000")
TRADING_ENDPOINT = "/api/periphery/monitoring/adapters/trading"
MAX_HISTORY = 20


def build_trading_payload(symbol: str, history: dict[str, list[float]]) -> dict[str, Any]:
    prices = history.get("prices", [])
    return {
        "payload": {
            "action_id": "trading-live-flow",
            "actor_id": "trading-connector",
            "intent": "trade_execution_review",
            "action_type": "trade",
            "irreversible": True,
            "symbol": symbol,
            "prices": prices,
            "highs": history.get("highs", []),
            "lows": history.get("lows", []),
            "volumes": history.get("volumes", []),
            "spreads_bps": history.get("spreads_bps", [5.0 for _ in prices]),
            "sentiment_scores": history.get("sentiment_scores", [0.05 for _ in prices]),
            "event_risk_scores": history.get("event_risk_scores", [0.1 for _ in prices]),
            "btc_reference_prices": history.get("btc_reference_prices", prices),
            "drawdown": 0.01,
            "exposure": 0.25,
            "slippage_bps": 1.0,
            "order_book_imbalance": 0.0,
        }
    }


def send_trading_payload(
    symbol: str,
    history: dict[str, list[float]],
    api_base: str = DEFAULT_API_BASE,
    timeout: int = 10,
):
    url = f"{api_base.rstrip('/')}{TRADING_ENDPOINT}"
    return requests.post(url, json=build_trading_payload(symbol, history), timeout=timeout)


def stream_to_kernel(api_base: str = DEFAULT_API_BASE):
    try:
        import ccxt
    except Exception as exc:
        raise RuntimeError("ccxt is required only for live trading stream") from exc

    exchange = ccxt.binance()
    symbol = "BTC/USDT"

    history = {
        "prices": [],
        "highs": [],
        "lows": [],
        "volumes": [],
    }

    print(f"📡 [CONNECTEUR] Trading live vers {api_base}{TRADING_ENDPOINT}")

    while True:
        try:
            ticker = exchange.fetch_ticker(symbol)

            for key, val in [
                ("prices", "last"),
                ("highs", "high"),
                ("lows", "low"),
                ("volumes", "baseVolume"),
            ]:
                history[key].append(float(ticker[val]))
                if len(history[key]) > MAX_HISTORY:
                    history[key].pop(0)

            if len(history["prices"]) >= 5:
                res = send_trading_payload(symbol, history, api_base=api_base, timeout=10)

                if res.status_code == 200:
                    data = res.json().get("data", res.json())
                    env = data.get("domain_sigma_envelope", {})
                    print(
                        "✅ [TRADING] Sigma envelope | "
                        f"domain={env.get('domain')} gate={env.get('x108_gate')} "
                        f"authority={env.get('decision_authority')} emits_act={env.get('emits_act')}"
                    )
                else:
                    print(f"⚠️ [TRADING] API error: {res.status_code} {res.text[:250]}")
            else:
                print(f"⏳ Accumulation des données... ({len(history['prices'])}/{MAX_HISTORY})")

            time.sleep(2)

        except Exception as e:
            print(f"❌ [TRADING] Error: {e}")
            time.sleep(5)


if __name__ == "__main__":
    stream_to_kernel()

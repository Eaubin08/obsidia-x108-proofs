import ccxt
import requests
import time
import sys

def stream_to_kernel():
    exchange = ccxt.binance()
    symbol = 'BTC/USDT'
    print(f"📡 [CONNECTEUR] Envoi des données vers le Kernel (Format Listes)...")

    while True:
        try:
            ticker = exchange.fetch_ticker(symbol)
            
            # On adapte le payload pour coller EXACTEMENT à tes listes dans contracts.py
            payload = {
                "domain": "trading",
                "state": {
                    "symbol": symbol,
                    "prices": [float(ticker['last'])],
                    "highs": [float(ticker['high'])],
                    "lows": [float(ticker['low'])],
                    "volumes": [float(ticker['baseVolume'])]
                },
                "votes": [
                    {
                        "agent_id": "BINANCE_LIVE",
                        "vote": "ALLOW",
                        "confidence": 0.99,
                        "domain": "trading"
                    }
                ]
            }

            requests.post("http://localhost:3001/kernel/ragnarok", json=payload)
            print(f"✅ Flux envoyé : {ticker['last']}")
            time.sleep(2)

        except Exception as e:
            print(f"❌ Erreur : {e}")
            time.sleep(5)

if __name__ == "__main__":
    stream_to_kernel()

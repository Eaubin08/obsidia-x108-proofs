import ccxt
import requests
import time
import sys

# Configuration du Buffer pour satisfaire Sigma
MAX_HISTORY = 20  # Nombre de bougies nécessaires pour la stabilité

def stream_to_kernel():
    exchange = ccxt.binance()
    symbol = 'BTC/USDT'
    
    # Initialisation des historiques
    history = {
        "prices": [],
        "highs": [],
        "lows": [],
        "volumes": []
    }

    print(f"📡 [CONNECTEUR] Initialisation de la Trinity Trading ({symbol})...")

    while True:
        try:
            ticker = exchange.fetch_ticker(symbol)
            
            # Mise à jour des listes (Rolling Buffer)
            for key, val in [("prices", 'last'), ("highs", 'high'), ("lows", 'low'), ("volumes", 'baseVolume')]:
                history[key].append(float(ticker[val]))
                # On garde seulement les MAX_HISTORY derniers éléments
                if len(history[key]) > MAX_HISTORY:
                    history[key].pop(0)

            # On n'envoie au Kernel que si on a assez de données pour être "Souverain"
            if len(history["prices"]) >= 5: # On commence à envoyer dès 5 points
                payload = {
                    "domain": "trading",
                    "state": {
                        "symbol": symbol,
                        "prices": history["prices"],
                        "highs": history["highs"],
                        "lows": history["lows"],
                        "volumes": history["volumes"],
                        # Ajout de champs vides pour éviter les "unexpected keyword" si besoin
                        "spreads_bps": [0.0],
                        "sentiment_scores": [0.5],
                        "event_risk_scores": [0.1],
                        "btc_reference_prices": history["prices"]
                    },
                    "votes": [
                        {
                            "agent_id": "BINANCE_LIVE_CORE",
                            "vote": "ALLOW",
                            "confidence": 0.99,
                            "domain": "trading"
                        }
                    ]
                }

                response = requests.post("http://localhost:3001/kernel/ragnarok", json=payload)
                
                status_color = "🟢" if len(history["prices"]) >= MAX_HISTORY else "🟡"
                print(f"{status_color} Flux envoyé ({len(history['prices'])}/{MAX_HISTORY} pts) : {ticker['last']}")
            else:
                print(f"⏳ Accumulation des données... ({len(history['prices'])}/{MAX_HISTORY})")

            time.sleep(2)

        except Exception as e:
            print(f"❌ Erreur : {e}")
            time.sleep(5)

if __name__ == "__main__":
    stream_to_kernel()
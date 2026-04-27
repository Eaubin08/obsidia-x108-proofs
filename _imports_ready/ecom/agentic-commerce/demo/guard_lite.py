import time

# Internal state (opaque, minimal)
_LAST_ACTION_TS = None

def evaluate(action):
    """
    Opaque temporal & coherence safety gate.
    Behavior is observable, logic is intentionally minimal.
    """

    global _LAST_ACTION_TS
    now = time.time()

    # --- Temporal constraint ---
    if _LAST_ACTION_TS is not None:
        delta = now - _LAST_ACTION_TS
        if delta < 10:   # temporal HOLD window (seconds)
            return "BLOCK"

    # --- Coherence proxy (intentionally opaque) ---
    coherence = action.get("coherence", 1.0)

    if coherence < 0.6:
        return "BLOCK"

    # --- Irreversibility guard ---
    amount = action.get("amount_usdc", 0)
    if amount > 0:
        _LAST_ACTION_TS = now

    return "ALLOW"

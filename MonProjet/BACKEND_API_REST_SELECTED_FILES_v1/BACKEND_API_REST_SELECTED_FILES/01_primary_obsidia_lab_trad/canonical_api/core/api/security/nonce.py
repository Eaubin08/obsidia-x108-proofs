import os
import json
import hashlib

NONCE_STORE_PATH = os.path.join(os.path.dirname(__file__), "nonce_store.json")

def _load_store():
    if not os.path.exists(NONCE_STORE_PATH):
        return set()
    with open(NONCE_STORE_PATH, "r", encoding="utf-8") as f:
        return set(json.load(f))

def _save_store(store):
    with open(NONCE_STORE_PATH, "w", encoding="utf-8") as f:
        json.dump(list(store), f)

def check_and_store_nonce(nonce: str):
    if not nonce:
        raise ValueError("Nonce required")

    nonce_hash = hashlib.sha256(nonce.encode()).hexdigest()
    store = _load_store()

    if nonce_hash in store:
        raise ValueError("Replay detected: nonce already used")

    store.add(nonce_hash)
    _save_store(store)

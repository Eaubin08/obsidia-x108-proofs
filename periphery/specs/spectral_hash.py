# Spectral hash minimal, non décisionnel
import hashlib
import re
from collections import Counter

def extract_features(payload):
    text = payload.decode("utf-8", errors="ignore") if isinstance(payload, (bytes, bytearray)) else str(payload)
    words = re.findall(r"[A-Za-zÀ-ÿ0-9_]+", text.lower())
    counts = Counter(words)
    urgency = sum(1 for w in words if w in {"urgent","vite","danger","bloque","crash","erreur","fail","risque"})
    tension = min(1.0, (text.count("!") + text.count("?") + urgency) / 10.0)
    repetition = max(counts.values()) / max(1, len(words)) if counts else 0.0
    return {
        "length": min(1.0, len(text) / 1000.0),
        "word_count": min(1.0, len(words) / 200.0),
        "urgency": min(1.0, urgency / 5.0),
        "tension": tension,
        "repetition": min(1.0, repetition),
        "hash": hashlib.sha256(text.encode("utf-8")).hexdigest()
    }

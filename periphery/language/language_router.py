from __future__ import annotations

_SUPPORTED_LANGUAGES = {"fr", "en", "es", "de", "it", "pt", "nl", "ar", "zh", "ja"}
_AUTHORITY_MARKERS = {"admin:", "root:", "system:", "kernel:", "sudo:", "override:"}


def detect_language(text: str) -> str:
    lower = text.lower()
    if any(w in lower for w in ["le ", "la ", "les ", "un ", "une ", "bonjour", "merci"]):
        return "fr"
    if any(w in lower for w in ["the ", "is ", "are ", "hello", "thank"]):
        return "en"
    return "unknown"


def has_authority_claim(text: str) -> bool:
    lower = text.lower()
    return any(m in lower for m in _AUTHORITY_MARKERS)


def route_language(text: str) -> dict:
    if has_authority_claim(text):
        return {
            "language": "UNKNOWN",
            "authority_claim_detected": True,
            "routable": False,
            "reason": "AUTHORITY_NOT_ROUTABLE",
        }
    lang = detect_language(text)
    return {
        "language": lang,
        "authority_claim_detected": False,
        "routable": lang != "unknown",
        "reason": "LANGUAGE_ROUTED" if lang != "unknown" else "LANGUAGE_UNKNOWN",
    }

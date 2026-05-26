"""
Brody Text Encoding — UTF-8 mojibake detection and repair
===========================================================
Detects and repairs common UTF-8 mojibake patterns that occur
when UTF-8 bytes are decoded as Windows-1252 or Latin-1.

Patterns fixed:
  "crÃ©ation" → "création"
  "mÃ©moire" → "mémoire"
  "rÃ©ponds" → "réponds"
  "dÃ©cision" → "décision"
  "prÃ©cÃ©dent" → "précédent"
  "Ã¨" → "è"
  "Ã " → "à"
  "â\u0080\u0099" → "'" (smart quote)
"""
from __future__ import annotations

# Known mojibake pairs: (garbled, correct)
_MOJIBAKE_MAP: dict[str, str] = {
    "Ã©": "é",
    "Ã¨": "è",
    "Ãª": "ê",
    "Ã«": "ë",
    "Ã ": "à",
    "Ã¢": "â",
    "Ã¹": "ù",
    "Ã»": "û",
    "Ã¼": "ü",
    "Ã®": "î",
    "Ã¯": "ï",
    "Ã´": "ô",
    "Ã¶": "ö",
    "Ã§": "ç",
    "Å\u0093": "œ",
    "â\u0080\u0099": "'",
    "â\u0080\u009c": '"',
    "â\u0080\u009d": '"',
    "â\u0080\u0093": "–",
    "â\u0080\u0094": "—",
    # Uppercase French (Latin-1: UTF-8 bytes decoded as ISO-8859-1, C1 range)
    "Ã": "É",    # É
    "Ã": "È",    # È
    "Ã": "Ê",    # Ê
    "Ã": "Ë",    # Ë
    "Ã": "À",    # À
    "Ã": "Â",    # Â
    "Ã": "Ù",    # Ù
    "Ã": "Û",    # Û
    "Ã": "Ü",    # Ü
    "Ã": "Î",    # Î
    "Ã": "Ô",    # Ô
    "Ã": "Ö",    # Ö
    "Ã": "Ç",    # Ç
    "Å": "Œ",    # Œ
    # Uppercase French (CP1252: UTF-8 bytes decoded as Windows-1252, printable)
    "Ã‰": "É",    # É
    "Ãˆ": "È",    # È
    "ÃŠ": "Ê",    # Ê
    "Ã‹": "Ë",    # Ë
    "Ã€": "À",    # À
    "Ã‚": "Â",    # Â
    "Ã™": "Ù",    # Ù
    "Ã›": "Û",    # Û
    "Ãœ": "Ü",    # Ü
    "ÃŽ": "Î",    # Î
    "Ã”": "Ô",    # Ô
    "Ã–": "Ö",    # Ö
    "Ã‡": "Ç",    # Ç
    "Å’": "Œ",    # Œ
    # French punctuation (Latin-1 supplement, same in both encodings)
    "Â«": "«",    # «
    "Â»": "»",    # »
    "Â°": "°",    # °
    "Â·": "·",    # ·
}


def is_mojibake(text: str) -> bool:
    """Check if text likely contains UTF-8 mojibake patterns."""
    if not text:
        return False
    for garbled in _MOJIBAKE_MAP:
        if garbled in text:
            return True
    return False


def normalize_brody_text(text: str) -> str:
    """
    Repair known UTF-8 mojibake patterns in Brody response text.
    Also applies basic whitespace cleanup.
    Does NOT modify valid UTF-8 text.
    """
    if not text:
        return text

    result = text
    for garbled, correct in _MOJIBAKE_MAP.items():
        result = result.replace(garbled, correct)

    # Clean trailing/leading whitespace but preserve paragraph breaks
    result = result.strip()

    return result


def safe_brody_decode(raw_bytes: bytes) -> str:
    """
    Safely decode bytes to string, trying UTF-8 first,
    then Windows-1252, then Latin-1 with replacement.
    Returns normalized text.
    """
    if not raw_bytes:
        return ""

    # Try UTF-8
    try:
        text = raw_bytes.decode("utf-8")
        return normalize_brody_text(text)
    except UnicodeDecodeError:
        pass

    # Try Windows-1252 (common mojibake source)
    try:
        text = raw_bytes.decode("cp1252")
        return normalize_brody_text(text)
    except UnicodeDecodeError:
        pass

    # Last resort: replace errors
    text = raw_bytes.decode("utf-8", errors="replace")
    return normalize_brody_text(text)

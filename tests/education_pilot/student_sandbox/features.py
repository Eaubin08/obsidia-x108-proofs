"""Generic contextual features (design R3 §1.2). Identical for every target word.

No sense, no cue word and no exam content is encoded here. The only lexical lists are
closed French grammatical classes (determiners / possessives, function words), which name
no sense of any word.

Contamination note (preregistration §7): design R3 cites the possessive "sa" as an example
determiner; that form never occurs in the teaching data and does occur in the private exams,
most likely an echo of the author having read them. It receives NO special treatment: it is one
member of the closed possessive class below, like every other determiner.
"""
from __future__ import annotations

import re
import unicodedata

WINDOW = 3

# Feature classes and their frozen weights (design R3 §1.3 table).
WEIGHTS = {"POS": 1.0, "NG": 1.0, "SURF": 1.0, "DET": 1.0, "BOW": 0.5, "CHAR": 0.3}
NON_TRIVIAL = ("POS", "NG")      # N6: position and target n-gram features, function words included

DETERMINERS = set("le la les l un une des du de d au aux ce cet cette ces mon ma mes ton ta tes son sa ses "
                  "notre nos votre vos leur leurs quel quelle quels quelles".split())
QUANTIFIERS = set("tout toute tous toutes".split())
FUNCTION_WORDS = DETERMINERS | QUANTIFIERS | set(
    "a à il elle ils elles on en et ne n pas plus se s qu que qui c est été avec dans je j me m tu te t nous "
    "vous y par pour sur sous vers ont sont être avoir fait très ou où mais donc car si sans".split())


def fold(text: str) -> str:
    """Lower-case, then fold accents (deterministic)."""
    decomposed = unicodedata.normalize("NFD", text.lower())
    return "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")


def tokenize(sentence: str) -> list[str]:
    return [fold(t) for t in re.findall(r"\w+", sentence)]


def stem(word: str) -> str:
    w = fold(word)
    return w[:max(4, len(w) - 2)]


def target_index(tokens: list[str], word: str) -> int | None:
    s = stem(word)
    for i, tok in enumerate(tokens):
        if tok.startswith(s):
            return i
    return None


def _trigrams(token: str) -> set[str]:
    padded = f"#{token}#"
    return {padded[i:i + 3] for i in range(len(padded) - 2)}


def extract(word: str, sentence: str) -> list[str]:
    """Sorted feature strings 'CLASS:value' for the first occurrence of `word`."""
    tokens = tokenize(sentence)
    raw = re.findall(r"\w+", sentence)
    i = target_index(tokens, word)
    if i is None:
        return []
    feats: set[str] = set()
    for off in range(-WINDOW, WINDOW + 1):
        j = i + off
        if off and 0 <= j < len(tokens):
            feats.add(f"POS:P{off:+d}={tokens[j]}")
    for a, b in ((i - 1, i + 1), (i, i + 2), (i - 2, i + 1), (i - 1, i + 2), (i, i + 3)):
        if a >= 0 and b <= len(tokens) and b - a >= 2:
            feats.add("NG:" + "_".join(tokens[a:b]))
    feats.add("SURF:" + ("plural" if tokens[i].endswith(("s", "x")) else "singular"))
    if raw[i][:1].isupper():
        feats.add("SURF:capital")
    for j in range(i - 1, max(-1, i - 3), -1):
        if tokens[j] in DETERMINERS:
            det = tokens[j]
            if j - 1 >= 0 and tokens[j - 1] in QUANTIFIERS:
                det = f"{tokens[j - 1]}_{det}"
            feats.add(f"DET:{det}")
            break
    content = [t for k, t in enumerate(tokens) if k != i and t not in FUNCTION_WORDS and len(t) > 2]
    feats.update(f"BOW:{t}" for t in content)
    for k in range(max(0, i - WINDOW), min(len(tokens), i + WINDOW + 1)):
        t = tokens[k]
        if k != i and t not in FUNCTION_WORDS and len(t) > 2:
            feats.update(f"CHAR:{g}" for g in _trigrams(t))
    return sorted(feats)


def weight(feature: str) -> float:
    return WEIGHTS[feature.split(":", 1)[0]]


def is_non_trivial(feature: str) -> bool:
    return feature.split(":", 1)[0] in NON_TRIVIAL

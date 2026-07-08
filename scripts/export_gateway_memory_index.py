#!/usr/bin/env python3
"""Exporteur read-only : memoire canonique -> index semantique du gateway.

Source  : periphery/obsidure_math_memory_readonly/MATH_MEMORY_INDEX.json
          (filtre : can_be_used_by_obsidure=true, status != MISSING_CONTEXT)
Sortie  : registries/gateway_memory_index.json
          entrees taguees par arbres dominants (34 arbres MMONDE, Shazam)

Regles :
  - lecture seule sur la source canonique (memory_write=False respecte)
  - le tagging reutilise les KEYWORDS de 05_SHAZAM_COGNITIF, mais avec
    normalisation (pliage d'accents + matching par mots entiers) pour
    corriger les deux defauts mesures au smoke test : sensibilite aux
    accents et faux positifs par sous-chaine ("moi" dans "memoire").
  - relancer cet export quand la memoire canonique evolue.
"""
from __future__ import annotations

import json
import re
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE = REPO_ROOT / "periphery" / "obsidure_math_memory_readonly" / "MATH_MEMORY_INDEX.json"
SHAZAM_DIR = REPO_ROOT / "periphery" / "OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1" / "05_SHAZAM_COGNITIF"
OUTPUT = REPO_ROOT / "registries" / "gateway_memory_index.json"

sys.path.insert(0, str(SHAZAM_DIR))
from shazam_cognitif import KEYWORDS  # noqa: E402


def normalize(text: str) -> str:
    folded = unicodedata.normalize("NFKD", str(text))
    folded = "".join(c for c in folded if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", folded.lower()).strip()


def words(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", normalize(text)))


# Table des 34 arbres, mots-cles normalises une seule fois.
TREE_KEYWORDS: dict[int, set[str]] = {
    idx: {normalize(k) for k in kws} for idx, kws in KEYWORDS.items()
}


def dominant_trees(text: str) -> dict[str, int]:
    """Arbres actives par matching mots entiers, accents plies."""
    ws = words(text)
    hits = {}
    for idx, kws in TREE_KEYWORDS.items():
        n = len(ws & kws)
        if n:
            hits[str(idx)] = n
    return hits


def main() -> int:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    entries = []
    for item in data.get("items", []):
        if not item.get("can_be_used_by_obsidure"):
            continue
        if item.get("status") == "MISSING_CONTEXT":
            continue
        text = " ".join(str(item.get(f, "") or "") for f in
                        ("name", "human_definition", "notes"))
        domains = item.get("related_domains") or []
        full = text + " " + " ".join(map(str, domains))
        entries.append({
            "id": item.get("id"),
            "name": item.get("name"),
            "answer": (item.get("human_definition") or "").strip(),
            "status": item.get("status"),
            "trees": dominant_trees(full),
            "tokens": sorted(words(full)),
            "source": "MATH_MEMORY_INDEX",
        })

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_ts": datetime.now(timezone.utc).isoformat(),
        "source_file": str(SOURCE.relative_to(REPO_ROOT)),
        "tagging": "SHAZAM_34_TREES_NORMALIZED_WHOLE_WORD",
        "decision_authority": "KX108_ONLY",
        "entry_count": len(entries),
        "entries": entries,
    }
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=1),
                      encoding="utf-8")
    print(f"exported {len(entries)} entries -> {OUTPUT.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

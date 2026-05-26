"""
Memory Candidate Ledger — append-only JSONL log of all memory candidates.
Never overwrites. No real memory write.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .memory_candidate import MemoryCandidate

_DEFAULT_LEDGER_PATH = Path("_local_audits") / "memory_candidate_ledger.jsonl"


def append_memory_candidate(candidate: MemoryCandidate, ledger_path: Path | None = None) -> None:
    path = ledger_path or _DEFAULT_LEDGER_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(candidate.to_dict(), ensure_ascii=False) + "\n")


def read_memory_candidates(ledger_path: Path | None = None) -> list[dict]:
    path = ledger_path or _DEFAULT_LEDGER_PATH
    if not path.exists():
        return []
    candidates = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    candidates.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return candidates

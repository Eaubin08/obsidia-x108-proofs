from __future__ import annotations

import hashlib
import json
import os
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any

from .gencoin_distribution import DistributionCandidate


_DEFAULT_LEDGER_PATH = os.path.join(
    os.path.dirname(__file__), "..", "audit", "gencoin_ledger.jsonl"
)


@dataclass
class LedgerEntry:
    ledger_id: str
    os3_ticket_id: str
    action_id: str
    x108_gate: str
    proof_valid: bool
    gross_value: float
    total_debt: float
    net_value: float
    gencoin_candidate: float
    mint_allowed: bool
    distribution: dict
    input_hash: str
    output_hash: str
    trace_hash: str
    timestamp: str
    assisted_ratio: float = 0.0
    truth_score: float = 1.0
    regime_state: str = "ON"

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        return d


def _sha256(obj: Any) -> str:
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, ensure_ascii=False, default=str).encode()
    ).hexdigest()


def append_ledger_entry(
    ticket: Any,
    debt: Any,
    dist: DistributionCandidate,
    ledger_path: str | None = None,
) -> LedgerEntry:
    ledger_path = ledger_path or _DEFAULT_LEDGER_PATH
    os.makedirs(os.path.dirname(ledger_path), exist_ok=True)

    entry = LedgerEntry(
        ledger_id=uuid.uuid4().hex,
        os3_ticket_id=ticket.ticket_id,
        action_id=ticket.action_id,
        x108_gate=str(ticket.x108_gate).upper(),
        proof_valid=bool(ticket.input_hash and ticket.output_hash and ticket.trace_hash),
        gross_value=debt.gross_value,
        total_debt=debt.total_debt,
        net_value=debt.net_value,
        gencoin_candidate=dist.gencoin_candidate,
        mint_allowed=dist.mint_allowed,
        distribution=dist.to_dict(),
        input_hash=ticket.input_hash,
        output_hash=ticket.output_hash,
        trace_hash=ticket.trace_hash,
        timestamp=datetime.now(timezone.utc).isoformat(),
        assisted_ratio=debt.assisted_ratio,
        truth_score=debt.truth_score,
        regime_state=debt.regime_state,
    )

    with open(ledger_path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry.to_dict(), ensure_ascii=False) + "\n")

    return entry


def read_ledger(ledger_path: str | None = None) -> list[dict[str, Any]]:
    ledger_path = ledger_path or _DEFAULT_LEDGER_PATH
    if not os.path.exists(ledger_path):
        return []
    entries = []
    with open(ledger_path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries

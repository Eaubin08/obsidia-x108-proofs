"""
Multi-agent consensus priority:
BLOCK if any agent votes BLOCK.
HOLD if any agent votes HOLD.
ALLOW otherwise.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ConsensusResult:
    consensus: str
    block_voters: list[str]
    hold_voters: list[str]
    allow_voters: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "consensus": self.consensus,
            "block_voters": self.block_voters,
            "hold_voters": self.hold_voters,
            "allow_voters": self.allow_voters,
        }


def multi_agent_consensus(votes: list[dict[str, str]]) -> ConsensusResult:
    block_voters = [v["agent_id"] for v in votes if v.get("vote", "").upper() == "BLOCK"]
    hold_voters = [v["agent_id"] for v in votes if v.get("vote", "").upper() == "HOLD"]
    allow_voters = [v["agent_id"] for v in votes if v.get("vote", "").upper() == "ALLOW"]

    if block_voters:
        consensus = "BLOCK"
    elif hold_voters:
        consensus = "HOLD"
    else:
        consensus = "ALLOW"

    return ConsensusResult(
        consensus=consensus,
        block_voters=block_voters,
        hold_voters=hold_voters,
        allow_voters=allow_voters,
    )

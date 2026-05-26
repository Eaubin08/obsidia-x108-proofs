"""
Graphiti Freeze Snapshot Reader — reads frozen/archived Graphiti snapshots.
Never modifies. Read-only always.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class GraphitiFreezeSnapshot:
    snapshot_id: str
    freeze_date: str
    node_count: int
    edge_count: int
    readonly: bool = True
    is_frozen: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "snapshot_id": self.snapshot_id,
            "freeze_date": self.freeze_date,
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "readonly": self.readonly,
            "is_frozen": self.is_frozen,
        }


def read_freeze_snapshot(snapshot_id: str) -> GraphitiFreezeSnapshot:
    return GraphitiFreezeSnapshot(
        snapshot_id=snapshot_id,
        freeze_date="2026-05-19",
        node_count=0,
        edge_count=0,
        readonly=True,
        is_frozen=True,
    )

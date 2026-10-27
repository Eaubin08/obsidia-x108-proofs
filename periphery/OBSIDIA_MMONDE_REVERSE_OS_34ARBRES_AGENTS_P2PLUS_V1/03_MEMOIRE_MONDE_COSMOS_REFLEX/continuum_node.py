from dataclasses import dataclass, field
from typing import List

@dataclass
class NodeContinuum:
    id: str
    description: str
    event_ids: List[str] = field(default_factory=list)
    divergence: float = 0.0
    non_decision: bool = True

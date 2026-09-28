"""Semantic frame — immutable structural representation of a request.

The frame never stores task IDs or expected answers. It captures meaning
(intent, entities, relations, quantities, constraints) so that solvers and
validators reason over structure instead of exact phrasings.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class SemanticEntity:
    text: str
    canonical: str
    entity_type: str
    source_span: tuple[int, int] | None = None
    confidence: float = 1.0


@dataclass(frozen=True)
class SemanticRelation:
    subject: str
    predicate: str
    object: str
    polarity: str = "positive"      # positive | negative
    confidence: float = 1.0


@dataclass(frozen=True)
class SemanticQuantity:
    value: float
    unit: str | None
    role: str                        # initial | percent_decrease | fixed_decrease | ...
    source_text: str = ""


@dataclass(frozen=True)
class SemanticConstraint:
    kind: str                        # EQUAL | NOT_EQUAL | ASSIGN | EXCLUDE | ALL_DIFFERENT | ...
    operands: tuple[str, ...]
    polarity: str = "positive"
    required: bool = True


@dataclass(frozen=True)
class SemanticFrame:
    intent: str
    entities: tuple[SemanticEntity, ...] = ()
    relations: tuple[SemanticRelation, ...] = ()
    quantities: tuple[SemanticQuantity, ...] = ()
    constraints: tuple[SemanticConstraint, ...] = ()
    output_constraints: object = None
    unknowns: tuple[str, ...] = ()
    contradictions: tuple[str, ...] = ()


def semantic_signature(frame: SemanticFrame) -> str:
    """Stable structural signature.

    Depends only on intent family, sorted entity types, relation predicates
    with polarity, quantity roles and constraint kinds — never on surface
    names, numbers or sentence order. Renaming entities or changing values
    keeps the signature identical; changing the logical structure changes it.
    """
    ent = ".".join(sorted({e.entity_type for e in frame.entities})) or "-"
    rel = ".".join(sorted({f"{r.predicate}:{r.polarity}" for r in frame.relations})) or "-"
    qty = ".".join(sorted({q.role for q in frame.quantities})) or "-"
    con = ".".join(sorted({c.kind for c in frame.constraints})) or "-"
    return f"{frame.intent}|{ent}|{rel}|{qty}|{con}"

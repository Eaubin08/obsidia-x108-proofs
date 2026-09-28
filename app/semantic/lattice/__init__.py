"""Non-sovereign cognitive lattice (experimental, V0).

Raw utterance -> UtteranceFrame of PredicateUnits (one object, many
projections) linked by typed LatticeRelations. Deterministic, stdlib-only,
no network, no model. The existing UnifiedInputIR remains the governable
summary; this package only describes.

decision_authority: KX108_ONLY
real_action: false
memory_write: false
kernel_mutation: false
emits_act: false
"""
from app.semantic.lattice.primitives import (  # noqa: F401
    BOUNDARY,
    Argument,
    ConnectionKind,
    LatticeRelation,
    PredicateUnit,
    RelationKind,
    UtteranceFrame,
)
from app.semantic.lattice.french_grammar import parse_utterance  # noqa: F401
from app.semantic.lattice.projections import (  # noqa: F401
    Connection,
    ProjectionAxis,
    connection,
    project,
    projections_of,
)

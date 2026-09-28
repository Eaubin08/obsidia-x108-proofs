"""EventTargetReference rejects self-contradictory target records.

EVENT_TARGET needs a target event; UNKNOWN_TARGET carries no target and is
never resolved; UNRESOLVED / AMBIGUOUS references carry no target event.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_coreference import EventTargetReference, ResolutionStatus, TargetKind

R, S, AMB, UNR = (ResolutionStatus.RESOLVED_EXPLICIT, ResolutionStatus.RESOLVED_STRUCTURAL,
                  ResolutionStatus.AMBIGUOUS, ResolutionStatus.UNRESOLVED)


def _ref(kind, status, target_predicate=None, target_event=None):
    return EventTargetReference("e_src", "u_src", kind, status, target_predicate, target_event)


@pytest.mark.parametrize("kind, status, predicate, event", [
    (TargetKind.EVENT_TARGET, S, "u1", None),
    (TargetKind.EVENT_TARGET, R, None, None),
    (TargetKind.UNKNOWN_TARGET, S, None, None),
    (TargetKind.UNKNOWN_TARGET, UNR, "u1", None),
    (TargetKind.UNKNOWN_TARGET, AMB, None, "e1"),
    (TargetKind.PROPOSITION_TARGET, UNR, None, "e1"),
    (TargetKind.EVENT_TARGET, AMB, "u1", "e1"),
    # M2 local shape invariants
    (TargetKind.PROPOSITION_TARGET, S, None, None),
    (TargetKind.PROPOSITION_TARGET, R, None, None),
    (TargetKind.PROPOSITION_TARGET, S, "u1", "e1"),
    (TargetKind.PROPOSITION_TARGET, R, "u1", "e1"),
    (TargetKind.EVENT_TARGET, S, None, "e1"),
    (TargetKind.EVENT_TARGET, R, None, "e1"),
    (TargetKind.ENTITY_TARGET, S, None, "e1"),
    (TargetKind.ENTITY_TARGET, S, "u1", "e1"),
])
def test_contradictory_target_records_are_rejected(kind, status, predicate, event):
    with pytest.raises(ValueError):
        _ref(kind, status, predicate, event)


@pytest.mark.parametrize("kind, status, predicate, event", [
    (TargetKind.EVENT_TARGET, S, "u1", "e1"),
    (TargetKind.EVENT_TARGET, R, "u1", "e1"),
    (TargetKind.PROPOSITION_TARGET, S, "u1", None),
    (TargetKind.PROPOSITION_TARGET, R, "u1", None),
    (TargetKind.PROPOSITION_TARGET, UNR, None, None),
    (TargetKind.PROPOSITION_TARGET, AMB, None, None),
    (TargetKind.ENTITY_TARGET, S, None, None),
    (TargetKind.UNKNOWN_TARGET, UNR, None, None),
    (TargetKind.UNKNOWN_TARGET, AMB, None, None),
])
def test_coherent_target_records_are_accepted(kind, status, predicate, event):
    assert _ref(kind, status, predicate, event).target_kind is kind

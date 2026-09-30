"""D1 micro-decisions (frozen): H03_APPAREMMENT_POLICY = B, H04_LABEL_POLICY = KEEP_LEGACY.

H03: "Apparemment, P" carries source_class INFERENCE and NO epistemic flow or
state (no UNCERTAIN, REPORTED, OBSERVED, SUPPORTED, VERIFIED); occurrence
unchanged.

H04: the complement of "apprend / voit que" keeps its legacy descriptive
label (ASSERTED / ASSERTED). LEGACY_LABEL != WORLD_ASSERTION: that label is
compatibility metadata, not semantic authority. The canonical semantics are
the holder relation (LEARNS / PERCEIVES_THAT) over a PRESUPPOSED complement,
whose occurrence claim is NO_ASSERTION; no OBSERVED / VERIFIED / SUPPORTED.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.complement_commitment import (
    ComplementCommitment, ConstructionType, PerspectiveKind, profile_for,
)
from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.language_flow_projection import project_epistemic_flows
from app.semantic.lattice.primitives import SourceClass, source_class


def test_apparemment_is_inference_without_epistemic_flow():
    f = parse_utterance("Apparemment, Paul a lancé P.")
    (u,) = f.units
    assert source_class(u) is SourceClass.INFERENCE
    assert project_epistemic_flows(f) == ()
    claims = {c.predicate_ref: c.occurrence_claim.value for c in build_frame_event_index(f).events()}
    assert claims[u.id] == "NO_ASSERTION"


@pytest.mark.parametrize("text,family,kind", [
    ("Marie apprend que Paul lance P.", "LEARN", PerspectiveKind.LEARNS),
    ("Marie voit que Paul lance P.", "PERCEPTION", PerspectiveKind.PERCEIVES_THAT),
])
def test_legacy_label_is_kept_but_is_not_a_world_assertion(text, family, kind):
    f = parse_utterance(text)
    _, p = f.units
    assert (p.pragmatic, p.epistemic) == ("ASSERTED", "ASSERTED")          # legacy label kept
    profile = profile_for(family, ConstructionType.QUE_PROPOSITION)
    assert profile.perspective_kind is kind and profile.base_commitment is ComplementCommitment.PRESUPPOSED
    event = next(c for c in build_frame_event_index(f).events() if c.predicate_ref == p.id)
    # LEGACY_LABEL != WORLD_ASSERTION: the claim comes from the presupposed commitment
    assert event.occurrence_claim.value == "NO_ASSERTION"
    assert event.occurrence_derivation.rule == "commitment:PRESUPPOSED"
    assert event.occurrence_derivation.provenance["commitment_rule"] == f"{family}/QUE_PROPOSITION:base"
    assert not {x.state for x in project_epistemic_flows(f)} & {"OBSERVED", "VERIFIED", "SUPPORTED"}

"""D1 (H03 + H04 + H05, approved core).

H03: a detached source carries a typed source_class (HUMAN, EVIDENCE_TRACE,
INFERENCE, SPEAKER), never a new epistemic state: "Selon Marie" and "Selon
les logs" are REPORTED (a trace is never SUPPORTED / VERIFIED); "Apparemment"
keeps no epistemic flow (its policy is held, H03_APPAREMMENT_POLICY).

H04: knowing / learning / seeing that P are relations (KNOWS, LEARNS,
PERCEIVES_THAT) with a PRESUPPOSED complement, never an epistemic state and
never OBSERVED; the descriptive label of the "apprend / voit que" complement is
held (H04_LABEL_POLICY). Closure policy is held (no open -> closed).

H05: "quand / lorsque P" -> TEMPORAL_ANCHOR(P, Q) (no order, condition or
cause); "pendant que P" is a temporal subordinator -> OVERLAPS(P, Q).
temporal_subordinate_open is kept (closure policy held).
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.language_flow_projection import project_epistemic_flows
from app.semantic.lattice.primitives import SourceClass, source_class
from app.semantic.lattice.projections import ProjectionAxis, project


def _claims(f):
    return {c.predicate_ref: c.occurrence_claim.value for c in build_frame_event_index(f).events()}


def _states(f):
    return {getattr(x, "state", None) for x in project_epistemic_flows(f)}


@pytest.mark.parametrize("text,cls,flow", [
    ("Selon Marie, Paul a lancé P.", SourceClass.HUMAN, {"REPORTED"}),
    ("Selon les logs, Paul a lancé P.", SourceClass.EVIDENCE_TRACE, {"REPORTED"}),
    ("Apparemment, Paul a lancé P.", SourceClass.INFERENCE, set()),
])
def test_h03_source_class_without_new_state(text, cls, flow):
    f = parse_utterance(text)
    (u,) = f.units
    assert source_class(u) is cls
    assert project(f, ProjectionAxis.EPISTEMIC)[u.id]["source_class"] == cls.value
    assert _states(f) == flow
    assert not _states(f) & {"VERIFIED", "SUPPORTED", "OBSERVED"}
    assert _claims(f)[u.id] == "NO_ASSERTION"


def test_h03_unattributed_frames_get_no_stamped_source():
    assert source_class(parse_utterance("Paul a lancé P.").units[0]) is None


@pytest.mark.parametrize("text", ["Marie sait que Paul a lancé P.", "Marie apprend que Paul a lancé P.",
                                  "Marie voit que Paul a lancé P."])
def test_h04_relations_not_states(text):
    f = parse_utterance(text)
    gov, p = f.units
    # the complement's descriptive label is held (H04_LABEL_POLICY): relabelling it would demote
    # the legacy occurrence status pinned by the migration contract
    assert _claims(f)[p.id] == "NO_ASSERTION"
    assert not _states(f) & {"OBSERVED", "VERIFIED", "SUPPORTED"}
    idx = build_frame_event_index(f)
    derivation = next(c for c in idx.events() if c.predicate_ref == p.id).occurrence_derivation
    assert derivation.rule == "commitment:PRESUPPOSED"


def test_h04_closure_policy_follows_the_profile():
    # H04 closure policy (option C): closed IFF the profile resolves (see test_d1_closure_policies)
    assert parse_utterance("Marie sait que Paul a lancé P.").closure
    assert parse_utterance("Marie apprend que Paul a lancé P.").closure


@pytest.mark.parametrize("text", ["Nadia lance Q quand Paul lance P.", "Quand Paul lance P, Nadia lance Q.",
                                  "Nadia lance Q lorsque Paul lance P.", "Lorsque Paul lance P, Nadia lance Q."])
def test_h05_quand_lorsque_temporal_anchor(text):
    f = parse_utterance(text)
    p = next(u for u in f.units if u.subject == "paul")
    q = next(u for u in f.units if u.subject == "nadia")
    rels = {(r.kind, r.source, r.target) for r in f.relations}
    assert ("TEMPORAL_ANCHOR", p.id, q.id) in rels
    assert not any(r.kind in {"PRECEDES", "CONDITIONS", "CAUSES", "OVERLAPS"} for r in f.relations)
    # H05 closure policy (option A): unique host + typed relation -> structurally closed
    assert f"temporal_subordinate_open:{p.id}" not in f.ambiguities and f.closure


@pytest.mark.parametrize("text", ["Nadia lance Q pendant que Paul lance P.", "Pendant que Paul lance P, Nadia lance Q."])
def test_h05_pendant_que_overlaps(text):
    f = parse_utterance(text)
    p = next(u for u in f.units if u.subject == "paul")
    q = next(u for u in f.units if u.subject == "nadia")
    assert ("OVERLAPS", p.id, q.id) in {(r.kind, r.source, r.target) for r in f.relations}
    assert not any(r.kind in {"PRECEDES", "CONDITIONS", "CAUSES", "EMBEDS"} for r in f.relations)
    assert not any(a.startswith("complement_governor_lost") for a in f.ambiguities)
    assert _claims(f)[p.id] not in {"ASSERTED_REALIZED", "ASSERTED_NOT_REALIZED"} and f.closure  # policy A


def test_h05_apres_que_control_is_unchanged():
    f = parse_utterance("Nadia lance Q après que Paul a lancé P.")
    assert ("PRECEDES", "u2", "u1") in {(r.kind, r.source, r.target) for r in f.relations}

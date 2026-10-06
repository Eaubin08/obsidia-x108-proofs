"""N12-T: "immédiatement" is a temporal cue on the existing temporal carrier.

It was reported by the provisional N7 manner marker (unrepresented_modifier_of) and kept
the frame open. It now rides UtteranceFrame.deixis / TemporalCueAttachment like
"maintenant" (same carrier, not the same meaning): an UNRESOLVED_TEMPORAL_CUE, no
missing marker, closure by the other blockers only. Tense is untouched (FUTURE stays
FUTURE), and the cue adds no request, prohibition, authority or occurrence claim.
"directement" stays the provisional N7 OPEN case.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_extraction import extract_event_candidates
from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary
from app.semantic.lattice.temporal_attachment import AttachmentStatus, attach_temporal_cues


def _view(text):
    f = parse_utterance(text)
    s = governable_summary(f)
    return f, s, [(u.predicate, u.subject, u.pragmatic, u.polarity, u.tense_aspect, tuple(a.text for a in u.objects))
                  for u in f.units], [e.occurrence_claim for e in build_frame_event_index(f).events()]


@pytest.mark.parametrize("text,ref,cue", [
    ("Paul lance P immédiatement.", "Paul lance P.", "immédiatement"),
    ("Paul lance P immediatement.", "Paul lance P.", "immediatement"),
    ("Lance P immédiatement.", "Lance P.", "immédiatement"),
    ("Lance immédiatement P.", "Lance P.", "immédiatement"),
    ("Paul lancera P immédiatement.", "Paul lancera P.", "immédiatement"),
])
def test_n12t_immediatement_is_a_temporal_cue_with_reference_semantics(text, ref, cue):
    f, s, rows, claims = _view(text)
    rf, rs, rrows, rclaims = _view(ref)
    assert rows == rrows and claims == rclaims  # same force, tense, objects, occurrence
    assert s["requested_world_actions"] == rs["requested_world_actions"] and f.constraints == rf.constraints
    assert s["confirmed_no_execute"] == rs["confirmed_no_execute"]
    assert f.deixis == (cue,) and not any("unrepresented_modifier_of" in m for m in f.missing)
    (att,) = attach_temporal_cues(f, extract_event_candidates(f))
    assert att.cue == cue and att.attachment_status == AttachmentStatus.UNRESOLVED_TEMPORAL_CUE
    assert f.closure == rf.closure


def test_n12t_maintenant_same_carrier_distinct_cue():
    a, b = parse_utterance("Paul lance P maintenant."), parse_utterance("Paul lance P immédiatement.")
    assert a.deixis == ("maintenant",) and b.deixis == ("immédiatement",) and a.closure and b.closure


@pytest.mark.parametrize("text,mod", [("Paul lance P directement.", "directement"), ("Paul lance P indirectement.", "indirectement"),
                                      ("Paul lance P automatiquement.", "automatiquement")])
def test_n12t_other_n7_modifiers_stay_provisional_open(text, mod):
    f = parse_utterance(text)
    assert [a.text for a in f.units[0].objects] == ["p"] and f.deixis == () and not f.closure
    assert any(m.endswith(":unrepresented_modifier_of=u1") for m in f.missing)

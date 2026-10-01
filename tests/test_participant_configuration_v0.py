"""ParticipantConfigurationRef V0: the canonical carrier of participant configuration.

DISTRIBUTIVE ("chacun"), COLLECTIVE ("ensemble") and SOLO ("tout seul") describe how
the participants of ONE predication realize it: one unit, one EventCandidate, no group
entity, no restriction, no authority. Coordinated or not ("Ils lancent chacun P" has no
CoordinationRef; group names the coordinated subject when there is one).
CoordinationRef.distributivity is only a legacy mirror of the DISTRIBUTIVE ref. A bare
"seul" ("P seul" may mean "only P"), a plural "seuls", a singular "ensemble" and a
subjectless imperative are not forced: the provisional marker keeps the frame open.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary


def _gov(f):
    s = governable_summary(f)
    return s["requested_world_actions"], s["confirmed_no_execute"], f.constraints, \
        [(u.pragmatic, u.polarity, u.action_agent, u.role) for u in f.units], \
        [e.occurrence_claim for e in build_frame_event_index(f).events()]


def _temp(f):
    return [m for m in f.missing if "subject_distributivity_of=" in m or "unrepresented_modifier_of=" in m]


@pytest.mark.parametrize("text,ref,kind,cue,coordinated", [
    ("Ils lancent chacun P.", "Ils lancent P.", "DISTRIBUTIVE", "chacun", False),
    ("Elles lancent chacune P.", "Elles lancent P.", "DISTRIBUTIVE", "chacune", False),
    ("Les agents lancent chacun P.", "Les agents lancent P.", "DISTRIBUTIVE", "chacun", False),
    ("Paul et Nadia lancent chacun P.", "Paul et Nadia lancent P.", "DISTRIBUTIVE", "chacun", True),
    ("Ils lancent P ensemble.", "Ils lancent P.", "COLLECTIVE", "ensemble", False),
    ("Paul et Nadia lancent P ensemble.", "Paul et Nadia lancent P.", "COLLECTIVE", "ensemble", True),
    ("Paul lance P tout seul.", "Paul lance P.", "SOLO", "tout seul", False),
])
def test_v0_positive_configuration(text, ref, kind, cue, coordinated):
    f, r = parse_utterance(text), parse_utterance(ref)
    (u,) = f.units
    (pc,) = f.participant_configurations
    group = next((c.id for c in f.coordinations if c.construction == "coordinated_subject"), None)
    assert (pc.unit, pc.role, pc.kind, pc.cue, pc.group) == (u.id, "subject", kind, cue, group)
    assert (group is not None) == coordinated and f.raw[pc.span[0]:pc.span[1]].lower() == cue
    assert [a.text for a in u.objects] == ["p"] and u.subject == r.units[0].subject and u.restriction is None
    assert not _temp(f) and f.closure == r.closure
    assert _gov(f) == _gov(r)  # descriptive only: same force, requests, constraints, occurrence, one event


def test_v0_legacy_distributivity_mirror_agrees():
    for text in ("Paul et Nadia lancent chacun P.", "Paul et Nadia ont chacun lancé P.",
                 "Paul et Nadia lanceront chacun P.", "Paul et Nadia lancent P."):
        f = parse_utterance(text)
        (c,) = [c for c in f.coordinations if c.construction == "coordinated_subject"]
        canonical = any(p.kind == "DISTRIBUTIVE" and p.group == c.id for p in f.participant_configurations)
        assert (c.distributivity == "EXPLICIT") == canonical


@pytest.mark.parametrize("text", ["Paul lance P seul.", "Paul et Nadia lancent P seuls.",
                                  "Paul lance P ensemble.", "Lance P tout seul."])
def test_v0_ambiguous_cues_not_forced(text):
    f = parse_utterance(text)
    assert not f.participant_configurations and len(_temp(f)) == 1 and not f.closure
    assert all(u.restriction is None for u in f.units)


@pytest.mark.parametrize("text", ["Paul lance chacun des tests.", "Paul lance tout.", "Paul lance P vite.",
                                  "Paul lance P automatiquement.", "Paul lance P directement.",
                                  "Paul lance P immédiatement.", "Paul et Nadia lancent P.", "Ils lancent P."])
def test_v0_controls_without_configuration(text):
    assert parse_utterance(text).participant_configurations == ()

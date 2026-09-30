"""D1 closure policies (H04 option C, H05 option A) + prerequisites D1-F3, D1-F1.

H04: complement governance is structurally complete IFF the complement
profile resolves (resolve_commitment(profile, operators) != UNRESOLVED);
otherwise unresolved_complement_governance keeps the frame open. Closure
is structural only (not truth, occurrence, verification or authority).
D1-F3: an inverted subject ("sait-elle que") no longer hides the governor.

H05: a temporal subordinate closes only with a typed relation toward exactly
one structural host; a coordinated host group on either side stays
temporal_scope_ambiguous (D1-F1) and open. Meanings and occurrences are
unchanged.

D1-F2 ("Marie sait qui a lancé P.") is deferred to H13 (not covered here).
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.language_flow_projection import project_epistemic_flows


def _claims(f):
    return {c.predicate_ref: (c.occurrence_claim.value, c.occurrence_derivation.rule)
            for c in build_frame_event_index(f).events()}


@pytest.mark.parametrize("text", ["Marie sait que Paul a lancé P.", "Marie ne sait pas que Paul a lancé P.",
                                  "Marie sait-elle que Paul a lancé P ?"])
def test_know_resolved_cells_close(text):
    f = parse_utterance(text)
    p = f.units[-1]
    assert not any(a.startswith(("unresolved_complement_governance", "complement_governor_lost"))
                   for a in f.ambiguities)
    assert ("EMBEDS", "u1", p.id) in {(r.kind, r.source, r.target) for r in f.relations}
    assert _claims(f)[p.id][0] == "NO_ASSERTION" or _claims(f)[p.id][0] == "UNRESOLVED"
    assert _claims(f)[p.id][0] != "ASSERTED_REALIZED"
    assert f.closure


@pytest.mark.parametrize("text", ["Marie saura que Paul a lancé P.", "Marie doit savoir que Paul a lancé P."])
def test_know_unresolved_cells_stay_open(text):
    f = parse_utterance(text)
    assert f"unresolved_complement_governance:{f.units[-1].id}" in f.ambiguities and not f.closure


@pytest.mark.parametrize("text", ["Marie apprend que Paul a lancé P.", "Marie voit que Paul a lancé P."])
def test_learn_perception_base_stays_closed(text):
    f = parse_utterance(text)
    assert f.closure and f.units[-1].pragmatic == "ASSERTED"          # legacy label kept (H04_LABEL_POLICY)


@pytest.mark.parametrize("text", ["Marie n'apprend pas que Paul a lancé P.", "Marie apprendra que Paul a lancé P.",
                                  "Marie n'a pas vu que Paul a lancé P.", "Marie a-t-elle vu que Paul a lancé P ?"])
def test_learn_perception_under_unresolved_operators_open(text):
    f = parse_utterance(text)
    p = f.units[-1]
    before = _claims(f)[p.id]
    assert f"unresolved_complement_governance:{p.id}" in f.ambiguities and not f.closure
    assert before[0] == "UNRESOLVED"                                     # occurrence unchanged
    assert not {x.state for x in project_epistemic_flows(f)} & {"OBSERVED", "VERIFIED", "SUPPORTED"}


@pytest.mark.parametrize("text,kind", [
    ("Nadia lance Q quand Paul lance P.", "TEMPORAL_ANCHOR"), ("Quand Paul lance P, Nadia lance Q.", "TEMPORAL_ANCHOR"),
    ("Nadia lance Q lorsque Paul lance P.", "TEMPORAL_ANCHOR"), ("Lorsque Paul lance P, Nadia lance Q.", "TEMPORAL_ANCHOR"),
    ("Nadia lance Q pendant que Paul lance P.", "OVERLAPS"), ("Pendant que Paul lance P, Nadia lance Q.", "OVERLAPS"),
])
def test_unique_host_temporal_subordinate_closes(text, kind):
    f = parse_utterance(text)
    p = next(u for u in f.units if u.subject == "paul")
    q = next(u for u in f.units if u.subject == "nadia")
    assert (kind, p.id, q.id) in {(r.kind, r.source, r.target) for r in f.relations}
    assert not any(r.kind in {"PRECEDES", "CONDITIONS", "CAUSES"} for r in f.relations)
    assert not any(a.startswith("temporal_subordinate_open") for a in f.ambiguities)
    assert _claims(f)[p.id][0] in {"UNRESOLVED", "NO_ASSERTION"}        # occurrence unchanged
    assert f.closure


@pytest.mark.parametrize("text", ["Pendant que Paul lance P, Nadia lance Q et exécute R.",
                                  "Quand Paul lance P, Nadia lance Q et exécute R.",
                                  "Nadia lance Q et exécute R pendant que Paul lance P."])
def test_coordinated_temporal_host_stays_ambiguous_and_open(text):
    f = parse_utterance(text)
    p = next(u for u in f.units if u.subject == "paul")
    assert any(a.startswith(f"temporal_scope_ambiguous:{p.id}:") for a in f.ambiguities)
    assert not any(r.kind in {"OVERLAPS", "TEMPORAL_ANCHOR"} for r in f.relations)
    assert not f.closure


def test_apres_que_control_is_unchanged():
    f = parse_utterance("Nadia lance Q après que Paul a lancé P.")
    assert ("PRECEDES", "u2", "u1") in {(r.kind, r.source, r.target) for r in f.relations}

"""NF9: a copula + attribute clause is reported, never silently dropped.

"Lance P si c'est prêt.": "être" followed by a non-participial attribute
built no draft (the BE branch only knows auxiliaries, presence and "en train
de") and, the clause containing a verb, it was never reported: the
protasis vanished (no CONDITIONS, no missing) and the frame was declared
closed; likewise under "après que", "que", "avant que" and in a sequence.
In those structural contexts the clause is now kept as unanalysed
predicative content (M8-0b missing) with its structural link
(conditional_protasis, ...), which blocks closure. No unit, event,
assertion, temporal or causal relation is created for it; the copular
proposition itself is not modelled. A standalone "C'est bon." and a
verbless "Ça, c'est bon." are unchanged.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.projections import ProjectionAxis, project
from app.semantic.lattice.semantic_closure import semantic_closure

MISSING = "unanalyzed_predicative_content:"


def _missing(f):
    return [(f.raw[int(m.split(":")[1].split("-")[0]):int(m.split(":")[1].split("-")[1])], m.split(":")[2])
            for m in f.missing if m.startswith(MISSING)]


@pytest.mark.parametrize("text,content,link", [
    ("Lance P si c'est prêt.", "c'est prêt", "conditional_protasis"),
    ("Lance P si le test est vert.", "le test est vert", "conditional_protasis"),
    ("Si c'est prêt, lance P.", "c'est prêt", "conditional_protasis"),
    ("Lance P si ce n'est pas prêt.", "ce n'est pas prêt", "conditional_protasis"),
    ("Lance P après que c'est prêt.", "c'est prêt", None),
    ("Lance P avant que le build est prêt.", "le build est prêt", None),
    ("Lance P, c'est prêt.", "c'est prêt", "root"),
    ("Paul lance P et c'est prêt.", "c'est prêt", None),
    ("C'est bon et Paul lance P.", "C'est bon", None),
    ("Marie dit que c'est prêt.", "c'est prêt", None),
])
def test_copula_attribute_clause_is_named_missing(text, content, link):
    f = parse_utterance(text)
    found = _missing(f)
    assert any(c == content and (link is None or ln == link) for c, ln in found), found
    assert f.closure is False and not semantic_closure(f).closed


@pytest.mark.parametrize("text,ref", [
    ("Lance P si c'est prêt.", "Lance P."),
    ("Lance P après que c'est prêt.", "Lance P."),
    ("Lance P, c'est prêt.", "Lance P."),
])
def test_nothing_is_invented_for_the_copular_clause(text, ref):
    f, r = parse_utterance(text), parse_utterance(ref)
    assert [(u.lemma, u.pragmatic, u.subject, [a.text for a in u.objects]) for u in f.units] == \
        [(u.lemma, u.pragmatic, u.subject, [a.text for a in u.objects]) for u in r.units]
    assert f.relations == () or not any(x.kind in {"CONDITIONS", "PRECEDES", "CAUSES"} for x in f.relations)
    assert len(build_frame_event_index(f).events()) == len(build_frame_event_index(r).events())
    gate = {k: v["requires_gate"] for k, v in project(f, ProjectionAxis.AUTHORITY).items()}
    ref_gate = {k: v["requires_gate"] for k, v in project(r, ProjectionAxis.AUTHORITY).items()}
    assert gate == ref_gate


@pytest.mark.parametrize("text", [
    "C'est bon.", "Ça, c'est bon.", "Est-ce que tu peux lancer P ?", "Paul est là et lance P.",
    "Le test est lancé et Paul lance P.", "Paul est en train de lancer P.", "Lance P, n'est-ce pas ?",
])
def test_standalone_or_analysed_copula_unchanged(text):
    f = parse_utterance(text)
    assert not any(c.startswith(("c'est", "C'est", "est")) for c, _ in _missing(f))

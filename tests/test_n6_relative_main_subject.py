"""N6: after a relative, the main predicate's subject is the antecedent, never the
relative's object; "aussi" is never an object.

"Le script qui sert à tester Q sert aussi à arrêter S" gave the main "servir" the subject
"q" and the object "aussi" (same in "Le script qui lance P lance Q": subject "p"). When the
antecedent clause is a bare NP and a second verb follows the relative's own verb in the
relative clause, that verb's subject is the antecedent NP (structural; no nearest NP).
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.french_grammar import parse_utterance


@pytest.mark.parametrize("text,main,subject,objs", [
    ("Le script qui sert à tester Q sert aussi à arrêter S.", "u3", "script", []),
    ("Le script qui sert à tester Q sert à arrêter S.", "u3", "script", []),
    ("Le script qui lance P lance aussi Q.", "u2", "script", ["q"]),
    ("Le script qui lance P lance Q.", "u2", "script", ["q"]),
    ("Paul qui lance P lance Q.", "u2", "paul", ["q"]),
])
def test_main_subject_is_antecedent(text, main, subject, objs):
    f = parse_utterance(text)
    u = f.unit(main)
    assert u.subject == subject and [a.text for a in u.objects] == objs
    assert all("aussi" not in a.text for x in f.units for a in x.objects)


def test_serve_for_purposes_kept():
    f = parse_utterance("Le script qui sert à tester Q sert aussi à arrêter S.")
    assert [(r.kind, r.source, r.target, r.evidence) for r in f.relations] == [
        ("EMBEDS", "u1", "u2", "servir_a"), ("EMBEDS", "u3", "u4", "servir_a")]
    assert [u.role for u in (f.unit("u2"), f.unit("u4"))] == ["PURPOSE", "PURPOSE"]


def test_unsupported_sense_still_reported():
    f = parse_utterance("Le système qui sert à analyser P sert à produire Q.")
    assert f.unit("u2").subject == "système" and not f.closure


def test_plain_aussi_unchanged():
    f = parse_utterance("Paul lance aussi Q.")
    assert [(u.subject, [a.text for a in u.objects]) for u in f.units] == [("paul", ["q"])]

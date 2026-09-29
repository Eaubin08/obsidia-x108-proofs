"""No nearest match for a pronoun whose nearest antecedent is one of several coordinated objects.

"Prépare le test et le build puis ne le lance pas": "le" could be the test or
the build. The parser used to bind it to the nearest ("build", RESOLVED_INTRA),
deriving NO_EXECUTE(build) in a frame declared closed. The reference now stays
UNRESOLVED with an "ambiguous_antecedent" marker naming the candidates; the
prohibition falls back to the wildcard (NO_EXECUTE(*): stricter, fail closed)
and the frame is not closed. A single antecedent, and one object shared by
coordinated predicates, are unchanged.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.french_grammar import parse_utterance


@pytest.mark.parametrize("text,pron", [
    ("Prépare le test et le build puis ne le lance pas.", "le"),
    ("Lance le test et le build puis arrête-le.", "le"),
    ("Lance le test et le build puis arrête-les.", "les"),
    ("Paul a lancé le test et le build puis il l'a arrêté.", "l'"),
    ("Lance-le puis prépare le test et le build.", "le"),
])
def test_pronoun_over_coordinated_objects_stays_open(text, pron):
    f = parse_utterance(text)
    arg = next(a for u in f.units for a in u.objects if a.text == pron)
    assert (arg.reference, arg.antecedent) == ("UNRESOLVED", None)
    assert any(a.startswith("ambiguous_antecedent:") and a.endswith("test,build") for a in f.ambiguities)
    assert not any(r.kind == "REFERS_TO" for r in f.relations)
    assert f.closure is False


def test_negated_execute_falls_back_to_wildcard():
    f = parse_utterance("Prépare le test et le build puis ne le lance pas.")
    assert f.constraints == ("NO_EXECUTE(*)",)


@pytest.mark.parametrize("text,antecedent", [
    ("Prépare le test puis ne le lance pas.", "test"),
    ("Paul doit lancer et exécuter le test puis il l'arrête.", "test"),
    ("Lance le test sur le serveur puis arrête-le.", "test"),
])
def test_single_or_shared_antecedent_unchanged(text, antecedent):
    f = parse_utterance(text)
    arg = next(a for u in f.units for a in u.objects if a.kind == "PRONOUN")
    assert (arg.reference, arg.antecedent) == ("RESOLVED_INTRA", antecedent)
    assert not any(a.startswith("ambiguous_antecedent:") for a in f.ambiguities)

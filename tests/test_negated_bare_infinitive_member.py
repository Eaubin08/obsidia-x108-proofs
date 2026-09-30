"""NF5: "et ne pas V" is shared only when its host licenses it; never a false prohibition.

"Paul veut lancer P et ne pas exécuter Q" / "Paul lance P et ne pas
exécuter Q": "ne pas" before the infinitive broke sharing, so "ne pas
exécuter Q" fell back to an independent injunctive prohibition (FORBIDDEN,
constraint NO_EXECUTE(q) for the runtime). Now:
- under a host operator (desire, obligation, ability, directive,
  periphrasis) the member shares it with its own local negation, exactly as
  the simple "Paul veut ne pas exécuter Q" (a real directive stays a
  prohibition: "Tu dois ... et ne pas V", "Veuillez ... et ne pas V");
- under a negated desire or a savoir chain it stays open (A1b / NF3a);
- under a plain assertive host with no operator it stays EMBEDDED, named
  infinitive_under_unrecognized_governor, with no prohibition and no
  NO_EXECUTE constraint.
"Lance P et ne pas exécuter Q" and "Ne pas exécuter Q" keep their
prohibition. Negated pouvoir / aller hosts (NEG-OPERATOR-ET) are unchanged.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.french_grammar import parse_utterance

_A = chr(39)


def _last(text):
    f = parse_utterance(text)
    return f, f.units[-1]


def _sig(u):
    return (u.polarity, u.modality, u.subject, u.tense_aspect, u.pragmatic, u.role, u.request_target)


@pytest.mark.parametrize("text,simple", [
    ("Paul veut lancer P et ne pas exécuter Q.", "Paul veut ne pas exécuter Q."),
    ("Je veux lancer P et ne pas exécuter Q.", "Je veux ne pas exécuter Q."),
    ("Paul doit lancer P et ne pas exécuter Q.", "Paul doit ne pas exécuter Q."),
    ("Tu dois lancer P et ne pas exécuter Q.", "Tu dois ne pas exécuter Q."),
    ("Paul veut lancer P mais ne pas exécuter Q.", "Paul veut ne pas exécuter Q."),
    ("Veuillez lancer P et ne pas exécuter Q.", "Veuillez ne pas exécuter Q."),
    ("Paul va lancer P et ne pas exécuter Q.", "Paul va ne pas exécuter Q."),
])
def test_licensed_host_shares_with_local_negation(text, simple):
    f, u = _last(text)
    _, ref = _last(simple)
    assert _sig(u) == _sig(ref)
    assert u.polarity == "negative"
    if ref.pragmatic != "FORBIDDEN":
        assert not any(c.startswith("NO_") for c in f.constraints)


@pytest.mark.parametrize("text", [
    "Paul lance P et ne pas exécuter Q.",
    "Paul a lancé P et ne pas exécuter Q.",
    "Nadia exécute Q, ne pas lancer P.",
])
def test_plain_assertive_host_never_creates_a_prohibition(text):
    f, u = _last(text)
    assert u.pragmatic == "EMBEDDED" and u.request_target == "NONE"
    assert f"infinitive_under_unrecognized_governor:{u.id}" in f.ambiguities
    assert not any(c.startswith("NO_") for c in f.constraints)
    assert f.closure is False


def test_negated_desire_host_keeps_the_member_open():
    f, u = _last("Paul ne veut pas lancer P et ne pas exécuter Q.")
    assert u.pragmatic == "EMBEDDED" and f"negated_scope_open:{u.id}" in f.ambiguities
    assert not any(c.startswith("NO_") for c in f.constraints)


@pytest.mark.parametrize("text", ["Lance P et ne pas exécuter Q.", "Ne pas exécuter Q.", "Lance P et n" + _A + "exécute pas Q."])
def test_true_directives_keep_their_prohibition(text):
    f, u = _last(text)
    assert u.pragmatic == "FORBIDDEN"
    assert "NO_EXECUTE(q)" in f.constraints


@pytest.mark.parametrize("text", ["Paul ne peut pas lancer P et ne pas exécuter Q.", "Paul ne va pas lancer P et ne pas exécuter Q."])
def test_neg_operator_et_is_untouched(text):
    f, u = _last(text)
    assert not any(a.endswith(u.id) and a.startswith(("infinitive_under_unrecognized_governor", "negated_scope_open"))
                   for a in f.ambiguities)

"""O2 (approved): PredicateUnit.subject_ref binds a "qui" relative to its structural antecedent.

The antecedent is the nominal Argument the grammar built at the end of the carrier, adjacent
to "qui" (or a verbless carrier that is exactly one NP). It reuses the Argument vocabulary
(reference RESOLVED_INTRA, antecedent head, antecedent_unit). Never the nearest / first /
last noun: an intervening complement leaves subject_ref None, coordinated nominals are
named ("ambiguous_antecedent"), never chosen. No semantic role is inferred beyond the
reference; the textual subject keeps its convention; object pronouns and "te" are untouched.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance


def _unit(f, predicate):
    return next(u for u in f.units if u.predicate == predicate)


def _claims(f):
    return {c.predicate_ref: c.occurrence_claim.value for c in build_frame_event_index(f).events()}


def test_fragment_relative_binds_exact_antecedent():
    f = parse_utterance("La mémoire qui sert à parler")
    ref = _unit(f, "SERVE_FOR").subject_ref
    assert (ref.text, ref.head, ref.kind, ref.reference, ref.antecedent) == (
        "la mémoire", "mémoire", "NP", "RESOLVED_INTRA", "mémoire")
    assert f.raw[ref.span[0]:ref.span[1]] == "La mémoire"
    assert _unit(f, "SPEAK").subject_ref is None


def test_detail_relative_binds_the_detail_object():
    f = parse_utterance("Détaille la mémoire qui sert à parler.")
    detail, serve, speak = _unit(f, "DETAIL"), _unit(f, "SERVE_FOR"), _unit(f, "SPEAK")
    (obj,) = detail.objects
    ref = serve.subject_ref
    assert (ref.text, ref.head, ref.span) == (obj.text, obj.head, obj.span)
    assert (ref.reference, ref.antecedent, ref.antecedent_unit) == ("RESOLVED_INTRA", "mémoire", detail.id)
    assert obj.reference == "PRESUPPOSED"  # the carrier's own object is not rewritten
    assert (speak.pragmatic, speak.role, speak.embedded_under) == ("EMBEDDED", "PURPOSE", serve.id)
    claims = _claims(f)
    assert serve.id not in claims
    assert claims.get(speak.id) not in {"ASSERTED_REALIZED", "ASSERTED_NOT_REALIZED", "PROJECTED_FUTURE", "POSSIBLE"}
    assert f.closure


def test_intervening_complement_is_never_bound_by_nearest_noun():
    # "le document de la mémoire qui": "mémoire" is nearest, "document" is the object;
    # neither is proven by structure -> no reference, frame open
    f = parse_utterance("Détaille le document de la mémoire qui sert à parler.")
    assert _unit(f, "SERVE_FOR").subject_ref is None
    assert not f.closure


@pytest.mark.parametrize("text", ["Compare le script et le document qui sert à parler.",
                                  "Détaille le script ou le document qui sert à parler."])
def test_coordinated_nominals_are_named_never_chosen(text):
    f = parse_utterance(text)
    serve = _unit(f, "SERVE_FOR")
    assert serve.subject_ref is None
    assert f"ambiguous_antecedent:{serve.id}:qui:script,document" in f.ambiguities
    assert not f.closure


def test_no_nominal_carrier_leaves_subject_ref_none():
    f = parse_utterance("Lance le test et le build qui échouent.")
    assert all(u.subject_ref is None for u in f.units) and not f.closure


@pytest.mark.parametrize("text,antecedent", [
    ("Prépare le test puis ne le lance pas.", "test"),
    ("Lance le test sur le serveur puis arrête-le.", "test"),
    ("Prépare la base puis lance le build puis arrête-la.", "base"),
])
def test_object_pronoun_resolution_unchanged(text, antecedent):
    f = parse_utterance(text)
    arg = next(a for u in f.units for a in u.objects if a.kind == "PRONOUN")
    assert (arg.reference, arg.antecedent) == ("RESOLVED_INTRA", antecedent)
    assert all(u.subject_ref is None for u in f.units)


def test_te_stays_unresolved_while_antecedent_binds():
    f = parse_utterance("Détaille la mémoire qui te sert à parler.")
    serve = _unit(f, "SERVE_FOR")
    assert (serve.subject_ref.text, serve.subject_ref.reference) == ("la mémoire", "RESOLVED_INTRA")
    (m,) = [m for m in f.missing if m.endswith(f":unresolved_clitic_of={serve.id}")]
    a, b = map(int, m.split(":")[1].split("-"))
    assert f.raw[a:b] == "te" and not f.closure


def test_speak_relative_precedent_unchanged():
    f = parse_utterance("Lance le script qui parle de KX108.")
    run, speak = _unit(f, "EXECUTE"), _unit(f, "SPEAK")
    assert (speak.pragmatic, speak.embedded_under, speak.objects) == ("ASSERTED", run.id, ())
    assert any(m.endswith(f":speak_complement_of={speak.id}") for m in f.missing) and not f.closure
    assert (speak.subject_ref.text, speak.subject_ref.antecedent_unit) == ("le script", run.id)


@pytest.mark.parametrize("text", ["La mémoire sert à parler.", "Détaille la mémoire qui sert à parler."])
def test_serve_for_semantics_unchanged(text):
    f = parse_utterance(text)
    serve, speak = _unit(f, "SERVE_FOR"), _unit(f, "SPEAK")
    assert serve.predicate_class == "other" and serve.pragmatic == "ASSERTED"
    assert ("EMBEDS", serve.id, speak.id, "servir_a") in [(r.kind, r.source, r.target, r.evidence) for r in f.relations]
    assert not any(r.kind in {"CAUSES", "REPORTS", "CONDITIONS", "REFERS_TO"} for r in f.relations)
    # main clause keeps its textual subject; the reference is only added for relatives
    assert (serve.subject, serve.subject_ref is None) == (("mémoire", True) if text.startswith("La") else (None, False))

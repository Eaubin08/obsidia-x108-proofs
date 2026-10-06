"""H16 option A: deontic scope of "avoir à", "être obligatoire / nécessaire de".

- "Tu as à lancer P", "Il est obligatoire de lancer P": OBLIGATION by the existing modal
  channel (as "il faut"); a third-party "Paul a à lancer P" is asserted, never requested.
- "Il n'est pas obligatoire / nécessaire de lancer P", "Pas besoin de lancer P": NOT_REQUIRED,
  never FORBIDDEN, no request, no constraint.
- "Il est nécessaire de lancer P": necessity is not an obligation: held under its
  unrecognised governor (open, possible request exposed fail-closed, never OBLIGATION).
- "Tu n'as pas à lancer P": both readings kept (deontic_scope_open), canonical and
  non-blocking; never NOT_REQUIRED, never FORBIDDEN.
- Questions: "Est-il / N'est-il pas obligatoire de lancer P ?" are question_or_request with
  the gate kept, never a prohibition; "Est-il nécessaire de lancer P ?" is not promoted.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary


def _one(f):
    (u,) = f.units
    return u


def _no_prohibition(f):
    s = governable_summary(f)
    assert not f.constraints and not s["confirmed_no_execute"] and not s["negated_execute_surfaces"]
    assert all(u.pragmatic != "FORBIDDEN" for u in f.units)


@pytest.mark.parametrize("text,subject", [("Tu as à lancer P.", "tu"), ("Il est obligatoire de lancer P.", "il")])
def test_obligation(text, subject):
    f = parse_utterance(text)
    u = _one(f)
    assert (u.modality, u.pragmatic, u.subject, [a.text for a in u.objects]) == ("OBLIGATION", "REQUESTED", subject, ["p"])
    assert governable_summary(f)["requested_world_actions"] == ["EXECUTE"] and f.closure
    _no_prohibition(f)


def test_third_party_obligation_is_asserted():
    f = parse_utterance("Paul a à lancer P.")
    u = _one(f)
    assert (u.modality, u.pragmatic, u.subject) == ("OBLIGATION", "ASSERTED", "paul")
    assert governable_summary(f)["requested_world_actions"] == [] and f.closure


@pytest.mark.parametrize("text", ["Il n'est pas obligatoire de lancer P.", "Il n'est pas nécessaire de lancer P.",
                                  "Pas besoin de lancer P."])
def test_not_required(text):
    f = parse_utterance(text)
    u = _one(f)
    assert u.pragmatic == "NOT_REQUIRED" and [a.text for a in u.objects] == ["p"]
    assert governable_summary(f)["requested_world_actions"] == [] and f.closure
    _no_prohibition(f)


@pytest.mark.parametrize("text", ["Il est nécessaire de lancer P.", "Est-il nécessaire de lancer P ?"])
def test_necessity_is_not_obligation(text):
    f = parse_utterance(text)
    u = _one(f)
    assert u.modality is None and u.pragmatic == "EMBEDDED"
    assert f"infinitive_under_unrecognized_governor:{u.id}" in f.ambiguities and not f.closure
    _no_prohibition(f)


def test_negated_have_to_is_canonical_double_reading():
    f = parse_utterance("Tu n'as pas à lancer P.")
    u = _one(f)
    assert u.pragmatic == "EMBEDDED" and u.pragmatic != "NOT_REQUIRED"
    assert f.ambiguities == ("deontic_scope_open:u1",)
    assert governable_summary(f)["requested_world_actions"] == [] and f.closure
    _no_prohibition(f)


@pytest.mark.parametrize("text,polarity", [("Est-il obligatoire de lancer P ?", "positive"),
                                           ("N'est-il pas obligatoire de lancer P ?", "negative")])
def test_obligation_question_is_question_or_request(text, polarity):
    f = parse_utterance(text)
    u = _one(f)
    assert (u.modality, u.pragmatic, u.polarity) == ("OBLIGATION", "INDIRECT_REQUEST", polarity)
    assert f"question_or_request:{u.id}" in f.ambiguities
    assert governable_summary(f)["requested_world_actions"] == ["EXECUTE"] and f.closure
    _no_prohibition(f)

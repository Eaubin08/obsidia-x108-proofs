"""N13: discovered deontic surfaces never fall through to a request.

- "T'as pas à lancer P": the familiar "t'" (tu) subject hid the negated
  "avoir à"; "Tu n'as rien à lancer P": "rien" was not a negator of it.
  Both take the N8 contract (deontic_scope_open, H16).
- "N'est-il pas / Il n'est pas obligatoire / nécessaire de lancer P": the
  negated necessity was an unknown preposition exposed as a request; it takes
  deontic_scope_open (absence of obligation or not: held, never FORBIDDEN).
"nécessaire" is not mapped to OBLIGATION. The positive "(Est-il) obligatoire
/ nécessaire de V" keeps its existing fail-closed state (possible request,
closure open): mapping it to the obligation chain would close an open frame.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary


# H16 option A (requalified): "ne pas avoir à" and the negated necessity question keep both
# readings canonically (deontic_scope_open, non-blocking); the declarative negated
# "obligatoire / nécessaire de" is NOT_REQUIRED; the negated obligation question is a
# question or request (gate kept). Never a prohibition in any case.
@pytest.mark.parametrize("text,prag,mark,requested", [
    ("T'as pas à lancer P.", "EMBEDDED", "deontic_scope_open", []),
    ("Tu n'as rien à lancer P.", "EMBEDDED", "deontic_scope_open", []),
    ("N'est-il pas nécessaire de lancer P ?", "EMBEDDED", "deontic_scope_open", []),
    ("Il n'est pas obligatoire de lancer P.", "NOT_REQUIRED", None, []),
    ("Il n'est pas nécessaire de lancer P.", "NOT_REQUIRED", None, []),
    ("N'est-il pas obligatoire de lancer P ?", "INDIRECT_REQUEST", "question_or_request", ["EXECUTE"]),
])
def test_negated_deontic_surface_is_never_a_prohibition(text, prag, mark, requested):
    f = parse_utterance(text)
    (u,) = f.units
    assert u.pragmatic == prag and u.pragmatic != "FORBIDDEN"
    if mark is not None:
        assert f"{mark}:{u.id}" in f.ambiguities
    s = governable_summary(f)
    assert s["requested_world_actions"] == requested and s["confirmed_no_execute"] is False
    assert f.constraints == () and f.closure


@pytest.mark.parametrize("text", ["Il est nécessaire de lancer P.", "Est-il nécessaire de lancer P ?"])
def test_positive_necessity_keeps_its_fail_closed_state(text):
    # H16 A: necessity is not an obligation
    f = parse_utterance(text)
    (u,) = f.units
    assert u.modality is None and u.pragmatic == "EMBEDDED" and not f.closure
    assert not any(a.startswith("deontic_scope_open") for a in f.ambiguities)


@pytest.mark.parametrize("text", ["Il est obligatoire de lancer P.", "Tu as à lancer P."])
def test_positive_obligation_surfaces_are_obligations(text):
    # H16 A (requalified, formerly unrecognised governors): the existing obligation channel
    f = parse_utterance(text)
    (u,) = f.units
    assert u.modality == "OBLIGATION" and u.pragmatic == "REQUESTED" and f.closure

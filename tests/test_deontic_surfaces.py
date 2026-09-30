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


@pytest.mark.parametrize("text", ["T'as pas à lancer P.", "Tu n'as rien à lancer P.",
                                  "N'est-il pas obligatoire de lancer P ?", "Il n'est pas obligatoire de lancer P.",
                                  "N'est-il pas nécessaire de lancer P ?", "Il n'est pas nécessaire de lancer P."])
def test_negated_deontic_surface_is_never_a_request(text):
    f = parse_utterance(text)
    (u,) = f.units
    assert u.pragmatic == "EMBEDDED" and u.modality is None
    assert f"deontic_scope_open:{u.id}" in f.ambiguities
    s = governable_summary(f)
    assert s["requested_world_actions"] == [] and s["confirmed_no_execute"] is False
    assert f.constraints == () and not f.closure


@pytest.mark.parametrize("text", ["Il est nécessaire de lancer P.", "Est-il nécessaire de lancer P ?",
                                  "Il est obligatoire de lancer P.", "Tu as à lancer P."])
def test_positive_surfaces_keep_their_fail_closed_state(text):
    f = parse_utterance(text)
    (u,) = f.units
    assert u.modality is None and u.pragmatic == "EMBEDDED" and not f.closure
    assert not any(a.startswith("deontic_scope_open") for a in f.ambiguities)

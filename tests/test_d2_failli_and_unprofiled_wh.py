"""D2 continuation: H07 ("a failli") + unprofiled interrogative governor.

H07: "Paul a failli lancer P" is ASSERTED_NOT_REALIZED at occurrence level;
it no longer projects an epistemic CONTRADICTED flow
(NON_REALIZATION != EPISTEMIC_CONTRADICTION). A genuine contradiction keeps
CONTRADICTED.

Unprofiled governor: "Paul se demande qui / où / quand ... P" ("demande" is
unknown to the lexicon) no longer loses its interrogative complement (a
relative asserted realized from the perfective past, or nothing): the WH
complement opens under the unresolved governor, stays UNRESOLVED and open.
SYNTAX RECOGNITION != SEMANTIC PROFILE AVAILABILITY: no profile is added.
The accepted H13 baseline (4389daa0, KNOW + interrogative complement) is
unchanged.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.language_flow_projection import project_epistemic_flows
from app.semantic.lattice.ordered_meaning_flow import derive_ordered_meaning_flows


def _claims(f):
    return {c.predicate_ref: (c.occurrence_claim.value, c.occurrence_derivation.rule)
            for c in build_frame_event_index(f).events()}


def test_failli_is_not_realized_without_contradiction():
    f = parse_utterance("Paul a failli lancer P.")
    (u,) = f.units
    assert _claims(f)[u.id] == ("ASSERTED_NOT_REALIZED", "averted")
    assert project_epistemic_flows(f) == ()
    assert not any(x.state == "CONTRADICTED" for x in derive_ordered_meaning_flows(f))


def test_plain_negation_is_unchanged():
    f = parse_utterance("Paul n'a pas lancé P.")
    assert _claims(f)[f.units[0].id][0] == "ASSERTED_NOT_REALIZED" and project_epistemic_flows(f) == ()


def test_genuine_contradiction_keeps_contradicted():
    f = parse_utterance("je croyais qu'il avait réussi, mais les logs montrent qu'il a échoué")
    assert any(x.state == "CONTRADICTED" for x in derive_ordered_meaning_flows(f))


@pytest.mark.parametrize("text", ["Paul se demande qui a lancé P.", "Paul se demande quand Marie a lancé P.",
                                  "Paul se demande où Marie a lancé P."])
def test_unprofiled_interrogative_governor_stays_open(text):
    f = parse_utterance(text)
    p = next(u for u in f.units if u.lemma == "lancer")
    assert _claims(f)[p.id][0] not in {"ASSERTED_REALIZED", "ASSERTED_NOT_REALIZED"}
    assert p.pragmatic == "EMBEDDED"
    assert f"unresolved_complement_governance:{p.id}" in f.ambiguities
    assert not f.closure


@pytest.mark.parametrize("text", ["Marie sait qui a lancé P.", "Marie ne sait pas qui a lancé P.",
                                  "Marie sait-elle qui a lancé P ?", "Marie sait quand Paul a lancé P."])
def test_accepted_h13_baseline_is_unchanged(text):
    f = parse_utterance(text)
    assert _claims(f)[f.units[-1].id] == ("NO_ASSERTION", "commitment:QUESTIONED") and f.closure


def test_h04_declarative_control_is_unchanged():
    f = parse_utterance("Marie sait que Paul a lancé P.")
    assert _claims(f)[f.units[-1].id] == ("NO_ASSERTION", "commitment:PRESUPPOSED") and f.closure

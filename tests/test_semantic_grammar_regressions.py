"""Regressions found on held-out sentences (not used to design the grammar)."""
from __future__ import annotations

import pytest

from app.semantic.lattice import parse_utterance


def _unit(frame, predicate):
    return next(u for u in frame.units if u.predicate == predicate)


# ── verb chains: reflexive / passive under a modal ───────────────────────
def test_reflexive_infinitive_stays_in_modal_chain():
    # Middle voice with a 3rd-person nominal subject: a requirement on the
    # artifact, not a request addressed to the agent.
    frame = parse_utterance("Le code du template doit s'exécuter et ses asserts passer.")
    u = _unit(frame, "EXECUTE")
    assert u.modality == "OBLIGATION"
    assert u.pragmatic == "ASSERTED"
    assert all(o.text != "s'" for x in frame.units for o in x.objects)
    assert "MUST" not in {x.predicate for x in frame.units}


def test_passive_under_modal():
    u = _unit(parse_utterance("le script doit être lancé"), "EXECUTE")
    assert u.verb_form == "PARTICIPLE"
    assert u.modality == "OBLIGATION"
    assert u.pragmatic == "ASSERTED"


def test_manner_adverb_is_not_an_object():
    u = _unit(parse_utterance("le serveur se lance tout seul"), "EXECUTE")
    assert u.objects == ()
    assert u.pragmatic == "ASSERTED"


# ── negation scope against unknown governors ─────────────────────────────
@pytest.mark.parametrize("text", [
    "n'oublie pas de lancer les tests",
    "n'hésite pas à lancer le script",
])
def test_negated_governor_does_not_negate_infinitive(text):
    u = _unit(parse_utterance(text), "EXECUTE")
    assert u.polarity == "positive"
    assert u.pragmatic == "REQUESTED"


def test_negation_inside_modal_chain():
    u = _unit(parse_utterance("peux-tu ne pas lancer les tests ?"), "EXECUTE")
    assert u.polarity == "negative"
    assert u.pragmatic == "FORBIDDEN"


def test_infinitive_under_unrecognized_governor_is_embedded():
    frame = parse_utterance("essaie de lancer le script")
    u = _unit(frame, "EXECUTE")
    assert u.pragmatic == "EMBEDDED"
    assert any(a.startswith("infinitive_under_unrecognized_governor") for a in frame.ambiguities)


@pytest.mark.parametrize("text, pragmatic", [
    ("comment lancer le script ?", "ASKED"),
    ("explain how to run it", "EMBEDDED"),
])
def test_wh_infinitive_is_not_injunctive(text, pragmatic):
    assert _unit(parse_utterance(text), "EXECUTE").pragmatic == pragmatic


def test_interjection_is_not_a_subject():
    u = _unit(parse_utterance("please do not delete the files"), "DELETE")
    assert u.subject is None
    assert u.pragmatic == "FORBIDDEN"
    assert "NO_DELETE(files)" in parse_utterance("please do not delete the files").constraints


def test_second_person_present_question_is_fail_closed_request():
    frame = parse_utterance("tu lances le script ?")
    assert _unit(frame, "EXECUTE").pragmatic == "INDIRECT_REQUEST"
    assert any(a.startswith("question_or_request") for a in frame.ambiguities)
    past = parse_utterance("tu as lancé le script ?")
    assert _unit(past, "EXECUTE").pragmatic == "ASKED"


def test_substring_is_not_a_verb():
    # OS Trad substring matching would see "lance" in "balance".
    assert parse_utterance("la balance est équilibrée").units == ()


# ── causality / sequence ─────────────────────────────────────────────────
def test_reason_clause_is_not_host_of_following_sequence():
    from app.semantic.lattice import ProjectionAxis, project
    frame = parse_utterance("lance les tests car le script a changé, puis pousse le code")
    ids = {u.predicate: u.id for u in frame.units}
    rels = {(r.kind, r.source, r.target) for r in frame.relations}
    assert ("CAUSES", ids["CHANGE"], ids["EXECUTE"]) in rels
    assert ("PRECEDES", ids["EXECUTE"], ids["PUSH"]) in rels
    causal = project(frame, ProjectionAxis.CAUSAL)
    assert causal[ids["EXECUTE"]]["caused_by"] == [ids["CHANGE"]]


def test_trailing_condition_attaches_to_preceding_request():
    frame = parse_utterance("pousse le code si les tests passent")
    ids = {u.predicate: u.id for u in frame.units}
    assert ("CONDITIONS", ids["PASS"], ids["PUSH"]) in {
        (r.kind, r.source, r.target) for r in frame.relations}


def test_negated_avant_de_orders_preparation_first():
    frame = parse_utterance("ne lance pas le script avant de le préparer")
    ids = {u.predicate: u.id for u in frame.units}
    assert ("PRECEDES", ids["PREPARE"], ids["EXECUTE"]) in {
        (r.kind, r.source, r.target) for r in frame.relations}
    assert _unit(frame, "PREPARE").object_head == "script"


# ── reference ────────────────────────────────────────────────────────────
def test_sans_clitic_resolves_to_main_object():
    frame = parse_utterance("installe le paquet sans le déployer")
    dep = _unit(frame, "DEPLOY")
    assert dep.polarity == "negative" and dep.object_head == "paquet"
    assert "NO_DEPLOY(paquet)" in frame.constraints


def test_pronoun_without_antecedent_blocks_closure():
    frame = parse_utterance("relance-le")
    assert frame.unresolved_references and frame.closure is False


# ── modality ─────────────────────────────────────────────────────────────
def test_impersonal_prohibition():
    frame = parse_utterance("il ne faut pas pousser le code")
    u = _unit(frame, "PUSH")
    assert (u.polarity, u.pragmatic, u.modality) == ("negative", "FORBIDDEN", "OBLIGATION")


def test_negated_belief_keeps_embedded_event_positive():
    frame = parse_utterance("je ne pense pas que tu lances le script")
    assert _unit(frame, "BELIEVE").polarity == "negative"
    u = _unit(frame, "EXECUTE")
    assert (u.polarity, u.pragmatic) == ("positive", "BELIEVED")


# ── governance consequences ──────────────────────────────────────────────
@pytest.mark.parametrize("text", [
    "n'oublie pas de lancer les tests",   # reminder = request
    "essaie de lancer le script",          # unrecognized governor: fail-closed
    "tu lances le script ?",               # question-or-request: fail-closed
])
def test_requests_in_disguise_hold(text):
    from app.router.decision import decide
    assert decide(text, memory_index={})["gate"]["verdict"] == "HOLD"


def test_substring_does_not_hold():
    from app.router.decision import decide
    assert decide("la balance est équilibrée", memory_index={})["gate"]["verdict"] != "HOLD"

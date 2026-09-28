"""M8-D2b: anaphoric perspective boundaries + inherited provenance.

A report / learning / propositional perception introduces its content as a
referable object only when the COMPLETE perspective path above it is
referable: a belief, a knowledge boundary, an unprofiled or unresolved
governor anywhere above makes the descendant non-bindable (fail closed).
Every occurrence value inherited from an ancestor names that ancestor in its
derivation provenance (`inherited_from`).
"""
from __future__ import annotations

from itertools import product

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.event_reference_resolution import (
    is_event_reference_bindable,
    resolve_explicit_event_references,
)
from app.semantic.lattice.french_grammar import parse_utterance

A = chr(39)
X = "Paul a lancé le test"
FOLLOW = " Luc a vu ce lancement."


def _launch_reference(text):
    frame = parse_utterance(text + FOLLOW)
    index = build_frame_event_index(frame)
    launch = [c for c in index.events() if c.event_ref.event_kind.value == "ACTION"
              and next(u for u in frame.units if u.id == c.predicate_ref).predicate == "EXECUTE"][0]
    [reference] = resolve_explicit_event_references(frame, index.events()).references
    return frame, launch, reference


@pytest.mark.parametrize("text", [
    f"Marie croit que Jean a appris que {X}.",
    f"Marie pense que Jean a appris que {X}.",
    f"Marie ne croit pas que Jean a appris que {X}.",
    f"Marie croit que Jean a vu que {X}.",
    f"Marie croit que Jean dit que {X}.",
    f"Marie sait que Jean a appris que {X}.",
    f"Marie découvre que Jean a appris que {X}.",
    f"Paul confirme que Marie a appris que {X}.",
    f"Si Marie croit que Jean a appris que {X}, Luc attend.",
])
def test_non_referable_ancestor_blocks_descendant_binding(text):
    frame, launch, reference = _launch_reference(text)
    assert is_event_reference_bindable(launch, frame)[0] is False
    assert reference.resolution_status.value != "RESOLVED_STRUCTURAL"
    assert reference.target_event is None


@pytest.mark.parametrize("text, reason", [
    (f"{X}.", "occurrence:ASSERTED_REALIZED"),
    ("Marie a vu Paul lancer le test.", "occurrence:ASSERTED_REALIZED"),
    ("Marie voit Paul lancer le test.", "occurrence:ASSERTED_REALIZED"),
    (f"Marie dit que {X}.", "perspective:REPORT"),
    (f"Marie a appris que {X}.", "perspective:LEARN"),
    (f"Marie a vu que {X}.", "perspective:PERCEPTION"),
    (f"Marie dit que Jean a appris que {X}.", "perspective:LEARN"),
    (f"Marie a appris que Jean dit que {X}.", "perspective:REPORT"),
])
def test_fully_referable_paths_still_bind(text, reason):
    frame, launch, reference = _launch_reference(text)
    assert is_event_reference_bindable(launch, frame) == (True, reason)
    assert reference.resolution_status.value == "RESOLVED_STRUCTURAL"
    assert reference.target_event == launch.event_ref.event_id


@pytest.mark.parametrize("text", [
    "Marie ne voit pas Paul lancer le test.",
    "Marie verra Paul lancer le test.",
    "Si Marie voit Paul lancer le test, Luc attend.",
    "Marie dit que Paul lance le test.",
    "Marie dit que Paul va lancer le test.",
    "Marie dit que Paul a failli lancer le test.",
    "Paul va lancer le test.",
    f"Paul n{A}a pas lancé le test.",
])
def test_non_realized_antecedents_stay_unbound(text):
    frame, launch, reference = _launch_reference(text)
    assert is_event_reference_bindable(launch, frame)[0] is False
    assert reference.resolution_status.value != "RESOLVED_STRUCTURAL"


def _event(text, predicate, nth=1):
    frame = parse_utterance(text)
    index = build_frame_event_index(frame)
    units = [u for u in frame.units if u.predicate == predicate]
    unit = units[nth - 1]
    return frame, unit, index.event_for(unit.id)


def _unit(frame, predicate):
    return next(u for u in frame.units if u.predicate == predicate)


def test_inherited_unresolved_governance_names_its_ancestor():
    frame, unit, event = _event(f"Paul confirme que Marie a appris que {X}.", "EXECUTE", nth=1)
    x = next(u for u in frame.units if u.predicate == "EXECUTE" and u.embedded_under)
    event = build_frame_event_index(frame).event_for(x.id)
    assert event.occurrence_derivation.rule == "unresolved_governance"
    origin = event.occurrence_derivation.provenance["inherited_from"]["unresolved_governance"]
    assert origin == _unit(frame, "CONFIRM").id


def test_inherited_attribution_boundary_names_its_ancestor():
    frame = parse_utterance("Paul dit que Marie a lancé le test que Jean a préparé.")
    index = build_frame_event_index(frame)
    inherited = [c for c in index.events() if c.occurrence_derivation.rule == "attribution_boundary"]
    assert inherited
    for c in inherited:
        assert c.occurrence_derivation.provenance["inherited_from"]["attribution_boundary"] == _unit(frame, "SAY").id


def test_inherited_question_names_its_ancestor():
    frame = parse_utterance("Pouvez-vous préciser ce que vous voulez faire ?")
    index = build_frame_event_index(frame)
    inherited = [c for c in index.events() if c.occurrence_derivation.rule == "question"
                 and next(u for u in frame.units if u.id == c.predicate_ref).pragmatic != "ASKED"]
    assert inherited
    for c in inherited:
        origin = c.occurrence_derivation.provenance["inherited_from"]["question"]
        assert next(u for u in frame.units if u.id == origin).pragmatic == "ASKED"


def test_local_values_do_not_claim_an_inherited_origin():
    frame, unit, event = _event(f"{X}.", "EXECUTE")
    assert "inherited_from" not in event.occurrence_derivation.provenance
    frame, unit, event = _event("Est-ce que Paul a lancé le test ?", "EXECUTE")
    assert event.occurrence_derivation.rule == "question"
    assert "inherited_from" not in event.occurrence_derivation.provenance


def test_boundary_and_provenance_adversarial_matrix():
    metrics = dict.fromkeys(("CASES", "NON_REFERABLE_ANCESTOR_BINDING", "INHERITED_ORIGIN_GAPS", "ORIGIN_NOT_AN_ANCESTOR",
                             "CLAIMS_WITHOUT_DERIVATION", "UNRESOLVED_ANTECEDENT_BOUND_THROUGH_BOUNDARY", "CRASH",
                             "POSITIVE_BINDINGS", "BOUNDARY_CASES"), 0)
    outer = {"croit": True, "pense": True, "ne croit pas": True, "sait": True, "découvre": True, "confirme": True,
             "dit": False, "a appris": False}
    inner = ("a appris que", "a vu que", "dit que")
    contents = ("{s} a lancé {x}", "{s} avait lancé {x}", "{s} a relancé {x}")
    for (o, blocking), i, c, s, x, fol in product(outer.items(), inner, contents, ("Paul", "Nadia", "Omar", "Le chef"),
                                                  ("le test", "le build", "le job"), (FOLLOW, " Luc a rapporté ce lancement.")):
        text = f"Marie {o} que Jean {i} {c.format(s=s, x=x)}.{fol}"
        metrics["CASES"] += 1
        try:
            frame = parse_utterance(text)
            index = build_frame_event_index(frame)
            refs = resolve_explicit_event_references(frame, index.events()).references
        except Exception:
            metrics["CRASH"] += 1
            continue
        units = {u.id: u for u in frame.units}
        for ev in index.events():
            d = ev.occurrence_derivation
            if d is None:
                metrics["CLAIMS_WITHOUT_DERIVATION"] += 1
                continue
            origins = d.provenance.get("inherited_from", {})
            u = units[ev.predicate_ref]
            local_question = d.rule == "question" and u.pragmatic == "ASKED"
            local_unresolved = d.rule == "unresolved_governance" and (
                u.epistemic == "UNRESOLVED_GOVERNANCE" or (u.embedded_under and (u.embedded_under, u.id) not in {
                    (r.source, r.target) for r in frame.relations}))
            if d.rule in {"attribution_boundary", "unresolved_governance", "question"} or d.rule.startswith(
                    "conditional:ancestry"):
                key = "conditional" if d.rule.startswith("conditional") else d.rule
                if key not in origins and not (local_question or local_unresolved):
                    metrics["INHERITED_ORIGIN_GAPS"] += 1
            ancestors, cur = set(), u
            while cur.embedded_under and cur.embedded_under not in ancestors:
                ancestors.add(cur.embedded_under)
                cur = units[cur.embedded_under]
            metrics["ORIGIN_NOT_AN_ANCESTOR"] += sum(1 for v in origins.values() if v not in ancestors)
        for ref in refs:
            if ref.resolution_status.value != "RESOLVED_STRUCTURAL":
                continue
            target = index.by_event_id(ref.target_event)
            if blocking:
                metrics["NON_REFERABLE_ANCESTOR_BINDING"] += 1
            else:
                metrics["POSITIVE_BINDINGS"] += 1
            if target.occurrence_claim.value == "UNRESOLVED" and blocking:
                metrics["UNRESOLVED_ANTECEDENT_BOUND_THROUGH_BOUNDARY"] += 1
        metrics["BOUNDARY_CASES"] += blocking

    assert metrics["CASES"] >= 1000, metrics
    assert metrics["POSITIVE_BINDINGS"] > 0 and metrics["BOUNDARY_CASES"] > 0, metrics
    for key in ("NON_REFERABLE_ANCESTOR_BINDING", "INHERITED_ORIGIN_GAPS", "ORIGIN_NOT_AN_ANCESTOR",
                "CLAIMS_WITHOUT_DERIVATION", "UNRESOLVED_ANTECEDENT_BOUND_THROUGH_BOUNDARY", "CRASH"):
        assert metrics[key] == 0, (key, metrics)

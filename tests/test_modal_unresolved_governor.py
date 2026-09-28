"""M8-0c: an unresolved complement governor under a modal never asserts X.

"Marie pourrait découvrir que X": the unknown infinitive was dropped, the
"que" clause fell back to a relative attached to the modal unit (ABLE / MUST)
and X came out ASSERTED / ASSERTED_OCCURRED. The unknown infinitive is now an
UNKNOWN_COMPLEMENT_GOVERNOR embedded under the modal unit (MODAL(G(X)), never
flattened), X is embedded under it, and no factivity profile is decided.
"aller + inf" folds into the governor as for known verbs (NEAR_FUTURE).
"""
from __future__ import annotations

from itertools import product

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import UNRESOLVED_GOVERNOR, parse_utterance

A = chr(39)
X = "Paul a lancé le test"
ASSERTED = "ASSERTED_OCCURRED"
MODALS = {"pourrait": "ABLE", "peut": "ABLE", "pourra": "ABLE", "devrait": "MUST", "doit": "MUST"}


def _analyse(text):
    frame = parse_utterance(text)
    return frame, build_frame_event_index(frame)


def _complement(frame):
    return next(u for u in frame.units if u.predicate == "EXECUTE")


def _chain(frame, modal_predicate):
    modal = next(u for u in frame.units if u.predicate == modal_predicate)
    governor = next(u for u in frame.units if u.predicate == UNRESOLVED_GOVERNOR)
    x = _complement(frame)
    kinds = {(r.kind, r.source, r.target, r.evidence) for r in frame.relations}
    assert governor.embedded_under == modal.id and ("EMBEDS", modal.id, governor.id, "modal+inf") in kinds
    assert x.embedded_under == governor.id and ("EMBEDS", governor.id, x.id, "que") in kinds
    return modal, governor, x


@pytest.mark.parametrize("modal, governor", list(product(MODALS, ["découvrir", "remarquer"])))
def test_modal_unresolved_governor_does_not_assert_complement(modal, governor):
    frame, index = _analyse(f"Marie {modal} {governor} que {X}.")
    _, gov, x = _chain(frame, MODALS[modal])

    assert gov.lemma == governor
    assert x.pragmatic == "EMBEDDED"
    assert index.event_for(x.id).occurrence_status.value != ASSERTED
    assert not any(m.startswith("unanalyzed_predicative_content:") and "governed_by" in m for m in frame.missing)


def test_negation_order_is_kept_apart():
    frame, _ = _analyse(f"Marie ne pourrait pas découvrir que {X}.")
    modal, gov, x = _chain(frame, "ABLE")
    assert (modal.polarity, gov.polarity, x.polarity) == ("negative", "positive", "positive")

    frame, _ = _analyse(f"Marie pourrait ne pas découvrir que {X}.")
    modal, gov, x = _chain(frame, "ABLE")
    assert (modal.polarity, gov.polarity, x.polarity) == ("positive", "negative", "positive")


def test_conditional_and_future_modal_do_not_assert_complement():
    frame, index = _analyse(f"Si Marie pouvait découvrir que {X}, Luc attendrait.")
    modal, _, x = _chain(frame, "ABLE")
    assert modal.pragmatic == "HYPOTHETICAL"
    assert index.event_for(x.id).occurrence_status.value != ASSERTED

    frame, index = _analyse(f"Marie pourra découvrir que {X}.")
    modal, _, x = _chain(frame, "ABLE")
    assert modal.tense_aspect == "FUTURE"
    assert index.event_for(x.id).occurrence_status.value != ASSERTED


@pytest.mark.parametrize("text, polarity", [
    (f"Marie va découvrir que {X}.", "positive"),
    (f"Marie ne va pas découvrir que {X}.", "negative"),
])
def test_aller_folds_into_governor_keeping_future_and_negation(text, polarity):
    frame, index = _analyse(text)
    gov = next(u for u in frame.units if u.predicate == UNRESOLVED_GOVERNOR)
    x = _complement(frame)
    assert (gov.tense_aspect, gov.polarity, x.embedded_under) == ("NEAR_FUTURE", polarity, gov.id)
    assert index.event_for(x.id).occurrence_status.value != ASSERTED


def test_unbuildable_governor_under_modal_is_subordinated():
    frame, index = _analyse(f"Marie pourrait se rendre compte que {X}.")
    modal = next(u for u in frame.units if u.predicate == "ABLE")
    x = _complement(frame)
    assert (x.pragmatic, x.epistemic, x.embedded_under) == ("EMBEDDED", "UNRESOLVED_GOVERNANCE", modal.id)
    assert f"complement_governor_lost:{x.id}" in frame.ambiguities
    assert index.event_for(x.id).occurrence_status.value != ASSERTED


@pytest.mark.parametrize("text, family, expected", [
    (f"Marie pourrait dire que {X}.", "SAY", "REPORTED"),
    (f"Marie pourrait croire que {X}.", "BELIEVE", "UNKNOWN"),
    (f"Marie dit que {X}.", "SAY", "REPORTED"),
    (f"Marie croit que {X}.", "BELIEVE", "UNKNOWN"),
    (f"Marie sait que {X}.", "KNOW", "UNKNOWN"),
    (f"Marie a appris que {X}.", "LEARN", ASSERTED),
    (f"Marie découvre que {X}.", UNRESOLVED_GOVERNOR, "UNKNOWN"),
])
def test_supported_and_non_modal_behaviour_is_unchanged(text, family, expected):
    frame, index = _analyse(text)
    assert any(u.predicate == family for u in frame.units)
    assert index.event_for(_complement(frame).id).occurrence_status.value == expected


def test_modal_unresolved_governor_adversarial_matrix():
    metrics = dict.fromkeys((
        "CASES", "MODAL_UNRESOLVED_COMPLEMENT_ASSERTED", "MODAL_SCOPE_LOST", "GOVERNOR_NEGATION_LOST",
        "COMPLEMENT_NEGATION_INVENTED", "CONDITIONAL_MODAL_COMPLEMENT_ASSERTED", "FUTURE_MODAL_COMPLEMENT_ASSERTED",
        "UNKNOWN_GOVERNOR_DEFAULT_FACTIVITY_COUNT", "SUPPORTED_FAMILY_DIFF", "LOST_GOVERNOR_REGRESSION",
        "LOST_CONTENT_REGRESSION", "CRASH", "UNRESOLVED_MODAL_GOVERNOR_CASES", "MODAL_SUPPORTED_GOVERNOR_CASES",
    ), 0)
    modals = {"pourrait": ("ABLE", "pos"), "peut": ("ABLE", "pos"), "pourra": ("ABLE", "fut"), "devrait": ("MUST", "pos"),
              "doit": ("MUST", "pos"), "ne pourrait pas": ("ABLE", "neg_modal"), "pourrait ne pas": ("ABLE", "neg_gov"),
              "ne doit pas": ("MUST", "neg_modal")}
    unresolved = ("découvrir", "remarquer", "constater", "réaliser", "admettre", "prétendre")
    supported = {"dire": ("SAY", "REPORTED"), "croire": ("BELIEVE", "UNKNOWN")}
    complements = (X, "Paul lance le build", f"Paul n{A}a pas lancé le job", "Paul lancera le lot", "Paul est parti")
    subjects = ("Marie", "Le chef", "Nadia", "Omar")
    placements = ("{c}.", "Si {c}, Luc attend.", "Luc dit que {c}.")

    for (modal, (mpred, mkind)), governor, comp, subject, place in product(
            modals.items(), (*unresolved, *supported), complements, subjects, placements):
        verb = modal.replace("pourrait", "pouvait").replace("peut", "pouvait") if place.startswith("Si") else modal
        text = place.format(c=f"{subject} {verb} {governor} que {comp}")
        metrics["CASES"] += 1
        try:
            frame, index = _analyse(text)
        except Exception:
            metrics["CRASH"] += 1
            continue
        known = "parti" not in comp
        x = next((u for u in frame.units if u.predicate == "EXECUTE" and u.embedded_under), None)
        if known and x is None:
            metrics["LOST_CONTENT_REGRESSION"] += 1
            continue
        if not known:
            if not any("unanalyzed_predicative_content" in m for m in frame.missing):
                metrics["LOST_CONTENT_REGRESSION"] += 1
            continue
        status = index.event_for(x.id).occurrence_status.value
        modal_unit = next((u for u in frame.units if u.predicate == mpred), None)
        if governor in supported:
            metrics["MODAL_SUPPORTED_GOVERNOR_CASES"] += 1
            family, _ = supported[governor]
            head = next((u for u in frame.units if u.predicate == family and u.id == x.embedded_under), None)
            if head is None or x.embedded_under != head.id or head.modality is None:
                metrics["SUPPORTED_FAMILY_DIFF"] += 1
            continue
        metrics["UNRESOLVED_MODAL_GOVERNOR_CASES"] += 1
        gov = next((u for u in frame.units if u.predicate == UNRESOLVED_GOVERNOR), None)
        if gov is None:
            metrics["LOST_GOVERNOR_REGRESSION"] += 1
            continue
        if status == ASSERTED:
            metrics["MODAL_UNRESOLVED_COMPLEMENT_ASSERTED"] += 1
            if place.startswith("Si"):
                metrics["CONDITIONAL_MODAL_COMPLEMENT_ASSERTED"] += 1
            if mkind == "fut":
                metrics["FUTURE_MODAL_COMPLEMENT_ASSERTED"] += 1
        if x.pragmatic in {"ASSERTED", "REPORTED", "BELIEVED"} and x.embedded_under == gov.id:
            metrics["UNKNOWN_GOVERNOR_DEFAULT_FACTIVITY_COUNT"] += 1
        if modal_unit is None or gov.embedded_under != modal_unit.id or x.embedded_under != gov.id:
            metrics["MODAL_SCOPE_LOST"] += 1
            continue
        if mkind == "neg_modal" and (modal_unit.polarity, gov.polarity) != ("negative", "positive"):
            metrics["GOVERNOR_NEGATION_LOST"] += 1
        if mkind == "neg_gov" and (modal_unit.polarity, gov.polarity) != ("positive", "negative"):
            metrics["GOVERNOR_NEGATION_LOST"] += 1
        if x.polarity != ("negative" if f"n{A}a pas" in comp else "positive"):
            metrics["COMPLEMENT_NEGATION_INVENTED"] += 1

    assert metrics["CASES"] >= 3000, metrics
    for key in ("UNRESOLVED_MODAL_GOVERNOR_CASES", "MODAL_SUPPORTED_GOVERNOR_CASES"):
        assert metrics[key] > 0, (key, metrics)
    for key in ("MODAL_UNRESOLVED_COMPLEMENT_ASSERTED", "MODAL_SCOPE_LOST", "GOVERNOR_NEGATION_LOST",
                "COMPLEMENT_NEGATION_INVENTED", "CONDITIONAL_MODAL_COMPLEMENT_ASSERTED",
                "FUTURE_MODAL_COMPLEMENT_ASSERTED", "UNKNOWN_GOVERNOR_DEFAULT_FACTIVITY_COUNT",
                "SUPPORTED_FAMILY_DIFF", "LOST_GOVERNOR_REGRESSION", "LOST_CONTENT_REGRESSION", "CRASH"):
        assert metrics[key] == 0, (key, metrics)

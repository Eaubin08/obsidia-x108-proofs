"""M8-D2: OccurrenceClaim wired as an additive event projection.

Every EventCandidate keeps its legacy OccurrenceStatus (compatibility,
EventIndex identity) and gains the canonical OccurrenceClaim + its
StatusDerivation, produced by the single occurrence adapter. Semantic
consumers migrate by purpose: nominal anaphora binds on the claim or on an
explicit referable perspective (report / learning / propositional perception),
never on legacy REPORTED; relations and ReviewJoin expose the claim next to the
legacy status without any truth semantics.
"""
from __future__ import annotations

import json
from dataclasses import replace

import pytest

from app.semantic.lattice.complement_commitment import StatusDerivation
from app.semantic.lattice.event_extraction import OccurrenceStatus, extract_event_candidates
from app.semantic.lattice.event_index import build_event_index, build_frame_event_index
from app.semantic.lattice.event_reference_resolution import (
    is_event_reference_bindable,
    resolve_explicit_event_references,
)
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.knowledge_event_extraction import extract_knowledge_event_targets
from app.semantic.lattice.meta_event_relations import extract_report_event_relations
from app.semantic.lattice.observation_event_extraction import extract_observation_event_targets
from app.semantic.lattice.occurrence_derivation import OccurrenceClaim
from app.semantic.lattice.occurrence_shadow import shadow_frame
from app.semantic.lattice.review_join import build_review_envelope

O = OccurrenceClaim
A = chr(39)
X = "Paul a lancé le test"


def _event(text, predicate="EXECUTE", nth=1):
    frame = parse_utterance(text)
    index = build_frame_event_index(frame)
    units = [u for u in frame.units if u.predicate == predicate]
    return frame, index, index.event_for(units[nth - 1].id)


def test_every_candidate_family_exposes_claim_and_derivation():
    frame = parse_utterance(f"Marie a vu que Jean a appris que {X}.")
    base = extract_event_candidates(frame)
    candidates = (*base, *extract_observation_event_targets(frame, base).observation_events,
                  *extract_knowledge_event_targets(frame, base).knowledge_events)
    assert {c.event_ref.event_kind.value for c in candidates} == {"ACTION", "OBSERVATION", "KNOWLEDGE_ACQUISITION"}
    for c in candidates:
        assert isinstance(c.occurrence_claim, OccurrenceClaim)
        assert isinstance(c.occurrence_derivation, StatusDerivation)
        assert c.occurrence_derivation.dimension == "occurrence"
        assert c.occurrence_derivation.value == c.occurrence_claim.value
        assert c.to_dict()["occurrence_claim"] == c.occurrence_claim.value
        assert isinstance(c.occurrence_status, OccurrenceStatus)  # legacy kept


@pytest.mark.parametrize("text, legacy, claim", [
    (f"Marie a appris que {X}.", "ASSERTED_OCCURRED", O.NO_ASSERTION),
    (f"Marie voit que {X}.", "ASSERTED_OCCURRED", O.NO_ASSERTION),
    (f"Marie dit que {X}.", "REPORTED", O.NO_ASSERTION),
    (f"Marie croit que {X}.", "UNKNOWN", O.NO_ASSERTION),
    (f"Marie sait que {X}.", "UNKNOWN", O.NO_ASSERTION),
    ("Paul va lancer le test.", "UNKNOWN", O.PROJECTED_FUTURE),
    ("Paul peut lancer le test.", "UNCERTAIN", O.POSSIBLE),
    ("Paul doit lancer le test.", "UNCERTAIN", O.UNRESOLVED),
    ("Paul veut lancer le test.", "UNCERTAIN", O.NO_ASSERTION),
    ("Ne lance pas le test.", "NEGATED", O.NO_ASSERTION),
    ("Paul ne lancera pas le test.", "NEGATED", O.PROJECTED_FUTURE),
    ("Marie voit Paul lancer le test.", "UNKNOWN", O.ASSERTED_REALIZED),
    (X + ".", "ASSERTED_OCCURRED", O.ASSERTED_REALIZED),
])
def test_wired_claim_next_to_unchanged_legacy_status(text, legacy, claim):
    frame, _, event = _event(text)
    assert event.occurrence_status.value == legacy
    assert event.occurrence_claim is claim
    if "ne lancera pas" in text:
        assert next(u for u in frame.units if u.id == event.predicate_ref).polarity == "negative"


def test_no_assertion_and_unresolved_stay_distinct():
    _, _, belief = _event(f"Marie croit que {X}.")
    _, _, unknown = _event(f"Marie découvre que {X}.")
    assert (belief.occurrence_claim, unknown.occurrence_claim) == (O.NO_ASSERTION, O.UNRESOLVED)
    assert belief.occurrence_status is unknown.occurrence_status is OccurrenceStatus.UNKNOWN


def test_reported_antecedent_stays_referable_through_the_report_perspective():
    frame = parse_utterance(f"Marie dit que {X}. Luc a vu ce lancement.")
    index = build_frame_event_index(frame)
    launch = next(c for c in index.events() if c.event_ref.event_kind.value == "ACTION")
    assert launch.occurrence_claim is O.NO_ASSERTION  # no occurrence claim ...
    bindable, reason = is_event_reference_bindable(launch, frame)
    assert bindable and reason == "perspective:REPORT"  # ... but a reported, referable event
    # The decision never reads legacy REPORTED: erasing it changes nothing.
    forged = replace(launch, occurrence_status=OccurrenceStatus.UNKNOWN)
    assert is_event_reference_bindable(forged, frame) == (True, "perspective:REPORT")
    [reference] = resolve_explicit_event_references(frame, index.events()).references
    assert reference.resolution_status.value == "RESOLVED_STRUCTURAL"
    assert reference.target_event == launch.event_ref.event_id


@pytest.mark.parametrize("text, bindable", [
    (f"{X}. Luc a vu ce lancement.", True),
    ("Paul va lancer le test. Luc a vu ce lancement.", False),
    (f"Paul n{A}a pas lancé le test. Luc a vu ce lancement.", False),
    (f"Marie croit que {X}. Luc a vu ce lancement.", False),
    (f"Marie a appris que {X}. Luc a vu ce lancement.", True),
    ("Marie a vu Paul lancer le test. Luc a rapporté ce lancement.", True),
])
def test_bindability_decomposes_legacy_overload(text, bindable):
    frame = parse_utterance(text)
    index = build_frame_event_index(frame)
    launch = next(c for c in index.events() if c.event_ref.event_kind.value == "ACTION")
    assert is_event_reference_bindable(launch, frame)[0] is bindable


def test_relations_and_review_join_expose_claim_without_truth():
    frame = parse_utterance(f"Marie dit que {X}.")
    index = build_frame_event_index(frame)
    [relation] = extract_report_event_relations(frame, index).relations
    assert relation.metadata["target_occurrence_status"] == "REPORTED"  # legacy kept
    assert relation.metadata["target_occurrence_claim"] == "NO_ASSERTION"
    assert relation.metadata["source_occurrence_claim"] == "NO_ASSERTION" or relation.metadata[
        "source_occurrence_claim"] == "ASSERTED_REALIZED"
    envelope = build_review_envelope(frame, index.events()[0].event_ref.event_id, index)
    for entry in envelope.events:
        assert entry["occurrence_claim"] in {c.value for c in O}
        assert entry["occurrence_derivation"]["dimension"] == "occurrence"
        assert "occurrence_status" in entry  # legacy kept
    dumped = json.dumps([dict(e) for e in envelope.events], default=str).lower()
    assert "verified" not in dumped and "truth" not in dumped


def test_event_identity_ignores_the_new_projection():
    frame = parse_utterance(f"Marie a appris que {X}.")
    base = extract_event_candidates(frame)
    retagged = tuple(replace(c, occurrence_claim=O.UNRESOLVED) for c in base)
    index = build_event_index(frame, base, retagged)
    assert not index.conflicts
    assert [c.event_ref.event_id for c in index.events()] == [c.event_ref.event_id for c in base]


def test_wired_claims_match_the_d1_oracle():
    texts = [f"Marie a appris que {X}.", f"Marie dit que {X}.", f"Marie n{A}a pas dit que {X}.", "Paul va lancer le test.",
             f"Si Marie apprend que {X}, Luc attend.", "Marie a vu Paul lancer le test.", "Luc attend avant que Paul lance le test.",
             f"Marie pourrait découvrir que {X}.", "Paul a failli lancer le test.", f"Marie doit apprendre que {X}."]
    for text in texts:
        frame = parse_utterance(text)
        index = build_frame_event_index(frame)
        for record in shadow_frame(frame):
            assert index.event_for(record.source_ref).occurrence_claim is record.new_occurrence_claim, (text, record)


def test_wired_occurrence_property_matrix():
    from itertools import product

    from app.semantic.lattice.occurrence_projection import FrameOccurrenceProjection

    metrics = dict.fromkeys((
        "CASES", "WIRED_CLAIM_DIFF_FROM_PURE", "MIGRATED_CLAIM_WITHOUT_DERIVATION",
        "NO_ASSERTION_COLLAPSED_WITH_UNRESOLVED", "PRESUPPOSITION_TO_ASSERTED_OCCURRENCE",
        "ATTRIBUTED_TO_ASSERTED_OCCURRENCE", "MENTIONED_TO_ASSERTED_OCCURRENCE", "QUESTIONED_TO_ASSERTED_OCCURRENCE",
        "UNRESOLVED_TO_ASSERTED_OCCURRENCE", "DIRECTIVE_TO_OCCURRENCE", "FUTURE_NEGATION_LOST", "CONDITION_SCOPE_LOST",
        "REPORTED_USED_AS_OCCURRENCE_AUTHORITY", "REPORTED_INFORMATION_LOST", "DIRECT_PROPOSITIONAL_PERCEPTION_COLLAPSE",
        "CRASH",
    ), 0)
    seen = dict.fromkeys(O, 0)
    asserted = {O.ASSERTED_REALIZED, O.ASSERTED_NOT_REALIZED}
    unresolved_rules = ("malformed_ancestry", "unresolved_governance", "commitment:UNRESOLVED", "entailed:no_parent",
                        "entailed:local_operator", "entertained:unsupported", "multi_operator", "modal:OBLIGATION",
                        "conditional_mood", "no_realization_signal")
    subjects = ("Paul", "Nadia", "Le chef", "Omar", "Jean", "Hugo", "Anne", "Luc")
    things = ("le test", "le build", "le job", "le lot", "le script", "la suite")
    contents = ("{s} a lancé {x}", "{s} lance {x}", "{s} lancera {x}", "{s} va lancer {x}", "{s} n" + A + "a pas lancé {x}",
                "{s} ne lancera pas {x}", "{s} pourrait lancer {x}", "{s} doit lancer {x}", "{s} veut lancer {x}",
                "{s} a failli lancer {x}")
    frames = ("{c}.", "Marie dit que {c}.", "Marie n" + A + "a pas dit que {c}.", "Marie croit que {c}.",
              "Marie ne croit pas que {c}.", "Marie sait que {c}.", "Marie a appris que {c}.", "Marie doit apprendre que {c}.",
              "Marie a vu que {c}.", "Si {c}, Luc attend.", "Si Marie lance le lot, {c}.", "Est-ce que {c} ?",
              "Luc attend avant que {c}.", "Marie découvre que {c}.", "Marie dit que Jean a appris que {c}.")
    texts = [f.format(c=c.format(s=s, x=x)) for f, c, s, x in product(frames, contents, subjects, things)]
    texts += [t.format(s=s, x=x) for t, s, x in product(
        ("Marie voit {s} lancer {x}.", "Marie ne voit pas {s} lancer {x}.", "Marie verra {s} lancer {x}.",
         "Lance {x}.", "Ne lance pas {x}.", "Si Marie voit {s} lancer {x}, Luc attend."), subjects, things)]
    for text in texts:
        try:
            frame = parse_utterance(text)
            index = build_frame_event_index(frame)
            pure = FrameOccurrenceProjection(frame)
        except Exception:
            metrics["CRASH"] += 1
            continue
        units = {u.id: u for u in frame.units}
        kinds = {r.kind for r in frame.relations}
        for c in index.events():
            metrics["CASES"] += 1
            unit = units[c.predicate_ref]
            claim, derivation = c.occurrence_claim, c.occurrence_derivation
            if derivation is None or claim is None or derivation.value != claim.value:
                metrics["MIGRATED_CLAIM_WITHOUT_DERIVATION"] += 1
                continue
            seen[claim] += 1
            if pure.claim(unit)[0].claim is not claim:
                metrics["WIRED_CLAIM_DIFF_FROM_PURE"] += 1
            rule = derivation.rule
            if (claim is O.NO_ASSERTION) == rule.startswith(unresolved_rules):
                metrics["NO_ASSERTION_COLLAPSED_WITH_UNRESOLVED"] += claim in {O.NO_ASSERTION, O.UNRESOLVED}
            commitment = derivation.provenance.get("commitment")
            if claim in asserted:
                metrics["PRESUPPOSITION_TO_ASSERTED_OCCURRENCE"] += commitment == "PRESUPPOSED"
                metrics["ATTRIBUTED_TO_ASSERTED_OCCURRENCE"] += commitment == "ATTRIBUTED"
                metrics["MENTIONED_TO_ASSERTED_OCCURRENCE"] += commitment == "MENTIONED"
                metrics["QUESTIONED_TO_ASSERTED_OCCURRENCE"] += commitment == "QUESTIONED"
                metrics["UNRESOLVED_TO_ASSERTED_OCCURRENCE"] += commitment == "UNRESOLVED"
                metrics["REPORTED_USED_AS_OCCURRENCE_AUTHORITY"] += c.occurrence_status is OccurrenceStatus.REPORTED
            if unit.pragmatic in {"REQUESTED", "INDIRECT_REQUEST", "FORBIDDEN"} and claim not in {O.NO_ASSERTION,
                                                                                                O.UNRESOLVED}:
                metrics["DIRECTIVE_TO_OCCURRENCE"] += 1
            if rule == "negation+future" and unit.polarity != "negative":
                metrics["FUTURE_NEGATION_LOST"] += 1
            if claim is O.CONTINGENT and "CONDITIONS" not in kinds and not any(
                    u.pragmatic == "HYPOTHETICAL" for u in frame.units):
                metrics["CONDITION_SCOPE_LOST"] += 1
            if c.occurrence_status is OccurrenceStatus.REPORTED and "REPORTS" not in kinds:
                metrics["REPORTED_INFORMATION_LOST"] += 1
            if unit.predicate == "EXECUTE" and unit.embedded_under is not None:
                perception = units[unit.embedded_under].predicate == "OBSERVE"
                direct = any(r.evidence == "observation+inf" and r.target == unit.id for r in frame.relations)
                if perception and ((direct and commitment == "PRESUPPOSED")
                                   or (not direct and commitment == "ENTAILED")):
                    metrics["DIRECT_PROPOSITIONAL_PERCEPTION_COLLAPSE"] += 1

    assert metrics["CASES"] >= 10000, metrics
    assert all(seen[c] > 0 for c in O), seen
    for key, value in metrics.items():
        if key != "CASES":
            assert value == 0, (key, metrics)

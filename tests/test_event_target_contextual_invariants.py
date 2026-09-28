"""M2: a resolved EVENT_TARGET must name an indexed predicate whose EventRef is
exactly target_event in the SAME frame index. Checked by one pure helper with
the index as explicit context (no global lookup, no repair, no re-selection).
"""
from __future__ import annotations

from dataclasses import replace
from itertools import product

from app.semantic.lattice.event_coreference import EventTargetReference, ResolutionStatus, TargetKind
from app.semantic.lattice.event_extraction import extract_event_candidates
from app.semantic.lattice.event_index import build_frame_event_index, target_index_violation
from app.semantic.lattice.event_reference_resolution import resolve_explicit_event_references
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.knowledge_event_extraction import extract_knowledge_event_targets
from app.semantic.lattice.meta_event_relations import (
    extract_belief_event_relations,
    extract_nominal_reference_relations,
    extract_report_event_relations,
)
from app.semantic.lattice.observation_event_extraction import extract_observation_event_targets

TWO = "Paul a lancé le build et Paul a lancé le test."


def _index_and_ids(text=TWO):
    frame = parse_utterance(text)
    index = build_frame_event_index(frame)
    return frame, index, [(c.predicate_ref, c.event_ref.event_id) for c in index.events()]


def _event_ref(predicate, event):
    return EventTargetReference("e_src", "u_src", TargetKind.EVENT_TARGET, ResolutionStatus.RESOLVED_STRUCTURAL,
                                predicate, event)


def test_matching_pair_passes():
    _, index, ((u1, e1), (u2, e2)) = _index_and_ids()
    assert target_index_violation(_event_ref(u1, e1), index) is None
    assert target_index_violation(_event_ref(u2, e2), index) is None


def test_swapped_pair_is_a_mismatch():
    _, index, ((u1, e1), (u2, e2)) = _index_and_ids()
    assert target_index_violation(_event_ref(u1, e2), index) == "target_event_mismatch"
    assert target_index_violation(_event_ref(u2, e1), index) == "target_event_mismatch"


def test_unknown_predicate_is_rejected():
    _, index, ((_, e1), _) = _index_and_ids()
    assert target_index_violation(_event_ref("u_missing", e1), index) == "target_predicate_not_indexed"


def test_foreign_event_is_rejected_even_with_a_local_looking_predicate():
    _, index, ((u1, _), _) = _index_and_ids()
    foreign = extract_event_candidates(parse_utterance("Paul a lancé le déploiement et Paul a lancé le test."))
    foreign_id = foreign[0].event_ref.event_id
    assert foreign[0].predicate_ref == u1 and index.by_event_id(foreign_id) is None
    assert target_index_violation(_event_ref(u1, foreign_id), index) == "target_event_mismatch"


def test_proposition_target_must_name_a_frame_predicate():
    frame, index, _ = _index_and_ids("Paul dit que le système s'est arrêté.")
    stop = next(u for u in frame.units if u.predicate == "STOP")
    ok = EventTargetReference("e", "u1", TargetKind.PROPOSITION_TARGET, ResolutionStatus.RESOLVED_STRUCTURAL, stop.id, None)
    bad = replace(ok, target_predicate="u_missing")
    assert target_index_violation(ok, index) is None
    assert target_index_violation(bad, index) == "target_predicate_not_in_frame"


def test_non_resolved_and_non_event_targets_need_no_context():
    _, index, _ = _index_and_ids()
    for kind, status in ((TargetKind.UNKNOWN_TARGET, ResolutionStatus.UNRESOLVED),
                         (TargetKind.UNKNOWN_TARGET, ResolutionStatus.AMBIGUOUS),
                         (TargetKind.PROPOSITION_TARGET, ResolutionStatus.UNRESOLVED),
                         (TargetKind.ENTITY_TARGET, ResolutionStatus.RESOLVED_STRUCTURAL)):
        assert target_index_violation(EventTargetReference("e", "u", kind, status), index) is None


def test_every_current_producer_is_contextually_valid():
    texts = (
        "Paul dit que Marie a lancé le test.", "Paul croit que Marie a dit que Jean a lancé le test.",
        "Paul dit que Marie a vu Jean lancer le test.", "J'ai appris que Paul a dit que Marie a lancé le test.",
        "Paul a lancé le test. J'ai observé ce lancement. Marie a mentionné ce lancement. Luc croit ce lancement.",
        "Paul dit qu'il a vu Marie lancer le test. Luc a mentionné cette observation.",
        "Paul dit que le système s'est arrêté.", "J'ai vu le test que Paul a lancé.", "Paul a lancé le test. J'ai observé ce fait.",
        "Paul nie que Marie a lancé le test.", "Paul confirme que Marie a appris que Jean a lancé le test.",
    )
    checked = 0
    for text, i in product(texts, range(15)):
        frame = parse_utterance(text.replace("le test", f"le test {i}"))
        index = build_frame_event_index(frame)
        base = extract_event_candidates(frame)
        records = (
            *resolve_explicit_event_references(frame, index.events()).references,
            *extract_observation_event_targets(frame, base).targets,
            *extract_knowledge_event_targets(frame, base).targets,
            *extract_report_event_relations(frame, index).targets,
            *extract_belief_event_relations(frame, index).targets,
            *extract_nominal_reference_relations(frame, index).targets,
        )
        for record in records:
            checked += 1
            assert target_index_violation(record, index) is None, (text, record.to_dict())
    assert checked > 300


def _expected_local_valid(kind, status, predicate, event) -> bool:
    resolved = status in {ResolutionStatus.RESOLVED_STRUCTURAL, ResolutionStatus.RESOLVED_EXPLICIT}
    if not resolved and event is not None:
        return False
    if kind is TargetKind.EVENT_TARGET:
        return resolved and bool(predicate) and bool(event)
    if kind is TargetKind.UNKNOWN_TARGET:
        return not resolved and predicate is None and event is None
    if kind is TargetKind.PROPOSITION_TARGET:
        return event is None and (not resolved or bool(predicate))
    return event is None  # ENTITY_TARGET


def test_target_invariant_adversarial_matrix():
    texts = (TWO, "Paul dit que Marie a lancé le test.", "Paul croit que Marie a vu Jean lancer le test.",
             "J'ai appris que Paul a dit que Marie a lancé le test.", "Paul dit que le système s'est arrêté.",
             "Paul a lancé le test. J'ai observé ce lancement.")
    metrics = dict.fromkeys(("CASES", "INVALID_LOCAL_ACCEPTED", "VALID_LOCAL_REJECTED",
                             "EVENT_PREDICATE_MISMATCH_ACCEPTED", "UNKNOWN_PREDICATE_EVENT_ACCEPTED",
                             "FOREIGN_EVENT_ACCEPTED", "VALID_CONTEXT_REJECTED"), 0)
    foreign_id = extract_event_candidates(parse_utterance("Omar a relancé le déploiement."))[0].event_ref.event_id
    for text in texts:
        frame = parse_utterance(text)
        index = build_frame_event_index(frame)
        events = index.events()
        (p1, e1) = (events[0].predicate_ref, events[0].event_ref.event_id)
        other_e = events[1].event_ref.event_id if len(events) > 1 else "event:other"
        predicates = {"none": None, "match": p1, "missing": "u_missing"}
        event_ids = {"none": None, "match": e1, "other": other_e, "foreign": foreign_id}
        for kind, status, (pk, predicate), (ek, event) in product(
                TargetKind, ResolutionStatus, predicates.items(), event_ids.items()):
            for _ in range(2):  # repeat: construction must be deterministic
                metrics["CASES"] += 1
                valid = _expected_local_valid(kind, status, predicate, event)
                try:
                    ref = EventTargetReference("e_src", "u_src", kind, status, predicate, event)
                except ValueError:
                    metrics["VALID_LOCAL_REJECTED"] += valid
                    continue
                if not valid:
                    metrics["INVALID_LOCAL_ACCEPTED"] += 1
                    continue
                violation = target_index_violation(ref, index)
                if kind is TargetKind.EVENT_TARGET:
                    consistent = pk == "match" and ek == "match"
                    if violation is None and not consistent:
                        metrics[{"missing": "UNKNOWN_PREDICATE_EVENT_ACCEPTED"}.get(pk) or
                                ("FOREIGN_EVENT_ACCEPTED" if ek == "foreign" else "EVENT_PREDICATE_MISMATCH_ACCEPTED")] += 1
                    if violation is not None and consistent:
                        metrics["VALID_CONTEXT_REJECTED"] += 1
    assert metrics["CASES"] >= 1000
    for key, value in metrics.items():
        if key != "CASES":
            assert value == 0, (key, metrics)

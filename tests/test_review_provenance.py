"""M3: ReviewEnvelope preserves event provenance and epistemic sources.

Event entries keep the EventRef and EventCandidate provenance as distinct
blocks. Epistemic contributions are lossless and source-bearing: one record per
upstream epistemic flow (state + source + path) and one per typed meta-event
relation (perspective with its source event, no state invented). The per-
predicate `epistemic_states` summary is only a derived view. Nothing here is
evidence, truth or consensus; membership and ids are unchanged.
"""
from __future__ import annotations

import json
from itertools import product

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.language_flow_projection import project_epistemic_flows
from app.semantic.lattice.review_join import build_review_envelope

FORBIDDEN_KEYS = {"truth_score", "verified", "trusted", "consensus", "winner", "authority"}


def _envelope(text: str, center_predicate: str | None = None):
    frame = parse_utterance(text)
    index = build_frame_event_index(frame)
    center = index.event_for(center_predicate) if center_predicate else index.events()[0]
    return frame, index, build_review_envelope(frame, center.event_ref.event_id, index)


def test_event_entries_keep_eventref_and_candidate_provenance_separately():
    frame, index, env = _envelope("Paul a lancé le test. Marie a mentionné ce lancement.")
    units = {u.id: u for u in frame.units}

    assert len(env.events) == 2
    for entry in env.events:
        candidate = index.event_for(entry["predicate_ref"])
        assert dict(entry["event_ref"]["provenance"]) == dict(candidate.event_ref.provenance)
        assert entry["event_ref"]["source_frame"] == candidate.event_ref.source_frame == index.frame_ref
        assert entry["event_ref"]["status"] == candidate.event_ref.status
        assert dict(entry["event_ref"]["metadata"]) == dict(candidate.event_ref.metadata)
        assert entry["candidate"]["extraction_status"] == candidate.extraction_status.value
        assert tuple(entry["candidate"]["provenance"]["span"]) == units[entry["predicate_ref"]].span
        assert entry["candidate"]["provenance"]["parser"] == units[entry["predicate_ref"]].provenance
        assert dict(entry["candidate"]["metadata"]) == dict(candidate.metadata)
        assert "extraction_version" in entry["event_ref"]["provenance"]


def test_nested_provenance_is_read_only_and_serialisable():
    _, _, env = _envelope("Paul dit que Marie a lancé le test.")
    entry = env.events[0]
    with pytest.raises(TypeError):
        entry["event_ref"]["provenance"]["source"] = "forged"  # type: ignore[index]
    with pytest.raises(TypeError):
        env.epistemic_contributions[0]["flow"]["provenance"]["evidence"] = "x"  # type: ignore[index]
    json.dumps(env.to_dict(), default=str)


def test_flow_contributions_keep_state_source_and_path():
    frame, index, env = _envelope("Paul croit que Marie a dit que Jean a lancé le test.", "u3")
    flows = [c for c in env.epistemic_contributions if c["origin"] == "epistemic_flow"]
    eid = lambda p: index.event_for(p).event_ref.event_id

    assert [(c["predicate_ref"], c["state"], c["source_predicate"], c["source_event"]) for c in flows] == [
        ("u2", "BELIEVED", "u1", eid("u1")), ("u3", "REPORTED", "u2", eid("u2"))]
    for contribution in flows:
        assert contribution["event_id"] == eid(contribution["predicate_ref"])
        assert contribution["flow"]["family"] == "EPISTEMIC_STATE"
        assert contribution["flow"]["provenance"]["parser"] is not None
        assert contribution["flow"]["provenance"]["evidence"] is None
        assert isinstance(contribution["flow_position"], int)


def test_multi_perspective_keeps_one_source_per_perspective():
    frame, index, env = _envelope(
        "Paul a lancé le test. J'ai observé ce lancement. Marie a mentionné ce lancement. Luc croit ce lancement.", "u1")
    perspectives = [c for c in env.epistemic_contributions if c["origin"] == "event_relation"]

    assert len({e["event_id"] for e in env.events}) == 4
    assert sorted((c["relation_kind"], c["source_predicate"]) for c in perspectives) == [
        ("BELIEVES_ABOUT", "u4"), ("OBSERVES", "u2"), ("REPORTS_ABOUT", "u3")]
    assert {c["event_id"] for c in perspectives} == {index.event_for("u1").event_ref.event_id}
    assert all(c["state"] is None for c in perspectives)
    for c in perspectives:
        relation = env.relations[c["relation_position"]]
        assert (relation.relation_kind.value, relation.source_event, relation.target_event, relation.status) == (
            c["relation_kind"], c["source_event"], c["event_id"], c["relation_status"])


def test_same_perspective_from_two_sources_is_not_collapsed():
    frame, index, env = _envelope("Paul a lancé le test. Marie a mentionné ce lancement. Luc a mentionné ce lancement.", "u1")
    reports = [c for c in env.epistemic_contributions if c.get("relation_kind") == "REPORTS_ABOUT"]

    assert len(reports) == 2
    assert len({c["source_event"] for c in reports}) == 2


def test_summary_is_derived_and_no_state_is_invented():
    for text in ("Paul croit que Marie a dit que Jean a lancé le test.", "Paul dit que Marie a vu Jean lancer le test.",
                 "Paul a lancé le test. J'ai observé ce lancement. Luc croit ce lancement."):
        frame, _, env = _envelope(text)
        upstream = {f.state for f in project_epistemic_flows(frame)}
        states = {c["state"] for c in env.epistemic_contributions if c["state"] is not None}
        assert states <= upstream
        for entry in env.events:
            derived = tuple(dict.fromkeys(c["state"] for c in env.epistemic_contributions
                                          if c["origin"] == "epistemic_flow" and c["predicate_ref"] == entry["predicate_ref"]))
            assert entry["epistemic_states"] == derived
        assert not FORBIDDEN_KEYS & set(env.to_dict())


def test_replay_is_deterministic():
    text = "Paul croit que Marie a dit que Jean a lancé le test. J'ai observé ce lancement. Luc a mentionné ce lancement."
    dumps = {json.dumps(_envelope(text, "u3")[2].to_dict(), sort_keys=True, default=str) for _ in range(4)}
    assert len(dumps) == 1


def test_review_provenance_adversarial_matrix():
    templates = (
        "{a} a relancé {x}.",
        "{a} a relancé {x}. {b} a observé ce lancement.",
        "{a} a relancé {x}. {b} a appris ce lancement.",
        "{a} a relancé {x}. {b} a mentionné ce lancement. {c} a mentionné ce lancement.",
        "{a} a relancé {x}. {b} croit ce lancement. {c} croit ce lancement.",
        "{a} a relancé {x}. {b} a observé ce lancement. {c} a mentionné ce lancement.",
        "{a} a relancé {x}. {b} a mentionné ce lancement. {c} croit ce lancement.",
        "{a} a relancé {x}. J'ai observé ce lancement. {b} a mentionné ce lancement. {c} croit ce lancement.",
        "{a} croit que {b} a dit que {c} a relancé {x}.",
        "{a} dit que {b} a vu {c} relancer {x}.",
        "{a} dit que {b} a appris que {c} a relancé {x}.",
        "{a} dit que {b} croit que {c} a relancé {x}.",
    )
    metrics = dict.fromkeys((
        "CASES", "EVENT_PROVENANCE_LOST", "CANDIDATE_PROVENANCE_LOST", "EPISTEMIC_SOURCE_LOST",
        "DISTINCT_SOURCES_COLLAPSED", "FLOW_ID_LOST", "RELATION_SOURCE_LOST", "NEW_STATE", "NEW_TRUTH_SCALAR",
        "NEW_CONSENSUS", "CONTRIBUTIONS",
    ), 0)
    people = ("Paul", "Nadia", "Omar", "Le directeur")
    for template, (a, b, c), x in product(templates, product(people, repeat=3), ("le script", "la suite", "le job")):
        if len({a, b, c}) < 3:
            continue
        frame = parse_utterance(template.format(a=a, b=b, c=c, x=x))
        index = build_frame_event_index(frame)
        flows = project_epistemic_flows(frame)
        for candidate in index.events():
            env = build_review_envelope(frame, candidate.event_ref.event_id, index)
            metrics["CASES"] += 1
            if set(env.to_dict()) & FORBIDDEN_KEYS or env.metadata["truth"] is not None:
                metrics["NEW_TRUTH_SCALAR"] += 1
            if env.metadata.get("conflict_resolution") != "none":
                metrics["NEW_CONSENSUS"] += 1
            for entry in env.events:
                ev = index.by_event_id(entry["event_id"])
                if dict(entry["event_ref"]["provenance"]) != dict(ev.event_ref.provenance):
                    metrics["EVENT_PROVENANCE_LOST"] += 1
                if dict(entry["candidate"]["provenance"]) != dict(ev.provenance):
                    metrics["CANDIDATE_PROVENANCE_LOST"] += 1
            members = {e["predicate_ref"] for e in env.events}
            expected_flows = [f for f in flows if f.source_object in members]
            got_flows = [c for c in env.epistemic_contributions if c["origin"] == "epistemic_flow"]
            if len(got_flows) != len(expected_flows):
                metrics["EPISTEMIC_SOURCE_LOST"] += 1
            for c in got_flows:
                metrics["CONTRIBUTIONS"] += 1
                if c["flow_position"] is None or _json(flows[c["flow_position"]].to_dict()) != _json(_plain(c["flow"])):
                    metrics["FLOW_ID_LOST"] += 1
                if c["state"] not in {f.state for f in flows}:
                    metrics["NEW_STATE"] += 1
            got_relations = [c for c in env.epistemic_contributions if c["origin"] == "event_relation"]
            metrics["CONTRIBUTIONS"] += len(got_relations)
            if len(got_relations) != len(env.relations):
                metrics["RELATION_SOURCE_LOST"] += 1
            keys = {(c["relation_kind"], c["source_event"], c["event_id"], c["relation_status"]) for c in got_relations}
            if len(keys) != len(got_relations):
                metrics["DISTINCT_SOURCES_COLLAPSED"] += 1
            for c in got_relations:
                if c["source_event"] is None or c["source_predicate"] is None:
                    metrics["RELATION_SOURCE_LOST"] += 1
    assert metrics["CASES"] >= 1500 and metrics["CONTRIBUTIONS"] > 0
    for key, value in metrics.items():
        if key not in {"CASES", "CONTRIBUTIONS"}:
            assert value == 0, (key, metrics)


def _plain(value):
    if hasattr(value, "items"):
        return {k: _plain(v) for k, v in value.items()}
    if isinstance(value, tuple):
        return [_plain(v) for v in value]
    return value


def _json(value):
    return json.loads(json.dumps(value, sort_keys=True, default=str))

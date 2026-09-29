"""ReviewJoin V1 (master block 25): join every projection, resolve nothing.

Contract (recovered SENS doctrine): JOIN != RESOLVE; readings are preserved by
dimension, perspective and provenance; no truth scalar, no winner, no
consensus, no fusion, no authority. V0's envelope is carried unchanged.
"""
from __future__ import annotations

import itertools

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.language_flow_projection import project_causal_flows, project_temporal_flows
from app.semantic.lattice.review_join import build_review_envelope
from app.semantic.lattice.review_join_v1 import READING_DIMENSIONS, build_review_join_v1


def _join(text, predicate=None):
    f = parse_utterance(text)
    idx = build_frame_event_index(f)
    center = (idx.event_for(predicate) if predicate else idx.events()[0]).event_ref.event_id
    return f, idx, center, build_review_join_v1(f, center, idx)


def test_v0_envelope_is_carried_unchanged():
    f, idx, center, rj = _join("Marie dit que Paul a lancé P.")
    assert rj.envelope.to_dict() == build_review_envelope(f, center, idx).to_dict()


def test_several_perspectives_on_one_event_coexist():
    f, idx, center, rj = _join("Marie dit que Paul a lancé P.", "u2")
    readings = rj.readings_for(center)
    dims = [(r["dimension"], r["status"]) for r in readings]
    assert ("occurrence", "NO_ASSERTION") in dims
    assert ("epistemic", "REPORTED") in dims and ("epistemic", "REPORTS_ABOUT") in dims
    assert ("temporal", "PAST") in dims
    assert all(r["provenance"]["source"] for r in readings)


def test_contradictory_readings_are_both_kept_and_nothing_wins():
    f, idx, center, rj = _join("Lance le test mais ne lance pas le test.", "u1")
    contra = [r for r in rj.readings if r["dimension"] == "contradiction"]
    assert contra and contra[0]["perspective"] == ["u2"]
    assert rj.open_items["closure"] is False
    assert any(b.startswith("contradiction:") for b in rj.open_items["closure_blockers"])
    assert (rj.metadata["truth"], rj.metadata["winner"], rj.metadata["conflict_resolution"]) == (None, None, "none")


@pytest.mark.parametrize("text,dimension,status", [
    ("Paul doit lancer P ou exécuter Q.", "coordination", "OR:disjunction"),
    ("Peux-tu lancer P et exécuter Q ?", "operator", "ABILITY_OR_PERMISSION:INDIRECT_REQUEST"),
    ("Peux-tu lancer P et exécuter Q ?", "ambiguity", "ability_permission_or_request:u1"),
    ("Prépare le test puis lance le build.", "temporal", "BEFORE:before"),
])
def test_structural_projections_are_joined(text, dimension, status):
    _, _, _, rj = _join(text)
    assert (dimension, status) in {(r["dimension"], r["status"]) for r in rj.readings}


def test_unresolved_reference_is_kept_open():
    f, idx, center, rj = _join("Lance le test et le build puis exécute-le.", "u2")
    assert ("reference", "UNRESOLVED:le") in {(r["dimension"], r["status"]) for r in rj.readings_for(center)}
    assert rj.open_items["closure"] is False


def test_no_authority_memory_or_verification():
    _, _, _, rj = _join("Marie a vu que Paul a lancé P.")
    md = rj.metadata
    assert (md["MEMORY_WRITE"], md["AUTHORIZED_FLOW_CREATED"], md["EXECUTED_FLOW_CREATED"],
            md["VERIFIED_FLOW_CREATED"], md["KX108_CALLED"]) == (0, 0, 0, 0, 0)
    assert not any(r["status"] in {"VERIFIED", "SUPPORTED"} for r in rj.readings)


_SUBJ = ["Paul", "Marie dit que Paul", "Marie croit que Paul", "Il paraît que Paul", "Selon Marie, Paul"]
_BODY = ["a lancé P et Nadia a exécuté Q", "a lancé P ou Nadia a exécuté Q", "lance P puis exécute Q",
         "doit lancer P et exécuter Q", "va lancer P", "n'a pas lancé P parce que Nadia a arrêté Q"]


def test_readings_are_exactly_the_sources_adversarial():
    """Independent recount: every reading has a source and every source a reading; nothing merged."""
    checked = 0
    for s, b in itertools.product(_SUBJ, _BODY):
        f = parse_utterance(f"{s} {b}.")
        idx = build_frame_event_index(f)
        for cand in idx.events():
            rj = build_review_join_v1(f, cand.event_ref.event_id, idx)
            members = {e["predicate_ref"] for e in rj.envelope.events}
            by = lambda d: [r for r in rj.readings if r["dimension"] == d]
            assert len(by("occurrence")) == len(members)
            assert len(by("epistemic")) == sum(c["predicate_ref"] in members for c in rj.envelope.epistemic_contributions)
            utt = [x for x in project_temporal_flows(f) if x.relation_type == "UTTERANCE_TIME" and x.source_object in members]
            assert len([r for r in by("temporal") if r["perspective"] == "utterance_time"]) == len(utt)
            want_coord = sum(m in members for c in f.coordinations for m in c.members)
            assert len(by("coordination")) == want_coord
            causal_ends = sum(e in members for x in project_causal_flows(f)
                              for e in (*f.relation_members(x.source_object), x.target_object))
            assert len(by("causal")) == causal_ends
            assert all(r["predicate_ref"] in members for r in rj.readings)
            assert rj.metadata["truth"] is None and rj.metadata["winner"] is None
            checked += 1
    assert checked > 50
    assert set(READING_DIMENSIONS) >= {"occurrence", "epistemic", "temporal", "causal"}

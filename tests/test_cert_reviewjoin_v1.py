"""Certification (block 25): ReviewJoin V1 joins without collapsing, resolves nothing.

Adversarial cases A-J: every perspective kept with its native status and provenance; no
winner, no truth, no fusion, no promotion, no memory, no authority; exception and purpose
never read as causal; argument coordinations keep AND / OR; a foreign center fails closed.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.review_join_v1 import build_review_join_v1


def _joins(text):
    f = parse_utterance(text)
    idx = build_frame_event_index(f)
    return f, {e.predicate_ref: build_review_join_v1(f, e.event_ref.event_id, idx) for e in idx.events()}


def _by(join, pred, dim):
    return [r for r in join.readings if r["predicate_ref"] == pred and r["dimension"] == dim]


def _safe(join):
    m = join.metadata
    assert (m["truth"], m["winner"], m["fusion"], m["conflict_resolution"], m["consensus"]) == (None, None, "none", "none", "none")
    assert (m["MEMORY_WRITE"], m["KX108_CALLED"], m["AUTHORIZED_FLOW_CREATED"], m["EXECUTED_FLOW_CREATED"],
            m["VERIFIED_FLOW_CREATED"]) == (0, 0, 0, 0, 0)
    for r in join.readings:
        assert r["provenance"].get("source") and str(r["status"]) not in {"TRUE", "FALSE", "ESTABLISHED", "OBSERVED"}


def test_a_compatible_projections_all_kept():
    _, j = _joins("Peux-tu lancer P et exécuter Q ?")
    for pred in ("u1", "u2"):
        dims = {r["dimension"] for r in j[pred].readings if r["predicate_ref"] == pred}
        assert {"occurrence", "temporal", "coordination", "operator", "ambiguity"} <= dims
        _safe(j[pred])


def test_b_contradictory_occurrences_visible_no_winner():
    f, j = _joins("Paul a lancé P et n'a pas lancé P.")
    assert [r["status"] for r in _by(j["u1"], "u1", "occurrence")] == ["ASSERTED_REALIZED"]
    assert [r["status"] for r in _by(j["u2"], "u2", "occurrence")] == ["ASSERTED_NOT_REALIZED"]
    for pred in ("u1", "u2"):
        assert [r["status"] for r in _by(j[pred], pred, "ambiguity")] == ["occurrence_conflict_open:u1:u2"]
        _safe(j[pred])
    assert not f.closure


def test_c_unknown_kept_beside_asserted_perspective():
    _, j = _joins("Marie dit que Paul a lancé P.")
    reported = j["u2"]
    assert [r["status"] for r in _by(reported, "u2", "occurrence")] == ["NO_ASSERTION"]   # never promoted
    assert {r["status"] for r in _by(reported, "u2", "epistemic")} == {"REPORTED", "REPORTS_ABOUT"}
    _safe(reported)


def test_d_temporal_and_causal_stay_distinct():
    _, j = _joins("Paul a lancé R parce que Marie a lancé P.")
    assert [r["status"] for r in _by(j["u1"], "u1", "causal")] == ["CAUSES:target"]
    assert all(":" not in str(r["status"]) for r in _by(j["u1"], "u1", "temporal"))


@pytest.mark.parametrize("text,dim,host_status", [("Paul lance R sauf si Marie lance P.", "exception", "EXCEPTS:target"),
                                                  ("Paul lance P pour tester Q.", "purpose", "PURPOSE:host")])
def test_e_f_exception_and_purpose_never_causal(text, dim, host_status):
    _, j = _joins(text)
    for pred, join in j.items():
        assert not [r for r in join.readings if r["dimension"] == "causal"]
        _safe(join)
    assert [r["status"] for r in _by(j["u1"], "u1", dim)] == [host_status]


def test_g_source_identity_preserved():
    _, j = _joins("Marie dit que Paul a lancé P.")
    sources = {(r["provenance"]["source"], str(r["perspective"])) for r in _by(j["u2"], "u2", "epistemic")}
    assert {s for s, _ in sources} == {"epistemic_flow", "event_relation"}
    assert all(p.startswith("event:") for _, p in sources)


def test_h_argument_coordination_kinds_kept():
    _, j = _joins("Paul et Nadia lancent P ou Q.")
    got = sorted((r["status"], tuple(r["provenance"]["member_texts"])) for r in _by(j["u1"], "u1", "coordination"))
    assert got == [("AND:coordinated_subject", ("paul", "nadia")), ("OR:coordinated_object", ("p", "q"))]


def test_i_open_content_kept_as_ambiguity():
    _, j = _joins("Paul permet à Marie de lancer P.")
    assert [r["status"] for r in _by(j["u1"], "u1", "ambiguity")] == ["infinitive_under_unrecognized_governor:u1"]
    assert not [r for r in j["u1"].readings if r["dimension"] in {"causal", "operator"}]
    _safe(j["u1"])


def test_j_foreign_center_fails_closed():
    f = parse_utterance("Paul lance P.")
    with pytest.raises(ValueError):
        build_review_join_v1(f, "event:not-in-this-frame")

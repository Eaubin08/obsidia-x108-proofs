"""Contracts of the non-sovereign cognitive lattice primitives."""
from __future__ import annotations

import dataclasses
import pathlib

import pytest

from app.semantic.lattice import (
    BOUNDARY, ConnectionKind, LatticeRelation, PredicateUnit, ProjectionAxis,
    UtteranceFrame, connection, parse_utterance, project, projections_of,
)
from app.semantic.lattice.ud_adapter import (
    UDToken, disagreements, fail_closed_requested_world_actions, frame_from_ud,
)

LATTICE_DIR = pathlib.Path(__file__).resolve().parents[1] / "app" / "semantic" / "lattice"


def test_frame_is_immutable_and_non_sovereign():
    frame = parse_utterance("prépare le script mais ne l'exécute pas")
    with pytest.raises(dataclasses.FrozenInstanceError):
        frame.raw = "x"  # type: ignore[misc]
    with pytest.raises(dataclasses.FrozenInstanceError):
        frame.units[0].polarity = "negative"  # type: ignore[misc]
    assert frame.boundary == BOUNDARY
    assert frame.boundary["decision_authority"] == "KX108_ONLY"
    assert frame.boundary["emits_act"] is False
    assert frame.boundary["memory_write"] is False


def test_lattice_has_no_io_network_or_authority_imports():
    forbidden = ("subprocess", "socket", "requests", "urllib", "httpx", "app.router",
                 "app.gates", "app.adapters", "open(", "stanza")
    for path in LATTICE_DIR.glob("*.py"):
        source = path.read_text(encoding="utf-8")
        code = "\n".join(line for line in source.splitlines()
                         if not line.lstrip().startswith("#"))
        for token in forbidden:
            assert f"import {token}" not in code and f"from {token}" not in code, (path, token)
        assert "open(" not in code, path


def test_raw_is_preserved_and_spans_point_into_raw():
    raw = "Prépare   le Script, mais NE l’exécute PAS !"
    frame = parse_utterance(raw)
    assert frame.raw == raw
    surfaces = {u.predicate: raw[u.span[0]:u.span[1]] for u in frame.units}
    assert surfaces == {"PREPARE": "Prépare", "EXECUTE": "exécute"}


def test_parsing_is_deterministic():
    text = "on m'a dit qu'il avait lancé le script, puis prépare le rapport"
    assert parse_utterance(text) == parse_utterance(text)


def test_one_object_many_projections_are_views_not_copies():
    frame = parse_utterance("on m'a dit qu'il avait lancé le script")
    execute = next(u for u in frame.units if u.predicate == "EXECUTE")
    views = projections_of(frame, execute.id)
    assert set(views) == {a.value for a in ProjectionAxis}
    assert views["SEMANTIC"]["predicate"] == "EXECUTE"
    assert views["GRAMMATICAL"]["verb_form"] == "PARTICIPLE"
    assert views["TEMPORAL"]["tense_aspect"] == "PLUPERFECT"
    assert views["EPISTEMIC"]["epistemic"] == "HEARSAY"
    assert views["PRAGMATIC"]["pragmatic"] == "REPORTED"
    assert views["PROVENANCE"]["raw_surface"] == "lancé"
    assert views["PROVENANCE"]["reported_by"]  # known BY the SAY unit
    assert views["AUTHORITY"] == {"authority": None, "decision_authority": "KX108_ONLY",
                                  "emits_act": False, "requires_gate": False}
    # every axis answers for every unit
    for axis in ProjectionAxis:
        assert set(project(frame, axis)) == {u.id for u in frame.units}


def test_requested_world_action_projects_gate_requirement():
    frame = parse_utterance("prépare le script puis lance les tests")
    auth = project(frame, ProjectionAxis.AUTHORITY)
    by_pred = {u.predicate: auth[u.id]["requires_gate"] for u in frame.units}
    assert by_pred == {"PREPARE": False, "EXECUTE": True}


def test_connection_kinds_from_language():
    seq = parse_utterance("prépare le script puis lance les tests puis pousse le code")
    u1, u2, u3 = (u.id for u in seq.units)
    assert connection(seq, u1, u2).kind is ConnectionKind.TEMPORAL_RELATION
    indirect = connection(seq, u1, u3)
    assert indirect.kind is ConnectionKind.INDIRECT_PATH
    assert indirect.path == (u1, u2, u3)

    contrast = parse_utterance("prépare le script mais ne l'exécute pas")
    a, b = (u.id for u in contrast.units)
    assert connection(contrast, a, b).kind is ConnectionKind.DIRECT_RELATION

    report = parse_utterance("on m'a dit qu'il avait lancé le script")
    a, b = (u.id for u in report.units)
    assert connection(report, a, b).kind is ConnectionKind.PROVENANCE_RELATION

    same = parse_utterance("lance les tests, lance le script")
    a, b = (u.id for u in same.units)
    assert connection(same, a, b).kind is ConnectionKind.SEMANTIC_SIMILARITY

    none = parse_utterance("prépare le script, supprime les logs")
    a, b = (u.id for u in none.units)
    assert connection(none, a, b).kind is ConnectionKind.NO_PROVEN_CONNECTION


def _unit(uid, pred):
    return PredicateUnit(id=uid, predicate=pred, lemma=pred.lower(), surface=pred.lower(),
                         span=(0, 0), clause=0, predicate_class="other", verb_form="FINITE")


def test_connection_shared_cause_and_shared_ancestor():
    units = tuple(_unit(i, p) for i, p in (("c", "CHANGE"), ("a", "EXECUTE"),
                                            ("b", "PUSH"), ("s", "SAY")))
    frame = UtteranceFrame(raw="", normalized="", units=units, relations=(
        LatticeRelation("CAUSES", "c", "a"), LatticeRelation("CAUSES", "c", "b")))
    assert connection(frame, "a", "b").kind is ConnectionKind.SHARED_CAUSE
    frame = UtteranceFrame(raw="", normalized="", units=units, relations=(
        LatticeRelation("REPORTS", "s", "a"), LatticeRelation("REPORTS", "s", "b")))
    assert connection(frame, "a", "b").kind is ConnectionKind.SHARED_ANCESTOR


def test_closure_semantics():
    assert parse_utterance("fais le").closure is False
    assert parse_utterance("prépare le script et exécute-le").closure is True
    # evidence need does not block meaning closure
    frame = parse_utterance("maman est là ?")
    assert frame.closure is True and frame.evidence_needs


# ── UD adapter boundary (no parser dependency) ───────────────────────────
def _ud_prepare_no_execute():
    # "prépare le script mais ne l'exécute pas" in UD (hand-built)
    return [
        UDToken(1, "prépare", "préparer", "VERB", 0, "root", {"Mood": "Imp"}, 0, 7),
        UDToken(2, "le", "le", "DET", 3, "det"),
        UDToken(3, "script", "script", "NOUN", 1, "obj"),
        UDToken(4, "mais", "mais", "CCONJ", 7, "cc"),
        UDToken(5, "ne", "ne", "ADV", 7, "advmod", {"Polarity": "Neg"}),
        UDToken(6, "l'", "le", "PRON", 7, "obj", {"PronType": "Prs"}),
        UDToken(7, "exécute", "exécuter", "VERB", 1, "conj", {"Mood": "Imp"}, 28, 35),
        UDToken(8, "pas", "pas", "ADV", 7, "advmod", {"Polarity": "Neg"}),
    ]


def test_ud_adapter_maps_negation_and_imperative():
    raw = "prépare le script mais ne l'exécute pas"
    ext = frame_from_ud(raw, _ud_prepare_no_execute())
    by_pred = {u.predicate: u for u in ext.units}
    assert by_pred["PREPARE"].pragmatic == "REQUESTED"
    assert by_pred["EXECUTE"].polarity == "negative"
    assert by_pred["EXECUTE"].pragmatic == "FORBIDDEN"
    assert by_pred["EXECUTE"].provenance == "external_ud"
    assert disagreements(parse_utterance(raw), ext) == []


def test_ud_fusion_is_fail_closed():
    raw = "prépare le script mais ne l'exécute pas"
    builtin = parse_utterance(raw)
    # An external parser that (wrongly) misses the negation must win caution.
    tokens = [t for t in _ud_prepare_no_execute() if t.lemma not in {"ne", "pas"}]
    ext = frame_from_ud(raw, tokens)
    assert "EXECUTE" not in fail_closed_requested_world_actions(builtin)
    assert "EXECUTE" in fail_closed_requested_world_actions(builtin, ext)
    assert disagreements(builtin, ext)

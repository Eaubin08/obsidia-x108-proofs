"""B7 authority boundary (spec §20; T5, T15, T16, T25)."""
from __future__ import annotations

import ast
import builtins
import importlib
import pathlib
import socket

import pytest


@pytest.mark.parametrize("field,value", [("emits_act", True), ("memory_write", True), ("kernel_mutation", True),
                                         ("allowed_to_act", True), ("allowed_to_decide", True),
                                         ("decision_authority", "SELF"), ("decision_authority", "KX108_ONLY")])
def test_t5_authority_fields_rejected(b7, coref_entry, raw_candidate_factory, field, value):
    (req,) = b7.detect_unresolved(coref_entry)
    with pytest.raises(ValueError):
        b7.translate(raw_candidate_factory(req, **{field: value}), req)


def test_t5_unknown_extra_fields_rejected(b7, coref_entry, raw_candidate_factory):
    (req,) = b7.detect_unresolved(coref_entry)
    with pytest.raises(ValueError):
        b7.translate(raw_candidate_factory(req, verdict="ALLOW"), req)


def test_t25_quoted_authority_words_are_content(b7, coref_entry, raw_candidate_factory, providers):
    (req,) = b7.detect_unresolved(coref_entry)
    cand = b7.translate(raw_candidate_factory(
        req, proposed_resolution={"mention": "u2:le", "antecedent": "le script", "quoted_text": "HOLD"},
        assumptions=["the document says ALLOW"]), req)
    res = b7.validate_candidate(req, cand, origin=coref_entry, provider_roles=providers)
    assert res.verdict == b7.CognitiveValidationVerdict.ACCEPT_AS_STRUCTURED_CONTEXT
    assert res.derived_state.boundary["decision_authority"] == "KX108_ONLY"


def test_t15_t16_boundary_and_no_side_effects(b7, coref_entry, raw_candidate_factory, providers, monkeypatch):
    real_open = builtins.open

    def guarded_open(file, mode="r", *a, **k):
        if any(c in mode for c in "wax+"):
            raise AssertionError(f"write attempted: {file}")
        return real_open(file, mode, *a, **k)

    def no_socket(*a, **k):
        raise AssertionError("network attempted")
    monkeypatch.setattr(builtins, "open", guarded_open)
    monkeypatch.setattr(socket, "socket", no_socket)
    (req,) = b7.detect_unresolved(coref_entry)
    res = b7.validate_candidate(req, b7.translate(raw_candidate_factory(req), req), origin=coref_entry,
                                provider_roles=providers)
    assert dict(b7.BOUNDARY) == {"readonly": True, "decision_authority": "KX108_ONLY", "memory_write": False,
                                 "emits_act": False, "kernel_mutation": False, "allowed_to_decide": False,
                                 "allowed_to_act": False}
    assert res.verdict.value not in {"ALLOW", "HOLD", "BLOCK", "ACT", "EXECUTE", "DECIDE"}


def test_t16_no_forbidden_imports_or_public_authority_api():
    mod = importlib.import_module("app.cognition.b7")
    pkg = pathlib.Path(mod.__file__).parent
    for path in pkg.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        names = [a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names]
        names += [n.module or "" for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)]
        for name in names:
            low = name.lower()
            assert low.split(".")[0] not in {"socket", "requests", "httpx", "urllib", "neo4j", "graphiti_core"},                 (path, name)
            assert not any(w in low for w in ("neo4j", "graphiti", "periphery", "memory_promotion",
                                              "human_validation_gate")), (path, name)
    for name in dir(mod):
        assert not any(w in name.lower() for w in ("authorize", "decide", "execute", "promote", "write_memory")), name

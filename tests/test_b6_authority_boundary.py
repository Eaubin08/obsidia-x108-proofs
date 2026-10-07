"""B6 authority boundary: no decision, no ACT, no write, no network, no Neo4j / Graphiti."""
from __future__ import annotations

import ast
import builtins
import inspect
import pathlib
import socket

import pytest

import app.harness.state_explicit as pkg
from app.harness.state_explicit.context_assembly import assemble_context
from app.harness.state_explicit.registry import WorkingStateRegistry
from app.harness.state_explicit.sens_adapter import sens_state_entries

_PKG = pathlib.Path(pkg.__file__).parent
_MATRIX = {"categories": ["PURE_RESPONSE"], "matrix": {"PURE_RESPONSE": {"brody_may": ["repondre"]}}}


def test_no_forbidden_imports():
    for path in _PKG.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        names = [a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names]
        names += [n.module or "" for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)]
        for name in names:
            low = name.lower()
            assert "neo4j" not in low and "graphiti" not in low and "periphery" not in low, (path, name)
            assert not low.startswith(("socket", "requests", "httpx", "urllib")), (path, name)


def test_no_public_decision_or_action_api():
    for mod in pkg.__all__:
        obj = getattr(pkg, mod)
        if inspect.isfunction(obj) or inspect.isclass(obj):
            assert not any(w in mod.lower() for w in ("authorize", "decide", "act_", "execute", "write")), mod


def test_full_flow_opens_no_socket_and_writes_no_file(monkeypatch):
    def no_socket(*a, **k):
        raise AssertionError("network attempted")

    real_open = builtins.open

    def guarded_open(file, mode="r", *a, **k):
        if any(c in mode for c in "wax+"):
            raise AssertionError(f"write attempted: {file}")
        return real_open(file, mode, *a, **k)
    monkeypatch.setattr(socket, "socket", no_socket)
    monkeypatch.setattr(builtins, "open", guarded_open)
    r = WorkingStateRegistry()
    for e in sens_state_entries("Lance P et exécute Q."):
        r.register(e)
    p = assemble_context("Lance P et exécute Q.", r, capability_matrix=_MATRIX).to_dict()
    assert p["boundary"]["allowed_to_act"] is False and p["boundary"]["memory_write"] is False


def test_requested_action_is_described_never_authorized():
    r = WorkingStateRegistry()
    for e in sens_state_entries("Lance P."):
        r.register(e)
    p = assemble_context("Lance P.", r, capability_matrix=_MATRIX).to_dict()
    frame = r.get("sens:frame").payload
    assert frame["requested_world_actions"] == ["EXECUTE"] and frame["requested_is_authorized"] is False
    assert not ({"ALLOW", "HOLD", "BLOCK", "ACT"} & {str(v) for v in p["boundary"].values()})
    assert p["boundary"]["decision_authority"] == "KX108_ONLY"


@pytest.mark.parametrize("payload_word", ["ACT", "HOLD", "BLOCK"])
def test_source_content_words_are_not_authority(payload_word):
    r = WorkingStateRegistry()
    for e in sens_state_entries(f"Paul écrit {payload_word}."):
        r.register(e)
    p = assemble_context("x", r, capability_matrix=_MATRIX).to_dict()
    assert p["boundary"]["emits_act"] is False and p["boundary"]["allowed_to_decide"] is False

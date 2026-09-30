"""R3b: the router boundary uses the configured router and never mutates import state.

router_decide() is reached from long-lived processes (MCP server, gateway,
cognitive ingress). It prepended OBSIDIA_ROUTER_ROOT to sys.path for good and
imported "app.router.decision" under the generic top-level name "app": with
this repository's own "app" already imported, the import silently resolved
to the local package instead of the configured router, and the router root
stayed in sys.path. The router must be imported and called with its root
and its own "app" namespace in scope only; sys.path and every "app" /
"app.*" module are restored exactly on every path (ok, import failure, router
exception, malformed decision), and no foreign "app" module survives.
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest

import app.semantic.lattice.french_grammar  # noqa: F401  (this repository's "app" is loaded)

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
for _p in (str(_REPO_ROOT / "scripts"), str(_REPO_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import obsidia_gateway_route_decision_v0 as RD  # noqa: E402

_OK = ("def decide(raw, memory_index=None):\n"
       "    import app.router.decision as me  # lazy import at call time, same namespace\n"
       "    return {'route': ROUTE, 'ir': {}, 'gate': {}, 'origin': me.__file__}\n")


def _router(root: Path, body: str, route: str = "FAKE_ROUTER") -> Path:
    (root / "app" / "router").mkdir(parents=True)
    (root / "app" / "__init__.py").write_text("", encoding="utf-8")
    (root / "app" / "router" / "__init__.py").write_text("", encoding="utf-8")
    (root / "app" / "router" / "decision.py").write_text(f"ROUTE = {route!r}\n" + body, encoding="utf-8")
    return root


def _snapshot():
    return list(sys.path), {n: m for n, m in sys.modules.items() if n == "app" or n.startswith("app.")}


def _assert_restored(saved, root: Path):
    path, mods = saved
    assert sys.path == path, "sys.path not restored exactly"
    now = {n: m for n, m in sys.modules.items() if n == "app" or n.startswith("app.")}
    assert now.keys() == mods.keys() and all(now[n] is mods[n] for n in mods), "app modules not restored exactly"
    assert not [n for n, m in now.items() if getattr(m, "__file__", None)
                and Path(m.__file__).resolve().is_relative_to(root.resolve())], "foreign app module left"


def test_configured_router_is_used_and_import_state_is_restored(tmp_path, monkeypatch):
    root = _router(tmp_path / "router", _OK)
    monkeypatch.setenv("OBSIDIA_ROUTER_ROOT", str(root))
    saved = _snapshot()
    decision, status = RD.router_decide("bonjour")
    assert status == RD.ROUTER_OK
    assert decision["route"] == "FAKE_ROUTER"
    assert Path(decision["origin"]).resolve().is_relative_to(root.resolve())
    _assert_restored(saved, root)


@pytest.mark.parametrize("body,status", [
    ("raise ImportError('broken router')\n", "ROUTER_UNAVAILABLE"),
    ("def decide(raw, memory_index=None):\n    raise RuntimeError('boom')\n", "ROUTER_EXCEPTION"),
    ("def decide(raw, memory_index=None):\n    return {'route': ''}\n", "MALFORMED_ROUTER_DECISION"),
])
def test_failure_paths_keep_their_status_and_restore_import_state(tmp_path, monkeypatch, body, status):
    root = _router(tmp_path / "router", body)
    monkeypatch.setenv("OBSIDIA_ROUTER_ROOT", str(root))
    saved = _snapshot()
    decision, got = RD.router_decide("bonjour")
    assert (decision, got) == (None, getattr(RD, status))
    _assert_restored(saved, root)


def test_absent_router_touches_nothing(tmp_path, monkeypatch):
    monkeypatch.setenv("OBSIDIA_ROUTER_ROOT", str(tmp_path / "absent"))
    saved = _snapshot()
    assert RD.router_decide("bonjour") == (None, RD.ROUTER_UNAVAILABLE)
    _assert_restored(saved, tmp_path / "absent")


def test_long_lived_process_sequence(tmp_path, monkeypatch):
    a = _router(tmp_path / "router_a", _OK, route="ROUTER_A")
    b = _router(tmp_path / "router_b", _OK, route="ROUTER_B")
    fg = sys.modules["app.semantic.lattice.french_grammar"]
    saved = _snapshot()
    for root, route in ((a, "ROUTER_A"), (b, "ROUTER_B"), (a, "ROUTER_A")):
        monkeypatch.setenv("OBSIDIA_ROUTER_ROOT", str(root))
        decision, status = RD.router_decide("bonjour")
        assert (status, decision["route"]) == (RD.ROUTER_OK, route)       # the configured router, never stale
        assert Path(decision["origin"]).resolve().is_relative_to(root.resolve())
        importlib.import_module("app.semantic.lattice.event_extraction")  # real app.semantic importable
        assert sys.modules["app.semantic.lattice.french_grammar"] is fg   # no identity corruption
        assert sys.path == saved[0]                                       # no accumulating roots

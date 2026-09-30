"""CLI tests: never leak import state into the rest of the suite (R3a).

Several CLI tests install a fake router package ("app/router" under
tmp_path), point OBSIDIA_ROUTER_ROOT at it and purge "app" / "app.*" from
sys.modules to force a reload; the router boundary then prepends that tmp
root to sys.path. Left as is, a later lazy "from app.semantic..." in another
test re-imports "app" from the fake package (ModuleNotFoundError), and the
real app.semantic modules are re-imported as new objects. Each CLI test
therefore runs between an exact snapshot and restoration of sys.path and of
every "app" / "app.*" entry of sys.modules.
"""
from __future__ import annotations

import sys

import pytest


def _app_modules() -> dict:
    return {name: mod for name, mod in sys.modules.items() if name == "app" or name.startswith("app.")}


@pytest.fixture(autouse=True)
def _restore_import_state():
    saved_path = list(sys.path)
    saved_modules = _app_modules()
    yield
    sys.path[:] = saved_path
    for name in list(_app_modules()):
        if name not in saved_modules:
            del sys.modules[name]
    sys.modules.update(saved_modules)

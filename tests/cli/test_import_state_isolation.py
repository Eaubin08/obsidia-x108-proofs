"""R3a: a CLI test never leaks import state into the rest of the suite.

The cognitive-ingress tests install a fake router package ("app/router" in
tmp_path), point OBSIDIA_ROUTER_ROOT at it and purge every "app" / "app.*"
module (_clean_import_cache), including the real app.semantic. Run in one
process with the semantic tests, the fake tmp roots stayed at the head of
sys.path and "app" was re-imported from a fake package: a later lazy
"from app.semantic..." raised ModuleNotFoundError, and even without that the
real app.semantic modules were re-imported as new objects.

These checks run the polluting test file between two probes in a fresh
pytest subprocess: after it, no fake router root may remain in sys.path, the
real "app" must still be the imported one, app.semantic must import, and the
app.semantic module objects must be the very same as before.
"""
from __future__ import annotations

import os
import subprocess
import sys
import textwrap
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]

_PROBE_A = textwrap.dedent('''
    import builtins, sys
    import app.semantic.lattice.french_grammar as fg

    def test_probe_before():
        builtins._r3_fg_id = id(sys.modules["app.semantic.lattice.french_grammar"])
        builtins._r3_path = list(sys.path)
''')

_PROBE_Z = textwrap.dedent('''
    import builtins, importlib, sys
    from pathlib import Path

    def test_probe_after():
        app = sys.modules.get("app")
        assert app is not None and Path(app.__file__).resolve().parent == Path(r"{repo}", "app").resolve(), app
        assert not [p for p in sys.path if p not in builtins._r3_path], "leaked sys.path entries"
        importlib.import_module("app.semantic.lattice.event_extraction")
        assert id(sys.modules["app.semantic.lattice.french_grammar"]) == builtins._r3_fg_id
''')


def test_cli_fake_router_tests_leave_no_import_state(tmp_path):
    a = tmp_path / "test_r3_probe_a.py"
    z = tmp_path / "test_r3_probe_z.py"
    a.write_text(_PROBE_A, encoding="utf-8")
    z.write_text(_PROBE_Z.replace("{repo}", str(_REPO)), encoding="utf-8")
    env = dict(os.environ, PYTHONPATH=str(_REPO), PYTHONIOENCODING="utf-8")
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--color=no",
         "--rootdir", str(_REPO), "-c", str(_REPO / "pytest.ini"),
         str(a), str(_REPO / "tests" / "cli" / "test_obsidia_cognitive_ingress_v0.py"), str(z)],
        cwd=str(_REPO), env=env, capture_output=True, text=True, timeout=600,
    )
    assert proc.returncode == 0, proc.stdout[-3000:] + proc.stderr[-2000:]

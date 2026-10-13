"""M33 RED — foundation boundary and runtime location (spec §5, §33, §34; R24)."""
from __future__ import annotations

import importlib
import subprocess
import sys

from tests.m33 import _harness as H


def test_runtime_location_outside_seal():
    paths = H.M32H.protected_paths()
    assert not any(p == "app/reconstruction" or p.startswith("app/reconstruction/") for p in paths)
    assert not (H.REPO / "app" / "cognition" / "m33").exists()


def test_runtime_package_present():
    H.require_runtime_dir()
    importlib.import_module(H.RUNTIME_MODULE)


def test_protected_paths_unchanged_since_m33_spec_base():
    assert H.protected_diff_since_m33_base() == []


def test_m33_not_reexported_through_sealed_init():
    for init in ("app/cognition/__init__.py", "app/knowledge/b8/__init__.py", "app/primitives/m32/__init__.py"):
        f = H.REPO / init
        if f.exists():
            assert "reconstruction" not in f.read_text(encoding="utf-8")


def test_foundation_sentinel_passes_with_m33_present():
    H.require_runtime_dir()
    proc = subprocess.run([sys.executable, "scripts/foundation_sentinel.py"], cwd=H.REPO, capture_output=True, text=True)
    assert proc.returncode == 0 and "All canonical foundation suites passed." in proc.stdout


def test_m32_does_not_register_m33_primitives():
    H.require_runtime_dir()
    text = "\n".join(f.read_text(encoding="utf-8") for f in H.M33_RUNTIME_DIR.rglob("*.py"))
    assert "register_type_spec" not in text and "register_implementation" not in text  # A13

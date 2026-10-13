"""M32 RED — sealed-foundation oracles (spec §14, §35, §36 R7(c)/R15/R16/R17).

Protected paths come from the foundation seal §4 + sentinel targets (never a duplicated M32 list).
Hardened per the final independent audit: the protected diff is ``git diff M32_BASE..HEAD`` over ALL
commits, not only commits touching M32 paths.
"""
from __future__ import annotations

import importlib
import subprocess
import sys

import pytest

from tests.m32 import _harness as H


def _runtime_package_present():
    assert H.M32_RUNTIME_DIR.is_dir(), "app/primitives/m32/ does not exist yet (RED)"
    importlib.import_module(H.RUNTIME_MODULE)


# Location (§14): allowed outside the seal; forbidden under app/cognition/.
def test_location_runtime_lives_in_app_primitives_m32():
    _runtime_package_present()


def test_location_forbidden_under_app_cognition():
    assert not H.FORBIDDEN_RUNTIME_DIR.exists()
    assert not any(p.startswith("app/primitives") for p in H.protected_paths())


def test_m32_not_reexported_through_sealed_init():
    for init in ("app/cognition/__init__.py", "app/knowledge/b8/__init__.py"):
        f = H.REPO / init
        if f.exists():
            assert "primitives" not in f.read_text(encoding="utf-8")


# Protected-path diff since certified M32_BASE (all commits).
def test_protected_path_diff_since_m32_base_is_zero():
    assert H.protected_diff_since_base() == []


def _sealed_oracle(layer):
    layer_dir, tests_dir, prefixes = H.SEALED_LAYERS[layer]
    _runtime_package_present()
    assert H.protected_diff_since_base() == []
    rc = subprocess.run([sys.executable, "-m", "pytest", tests_dir, "-q", "-p", "no:cacheprovider"],
                        cwd=H.REPO, capture_output=True, text=True).returncode
    assert rc == 0, f"{tests_dir} regression failed"
    assert H.sealed_attribute_assignments(H.M32_RUNTIME_DIR, prefixes) == []
    collisions = H.m32_defined_names() & H.public_names(layer_dir)
    assert collisions == set(), f"competing public names vs {layer}: {sorted(collisions)}"


# R7(c) — B8 sealed oracle.
def test_r7c_b8_sealed_oracle():
    _sealed_oracle("B8")


# R15 — B7 role semantics unchanged.
def test_r15_b7_sealed_oracle():
    _sealed_oracle("B7")


# R16 — B9 path semantics unchanged.
def test_r16_b9_sealed_oracle():
    _sealed_oracle("B9")


# R17 — foundation sentinel remains PASS (with the M32 runtime present).
def test_r17_foundation_sentinel_passes_with_m32_present():
    _runtime_package_present()
    proc = subprocess.run([sys.executable, "scripts/foundation_sentinel.py"], cwd=H.REPO,
                          capture_output=True, text=True)
    assert proc.returncode == 0
    assert "All canonical foundation suites passed." in proc.stdout


# Oracle non-vacuity: the competing-name and attribute-assignment detectors fire on hostile fixtures.
def test_competing_name_detector_fires_on_hostile_fixture(tmp_path):
    (tmp_path / "evil.py").write_text("class CognitivePath:\n    pass\n", encoding="utf-8")
    assert "CognitivePath" in H.m32_defined_names(tmp_path) & H.public_names("app/cognition/b9")


def test_import_only_is_not_redefinition(tmp_path):
    (tmp_path / "ok.py").write_text("from app.cognition.b9.contracts import CognitivePath\n", encoding="utf-8")
    assert H.m32_defined_names(tmp_path) & H.public_names("app/cognition/b9") == set()
    assert H.sealed_attribute_assignments(tmp_path, ("app.cognition.b9",)) == []


def test_attribute_assignment_detector_fires(tmp_path):
    (tmp_path / "patch.py").write_text(
        "import app.cognition.b7.router as r\nr.route = None\n"
        "from app.cognition.b9 import contracts\nsetattr(contracts, 'X', 1)\n", encoding="utf-8")
    hits = H.sealed_attribute_assignments(tmp_path, ("app.cognition.b7", "app.cognition.b9"))
    assert len(hits) == 2


@pytest.mark.parametrize("layer", ["B7", "B8", "B9"])
def test_public_names_exclude_plain_imports(layer):
    names = H.public_names(H.SEALED_LAYERS[layer][0])
    assert names, f"{layer} public surface empty"
    assert not {"Enum", "dataclass", "Any"} & names

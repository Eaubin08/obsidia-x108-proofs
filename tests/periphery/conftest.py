# OBSIDIA_RECURSIVE_MANIFEST_TEST_FIXTURE_V1
#
# The production manifest is an explicit CI artifact and is intentionally
# not required to be committed to a pristine checkout.
#
# These three tests validate the real generator contract in an isolated
# temporary filesystem instead of depending on a stale repository artifact.

import subprocess as _manifest_subprocess
import sys as _manifest_sys
from pathlib import Path as _ManifestPath

import pytest as _manifest_pytest


_MANIFEST_TEST_MODULES = {
    "test_recursive_manifest_schema.py",
    "test_recursive_manifest_excludes_forbidden.py",
    "test_recursive_manifest_root_hash.py",
}


@_manifest_pytest.fixture(autouse=True)
def _recursive_manifest_generated_fixture(request, tmp_path, monkeypatch):
    """
    Materialize the real recursive-manifest artifacts only for the legacy
    V5A manifest tests.

    Writes are confined to pytest tmp_path.
    Production repository remains untouched.
    """
    filename = _ManifestPath(str(request.fspath)).name

    if filename not in _MANIFEST_TEST_MODULES:
        yield
        return

    repo_root = _ManifestPath(__file__).resolve().parents[2]

    generator = (
        repo_root
        / "scripts"
        / "generate_recursive_manifest.py"
    )

    assert generator.is_file(), (
        f"recursive manifest generator missing: {generator}"
    )

    # At least one legitimate entry is required by the schema contract.
    (tmp_path / "allowed.txt").write_text(
        "allowed\n",
        encoding="utf-8",
    )

    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "keep.py").write_text(
        "VALUE = 1\n",
        encoding="utf-8",
    )

    # Deliberately materialize forbidden surfaces.
    forbidden = {
        ".git": "git-internal",
        ".venv": "venv-internal",
        "node_modules": "node-internal",
        "__pycache__": "cache-internal",
    }

    for dirname, payload in forbidden.items():
        d = tmp_path / dirname
        d.mkdir()
        (d / "forbidden.txt").write_text(
            payload + "\n",
            encoding="utf-8",
        )

    (tmp_path / "forbidden.zip").write_bytes(
        b"not-a-real-zip-needed-for-exclusion-test"
    )

    proc = _manifest_subprocess.run(
        [
            _manifest_sys.executable,
            str(generator),
        ],
        cwd=str(tmp_path),
        stdout=_manifest_subprocess.PIPE,
        stderr=_manifest_subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30,
    )

    assert proc.returncode == 0, (
        "recursive manifest generation failed\n"
        f"stdout:\n{proc.stdout}\n"
        f"stderr:\n{proc.stderr}"
    )

    manifest = (
        tmp_path
        / "MANIFEST_SHA256_RECURSIVE.json"
    )

    root_hash = (
        tmp_path
        / "MANIFEST_SHA256_RECURSIVE_ROOT.txt"
    )

    assert manifest.is_file()
    assert root_hash.is_file()

    # Existing tests use relative paths by design.
    monkeypatch.chdir(tmp_path)

    yield

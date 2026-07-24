"""Root conftest.py — pytest collection configuration.

Excludes directories that must not be collected by the root test runner:
- freeze/     : archival snapshots; test files have duplicate basenames to tests/
- _EPHEMERAL_CODE_SANDBOX_* : ephemeral sandboxes, not part of the test suite

sys.path additions for sub-packages that need their own directory on the path:
- proofs/V18_3_1/engine_buildable_0_9_3_1/ : entrypoint.py lives here, not installed.

DECISION_AUTHORITY=KX108_ONLY. No IO. No network. No ACT.
"""
from __future__ import annotations
import sys
from pathlib import Path

collect_ignore_glob = [
    "freeze/*",
    "_EPHEMERAL_CODE_SANDBOX_*/*",
]

# entrypoint.py lives in engine_buildable_0_9_3_1/ and is not an installed package.
# Tests under that directory import it directly, so we add the directory to sys.path here
# rather than placing a conftest.py inside the sealed proofs/V18_3_1/ tree.
_engine_dir = str(Path(__file__).parent / "proofs" / "V18_3_1" / "engine_buildable_0_9_3_1")
if _engine_dir not in sys.path:
    sys.path.insert(0, _engine_dir)

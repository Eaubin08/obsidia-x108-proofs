"""M33 RED fixtures. Source of truth: docs/architecture/M33_ARM_RECONSTRUCTION_SPEC_V1.md at
M33_SPEC_BASE=20bffb2442fac0057318596af79784fef32551b9. Runtime target: ``app.reconstruction.m33``.

The ``m`` fixture is lazy: the runtime is imported on first attribute access inside a test body, so a
missing runtime makes each runtime-dependent test FAIL with "M33 runtime app/reconstruction/m33 is absent
(certified RED)" — no collection error, no skip, no fallback implementation.
"""
from __future__ import annotations

import pytest

from tests.m33 import _harness as H


class _LazyM33:
    def __getattr__(self, name):
        return getattr(H.rt(), name)


@pytest.fixture
def m():
    return _LazyM33()

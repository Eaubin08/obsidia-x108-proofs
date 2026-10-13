"""M32 RED contract — shared fixtures.

Source of truth: docs/architecture/M32_COMMON_COGNITIVE_PRIMITIVES_SPEC_V1.md (independently certified,
M32_BASE=faf72a25fb912a27b4be9a71d1b1a07f0e8fca79). Runtime target: ``app.primitives.m32``.

The ``m32`` fixture is a lazy handle: the module is imported on first attribute access inside the test
body, so until the runtime exists every runtime-dependent test FAILS with a clean ModuleNotFoundError
(no collection or fixture-setup error). Runtime-independent oracle tests still execute.
"""
from __future__ import annotations

import importlib

import pytest

from tests.m32 import _harness as H


class _LazyM32:
    def __getattr__(self, name):
        return getattr(importlib.import_module(H.RUNTIME_MODULE), name)


@pytest.fixture
def m32():
    return _LazyM32()

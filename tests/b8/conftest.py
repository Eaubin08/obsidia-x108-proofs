"""B8 deterministic core RED contract — shared fixtures.

Source: docs/architecture/B8_KNOWLEDGE_PROMOTION_SPEC_V1.md (CLOSED, certified at 99391f39, closure
ea6eb1da). Future runtime target: ``app.knowledge.b8`` (isolated: no app.cognition, no runtime authority).
The ``b8`` fixture is a lazy handle: the module is imported on first attribute access inside the test
body, so until the runtime exists every test FAILS with a clean ModuleNotFoundError (no collection or
fixture-setup error).
"""
from __future__ import annotations

import importlib
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SPEC = ROOT / "docs" / "architecture" / "B8_KNOWLEDGE_PROMOTION_SPEC_V1.md"
B8_PACKAGE_DIR = ROOT / "app" / "knowledge" / "b8"


class _LazyB8:
    def __getattr__(self, name):
        return getattr(importlib.import_module("app.knowledge.b8"), name)


@pytest.fixture
def b8():
    return _LazyB8()


@pytest.fixture(scope="session")
def spec_text():
    return SPEC.read_text(encoding="utf-8")


SLOT = "b8slot_" + "a" * 64
CLAIM = "b8claim_" + "b" * 64
RECORDED_AT = "2026-10-07T00:00:00Z"


def candidate_snapshot(b8, *, slot_revision=3, extra_records=()):
    """One claim at CANDIDATE (record_version 1) on SLOT, slot revision `slot_revision`."""
    record = b8.KnowledgeRecord(claim_id=CLAIM, claim_version=1, record_version=1,
                                state=b8.ClaimState.CANDIDATE, previous_record_id=None)
    return b8.SlotSnapshot(slot_id=SLOT, slot_revision=slot_revision,
                           records=(record, *extra_records), applied_requests={})


def hold_request(b8, **overrides):
    """T2 CANDIDATE → HELD: the simplest legal transition (needs only an explicit reason)."""
    fields = dict(claim_id=CLAIM, expected_claim_version=1, expected_state=b8.ClaimState.CANDIDATE,
                  expected_record_version=1, slot_id=SLOT, expected_slot_revision=3,
                  target_state=b8.ClaimState.HELD, refs=(), requester_ref="requester:test",
                  reason="awaiting evidence")
    fields.update(overrides)
    return b8.TransitionRequest(**fields)

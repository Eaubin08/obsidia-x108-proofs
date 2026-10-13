"""CSSA V0.2 adversarial checkpoint and crash-boundary tests."""
import json
from hashlib import sha256

import pytest

from periphery.cssa_checkpoint_guard_v02 import (
    fingerprint_cssa_checkpoint, resume_cssa_anchored,
)
from periphery.cssa_local_checkpoint_v02 import run_cssa_local_checkpoint


def delivery(n, subject="Question supporter"):
    return {
        "source": "synthetic", "source_id": str(n), "thread_id": "t",
        "message": {"message_id": str(n), "subject": subject,
                    "body": "Fictif", "sender": "nobody@invalid.example"},
        "attachments": [],
    }


def test_trusted_anchor_allows_valid_resume(tmp_path):
    path = tmp_path / "cssa.json"
    rows = [delivery(1), delivery(2)]
    run_cssa_local_checkpoint(rows, path)
    anchor = fingerprint_cssa_checkpoint(path)
    result = resume_cssa_anchored(rows, path, anchor)
    assert result["report"]["processed"] == 1


def test_recomputed_unkeyed_receipt_does_not_bypass_trusted_anchor(tmp_path):
    path = tmp_path / "cssa.json"
    rows = [delivery(1), delivery(2)]
    run_cssa_local_checkpoint(rows, path)
    anchor = fingerprint_cssa_checkpoint(path)
    modified = json.loads(path.read_text(encoding="utf-8"))
    modified["token"]["next_index"] = 2
    modified["receipt"] = sha256(json.dumps(
        modified["token"], sort_keys=True, ensure_ascii=False,
        separators=(",", ":"), allow_nan=False
    ).encode("utf-8")).hexdigest()
    path.write_text(json.dumps(modified), encoding="utf-8")
    with pytest.raises(ValueError, match="CSSA_CHECKPOINT_ANCHOR_MISMATCH"):
        resume_cssa_anchored(rows, path, anchor)


def test_missing_or_invalid_anchor_fails_closed(tmp_path):
    path = tmp_path / "cssa.json"
    run_cssa_local_checkpoint([delivery(1)], path)
    with pytest.raises(ValueError, match="CSSA_TRUSTED_ANCHOR_INVALID"):
        resume_cssa_anchored([delivery(1)], path, "not-a-sha")


def test_atomic_replace_failure_preserves_previous_checkpoint(tmp_path, monkeypatch):
    path = tmp_path / "cssa.json"
    rows = [delivery(1), delivery(2)]
    run_cssa_local_checkpoint(rows, path)
    before = path.read_bytes()

    def failing_replace(*_args, **_kwargs):
        raise OSError("injected replace failure")

    monkeypatch.setattr("periphery.cssa_local_checkpoint_v02.os.replace", failing_replace)
    with pytest.raises(OSError, match="injected replace failure"):
        run_cssa_local_checkpoint(rows, path, resume=True)
    assert path.read_bytes() == before
    assert list(tmp_path.glob(".cssa-checkpoint-*.tmp")) == []


def test_partial_failure_at_fsync_keeps_checkpoint(tmp_path, monkeypatch):
    path = tmp_path / "cssa.json"
    rows = [delivery(1), delivery(2)]
    run_cssa_local_checkpoint(rows, path)
    before = path.read_bytes()

    def failing_fsync(*_args):
        raise OSError("injected fsync failure")

    monkeypatch.setattr("periphery.cssa_local_checkpoint_v02.os.fsync", failing_fsync)
    with pytest.raises(OSError, match="injected fsync failure"):
        run_cssa_local_checkpoint(rows, path, resume=True)
    assert path.read_bytes() == before
    assert list(tmp_path.glob(".cssa-checkpoint-*.tmp")) == []


def test_changed_dataset_does_not_replace_checkpoint(tmp_path):
    path = tmp_path / "cssa.json"
    run_cssa_local_checkpoint([delivery(1), delivery(2)], path)
    before = path.read_bytes()
    with pytest.raises(ValueError, match="CSSA_CHECKPOINT_INVALID"):
        run_cssa_local_checkpoint([delivery(1), delivery(3)], path, resume=True)
    assert path.read_bytes() == before


def test_conflicting_delivery_blocks_checkpoint_on_initial_run(tmp_path):
    path = tmp_path / "cssa.json"
    result = run_cssa_local_checkpoint([
        delivery(1), delivery(1, "Newsletter du club")
    ], path)
    assert result["report"]["status"] == "BLOCK"
    assert not path.exists()

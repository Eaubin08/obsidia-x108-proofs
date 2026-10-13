"""CSSA V0.2 disk-only checkpoint tests; all paths use pytest tmp_path."""
import json

import pytest

from periphery.cssa_local_checkpoint_v02 import run_cssa_local_checkpoint


def delivery(n, subject="Question supporter"):
    return {
        "source": "fake-box", "source_id": str(n), "thread_id": "thread1",
        "message": {"message_id": str(n), "subject": subject,
                    "body": "Fictif", "sender": "nobody@invalid.example"},
        "attachments": [],
    }


def test_checkpoint_persists_then_resumes(tmp_path):
    path = tmp_path / "cssa.json"
    rows = [delivery(1), delivery(2), delivery(3)]
    first = run_cssa_local_checkpoint(rows, path, batch_size=1)
    assert first["report"]["processed"] == 1
    assert path.exists()
    second = run_cssa_local_checkpoint(rows, path, batch_size=1, resume=True)
    assert second["report"]["processed"] == 1
    third = run_cssa_local_checkpoint(rows, path, batch_size=2, resume=True)
    assert third["report"]["processed"] == 1
    assert json.loads(path.read_text(encoding="utf-8"))["token"]["next_index"] == 3


def test_without_resume_existing_file_is_untouched(tmp_path):
    path = tmp_path / "cssa.json"
    run_cssa_local_checkpoint([delivery(1)], path)
    before = path.read_bytes()
    with pytest.raises(ValueError, match="CSSA_CHECKPOINT_ALREADY_EXISTS"):
        run_cssa_local_checkpoint([delivery(1)], path)
    assert path.read_bytes() == before


def test_modified_checkpoint_receipt_rejected(tmp_path):
    path = tmp_path / "cssa.json"
    run_cssa_local_checkpoint([delivery(1), delivery(2)], path)
    data = json.loads(path.read_text(encoding="utf-8"))
    data["token"]["next_index"] = 2
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError, match="CSSA_CHECKPOINT_RECEIPT_INVALID"):
        run_cssa_local_checkpoint([delivery(1), delivery(2)], path, resume=True)


def test_changed_dataset_fails_and_does_not_advance(tmp_path):
    path = tmp_path / "cssa.json"
    run_cssa_local_checkpoint([delivery(1), delivery(2)], path)
    before = path.read_bytes()
    with pytest.raises(ValueError, match="CSSA_CHECKPOINT_INVALID"):
        run_cssa_local_checkpoint([delivery(1), delivery(3)], path, resume=True)
    assert path.read_bytes() == before


def test_malformed_checkpoint_json_rejected(tmp_path):
    path = tmp_path / "cssa.json"
    path.write_text("{bad json", encoding="utf-8")
    with pytest.raises(ValueError, match="CSSA_CHECKPOINT_READ_FAILED"):
        run_cssa_local_checkpoint([delivery(1)], path, resume=True)


def test_absent_checkpoint_rejected(tmp_path):
    with pytest.raises(ValueError, match="CSSA_CHECKPOINT_MISSING_OR_TOO_LARGE"):
        run_cssa_local_checkpoint([delivery(1)], tmp_path / "absent.json", resume=True)


def test_invalid_batch_size_and_extension_rejected(tmp_path):
    with pytest.raises(ValueError, match="CSSA_BATCH_SIZE_INVALID"):
        run_cssa_local_checkpoint([], tmp_path / "file.json", batch_size=0)
    with pytest.raises(ValueError, match="CSSA_CHECKPOINT_PATH_INVALID"):
        run_cssa_local_checkpoint([], tmp_path / "file.txt")


def test_collision_blocks_without_creating_checkpoint(tmp_path):
    path = tmp_path / "cssa.json"
    result = run_cssa_local_checkpoint([
        delivery(1, "Question supporter"),
        delivery(1, "Newsletter du club"),
    ], path)
    assert result["report"]["status"] == "BLOCK"
    assert not path.exists()


def test_invalid_mail_metadata_rejected_without_checkpoint(tmp_path):
    path = tmp_path / "cssa.json"
    with pytest.raises(ValueError, match="CSSA_ATTACHMENT_METADATA_INVALID"):
        run_cssa_local_checkpoint([{
            **delivery(1), "attachments": [{"name": "bad", "sha256": "INVALID"}]
        }], path)
    assert not path.exists()


def test_empty_input_creates_complete_checkpoint(tmp_path):
    path = tmp_path / "cssa.json"
    result = run_cssa_local_checkpoint([], path)
    assert result["report"]["processed"] == 0
    assert json.loads(path.read_text(encoding="utf-8"))["token"]["next_index"] == 0

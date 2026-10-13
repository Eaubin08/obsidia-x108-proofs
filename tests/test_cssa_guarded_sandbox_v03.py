"""CSSA V0.3 guarded pipeline regression. Synthetic accounts only."""
import pytest

from periphery.cssa_guarded_sandbox_v03 import run_cssa_guarded_v03


def item(n, sender="test@invalid.example", attested=None):
    return {
        "source": "MAILBOX_FAKE", "source_id": str(n), "thread_id": "t",
        "claimed_sender": sender,
        "provider_attested_sender": sender if attested is None else attested,
        "message": {"message_id": str(n), "subject": "Question supporter",
                    "body": "Fictif", "sender": sender},
        "attachments": [],
    }


def test_guarded_checkpoint_and_resume(tmp_path):
    path = tmp_path / "cssa-state.json"
    messages = [item(1), item(2)]
    first = run_cssa_guarded_v03(
        messages, sandbox_root=tmp_path, checkpoint_path=path, batch_size=1)
    assert first["processed"] == 1
    assert first["status"] == "HOLD"
    assert path.exists()
    assert not (tmp_path / "cssa-state.json.lock").exists()
    second = run_cssa_guarded_v03(
        messages, sandbox_root=tmp_path, checkpoint_path=path,
        batch_size=1, resume=True)
    assert second["processed"] == 1
    assert second["external_actions"] == []
    assert second["kx108_decision"] is None


def test_spoofed_sender_prevented_before_any_write(tmp_path):
    path = tmp_path / "cssa-state.json"
    with pytest.raises(ValueError, match="CSSA_V03_SENDER_BLOCKED"):
        run_cssa_guarded_v03(
            [item(1, attested="different@invalid.example")],
            sandbox_root=tmp_path, checkpoint_path=path)
    assert not path.exists()


def test_untrusted_provider_prevented(tmp_path):
    message = item(1)
    message["source"] = "SMTP_REAL"
    with pytest.raises(ValueError, match="CSSA_V03_SENDER_BLOCKED"):
        run_cssa_guarded_v03(
            [message], sandbox_root=tmp_path,
            checkpoint_path=tmp_path / "cssa-state.json")


def test_existing_lock_denies_concurrent_worker(tmp_path):
    path = tmp_path / "cssa-state.json"
    lock = tmp_path / "cssa-state.json.lock"
    lock.write_text("other worker", encoding="utf-8")
    with pytest.raises(ValueError, match="CSSA_V03_CONCURRENT_ACCESS_BLOCKED"):
        run_cssa_guarded_v03(
            [item(1)], sandbox_root=tmp_path, checkpoint_path=path)
    assert lock.read_text(encoding="utf-8") == "other worker"
    assert not path.exists()


def test_unsafe_filename_rejected(tmp_path):
    with pytest.raises(ValueError, match="CSSA_V03_PATH"):
        run_cssa_guarded_v03(
            [item(1)], sandbox_root=tmp_path,
            checkpoint_path=tmp_path / "unrelated.json")


def test_batch_limit_blocks_without_checkpoint(tmp_path):
    with pytest.raises(ValueError, match="CSSA_V03_BATCH_LIMIT"):
        run_cssa_guarded_v03(
            [item(i) for i in range(101)], sandbox_root=tmp_path,
            checkpoint_path=tmp_path / "cssa-state.json")
    assert not (tmp_path / "cssa-state.json").exists()


def test_collision_blocks_without_checkpoint(tmp_path):
    path = tmp_path / "cssa-state.json"
    first = item(1)
    second = item(1)
    second["message"]["subject"] = "Newsletter du club"
    result = run_cssa_guarded_v03(
        [first, second], sandbox_root=tmp_path, checkpoint_path=path)
    assert result["status"] == "BLOCK"
    assert result["processed"] == 0
    assert not path.exists()

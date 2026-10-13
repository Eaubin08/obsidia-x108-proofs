"""CSSA in-memory provider hardening regression."""
from copy import deepcopy

import pytest

from periphery.cssa_sandbox_hardening_v01 import (
    harden_cssa_sandbox, verify_cssa_hardening,
)


def delivery(source, sid, thread, subject, attachments=None):
    return {
        "source": source, "source_id": sid, "thread_id": thread,
        "message": {"message_id": sid, "subject": subject,
                    "body": "Synthétique", "sender": "test@invalid.example"},
        "attachments": attachments or [],
    }


def test_thread_groups_multiple_messages():
    result = harden_cssa_sandbox([
        delivery("box", "1", "thread", "Question supporter"),
        delivery("box", "2", "thread", "Demande de renseignement"),
    ])
    assert verify_cssa_hardening(result)
    assert result["report"]["threads"]["thread"] == ["box:1", "box:2"]
    assert result["report"]["processed"] == 2
    assert result["report"]["status"] == "HOLD"


def test_distinct_sources_do_not_collapse_same_message_id():
    result = harden_cssa_sandbox([
        delivery("a", "id1", "t1", "Question supporter"),
        delivery("b", "id1", "t2", "Question supporter"),
    ])
    assert result["report"]["processed"] == 2
    assert not result["report"]["duplicates"]
    assert verify_cssa_hardening(result)


def test_duplicate_is_not_processed_twice():
    d = delivery("a", "1", "t", "Question supporter")
    result = harden_cssa_sandbox([d, deepcopy(d)])
    assert result["report"]["processed"] == 1
    assert result["report"]["duplicates"] == ["a:1"]


def test_source_id_collision_blocks_all():
    result = harden_cssa_sandbox([
        delivery("a", "1", "t", "Question supporter"),
        delivery("a", "1", "t", "Newsletter du club"),
    ])
    assert result["report"]["status"] == "BLOCK"
    assert result["report"]["processed"] == 0
    assert result["report"]["events"] == []
    assert result["report"]["conflicts"] == ["a:1"]


def test_attachment_metadata_not_opened():
    result = harden_cssa_sandbox([
        delivery("box", "1", "t", "Question supporter",
                 [{"name": "dummy.pdf", "sha256": "a" * 64}])
    ])
    assert result["report"]["declared_attachments"] == 1
    assert result["report"]["attachment_content_accessed"] is False
    assert result["report"]["provider_writes"] is False


@pytest.mark.parametrize("attachment", [
    {"name": "bad.pdf", "sha256": "not-a-hash"},
    {"sha256": "b" * 64},
    {"name": "bad.pdf", "sha256": "A" * 64},
])
def test_invalid_attachment_metadata_rejected(attachment):
    with pytest.raises(ValueError, match="CSSA_ATTACHMENT_METADATA_INVALID"):
        harden_cssa_sandbox([delivery("box", "1", "t", "Question supporter", [attachment])])


def test_resume_after_checkpoint_without_repeating_delivery():
    data = [
        delivery("a", "1", "thread", "Question supporter"),
        delivery("a", "2", "thread", "Newsletter du club"),
    ]
    first = harden_cssa_sandbox(data, stop_after=1)
    assert first["report"]["processed"] == 1
    checkpoint = first["report"]["checkpoint"]
    resumed = harden_cssa_sandbox(data, checkpoint=checkpoint)
    assert resumed["report"]["processed"] == 1
    assert first["report"]["events"] != resumed["report"]["events"]
    assert verify_cssa_hardening(resumed)


def test_invalid_checkpoint_fails_closed():
    data = [delivery("a", "1", "t", "Question supporter")]
    with pytest.raises(ValueError, match="CSSA_CHECKPOINT_INVALID"):
        harden_cssa_sandbox(data, checkpoint={"dataset_sha256": "wrong", "next_index": 0})


def test_receipt_tampering_detected():
    result = harden_cssa_sandbox([delivery("a", "1", "t", "Question supporter")])
    result["report"]["provider_writes"] = True
    assert not verify_cssa_hardening(result)


def test_empty_batch_and_zero_checkpoint():
    assert harden_cssa_sandbox([], stop_after=0)["report"]["processed"] == 0
    assert verify_cssa_hardening(harden_cssa_sandbox([]))

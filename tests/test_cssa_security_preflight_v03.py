"""CSSA V0.3 preflight contract tests, no real security authentication."""
import pytest

from periphery.cssa_security_preflight_v03 import (
    check_cssa_checkpoint_location, inspect_cssa_sender_claim,
    preflight_cssa_batch,
)


def test_bounded_checkpoint_name_inside_root(tmp_path):
    target = tmp_path / "cssa-test.json"
    report = check_cssa_checkpoint_location(tmp_path, target)
    assert report["status"] == "HOLD"
    assert report["external_actions"] == []


def test_rejects_parent_escape(tmp_path):
    with pytest.raises(ValueError, match="CSSA_V03_PATH"):
        check_cssa_checkpoint_location(tmp_path, tmp_path.parent / "cssa-escape.json")


def test_rejects_non_cssa_checkpoint_name(tmp_path):
    with pytest.raises(ValueError, match="CSSA_V03_PATH_POLICY"):
        check_cssa_checkpoint_location(tmp_path, tmp_path / "other.json")


def test_rejects_symlinked_target(tmp_path):
    actual = tmp_path / "safe.json"
    actual.write_text("{}", encoding="utf-8")
    alias = tmp_path / "cssa-alias.json"
    try:
        alias.symlink_to(actual)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks not available on this environment")
    with pytest.raises(ValueError, match="CSSA_V03_PATH_SYMLINK_OR_NONFILE"):
        check_cssa_checkpoint_location(tmp_path, alias)


def test_sender_mismatch_blocks_without_exposing_address():
    report = inspect_cssa_sender_claim({
        "source": "MAILBOX_FAKE", "claimed_sender": "admin@invalid.example",
        "provider_attested_sender": "attacker@invalid.example",
    })
    assert report["status"] == "BLOCK"
    assert "admin@invalid.example" not in str(report)


def test_missing_provider_attestation_blocks():
    assert inspect_cssa_sender_claim({
        "source": "MAILBOX_FAKE", "claimed_sender": "example@invalid.example",
    })["status"] == "BLOCK"


def test_matching_fake_sender_remains_hold_not_verified():
    report = inspect_cssa_sender_claim({
        "source": "MAILBOX_FAKE", "claimed_sender": "A@invalid.example",
        "provider_attested_sender": "a@invalid.example",
    })
    assert report["status"] == "HOLD"
    assert report["reason"] == "SYNTHETIC_SENDER_MATCH_ONLY"


def test_untrusted_source_blocks():
    assert inspect_cssa_sender_claim({
        "source": "SMTP_REAL", "claimed_sender": "a@invalid.example",
        "provider_attested_sender": "a@invalid.example",
    })["status"] == "BLOCK"


def test_size_and_count_limits():
    with pytest.raises(ValueError, match="CSSA_V03_BATCH_LIMIT"):
        preflight_cssa_batch([1, 2], max_items=1)
    with pytest.raises(ValueError, match="CSSA_V03_BATCH_SIZE_LIMIT"):
        preflight_cssa_batch(["x" * 100], max_chars=10)


def test_invalid_limits_and_malformed_data():
    with pytest.raises(ValueError, match="CSSA_V03_LIMIT_INVALID"):
        preflight_cssa_batch([], max_items=0)
    with pytest.raises(ValueError, match="CSSA_V03_BATCH_MALFORMED"):
        preflight_cssa_batch([object()])


def test_minimal_data_disclosure():
    result = preflight_cssa_batch([{"sender": "private@invalid.example"}])
    assert result == {"status": "HOLD", "items": 1,
                      "contains_personal_data": "UNKNOWN", "external_actions": []}

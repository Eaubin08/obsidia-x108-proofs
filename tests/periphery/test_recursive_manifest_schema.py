"""
V5A Test: Recursive manifest schema validation.
"""
import json, os, pytest


def test_manifest_exists():
    """Recursive manifest must exist."""
    assert os.path.exists("MANIFEST_SHA256_RECURSIVE.json")


def test_manifest_root_hash_exists():
    """Root hash file must exist."""
    assert os.path.exists("MANIFEST_SHA256_RECURSIVE_ROOT.txt")


def test_manifest_has_required_keys():
    """Manifest must have generated_at, total_files, total_bytes, entries."""
    with open("MANIFEST_SHA256_RECURSIVE.json") as f:
        m = json.load(f)
    for key in ["generated_at", "total_files", "total_bytes", "entries"]:
        assert key in m, f"Missing key: {key}"
    assert len(m["entries"]) > 0


def test_manifest_entries_have_required_keys():
    """Each entry must have path, sha256, size_bytes."""
    with open("MANIFEST_SHA256_RECURSIVE.json") as f:
        m = json.load(f)
    for entry in m["entries"]:
        for key in ["path", "sha256", "size_bytes"]:
            assert key in entry, f"Entry missing {key}: {entry.get('path','?')}"


def test_manifest_sha256_is_valid_hex():
    """All SHA-256 entries must be 64-character hex strings."""
    with open("MANIFEST_SHA256_RECURSIVE.json") as f:
        m = json.load(f)
    for entry in m["entries"]:
        assert len(entry["sha256"]) == 64, f"Invalid SHA-256 length in {entry['path']}"
        assert all(c in "0123456789abcdef" for c in entry["sha256"]), f"Non-hex SHA-256 in {entry['path']}"


def test_root_hash_is_valid_hex():
    """Root hash must be 64-character hex."""
    with open("MANIFEST_SHA256_RECURSIVE_ROOT.txt") as f:
        root = f.read().strip()
    assert len(root) == 64
    assert all(c in "0123456789abcdef" for c in root)

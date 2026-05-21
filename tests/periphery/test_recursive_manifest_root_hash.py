"""
V5A Test: Recursive manifest root hash integrity.
"""
import hashlib, json, pytest


def test_root_hash_matches_manifest():
    """Root hash must match SHA-256 of concatenated sorted entry hashes."""
    with open("MANIFEST_SHA256_RECURSIVE.json") as f:
        m = json.load(f)
    sorted_hashes = [e["sha256"] for e in m["entries"]]
    computed_root = hashlib.sha256("".join(sorted_hashes).encode()).hexdigest()
    with open("MANIFEST_SHA256_RECURSIVE_ROOT.txt") as f:
        stored_root = f.read().strip()
    assert computed_root == stored_root, "Root hash mismatch — manifest may be corrupted"


def test_root_hash_is_64_char_hex():
    """Root hash must be 64-character lowercase hex."""
    with open("MANIFEST_SHA256_RECURSIVE_ROOT.txt") as f:
        root = f.read().strip()
    assert len(root) == 64
    assert all(c in "0123456789abcdef" for c in root)


def test_root_hash_not_empty():
    """Root hash must not be empty."""
    with open("MANIFEST_SHA256_RECURSIVE_ROOT.txt") as f:
        root = f.read().strip()
    assert len(root) > 0

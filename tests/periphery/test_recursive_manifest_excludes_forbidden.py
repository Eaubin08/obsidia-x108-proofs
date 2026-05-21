"""
V5A Test: Recursive manifest excludes forbidden files/directories.
"""
import json, os, pytest


def test_manifest_excludes_pycache():
    """Manifest must not contain __pycache__ entries."""
    with open("MANIFEST_SHA256_RECURSIVE.json") as f:
        m = json.load(f)
    for entry in m["entries"]:
        assert "__pycache__" not in entry["path"], f"__pycache__ in manifest: {entry['path']}"


def test_manifest_excludes_node_modules():
    """Manifest must not contain node_modules entries."""
    with open("MANIFEST_SHA256_RECURSIVE.json") as f:
        m = json.load(f)
    for entry in m["entries"]:
        assert "node_modules" not in entry["path"], f"node_modules in manifest: {entry['path']}"


def test_manifest_excludes_git_dir():
    """Manifest must not contain .git entries."""
    with open("MANIFEST_SHA256_RECURSIVE.json") as f:
        m = json.load(f)
    for entry in m["entries"]:
        assert not entry["path"].startswith(".git"), f".git in manifest: {entry['path']}"


def test_manifest_excludes_venv():
    """Manifest must not contain .venv entries."""
    with open("MANIFEST_SHA256_RECURSIVE.json") as f:
        m = json.load(f)
    for entry in m["entries"]:
        assert ".venv" not in entry["path"], f".venv in manifest: {entry['path']}"


def test_manifest_excludes_zips():
    """Manifest must not contain .zip entries."""
    with open("MANIFEST_SHA256_RECURSIVE.json") as f:
        m = json.load(f)
    for entry in m["entries"]:
        assert not entry["path"].endswith(".zip"), f".zip in manifest: {entry['path']}"

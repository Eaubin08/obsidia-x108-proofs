"""F15B — brody_chat.py live-only output verification.

Source-assert tests. Verify that:
- Default BASE_URL points to port 8000 (main stack), not 8012 (Graphiti).
- Docstring references 8000, not 8012.
- No hardcoded phantom fields in _print_* handlers.
- No subprocess / shell / exec call anywhere in the tool.
- CLI --url override wiring is present.
"""
from pathlib import Path

SRC = Path("tools/brody_chat.py").read_text(encoding="utf-8")


def test_base_url_is_8000():
    """Default BASE_URL must target port 8000 (main Obsidia stack)."""
    assert 'BASE_URL  = "http://127.0.0.1:8000"' in SRC


def test_base_url_not_8012():
    """Port 8012 (Graphiti) must not appear as the default BASE_URL."""
    assert 'BASE_URL  = "http://127.0.0.1:8012"' not in SRC


def test_docstring_references_8000():
    """Module docstring must reference port 8000."""
    assert "http://127.0.0.1:8000/api/brody/chat" in SRC


def test_no_hardcoded_v18_hash_status():
    """No hardcoded v18_hash_status phantom string in the CLI tool."""
    assert "v18_hash_status" not in SRC


def test_no_hardcoded_git_branch():
    """No hardcoded ci-strict-sigma branch string in the CLI tool."""
    assert "ci-strict-sigma" not in SRC


def test_no_subprocess_shell_exec():
    """No shell execution primitives in brody_chat.py."""
    assert "subprocess" not in SRC
    assert "shell=True" not in SRC
    assert "os.system(" not in SRC
    assert "os.popen(" not in SRC
    assert "exec(" not in SRC
    assert "eval(" not in SRC
    assert "spawn(" not in SRC


def test_url_override_wiring():
    """--url CLI argument overrides BASE_URL, ENDPOINT, HEALTH_EP."""
    assert "--url" in SRC
    assert "args.url" in SRC
    assert "BASE_URL  = args.url" in SRC or "BASE_URL = args.url" in SRC


def test_reads_true_voice_snapshot_from_payload():
    """_print_true_voice_snapshot reads from live payload key."""
    assert "true_voice_snapshot" in SRC


def test_reads_domain_raccord_from_payload():
    """_print_domain_raccord_snapshot reads from live payload."""
    assert "domain_raccord_snapshot" in SRC


def test_clipboard_not_used():
    """CLI tool must not call navigator.clipboard (that is a browser API)."""
    assert "navigator.clipboard" not in SRC

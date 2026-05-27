"""F14 — COPY COMMAND button in BrodyTerminalView.

Source-assert tests. Verify that:
- The button exists and is conditional on commandCopy.command presence.
- The handler uses navigator.clipboard.writeText — nothing else.
- No shell / exec / fetch call in the handler.
- Boundary labels are displayed alongside the button.
- Existing handleCopy (full response copy) is not broken.
"""
from pathlib import Path

SRC = Path("apps/obsidia-workbench/src/views/ChatView.tsx").read_text(encoding="utf-8")


def test_copy_command_button_present_in_brody_terminal_view():
    """Button COPY CMD exists inside BrodyTerminalView function."""
    # cmdCopied state wired
    assert "const [cmdCopied, setCmdCopied] = useState(false)" in SRC
    # handler defined
    assert "handleCopyCommand" in SRC
    # button renders with handler
    assert "onClick={handleCopyCommand}" in SRC
    # button label
    assert "COPY CMD" in SRC
    assert "COPIED" in SRC


def test_copy_command_only_when_command_present():
    """Button is conditional — only rendered when copyableCommand is non-null and not '-'."""
    assert "hasCopyableCommand" in SRC
    assert "copyableCommand && copyableCommand !== \"-\"" in SRC
    assert "{hasCopyableCommand && (" in SRC


def test_copy_command_clipboard_writetext_only():
    """Handler calls navigator.clipboard.writeText with copyableCommand — nothing else."""
    assert "navigator.clipboard.writeText(copyableCommand)" in SRC
    # handler must guard on empty/dash
    assert 'if (!copyableCommand || copyableCommand === "-") return' in SRC


def test_copy_command_no_exec_no_fetch_no_shell():
    """Handler must not contain any execution primitive."""
    # Isolate the handleCopyCommand block
    start = SRC.find("const handleCopyCommand")
    end = SRC.find("\n  }", start) + 4
    handler_src = SRC[start:end]
    assert "fetch(" not in handler_src
    assert "exec(" not in handler_src
    assert "shell" not in handler_src
    assert "spawn" not in handler_src
    assert "eval(" not in handler_src


def test_copy_command_boundary_labels_displayed():
    """Button section displays copy_only, execution_allowed_for_brody, packet_executed labels."""
    assert "copy_only=true" in SRC
    assert "execution_allowed_for_brody=false" in SRC
    assert "packet_executed=false" in SRC


def test_copy_command_feedback_visual():
    """Visual feedback: cmdCopied state toggles Check/Copy icon and label."""
    assert "cmdCopied" in SRC
    assert "setCmdCopied(true)" in SRC
    assert "setCmdCopied(false)" in SRC
    # Check icon used for feedback
    assert "Check size={8}" in SRC
    # Copy icon used at rest
    assert "Copy size={8}" in SRC


def test_existing_copy_response_not_broken():
    """Original handleCopy (full Brody response) is intact and unaffected."""
    assert "const handleCopy = async () => {" in SRC
    assert "navigator.clipboard.writeText(msg.content)" in SRC
    assert "onClick={handleCopy}" in SRC

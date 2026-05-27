from pathlib import Path


def test_chat_terminal_displays_existing_human_command_packet():
    src = Path("apps/obsidia-workbench/src/views/ChatView.tsx").read_text(encoding="utf-8")
    assert "automation_snapshot" in src
    assert "operator_loop" in src
    assert "command_copy_block" in src
    assert "human_command_packet" in src
    assert "HUMAN_COMMAND_PACKET_READONLY" in src
    assert "human_command_packet_ready=${String" in src
    assert "command_gate_classification=${String" in src
    assert "execution_allowed_for_brody=${String" in src
    assert "brody_execute_allowed=${String" in src
    assert "copy_only=${String" in src
    assert "present_packet_to_operator=${String" in src
    assert "copy_command=${String" in src


def test_chat_terminal_command_packet_does_not_grant_execution():
    src = Path("apps/obsidia-workbench/src/views/ChatView.tsx").read_text(encoding="utf-8")
    assert "packet_executed=${String" in src
    assert "operator_can_write=${String" in src
    assert "operator_can_decide=${String" in src
    assert "emits_act=${String" in src
    assert "emits_verdict=${String" in src

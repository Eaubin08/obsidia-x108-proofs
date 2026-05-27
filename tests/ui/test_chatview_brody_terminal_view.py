from pathlib import Path


def test_chatview_contains_brody_terminal_view():
    src = Path("apps/obsidia-workbench/src/views/ChatView.tsx").read_text(encoding="utf-8")
    assert "function BrodyTerminalView" in src
    assert "operator_view_packet" in src
    assert "OBSIDIA_TERMINAL_VIEW_V1" in src
    assert "BRODY TERMINAL" in src
    assert "<BrodyTerminalView payload={msg.backendPayload" in src


def test_chat_terminal_boundary_lines():
    src = Path("apps/obsidia-workbench/src/views/ChatView.tsx").read_text(encoding="utf-8")
    assert "decision_authority=${String" in src
    assert "KX108_ONLY" in src
    assert "readonly=${String" in src
    assert "emits_act=${String" in src
    assert "emits_verdict=${String" in src
    assert "operator_can_write=${String" in src
    assert "operator_can_decide=${String" in src
    assert "value_layer_scores_null=${String" in src

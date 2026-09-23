from pathlib import Path


def test_rightpanel_exposes_operator_view_packet():
    src = Path("apps/obsidia-workbench/src/components/RightPanel.tsx").read_text(encoding="utf-8")
    assert "const operatorView = live?.operator_view_packet" in src
    assert "Transverse Operator View" in src
    assert 'operatorView["system_status"]' in src
    assert 'operatorView["next_safe_action"]' in src
    assert 'opSummary["safe_boundary_ok"]' in src
    assert 'opSummary["operator_can_write"]' in src
    assert 'opSummary["operator_can_decide"]' in src
    assert 'opBlocked["hard_risks"]' in src
    assert 'opBlocked["missing_packets"]' in src


def test_rightpanel_operator_view_boundary_copyables():
    src = Path("apps/obsidia-workbench/src/components/RightPanel.tsx").read_text(encoding="utf-8")
    assert 'k="decision_authority"' in src
    assert 'KX108_ONLY' in src
    assert 'k="readonly"' in src
    assert 'k="emits_act"' in src
    assert 'k="emits_verdict"' in src

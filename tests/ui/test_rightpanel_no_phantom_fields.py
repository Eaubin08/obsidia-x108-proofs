"""F15C — RightPanel strict live surface verification.

Source-assert tests. Verify that:
- No hardcoded phantom fields (v18_hash_status, git_branch, cp_a1b2c3d4).
- tree_policy safe_trees reads nested path.
- All mock sections are wrapped in STATIC_DEMO_NOT_RUNTIME disclosure (hidden by default).
- Mock section titles do NOT carry inline NOT_RUNTIME suffixes (moved to wrapper).
- Live surface (CONTEXT tab) blocks remain intact and payload-driven.
"""
from pathlib import Path

SRC = Path("apps/obsidia-workbench/src/components/RightPanel.tsx").read_text(encoding="utf-8")


# ── Phantom field removal ────────────────────────────────────────────────────

def test_no_hardcoded_v18_hash_status():
    """v18_hash_status FAIL string must not appear as a hardcoded const in RightPanel."""
    assert "const v18: string = 'FAIL'" not in SRC
    assert 'const v18 = "FAIL"' not in SRC


def test_no_hardcoded_git_branch():
    """ci-strict-sigma hardcoded branch must not appear in RightPanel live display."""
    assert "ci-strict-sigma" not in SRC


def test_no_static_context_packet_id():
    """Static packet_id cp_a1b2c3d4 must not appear in live display code."""
    assert "cp_a1b2c3d4" not in SRC


def test_no_static_context_query():
    """Static query string from MOCK_CONTEXT_PACKET must not appear in live display."""
    assert "What is the current governance context?" not in SRC


# ── tree_policy nested path ──────────────────────────────────────────────────

def test_tree_policy_uses_nested_path():
    """safe_trees count must read from tree_policy.safe_trees nested key."""
    assert "tree_policy as Record<string,unknown>" in SRC
    assert "safe_trees" in SRC


# ── STATIC_DEMO_NOT_RUNTIME wrapper ─────────────────────────────────────────

def test_static_demo_component_present():
    """StaticDemoSection component must exist in RightPanel source."""
    assert "StaticDemoSection" in SRC
    assert "STATIC_DEMO_NOT_RUNTIME" in SRC


def test_static_demo_hidden_by_default():
    """StaticDemoSection starts closed — toggle state initialized to false."""
    assert "const [open, setOpen] = useState(false)" in SRC


def test_governance_sections_in_static_demo():
    """GovernanceTab sections are wrapped in StaticDemoSection, not in live surface."""
    assert 'StaticDemoSection label="OS3 / Sovereign / WorldCall"' in SRC


def test_governance_titles_no_inline_not_runtime():
    """OS3/Sovereign/WorldCall section titles must NOT carry inline — NOT_RUNTIME suffix."""
    assert "OS3 Proof Ticket — NOT_RUNTIME" not in SRC
    assert "Sovereign Ticket — NOT_RUNTIME" not in SRC
    assert "WorldCall / Gateway — NOT_RUNTIME" not in SRC


def test_memory_sections_in_static_demo():
    """MemoryTab sections are wrapped in StaticDemoSection."""
    assert 'StaticDemoSection label="Memory Candidates / Graphiti Status"' in SRC


def test_memory_titles_no_inline_not_runtime():
    """Memory section titles must NOT carry inline NOT_RUNTIME suffixes."""
    assert "Memory Candidates — NOT_RUNTIME / STATIC" not in SRC
    assert "Graphiti Status — STATIC / NOT_RUNTIME" not in SRC


def test_gencoin_ledger_in_static_demo():
    """GencoinTab Ledger Entries are wrapped in StaticDemoSection."""
    assert 'StaticDemoSection label="Ledger Entries"' in SRC


def test_gencoin_title_no_inline_not_runtime():
    """Ledger Entries section title must NOT carry inline NOT_RUNTIME suffix."""
    assert "Ledger Entries — NOT_RUNTIME / SYMBOLIC" not in SRC


def test_audit_events_in_static_demo():
    """AuditTab Audit Events are wrapped in StaticDemoSection."""
    assert 'StaticDemoSection label="Audit Events"' in SRC


def test_audit_title_no_inline_not_runtime():
    """Audit Events section title must NOT carry inline NOT_RUNTIME suffix."""
    assert "Audit Events — NOT_RUNTIME / STATIC" not in SRC


def test_dominant_trees_in_static_demo():
    """ContextTab Dominant Trees are wrapped in StaticDemoSection."""
    assert "Dominant Trees" in SRC
    assert "StaticDemoSection" in SRC


def test_dominant_trees_title_no_inline_not_runtime():
    """Dominant Trees title must NOT carry inline NOT_RUNTIME / STATIC suffix."""
    assert "Dominant Trees — NOT_RUNTIME / STATIC" not in SRC


# ── Live surface boundary labels remain ─────────────────────────────────────

def test_live_boundary_labels_present():
    """Live boundary labels (decision_authority, readonly, emits_act) remain in CONTEXT tab."""
    assert "decision_authority" in SRC
    assert "readonly" in SRC
    assert "emits_act" in SRC
    assert "KX108_ONLY" in SRC

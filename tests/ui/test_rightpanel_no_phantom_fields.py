"""F16B — RightPanel live source verification.

Source-assert tests verifying:
- No hardcoded phantom fields (v18_hash_status, git_branch, cp_a1b2c3d4)
- No mock data in runtime surface (MOCK_* removed from runtime rendering)
- Live sources wired: tree_signal_packet, candidate_memory_snapshot,
  gencoin_shadow_packet, audit_event, endpoint fetch for governance
- LIVE_EMPTY_REGISTRY for gencoin ledger
- Boundary labels present in CONTEXT tab
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


# ── Mock removal from runtime surface ───────────────────────────────────────

def test_no_mock_os3_ticket():
    """MOCK_OS3_TICKET must not appear in RightPanel source."""
    assert "MOCK_OS3_TICKET" not in SRC


def test_no_mock_sovereign_ticket():
    """MOCK_SOVEREIGN_TICKET must not appear in RightPanel source."""
    assert "MOCK_SOVEREIGN_TICKET" not in SRC


def test_no_mock_world_calls():
    """MOCK_WORLD_CALLS must not appear in RightPanel source."""
    assert "MOCK_WORLD_CALLS" not in SRC


def test_no_mock_memory_candidates():
    """MOCK_MEMORY_CANDIDATES must not appear in RightPanel source."""
    assert "MOCK_MEMORY_CANDIDATES" not in SRC


def test_no_mock_gencoin():
    """MOCK_GENCOIN must not appear in RightPanel source."""
    assert "MOCK_GENCOIN" not in SRC


def test_no_mock_audit():
    """MOCK_AUDIT must not appear in RightPanel source."""
    assert "MOCK_AUDIT" not in SRC


def test_no_mock_context_packet_dominant_trees():
    """cp.dominant_trees from MOCK_CONTEXT_PACKET must not be the source."""
    assert "cp.dominant_trees" not in SRC
    assert "MOCK_CONTEXT_PACKET" not in SRC


# ── Live sources wired ───────────────────────────────────────────────────────

def test_dominant_trees_reads_tree_signal_packet():
    """Dominant Trees block must read from live.tree_signal_packet."""
    assert "tree_signal_packet" in SRC


def test_memory_tab_reads_candidate_memory_snapshot():
    """MemoryTab must read from candidate_memory_snapshot.latest_candidates."""
    assert "candidate_memory_snapshot" in SRC
    assert "latest_candidates" in SRC


def test_memory_tab_reads_graphiti_status():
    """MemoryTab must read graphiti_status from live payload."""
    assert "graphiti_status" in SRC


def test_gencoin_tab_reads_shadow_packet():
    """GencoinTab must read from live.gencoin_shadow_packet."""
    assert "gencoin_shadow_packet" in SRC


def test_gencoin_tab_live_empty_registry():
    """GencoinTab must display LIVE_EMPTY_REGISTRY for ledger."""
    assert "LIVE_EMPTY_REGISTRY" in SRC


def test_audit_tab_reads_audit_event():
    """AuditTab must read from live.audit_event."""
    assert "audit_event" in SRC


def test_governance_tab_uses_endpoint_fetch():
    """GovernanceTab must fetch from real endpoints using useEffect."""
    assert "useEffect" in SRC
    assert "/api/os3/tickets" in SRC
    assert "/api/worldcalls" in SRC


# ── Live boundary labels present ─────────────────────────────────────────────

def test_live_boundary_labels_present():
    """Live boundary labels (decision_authority, readonly, emits_act) remain in CONTEXT tab."""
    assert "decision_authority" in SRC
    assert "readonly" in SRC
    assert "emits_act" in SRC
    assert "KX108_ONLY" in SRC

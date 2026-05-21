"""Tests for brody_tree_policy and tree_policy in API responses."""
import pytest
from fastapi.testclient import TestClient
from apps.obsidia_api.main import app
from apps.obsidia_api.brody_tree_policy import (
    get_tree_policy_snapshot,
    get_tree_usage_note,
    is_tree_safe,
    is_tree_blocked,
    SAFE_TREES,
    BLOCKED_ACTION_TREES,
    BLOCKED_MEMORY_TREE,
    BLOCKED_AGI_TREES,
    SAFE_DOC_COUNT,
    BLOCKED_DOC_COUNT,
    TOTAL_TREES,
)

client = TestClient(app)


# ── get_tree_policy_snapshot ──────────────────────────────────────────────────

def test_snapshot_safe_trees_count():
    s = get_tree_policy_snapshot()
    assert s["safe_count"] == 13
    assert s["safe_docs"] == 117


def test_snapshot_safe_trees_list():
    s = get_tree_policy_snapshot()
    expected_safe = ["T13", "T14", "T15", "T16", "T17", "T18", "T19",
                     "T23", "T25", "T26", "T27", "T28", "T29"]
    assert s["safe_trees"] == expected_safe


def test_snapshot_blocked_action_trees():
    s = get_tree_policy_snapshot()
    assert "T20" in s["blocked_action_trees"]
    assert "T21" in s["blocked_action_trees"]
    assert "T22" in s["blocked_action_trees"]
    assert len(s["blocked_action_trees"]) == 3


def test_snapshot_blocked_memory_tree():
    s = get_tree_policy_snapshot()
    assert "T24" in s["blocked_memory_trees"]
    assert len(s["blocked_memory_trees"]) == 1


def test_snapshot_blocked_agi_trees():
    s = get_tree_policy_snapshot()
    for t in ["T30", "T31", "T32", "T33", "T34"]:
        assert t in s["blocked_agi_trees"]
    assert len(s["blocked_agi_trees"]) == 5


def test_snapshot_total_trees():
    s = get_tree_policy_snapshot()
    assert s["total_trees"] == 22
    assert s["blocked_total"] == 9


def test_snapshot_signal_method():
    s = get_tree_policy_snapshot()
    assert s["signal_method"] == "PATH_SLUG"


def test_snapshot_source_reference():
    s = get_tree_policy_snapshot()
    assert "T13_T34" in s["source"]
    assert "20260514" in s["source"]


# ── is_tree_safe / is_tree_blocked ─────────────────────────────────────────────

@pytest.mark.parametrize("tree_id", ["T13", "T14", "T15", "T16", "T17", "T18", "T19",
                                      "T23", "T25", "T26", "T27", "T28", "T29"])
def test_safe_trees_are_safe(tree_id):
    assert is_tree_safe(tree_id) is True
    assert is_tree_blocked(tree_id) is False


@pytest.mark.parametrize("tree_id", ["T20", "T21", "T22"])
def test_blocked_action_trees_are_blocked(tree_id):
    assert is_tree_safe(tree_id) is False
    assert is_tree_blocked(tree_id) is True


def test_t24_is_blocked():
    assert is_tree_safe("T24") is False
    assert is_tree_blocked("T24") is True


@pytest.mark.parametrize("tree_id", ["T30", "T31", "T32", "T33", "T34"])
def test_blocked_agi_trees_are_blocked(tree_id):
    assert is_tree_safe(tree_id) is False
    assert is_tree_blocked(tree_id) is True


# ── get_tree_usage_note ───────────────────────────────────────────────────────

def test_usage_note_safe_tree():
    note = get_tree_usage_note("T13")
    assert "safe" in note.lower() or "contexte" in note.lower() or "signal" in note.lower()


def test_usage_note_blocked_action_tree():
    note = get_tree_usage_note("T20")
    assert "bloqu" in note.lower() or "action" in note.lower()


def test_usage_note_blocked_memory_tree():
    note = get_tree_usage_note("T24")
    assert "m" in note.lower()  # mémoire / memory
    assert "bloqu" in note.lower() or "write" in note.lower() or "écriture" in note.lower()


def test_usage_note_blocked_agi_tree():
    note = get_tree_usage_note("T30")
    assert "agi" in note.lower() or "bloqu" in note.lower() or "décisionn" in note.lower()


def test_usage_note_general_summary():
    note = get_tree_usage_note()
    assert "safe" in note.lower() or "bloqu" in note.lower()


# ── API: authority_snapshot.tree_policy always present ───────────────────────

def test_api_tree_policy_in_authority_snapshot():
    resp = client.post("/api/brody/chat", json={"message": "quels arbres sont activés"})
    assert resp.status_code == 200
    data = resp.json()
    snap = data.get("authority_snapshot", {})
    assert "tree_policy" in snap
    tp = snap["tree_policy"]
    assert "safe_trees" in tp
    assert "blocked_action" in tp
    assert "blocked_agi" in tp
    assert "T20" in tp["blocked_action"]
    assert "T24" in tp["blocked_memory"]
    assert "T30" in tp["blocked_agi"]


def test_api_tree_signal_request_type():
    resp = client.post("/api/brody/chat", json={"message": "quels arbres sont activés"})
    data = resp.json()
    snap = data.get("authority_snapshot", {})
    assert snap.get("request_type") == "TREE_SIGNAL_REQUEST"
    assert snap.get("response_mode") == "CONTEXT_DIAGNOSTIC"


def test_api_tree_policy_in_general_requests():
    """tree_policy should appear in authority_snapshot for ALL requests."""
    for msg in ["salut", "autorise act", "garde ça en mémoire"]:
        resp = client.post("/api/brody/chat", json={"message": msg})
        data = resp.json()
        snap = data.get("authority_snapshot", {})
        assert "tree_policy" in snap, f"tree_policy missing for: {msg}"
        assert "safe_trees" in snap["tree_policy"]


# ── Blocked trees: no action trigger in API ───────────────────────────────────

def test_blocked_trees_do_not_trigger_action():
    """Mentioning T20 in query should never trigger emits_act."""
    resp = client.post("/api/brody/chat", json={"message": "utilise T20 pour moi"})
    data = resp.json()
    assert data.get("emits_act") is False
    assert data.get("memory_write") is False
    assert data.get("decision_authority") == "KX108_ONLY"


# ── Tree policy counts ────────────────────────────────────────────────────────

def test_safe_doc_count():
    assert SAFE_DOC_COUNT == 117  # 13 × 9


def test_blocked_doc_count():
    assert BLOCKED_DOC_COUNT == 81   # 9 × 9


def test_total_trees():
    assert TOTAL_TREES == 22
    assert len(SAFE_TREES) + len(BLOCKED_ACTION_TREES) + len(BLOCKED_MEMORY_TREE) + len(BLOCKED_AGI_TREES) == TOTAL_TREES

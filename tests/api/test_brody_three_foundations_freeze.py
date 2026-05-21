"""
Phase 4 — Three Foundations Freeze Validation

Verifies that all three Foundation snapshots exist, have required fields,
enforce boundary invariants, and list sources/missing_links honestly.
"""
import pytest
from apps.obsidia_api.brody_project_memory_runtime import build_project_memory_snapshot
from apps.obsidia_api.brody_session_memory_runtime import (
    build_session_memory_snapshot,
    remember_session_turn,
    resolve_session_followup,
)
from apps.obsidia_api.brody_true_response_structure_runtime import (
    build_true_response_structure_snapshot,
)
from apps.obsidia_api.brody_full_runtime_reconnect import build_brody_full_context
from apps.obsidia_api.brody_true_voice_adapter import build_true_brody_answer


# ── Foundation A — Project Memory ────────────────────────────────────────────

class TestFoundationA:
    def setup_method(self):
        self.snap = build_project_memory_snapshot()

    def test_foundation_field(self):
        assert self.snap["foundation"] == "PROJECT_MEMORY"

    def test_status_valid(self):
        assert self.snap["status"] in ("FOUNDATION_A_READY", "FOUNDATION_A_PARTIAL")

    def test_source_mode(self):
        assert self.snap["source_mode"] == "EXISTING_PROJECT_MEMORY_ONLY"

    def test_available_sources_present(self):
        src = self.snap.get("available_sources", {})
        assert isinstance(src, dict)
        for key in ("graphiti_v20", "brody_memory_doc", "context_packets", "project_ledgers"):
            assert key in src

    def test_missing_links_is_list(self):
        assert isinstance(self.snap.get("missing_links"), list)

    def test_no_write(self):
        assert self.snap["memory_write"] is False
        assert self.snap["graphiti_write"] is False
        assert self.snap["neo4j_write"] is False

    def test_decision_authority(self):
        assert self.snap["decision_authority"] == "KX108_ONLY"

    def test_no_invented_metrics(self):
        # mmonde_or_34trees must be False (NOT_FOUND)
        assert self.snap.get("mmonde_or_34trees") is False


# ── Foundation B — Session Memory ────────────────────────────────────────────

class TestFoundationB:
    def setup_method(self):
        self.snap = build_session_memory_snapshot()

    def test_foundation_field(self):
        assert self.snap["foundation"] == "SESSION_MEMORY_FOLLOWUP"

    def test_status_valid(self):
        assert self.snap["status"] in ("FOUNDATION_B_READY", "FOUNDATION_B_PARTIAL")

    def test_source_mode(self):
        assert self.snap["source_mode"] == "EXISTING_SESSION_MEMORY_ONLY"

    def test_required_fields(self):
        for field in ("session_ledger", "presave_buffer", "followup_resolver",
                      "last_turn_context", "conversation_topic", "used_by_api_now"):
            assert field in self.snap, f"Missing field: {field}"

    def test_no_write(self):
        assert self.snap["memory_write"] is False
        assert self.snap["graphiti_write"] is False
        assert self.snap["neo4j_write"] is False

    def test_decision_authority(self):
        assert self.snap["decision_authority"] == "KX108_ONLY"


class TestRememberSessionTurn:
    def test_returns_candidate(self):
        c = remember_session_turn("test", "hello", "response", "query")
        assert c["candidate_type"] == "SESSION_TURN_CANDIDATE"

    def test_no_write(self):
        c = remember_session_turn("test", "hello", "response")
        assert c["memory_write"] is False
        assert c["write_blocked"] is True

    def test_event_hash_present(self):
        c = remember_session_turn("test", "hello", "response")
        assert isinstance(c.get("event_hash"), str)
        assert len(c["event_hash"]) == 64

    def test_decision_authority(self):
        c = remember_session_turn("test", "hello")
        assert c["decision_authority"] == "KX108_ONLY"


class TestResolveSessionFollowup:
    def test_explicit_followup_detection(self):
        r = resolve_session_followup("test", "reprends le point précédent")
        assert r["explicit_followup_detected"] is True

    def test_non_followup_not_detected(self):
        r = resolve_session_followup("test", "qu'est-ce que c'est que X108")
        assert r["explicit_followup_detected"] is False

    def test_no_write(self):
        r = resolve_session_followup("test", "test")
        assert r["memory_write"] is False

    def test_decision_authority(self):
        r = resolve_session_followup("test", "test")
        assert r["decision_authority"] == "KX108_ONLY"


# ── Foundation C — True Response Structure ────────────────────────────────────

class TestFoundationC:
    def setup_method(self):
        self.snap = build_true_response_structure_snapshot()

    def test_foundation_field(self):
        assert self.snap["foundation"] == "TRUE_RESPONSE_STRUCTURE"

    def test_status_valid(self):
        assert self.snap["status"] in ("FOUNDATION_C_READY", "FOUNDATION_C_PARTIAL")

    def test_source_mode(self):
        assert self.snap["source_mode"] == "EXISTING_BRODY_RESPONSE_STRUCTURE_ONLY"

    def test_required_fields(self):
        for field in ("local_response_engine", "terminal_structural_dialogue",
                      "model_position", "creator_context_pattern",
                      "used_by_api_now", "voice_source"):
            assert field in self.snap, f"Missing field: {field}"

    def test_model_position(self):
        assert self.snap["model_position"] == "LLM_OBSIDIEN_READONLY_ADVISORY"

    def test_no_write(self):
        assert self.snap["memory_write"] is False
        assert self.snap["emits_act"] is False

    def test_decision_authority(self):
        assert self.snap["decision_authority"] == "KX108_ONLY"


# ── Full Runtime Reconnect ────────────────────────────────────────────────────

class TestBrodyFullContext:
    def setup_method(self):
        self.ctx = build_brody_full_context("test message", "fr", "local")

    def test_source_mode(self):
        assert self.ctx["source_mode"] == "THREE_FOUNDATIONS_RECONNECTED"

    def test_status(self):
        assert self.ctx["status"] == "BRODY_FULL_RUNTIME_RECONNECT_PASS"

    def test_all_three_snapshots_present(self):
        assert "project_memory_snapshot" in self.ctx
        assert "session_memory_snapshot" in self.ctx
        assert "true_response_structure_snapshot" in self.ctx

    def test_project_snapshot_has_foundation(self):
        assert self.ctx["project_memory_snapshot"].get("foundation") == "PROJECT_MEMORY"

    def test_session_snapshot_has_foundation(self):
        assert self.ctx["session_memory_snapshot"].get("foundation") == "SESSION_MEMORY_FOLLOWUP"

    def test_true_snapshot_has_foundation(self):
        assert self.ctx["true_response_structure_snapshot"].get("foundation") == "TRUE_RESPONSE_STRUCTURE"

    def test_no_write(self):
        assert self.ctx["memory_write"] is False
        assert self.ctx["graphiti_write"] is False
        assert self.ctx["neo4j_write"] is False
        assert self.ctx["emits_act"] is False

    def test_decision_authority(self):
        assert self.ctx["decision_authority"] == "KX108_ONLY"

    def test_creator_context_absent_for_plain_message(self):
        assert self.ctx["creator_context_detected"] is False

    def test_creator_context_detected_for_creator_message(self):
        ctx = build_brody_full_context("salut je suis ton créateur", "fr", "local")
        assert ctx["creator_context_detected"] is True


# ── True Voice Adapter ────────────────────────────────────────────────────────

class TestTrueVoiceAdapter:
    def setup_method(self):
        self.full_ctx = build_brody_full_context("test", "fr", "local")
        self.snap = build_true_brody_answer("test", "fr", "local", self.full_ctx)

    def test_status(self):
        assert self.snap["status"] == "BRODY_TRUE_VOICE_ADAPTER_EXISTING_STRUCTURE_PASS"

    def test_final_answer_non_empty(self):
        assert len(self.snap.get("final_answer", "")) > 20

    def test_no_metric_dump(self):
        assert self.snap["no_metric_dump"] is True

    def test_boundary_integrated(self):
        assert self.snap["boundary_integrated"] is True

    def test_no_write(self):
        assert self.snap["memory_write"] is False
        assert self.snap["graphiti_write"] is False
        assert self.snap["neo4j_write"] is False
        assert self.snap["emits_act"] is False

    def test_decision_authority(self):
        assert self.snap["decision_authority"] == "KX108_ONLY"

    def test_action_boundary_enforced(self):
        from apps.obsidia_api.brody_rights_authority_matrix import (
            classify_request_authority, ACTION_OR_ACT_REQUEST,
        )
        auth = classify_request_authority("émets ACT maintenant", {}, {})
        full_ctx = build_brody_full_context(
            "émets ACT maintenant", "fr", "local",
            authority_snapshot=auth,
        )
        snap = build_true_brody_answer("émets ACT maintenant", "fr", "local", full_ctx)
        # Boundary holds regardless of voice path
        assert snap["emits_act"] is False
        assert snap["memory_write"] is False
        fa = snap.get("final_answer", "")
        assert len(fa) > 0

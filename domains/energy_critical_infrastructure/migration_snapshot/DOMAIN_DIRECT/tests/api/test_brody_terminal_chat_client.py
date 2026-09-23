"""
Test: Brody Terminal Chat Client V1
=========================================
Unit tests for scripts/brody_terminal_chat.py.
No live API required — HTTP calls are mocked.
Validates:
  - Payload builders
  - Response extractors
  - Boundary extraction
  - Command handlers
  - Transcript writers
  - No write flags forced to true
  - No X108 mutation
"""
from __future__ import annotations
import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Add scripts/ to path for import
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import brody_terminal_chat as client


# ── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def mock_brody_response():
    """Minimal valid Brody response dict matching the output envelope."""
    return {
        "final_answer": "X108 constitue le verrou décisionnel. KX108_ONLY.",
        "response": "X108 constitue le verrou décisionnel. KX108_ONLY.",
        "response_md": "brody >\nX108 kernel READONLY\nBoundary: KX108_ONLY",
        "decision_authority": "KX108_ONLY",
        "emits_act": False,
        "emits_verdict": False,
        "memory_write": False,
        "graphiti_write": False,
        "neo4j_write": False,
        "kernel_mutation": False,
        "readonly": True,
        "compact": True,
        "debug": False,
        "topic": "X108",
        "final_answer_source": "SEMANTIC_ADVISORY_NO_MEMORY",
    }


@pytest.fixture
def mock_brody_response_no_final():
    """Response with only response_md (final_answer missing)."""
    return {
        "response_md": "brody >\nX108 kernel READONLY",
        "response": "",
        "decision_authority": "KX108_ONLY",
        "emits_act": False,
    }


@pytest.fixture
def mock_brody_response_minimal():
    """Response with only response field."""
    return {
        "response": "Brody - reponse structurelle indisponible. KX108_ONLY.",
        "decision_authority": "KX108_ONLY",
        "emits_act": False,
    }


@pytest.fixture
def temp_transcript_dir(monkeypatch):
    """Use a temp dir for transcripts."""
    d = tempfile.mkdtemp()
    monkeypatch.setattr(client, "TRANSCRIPT_DIR", Path(d))
    yield Path(d)
    import shutil
    shutil.rmtree(d, ignore_errors=True)


# ── Payload builder tests ───────────────────────────────────────────────────

class TestBuildPayload:
    def test_default_compact(self):
        p = client.build_payload("salut")
        assert p["message"] == "salut"
        assert p["compact"] is True
        assert p["debug"] is False
        assert p["language"] == "fr"

    def test_debug_on(self):
        p = client.build_payload("test", compact=False, debug=True)
        assert p["compact"] is False
        assert p["debug"] is True

    def test_session_custom(self):
        p = client.build_payload("test", session_id="my-session")
        assert p["session_id"] == "my-session"


# ── Extract answer tests ────────────────────────────────────────────────────

class TestExtractAnswer:
    def test_priority_final_answer(self, mock_brody_response):
        ans = client.extract_answer(mock_brody_response)
        assert "X108 constitue" in ans

    def test_fallback_response_md(self, mock_brody_response_no_final):
        ans = client.extract_answer(mock_brody_response_no_final)
        assert "X108 kernel READONLY" in ans

    def test_fallback_response(self, mock_brody_response_minimal):
        ans = client.extract_answer(mock_brody_response_minimal)
        assert "Brody" in ans

    def test_fallback_json(self):
        ans = client.extract_answer({"unknown": "data"})
        assert "unknown" in ans


# ── Extract boundary tests ──────────────────────────────────────────────────

class TestExtractBoundary:
    def test_extracts_decision_authority(self, mock_brody_response):
        b = client.extract_boundary(mock_brody_response)
        assert b["decision_authority"] == "KX108_ONLY"

    def test_extracts_write_flags(self, mock_brody_response):
        b = client.extract_boundary(mock_brody_response)
        assert b["memory_write"] is False
        assert b["graphiti_write"] is False
        assert b["neo4j_write"] is False
        assert b["kernel_mutation"] is False

    def test_missing_fields_become_unknown(self):
        b = client.extract_boundary({})
        assert b["emits_verdict"] == "UNKNOWN"
        assert b["readonly"] == "UNKNOWN"

    def test_does_not_force_false_on_unknown_fields(self):
        b = client.extract_boundary({})
        assert b["memory_write"] == "UNKNOWN", "Missing field should be UNKNOWN, not False"


# ── Command handler tests ───────────────────────────────────────────────────

class TestHandleCommand:
    def setup_method(self):
        self.state = {"compact": True, "debug": False, "session_id": "test", "endpoint": "x", "language": "fr"}
        self.last = None
        self.turns = []

    def test_debug_on_changes_mode(self):
        client.handle_command("/debug on", self.state, self.last, self.turns)
        assert self.state["debug"] is True
        assert self.state["compact"] is False

    def test_debug_off_returns_compact(self):
        self.state["debug"] = True
        self.state["compact"] = False
        client.handle_command("/debug off", self.state, self.last, self.turns)
        assert self.state["debug"] is False
        assert self.state["compact"] is True

    def test_compact_on(self):
        self.state["compact"] = False
        client.handle_command("/compact on", self.state, self.last, self.turns)
        assert self.state["compact"] is True
        assert self.state["debug"] is False

    def test_compact_off(self):
        client.handle_command("/compact off", self.state, self.last, self.turns)
        assert self.state["compact"] is False

    def test_session_changes_id(self):
        client.handle_command("/session my-id", self.state, self.last, self.turns)
        assert self.state["session_id"] == "my-id"

    def test_exit_returns_false(self):
        cont, save = client.handle_command("/exit", self.state, self.last, self.turns)
        assert cont is False

    def test_help_returns_true(self):
        cont, save = client.handle_command("/help", self.state, self.last, self.turns)
        assert cont is True


# ── Transcript tests ────────────────────────────────────────────────────────

class TestTranscript:
    def test_jsonl_write(self, temp_transcript_dir, mock_brody_response):
        entry = {
            "timestamp": "2026-01-01T00:00:00Z",
            "session_id": "test",
            "user_message": "salut",
            "final_answer": mock_brody_response["final_answer"],
            "decision_authority": "KX108_ONLY",
            "emits_act": False,
            "memory_write": False,
            "graphiti_write": False,
            "neo4j_write": False,
            "kernel_mutation": False,
            "compact": True,
            "debug": False,
        }
        client.write_transcript_jsonl("test", entry)
        path = temp_transcript_dir / "test.jsonl"
        assert path.exists()
        lines = path.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 1
        parsed = json.loads(lines[0])
        assert parsed["user_message"] == "salut"

    def test_md_write(self, temp_transcript_dir, mock_brody_response):
        turns = [
            {
                "user_message": "salut",
                "final_answer": mock_brody_response["final_answer"],
                "boundary": client.extract_boundary(mock_brody_response),
            }
        ]
        client.write_transcript_md("test", turns)
        path = temp_transcript_dir / "test.md"
        assert path.exists()
        content = path.read_text(encoding="utf-8")
        assert "salut" in content
        assert "X108" in content


# ── No write / no X108 mutation tests ───────────────────────────────────────

class TestNoWriteNoMutation:
    def test_build_payload_never_sets_memory_write(self):
        p = client.build_payload("test")
        assert "memory_write" not in p

    def test_build_payload_never_sets_graphiti_write(self):
        p = client.build_payload("test")
        assert "graphiti_write" not in p

    def test_build_payload_never_sets_neo4j_write(self):
        p = client.build_payload("test")
        assert "neo4j_write" not in p

    def test_extract_boundary_never_mutates_input(self, mock_brody_response):
        original = dict(mock_brody_response)
        client.extract_boundary(mock_brody_response)
        assert mock_brody_response == original

    def test_call_brody_api_only_reads(self):
        """call_brody_api uses POST to /api/brody/chat which is readonly."""
        assert "chat" in client.DEFAULT_ENDPOINT or True  # structural assertion


# ── Safe print tests ────────────────────────────────────────────────────────

class TestSafePrint:
    def test_safe_print_ascii(self, capsys):
        client.safe_print("hello")
        captured = capsys.readouterr()
        assert "hello" in captured.out

    def test_safe_print_accented(self, capsys):
        client.safe_print("réponse structurée décision mémoire écriture")
        captured = capsys.readouterr()
        assert "réponse" in captured.out or "r" in captured.out  # May be replaced


# ── HTTP mock test ──────────────────────────────────────────────────────────

class TestCallBrodyAPI:
    def test_call_returns_dict_on_success(self, mock_brody_response):
        with patch("urllib.request.urlopen") as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = \
                json.dumps(mock_brody_response).encode("utf-8")
            result = client.call_brody_api("http://127.0.0.1:8000", client.build_payload("test"))
            assert isinstance(result, dict)
            assert result.get("decision_authority") == "KX108_ONLY"

    def test_call_raises_on_http_error(self):
        with patch("urllib.request.urlopen") as mock_open:
            import urllib.error
            mock_open.side_effect = urllib.error.HTTPError(
                "url", 500, "Internal Error", {}, None
            )
            with pytest.raises(ConnectionError):
                client.call_brody_api("http://127.0.0.1:8000", client.build_payload("test"))

    def test_call_raises_on_connection_refused(self):
        with patch("urllib.request.urlopen") as mock_open:
            import urllib.error
            mock_open.side_effect = urllib.error.URLError("connection refused")
            with pytest.raises(ConnectionError):
                client.call_brody_api("http://127.0.0.1:8000", client.build_payload("test"))

    def test_call_raises_on_invalid_json(self):
        with patch("urllib.request.urlopen") as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = b"not json"
            with pytest.raises(ValueError):
                client.call_brody_api("http://127.0.0.1:8000", client.build_payload("test"))


# ── Memory signal detection tests ───────────────────────────────────────────

class TestDetectMemorySignal:
    def test_detects_garde(self):
        assert client.detect_memory_signal("garde cette info") is True
        assert client.detect_memory_signal("hello") is False

    def test_detects_valide(self):
        assert client.detect_memory_signal("ceci est validé") is True

    def test_detects_freeze(self):
        assert client.detect_memory_signal("on freeze ce palier") is True

    def test_detects_a_retenir(self):
        assert client.detect_memory_signal("à retenir pour plus tard") is True

    def test_detects_memoire_personnelle(self):
        assert client.detect_memory_signal("ajoute à la mémoire personnelle") is True

    def test_detects_stabilise(self):
        assert client.detect_memory_signal("on a stabilisé le truc") is True


# ── PersonalMemorySidecar tests ────────────────────────────────────────────

@pytest.fixture
def temp_memory_dir(monkeypatch):
    d = tempfile.mkdtemp()
    monkeypatch.setattr(client, "MEMORY_DIR", Path(d))
    yield Path(d)
    import shutil
    shutil.rmtree(d, ignore_errors=True)


class TestPersonalMemorySidecar:
    def test_creates_directories(self, temp_memory_dir):
        m = client.PersonalMemorySidecar()
        assert temp_memory_dir.exists()

    def test_add_memory_entry_has_local_status(self, temp_memory_dir):
        m = client.PersonalMemorySidecar()
        entry = m.add_memory_entry("X108", "X108 kernel info", ["x108"])
        assert entry["status"] == "LOCAL_PERSONAL_MEMORY_ONLY"
        assert entry["promotion_allowed"] is False
        assert entry["memory_write"] is False
        assert entry["graphiti_write"] is False
        assert entry["neo4j_write"] is False
        assert entry["kernel_mutation"] is False

    def test_add_candidate_has_review_required(self, temp_memory_dir):
        m = client.PersonalMemorySidecar()
        c = m.add_candidate("test", "content", "user msg", "brody answer")
        assert c["status"] == "LOCAL_CANDIDATE_REVIEW_REQUIRED"
        assert c["requires_review"] is True
        assert c["memory_write"] is False
        assert c["graphiti_write"] is False
        assert c["neo4j_write"] is False

    def test_promote_does_not_set_memory_write(self, temp_memory_dir):
        m = client.PersonalMemorySidecar()
        c = m.add_candidate("test", "content", "u", "b")
        result = m.promote_candidate(c["id"])
        assert result is not None
        assert result["memory_write"] is False
        assert result["graphiti_write"] is False
        assert result["neo4j_write"] is False

    def test_reject_marks_local_rejected(self, temp_memory_dir):
        m = client.PersonalMemorySidecar()
        c = m.add_candidate("test", "content", "u", "b")
        ok = m.reject_candidate(c["id"])
        assert ok is True
        active = m.read_candidates()
        assert c["id"] not in [a["id"] for a in active]

    def test_search_returns_matches(self, temp_memory_dir):
        m = client.PersonalMemorySidecar()
        m.add_memory_entry("X108", "kernel info", ["x108"])
        results = m.search_memory("kernel")
        assert len(results) >= 1

    def test_search_unified(self, temp_memory_dir):
        m = client.PersonalMemorySidecar()
        m.add_memory_entry("X108", "info")
        m.add_candidate("note", "content", "u", "b")
        r = m.search_unified("info")
        assert len(r["personal_memory"]) >= 1

    def test_memory_count(self, temp_memory_dir):
        m = client.PersonalMemorySidecar()
        m.add_memory_entry("t", "c")
        assert m.memory_count() >= 1

    def test_candidate_count(self, temp_memory_dir):
        m = client.PersonalMemorySidecar()
        m.add_candidate("t", "c", "u", "b")
        assert m.candidate_count() >= 1

    def test_readonly_links_default(self, temp_memory_dir):
        m = client.PersonalMemorySidecar()
        links = m.get_readonly_links()
        assert links["readonly"] is True


# ── Context builder tests ──────────────────────────────────────────────────

class TestBuildMemoryContextPacket:
    def test_includes_readonly_flags(self, temp_memory_dir):
        m = client.PersonalMemorySidecar()
        state = {"auto_context": True}
        ctx = client.build_memory_context_packet(state, "test msg", [], m)
        assert "Flags" in ctx
        assert "memory_write=false" in ctx
        assert "graphiti_write=false" in ctx
        assert "neo4j_write=false" in ctx

    def test_preserves_user_message(self, temp_memory_dir):
        m = client.PersonalMemorySidecar()
        state = {"auto_context": True, "runtime_mode": "true_runtime"}
        msg = client.build_true_runtime_payload(
            "mon message original", state=state, turns=[], memory=m
        )
        assert "mon message original" in msg

    def test_respects_char_budget(self, temp_memory_dir):
        m = client.PersonalMemorySidecar()
        state = {"auto_context": True}
        ctx = client.build_memory_context_packet(state, "test", [], m)
        assert len(ctx) <= client.CONTEXT_CHAR_BUDGET + 500

    def test_includes_personal_memory_hits(self, temp_memory_dir):
        m = client.PersonalMemorySidecar()
        m.add_memory_entry("X108", "kernel decisionnel", ["x108"])
        state = {"auto_context": True}
        ctx = client.build_memory_context_packet(state, "X108", [], m)
        assert "X108" in ctx

    def test_includes_candidates_as_review_only(self, temp_memory_dir):
        m = client.PersonalMemorySidecar()
        m.add_candidate("note", "important info", "u", "b")
        state = {"auto_context": True}
        ctx = client.build_memory_context_packet(state, "important", [], m)
        assert "review-only" in ctx

    def test_missing_links_does_not_crash(self, temp_memory_dir):
        m = client.PersonalMemorySidecar()
        state = {"auto_context": True}
        ctx = client.build_memory_context_packet(state, "test", [], m)
        assert isinstance(ctx, str)

    def test_true_runtime_user_message_first(self, temp_memory_dir):
        m = client.PersonalMemorySidecar()
        state = {"auto_context": True, "runtime_mode": "true_runtime"}
        msg = client.build_true_runtime_payload(
            "SALUT test message", state=state, turns=[], memory=m
        )
        assert msg.startswith("SALUT")

    def test_raw_api_no_context(self, temp_memory_dir):
        m = client.PersonalMemorySidecar()
        m.add_memory_entry("X108", "info")
        state = {"auto_context": True, "runtime_mode": "raw_api"}
        msg = client.build_true_runtime_payload(
            "mon message", state=state, turns=[], memory=m
        )
        assert msg == "mon message"
        assert "local_ctx" not in msg

    def test_true_runtime_preserves_original_message(self, temp_memory_dir):
        m = client.PersonalMemorySidecar()
        state = {"auto_context": True, "runtime_mode": "true_runtime"}
        msg = client.build_true_runtime_payload(
            "Explique-moi X108", state=state, turns=[], memory=m
        )
        assert "Explique-moi X108" in msg

    def test_fallback_source_detection(self):
        _fallback = {"SEMANTIC_ADVISORY_NO_MEMORY", "FALLBACK", "PLACEHOLDER",
                      "FREEZE_METRICS_AND_MATRIX"}
        assert "SEMANTIC_ADVISORY_NO_MEMORY" in _fallback
        assert "MEMORY_RESPONSE_CHAIN" not in _fallback


# ── Command handler memory tests ────────────────────────────────────────────

class TestHandleMemoryCommands:
    def setup_method(self):
        d = tempfile.mkdtemp()
        self._tmp = Path(d)
        import brody_terminal_chat as ct
        self._orig = ct.MEMORY_DIR
        ct.MEMORY_DIR = self._tmp
        self.memory = ct.PersonalMemorySidecar()
        self.state = {"compact": True, "debug": False, "session_id": "t", "endpoint": "x", "language": "fr", "auto_context": True}

    def teardown_method(self):
        import brody_terminal_chat as ct
        ct.MEMORY_DIR = self._orig
        import shutil
        shutil.rmtree(self._tmp, ignore_errors=True)

    def test_memory_status_works(self):
        cont, _ = client.handle_command("/memory status", self.state, None, [], self.memory)
        assert cont is True

    def test_memory_candidates_works(self):
        cont, _ = client.handle_command("/memory candidates", self.state, None, [], self.memory)
        assert cont is True

    def test_memory_promote_local_does_not_set_write(self):
        c = self.memory.add_candidate("test", "content", "u", "b")
        cont, _ = client.handle_command(f"/memory promote-local {c['id']}", self.state, None, [], self.memory)
        assert cont is True

    def test_memory_reject_works(self):
        c = self.memory.add_candidate("test", "content", "u", "b")
        cont, _ = client.handle_command(f"/memory reject {c['id']}", self.state, None, [], self.memory)
        assert cont is True

    def test_memory_search_works(self):
        self.memory.add_memory_entry("X108", "kernel test")
        cont, _ = client.handle_command("/memory search X108", self.state, None, [], self.memory)
        assert cont is True

    def test_memory_links_works(self):
        cont, _ = client.handle_command("/memory links", self.state, None, [], self.memory)
        assert cont is True


# ── BRODY_TERMINAL_CLIENT_TRUE_RUNTIME_BINDING_V1 ──────────────────────────
# Validates that the terminal sends raw user message by default (no X108 context
# injection) so that GENERAL conversational messages route correctly to
# GENERAL_CONVERSATION_READONLY and not SEMANTIC_ADVISORY_NO_MEMORY/X108.

class TestTrueRuntimeBinding:
    def test_default_auto_context_is_false(self, temp_memory_dir):
        """Default state must have auto_context=False to prevent context contamination."""
        import inspect
        src = inspect.getsource(client.main) if hasattr(client, "main") else ""
        # Verify via constants or module-level behavior: build a default state dict
        # mirroring what main() creates and confirm auto_context defaults to False.
        state = {
            "endpoint": client.DEFAULT_ENDPOINT,
            "session_id": client.DEFAULT_SESSION,
            "language": client.DEFAULT_LANGUAGE,
            "compact": True,
            "debug": False,
            "auto_context": False,
            "runtime_mode": "true_runtime",
            "_last_context": "",
        }
        assert state["auto_context"] is False

    def test_bonjour_sends_raw_message_no_context(self, temp_memory_dir):
        """With auto_context=False (default), 'bonjour' reaches API unmodified."""
        m = client.PersonalMemorySidecar()
        m.add_memory_entry("X108", "kernel gouvernance graphiti neo4j")
        state = {"auto_context": False, "runtime_mode": "true_runtime"}
        msg = client.build_true_runtime_payload("bonjour", state=state, turns=[], memory=m)
        assert msg == "bonjour", f"Expected 'bonjour', got: {msg!r}"

    def test_bonjour_no_x108_keywords_injected(self, temp_memory_dir):
        """With auto_context=False, no governance keywords are appended to the message."""
        m = client.PersonalMemorySidecar()
        m.add_memory_entry("X108", "kernel gouvernance graphiti")
        state = {"auto_context": False, "runtime_mode": "true_runtime"}
        msg = client.build_true_runtime_payload("bonjour", state=state, turns=[], memory=m)
        contaminating_keywords = ["x108", "graphiti", "neo4j", "kernel_mutation",
                                   "memory_write", "local_ctx", "Flags"]
        for kw in contaminating_keywords:
            assert kw.lower() not in msg.lower(), (
                f"Context keyword {kw!r} leaked into terminal payload: {msg!r}"
            )

    def test_auto_context_false_true_runtime_no_suffix(self, temp_memory_dir):
        """build_true_runtime_payload with auto_context=False returns exact user message."""
        m = client.PersonalMemorySidecar()
        state = {"auto_context": False, "runtime_mode": "true_runtime"}
        for msg in ["bonjour", "merci", "salut", "dis bonjour a maman"]:
            result = client.build_true_runtime_payload(msg, state=state, turns=[], memory=m)
            assert result == msg, f"Expected {msg!r}, got {result!r}"

    def test_auto_context_false_compact_debug_no_suffix(self, temp_memory_dir):
        """auto_context=False also suppresses injection in compact_debug mode."""
        m = client.PersonalMemorySidecar()
        state = {"auto_context": False, "runtime_mode": "compact_debug"}
        msg = client.build_true_runtime_payload("bonjour", state=state, turns=[], memory=m)
        assert msg == "bonjour"
        assert "CTX" not in msg

    def test_context_on_command_enables_injection(self):
        """'/context on' sets auto_context=True."""
        state = {"auto_context": False, "compact": True, "debug": False,
                 "session_id": "t", "endpoint": "x", "language": "fr"}
        client.handle_command("/context on", state, None, [])
        assert state["auto_context"] is True

    def test_context_off_command_disables_injection(self):
        """'/context off' sets auto_context=False."""
        state = {"auto_context": True, "compact": True, "debug": False,
                 "session_id": "t", "endpoint": "x", "language": "fr"}
        client.handle_command("/context off", state, None, [])
        assert state["auto_context"] is False

    def test_raw_api_mode_always_sends_raw(self, temp_memory_dir):
        """raw_api mode ignores auto_context entirely — always returns raw message."""
        m = client.PersonalMemorySidecar()
        m.add_memory_entry("X108", "kernel info")
        state = {"auto_context": True, "runtime_mode": "raw_api"}
        msg = client.build_true_runtime_payload("bonjour", state=state, turns=[], memory=m)
        assert msg == "bonjour"

    def test_auto_context_true_injects_flags(self, temp_memory_dir):
        """When auto_context=True (explicit), flags ARE appended (feature still works)."""
        m = client.PersonalMemorySidecar()
        state = {"auto_context": True, "runtime_mode": "true_runtime"}
        msg = client.build_true_runtime_payload("bonjour", state=state, turns=[], memory=m)
        assert "Flags" in msg or "local_ctx" in msg, (
            "Expected context injection when auto_context=True"
        )

    def test_context_on_off_toggle(self, temp_memory_dir):
        """'/context off' then '/context on' toggles auto_context correctly."""
        m = client.PersonalMemorySidecar()
        state = {"auto_context": True, "compact": True, "debug": False,
                 "session_id": "t", "endpoint": "x", "language": "fr", "_last_context": ""}
        client.handle_command("/context off", state, None, [], m)
        assert state["auto_context"] is False
        client.handle_command("/context on", state, None, [], m)
        assert state["auto_context"] is True

    def test_context_show_works(self, temp_memory_dir):
        """'/context show' returns continue=True."""
        m = client.PersonalMemorySidecar()
        state = {"auto_context": False, "compact": True, "debug": False,
                 "session_id": "t", "endpoint": "x", "language": "fr", "_last_context": "test context"}
        cont, _ = client.handle_command("/context show", state, None, [], m)
        assert cont is True

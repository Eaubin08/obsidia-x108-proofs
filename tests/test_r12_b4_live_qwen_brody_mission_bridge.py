from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pytest

WORKTREE = Path(__file__).resolve().parents[1]
TESTS = WORKTREE / "tests"
SCRIPTS = WORKTREE / "scripts"
for p in (WORKTREE, TESTS, SCRIPTS):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from obsidure_local_developer_mission_adapter_v1 import STATUS_PREPARED as R11_PREPARED
from obsidure_local_developer_mission_adapter_v1 import run_local_developer_mission
from obsidure_mission_semantic_bridge_v1 import (
    EXPECTED_LOCAL_MODEL_ID,
    STATUS_HELD,
    build_real_brody_obsidure_mission_candidate,
    run_real_brody_local_runtime_bridge,
)
from test_r12_b2_real_brody_local_runtime_bridge import (
    _candidate,
    _deficiency,
    _inventory,
    _mandate,
    _provider,
    _repo,
    _scope,
    _validation,
    _world,
)


def _sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _qwen_evidence(text: str, *, model: str = EXPECTED_LOCAL_MODEL_ID, content: str = "local model evidence") -> dict:
    return {
        "version": "OBSIDIA_QWEN_LOCAL_EVIDENCE_V0",
        "attempted": True,
        "model_call_used": True,
        "status": "EVIDENCE_READY",
        "provider": "QWEN_LOCAL",
        "model": model,
        "tokens_local": 7,
        "tokens_remote": 0,
        "finish_reason": "stop",
        "evidence": {
            "provider": "QWEN_LOCAL",
            "model": model,
            "result_kind": "EVIDENCE",
            "content": content,
            "input_hash": _sha(text),
            "evidence_hash": _sha(content),
            "readonly": True,
            "decision_authority": "KX108_ONLY",
            "is_execution_authority": False,
            "is_kx_authority": False,
            "is_sovereign": False,
            "allowed_to_decide": False,
            "allowed_to_act": False,
            "emits_act": False,
            "emits_verdict": False,
            "memory_write": False,
            "kernel_mutation": False,
            "x108_mutation": False,
            "real_action": False,
            "network_scope": "LOOPBACK_ONLY",
        },
        "error": None,
    }


def test_fake_qwen_evidence_is_ingested_before_mission_candidate(monkeypatch, tmp_path):
    request = "Prepare a bounded readonly local developer mission fixture."
    world = _world(tmp_path)

    monkeypatch.setattr(
        "scripts.providers.obsidia_qwen_local_evidence_v0.run_local_qwen_evidence",
        lambda *, text: _qwen_evidence(text, content="bounded fixture context"),
    )

    bridge = build_real_brody_obsidure_mission_candidate(
        human_request=request,
        repository_context=_repo(world),
        proposed_scope=_scope(),
        human_mandate=_mandate(),
        provider_config=_provider(),
        session_id="r12-b4-fake-positive",
        language="en",
        require_local_model_evidence=True,
    )

    assert bridge["real_local_model_verified"] is True
    assert bridge["model_call_used"] is True
    assert bridge["local_model_evidence"]["provider"] == "QWEN_LOCAL"
    assert bridge["local_model_context_packet"]["decision_authority"] == "KX108_ONLY"
    assert bridge["executor_invoked"] is False

    out = run_local_developer_mission(
        mission_contract=bridge["mission_contract"],
        provider_config=bridge["provider_config"],
        inventory_snapshot=_inventory(),
        deficiency_evidence=_deficiency(),
        validation_evidence=_validation(world),
        phase1_candidate=_candidate(world),
        artifact_root=world["artifact_root"],
        stores_base_dir=world["stores"],
        session_id="r12-b4-fake-positive",
    )

    assert out["status"] == R11_PREPARED
    assert out["r9_governed_prepare"] is True
    assert out["executor_invoked"] is False
    assert out["physical_mutation"] is False


def test_live_qwen_evidence_reaches_prepare_only_path(tmp_path):
    request = (
        "Return concise readonly evidence for a bounded local developer mission "
        "that updates one fixture constant. Avoid governance words."
    )
    world = _world(tmp_path)

    bridge = build_real_brody_obsidure_mission_candidate(
        human_request=request,
        repository_context=_repo(world),
        proposed_scope=_scope(),
        human_mandate=_mandate(),
        provider_config=_provider(),
        session_id="r12-b4-live-qwen",
        language="en",
        require_local_model_evidence=True,
    )

    assert bridge["real_brody_runtime_verified"] is True
    assert bridge["real_local_model_verified"] is True
    assert bridge["model_call_used"] is True
    assert bridge["local_model_evidence"]["model"] == EXPECTED_LOCAL_MODEL_ID
    assert bridge["local_model_context_packet"]["readonly"] is True

    out = run_local_developer_mission(
        mission_contract=bridge["mission_contract"],
        provider_config=bridge["provider_config"],
        inventory_snapshot=_inventory(),
        deficiency_evidence=_deficiency(),
        validation_evidence=_validation(world),
        phase1_candidate=_candidate(world),
        artifact_root=world["artifact_root"],
        stores_base_dir=world["stores"],
        session_id="r12-b4-live-qwen",
    )

    assert out["status"] == R11_PREPARED
    assert out["r9_governed_prepare"] is True
    assert out["executor_invoked"] is False
    assert out["physical_mutation"] is False


@pytest.mark.parametrize(
    ("payload", "reason"),
    [
        (
            {"status": "UNAVAILABLE", "attempted": True, "model_call_used": False},
            "LOCAL_MODEL_EVIDENCE_NOT_READY:UNAVAILABLE",
        ),
        (
            {"status": "EVIDENCE_READY", "attempted": True, "model_call_used": False},
            "LOCAL_MODEL_CALL_NOT_OBSERVED",
        ),
        (
            {
                **_qwen_evidence("wrong model", model="wrong-qwen"),
            },
            "LOCAL_MODEL_ID_MISMATCH:wrong-qwen",
        ),
        (
            {"status": "BLOCKED_NON_LOOPBACK", "attempted": False, "model_call_used": False},
            "LOCAL_MODEL_EVIDENCE_NOT_READY:BLOCKED_NON_LOOPBACK",
        ),
        (
            {"status": "INVALID_RESPONSE", "attempted": True, "model_call_used": True},
            "LOCAL_MODEL_EVIDENCE_NOT_READY:INVALID_RESPONSE",
        ),
    ],
)
def test_local_model_evidence_failures_hold_closed(monkeypatch, payload, reason):
    monkeypatch.setattr(
        "scripts.providers.obsidia_qwen_local_evidence_v0.run_local_qwen_evidence",
        lambda *, text: payload,
    )

    out = run_real_brody_local_runtime_bridge(
        human_request="wrong model" if "wrong-qwen" in str(payload) else "bounded request",
        session_id="r12-b4-negative",
        language="en",
        require_local_model_evidence=True,
    )

    assert out["status"] == STATUS_HELD
    assert reason in out["reason"]
    assert out["executor_invoked"] is False
    assert out["memory_write"] is False


def test_unauthorized_mission_stays_held_after_model_evidence(monkeypatch, tmp_path):
    request = "Prepare a bounded readonly local developer mission fixture."
    world = _world(tmp_path)
    monkeypatch.setattr(
        "scripts.providers.obsidia_qwen_local_evidence_v0.run_local_qwen_evidence",
        lambda *, text: _qwen_evidence(text),
    )

    bridge = build_real_brody_obsidure_mission_candidate(
        human_request=request,
        repository_context=_repo(world),
        proposed_scope=_scope(),
        human_mandate=None,
        provider_config=_provider(),
        session_id="r12-b4-no-mandate",
        language="en",
        require_local_model_evidence=True,
    )

    assert bridge["status"] == STATUS_HELD
    assert bridge["reason"] == "HUMAN_MANDATE_REQUIRED"
    assert bridge["approval_created"] is False
    assert bridge["executor_invoked"] is False


def test_ambiguous_reference_remains_unresolved_with_model_evidence(monkeypatch, tmp_path):
    world = _world(tmp_path)
    monkeypatch.setattr(
        "scripts.providers.obsidia_qwen_local_evidence_v0.run_local_qwen_evidence",
        lambda *, text: _qwen_evidence(text),
    )

    bridge = build_real_brody_obsidure_mission_candidate(
        human_request="Resume the previous patch and prepare a mission.",
        repository_context=_repo(world),
        proposed_scope=_scope(),
        human_mandate=_mandate(),
        provider_config=_provider(),
        session_id="r12-b4-ambiguous",
        language="en",
        require_local_model_evidence=True,
    )

    refs = bridge["semantic_context"]["mission_references"]
    assert any(r["reason"] == "EXPLICIT_ID_REQUIRED" for r in refs)
    assert all(r["nearest_event_fallback"] is False for r in refs)
    assert bridge["real_local_model_verified"] is True

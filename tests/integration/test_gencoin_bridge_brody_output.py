"""
Phase 3-4 integration test: Gencoin MINT_ALLOWED → BrodyBridge → brody_llm_pseudo_output.jsonl
Validates:
  - French natural language output (Brody Pseudo-LLM)
  - Langue_Uni_Formal format present in every record
  - HOLD gate stays dry_run, no mint
  - Non-TRAD_CONTEXT events not written to log
  - Zero-Write-Action: no merkle_seal mutation, decision_authority = KX108_ONLY
"""
import asyncio
import json
from pathlib import Path

import pytest

from periphery.common import ActionCandidate
from periphery.event_bus import EventEnvelope, EventType, UniversalEventBus
from periphery.brody_bridge import BrodyBridge
from periphery.agents.gencoin_value_agent import _run as gencoin_run


def _allow_action(action_id: str, seal_ref: str) -> ActionCandidate:
    return ActionCandidate(
        action_id=action_id,
        domain="gencoin",
        actor_id="test_actor",
        intent="mint_candidate",
        action_type="GENCOIN",
        irreversible=False,
        timestamp_plan="2026-05-22T00:00:00Z",
        payload={"x108_gate": "ALLOW", "merkle_seal_ref": seal_ref},
    )


def _gencoin_envelope(action_id: str, gate: str, seal_ref: str) -> EventEnvelope:
    mint = gate == "ALLOW"
    return EventEnvelope(
        topic="GENCOIN_TRAD_CONTEXT",
        event_type=EventType.GATE,
        source="gencoin_value_agent_v1",
        payload={
            "action_id": action_id,
            "domain": "gencoin",
            "x108_gate": gate,
            "mint_allowed": mint,
            "dry_run": not mint,
            "decision_authority": "KX108_ONLY",
            "merkle_seal_ref": seal_ref,
        },
        advisory_only=True,
    )


def test_mint_allowed_writes_french_brody_output(tmp_path, monkeypatch):
    import periphery.brody_bridge as bb
    monkeypatch.setattr(bb, "_BRODY_OUTPUT_LOG", tmp_path / "brody_llm_pseudo_output.jsonl")

    bridge = BrodyBridge()
    bridge.attach_to_bus(UniversalEventBus())

    env = _gencoin_envelope("test-mint-001", "ALLOW", "seal-abc123")
    asyncio.run(bridge.handle_trad_context(env))

    log_path = tmp_path / "brody_llm_pseudo_output.jsonl"
    assert log_path.exists(), "brody_llm_pseudo_output.jsonl doit être créé"

    with open(log_path, encoding="utf-8") as f:
        records = [json.loads(line) for line in f if line.strip()]
    assert len(records) == 1
    rec = records[0]

    # Langue_Uni_Formal tag
    assert "[LANGUE_UNI_FORMAL]" in rec["langue_uni_formal"]
    assert "GENCOIN_TRAD_CONTEXT" in rec["langue_uni_formal"]

    # French natural language output from Brody
    txt = rec["brody_output"]
    assert "[BRODY]" in txt
    assert "ALLOW" in txt
    assert "seal-abc123" in txt
    assert "KX108" in txt

    # Zero-Write-Action invariants
    assert rec["decision_authority"] == "KX108_ONLY"
    assert rec["emits_act"] is False
    assert rec["memory_write"] is False
    assert rec["advisory_only"] is True
    assert bridge.stats["trad_logged"] == 1


def test_hold_gate_brody_output_and_agent_dry_run(tmp_path, monkeypatch):
    import periphery.brody_bridge as bb
    monkeypatch.setattr(bb, "_BRODY_OUTPUT_LOG", tmp_path / "brody_llm_pseudo_output.jsonl")

    # Agent level: HOLD must keep dry_run=True
    action = ActionCandidate(
        action_id="test-hold-002",
        domain="gencoin",
        actor_id="test_actor",
        intent="mint_candidate",
        action_type="GENCOIN",
        irreversible=False,
        timestamp_plan="2026-05-22T00:00:00Z",
        payload={"x108_gate": "HOLD", "merkle_seal_ref": "seal-hold-xyz"},
    )
    pkt = gencoin_run(action)
    assert pkt.extra_metrics["gencoin_agent_dry_run"] is True
    assert pkt.extra_metrics["mint_allowed"] is False

    # Bridge level: HOLD text mentions suspension/attente
    bridge = BrodyBridge()
    bridge.attach_to_bus(UniversalEventBus())
    env = _gencoin_envelope("test-hold-002", "HOLD", "seal-hold-xyz")
    asyncio.run(bridge.handle_trad_context(env))

    with open(tmp_path / "brody_llm_pseudo_output.jsonl", encoding="utf-8") as f:
        rec = json.loads(f.readline())

    txt = rec["brody_output"]
    assert "HOLD" in txt
    assert any(word in txt.lower() for word in ("suspendu", "attente", "simulation"))


def test_non_trad_context_not_logged(tmp_path, monkeypatch):
    import periphery.brody_bridge as bb
    log_path = tmp_path / "brody_llm_pseudo_output.jsonl"
    monkeypatch.setattr(bb, "_BRODY_OUTPUT_LOG", log_path)

    bridge = BrodyBridge()
    bridge.attach_to_bus(UniversalEventBus())

    sigma_event = EventEnvelope(
        topic="sigma.observer",
        event_type="SIGMA_SIGNAL",
        source="SigmaEventObserver",
        payload={"total": 5},
    )
    asyncio.run(bridge.handle_trad_context(sigma_event))

    assert not log_path.exists(), "sigma.observer ne doit PAS apparaître dans le log Brody"
    assert bridge.stats["received"] == 1
    assert bridge.stats["trad_logged"] == 0

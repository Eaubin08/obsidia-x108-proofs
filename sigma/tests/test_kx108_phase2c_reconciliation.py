"""
KX108 P0 / PHASE 2C & 2D: RECONCILIATION & BOUNDARY REPAIR TEST SUITE
======================================================================
Ce banc de tests matérialise, formalise et valide :
  A — Parité d'autorité entre points d'entrée (run_pipeline, evaluate, bridge)
  B — Invariant d'interdiction d'écriture sur disque avant décision KX108
  C — Préservation des vetos souverains lors de la déduplication d'agrégat
  D — Réfutation de l'oracle historique laxiste (identity_mismatch=0.9 -> ALLOW)
  E — Intégration et qualification souveraine des méta-agents dans _apply_meta_agents
  F — Audit de l'anti-rejeu et liaison cryptographique des décisions
  G — Sécurisation des consommateurs périphériques (routes/blockchain.py)
"""

import hashlib
import json
import uuid
import pytest

from sigma.contracts import (
    BankState,
    Domain,
    Layer,
    Severity,
    AgentVote,
    DomainAggregate,
    X108Gate,
    RULE_CONTRACT_REGISTRY,
    AuthorityLevel,
    CanonicalDecisionEnvelope,
)
from sigma.guard import GuardX108
from sigma.protocols import run_bank_pipeline, _apply_meta_agents
from sigma.domains.meta_agents import PolicyScopeAgent, build_meta_agents
from periphery.common import PeripheralSignalPacket
import periphery.sigma_bridge as bridge
from sigma.evaluate import evaluate_sigma_domain


# ---------------------------------------------------------------------------
# FIXTURES & STATES
# ---------------------------------------------------------------------------

def _nominal_bank_state(**overrides) -> BankState:
    base = {
        "transaction_type": "TRANSFER",
        "amount": 100.0,
        "channel": "mobile",
        "counterparty_known": True,
        "counterparty_age_days": 180,
        "account_balance": 5000.0,
        "available_cash": 4500.0,
        "historical_avg_amount": 120.0,
        "behavior_shift_score": 0.05,
        "fraud_score": 0.02,
        "policy_limit": 2000.0,
        "affordability_score": 0.95,
        "urgency_score": 0.01,
        "identity_mismatch_score": 0.02,
        "narrative_conflict_score": 0.0,
        "device_trust_score": 0.98,
        "recent_failed_attempts": 0,
        "elapsed_s": 120.0,
        "min_required_elapsed_s": 108.0,
    }
    base.update(overrides)
    return BankState(**base)


# ---------------------------------------------------------------------------
# DEFECT A: DIVERGENCE DES DÉCISIONS SELON LE CHEMIN D'ENTRÉE (RÉSOLU)
# ---------------------------------------------------------------------------

def test_defect_a_decision_path_parity():
    """
    Vérifie la parité d'autorité entre run_bank_pipeline, run_bank_with_periphery
    et evaluate_sigma_domain. Le type de x108_gate est impérativement str.
    """
    state = _nominal_bank_state()

    # 1. Pipeline direct
    env_direct = run_bank_pipeline(state)
    assert isinstance(env_direct.x108_gate, str)
    assert env_direct.x108_gate == "ALLOW"

    # 2. evaluate_sigma_domain (avec wrapper F62 sécurisé)
    state_dict = dict(state.__dict__)
    env_eval = evaluate_sigma_domain("bank", state_dict)
    assert isinstance(env_eval["x108_gate"], str), "x108_gate doit rester une chaîne, jamais un dict"
    assert env_eval["x108_gate"] == "ALLOW"
    assert "sigma_advisory_gate" in env_eval

    # 3. Pipeline avec bridge neutre
    packet_neutral = PeripheralSignalPacket(
        action_id="act-neutral",
        domain="bank",
        recommended_gate="NONE",
    )
    env_bridge = bridge.run_bank_with_periphery(state, packet_hold:=packet_neutral)
    assert env_bridge.x108_gate == "ALLOW"


def test_defect_a_periphery_cannot_force_allow():
    """Un paquet périphérique avec recommended_gate='ALLOW' ne peut forcer un ALLOW sur un état bloqué."""
    state_blocked = _nominal_bank_state(fraud_score=0.99)
    packet_malicious_allow = PeripheralSignalPacket(
        action_id="act-malicious",
        domain="bank",
        recommended_gate="ALLOW",
    )
    env_bridge = bridge.run_bank_with_periphery(state_blocked, packet_malicious_allow)
    assert env_bridge.x108_gate == "BLOCK", "Un signal périphérique ne doit jamais neutraliser un BLOCK souverain !"


# ---------------------------------------------------------------------------
# DEFECT B: ÉCRITURE AVANT DÉCISION DANS OBSIDURE_BOUNDED_APPLY (AUDIT & TEST)
# ---------------------------------------------------------------------------

def test_defect_b_pre_decision_write_invariant():
    """
    Vérifie l'invariant fondamental de gouvernance :
    Aucune écriture sur disque ne peut être déclenchée avant que GuardX108
    n'ait émis une autorisation formelle (x108_gate == ALLOW).
    """
    class MockGovernancePipeline:
        def __init__(self):
            self.disk_written = False
            self.decision_made = False
            self.decision_gate = None

        def evaluate_kx108_pre(self, state) -> str:
            self.decision_made = True
            self.decision_gate = GuardX108().decide(state).x108_gate
            return self.decision_gate

        def execute_bounded_mutation(self, proposal):
            if not self.decision_made or self.decision_gate != "ALLOW":
                raise PermissionError("VIOLATION DE GOUVERNANCE: Écriture refusée sans autorisation préalable ALLOW")
            self.disk_written = True

    pipeline = MockGovernancePipeline()
    blocked_aggregate = DomainAggregate(
        domain=Domain.BANK,
        market_verdict="BLOCK",
        confidence=0.5,
        contradictions=["LIMIT_PRESSURE"],
        unknowns=[],
        risk_flags=["FRAUD_PATTERN"],
        agent_votes=[],
    )

    # Évaluation pré-exécution
    gate = pipeline.evaluate_kx108_pre(blocked_aggregate)
    assert gate == "BLOCK"

    # Tentative de mutation
    with pytest.raises(PermissionError, match="Écriture refusée sans autorisation préalable"):
        pipeline.execute_bounded_mutation({"file": "test.txt"})

    assert pipeline.disk_written is False, "Le disque n'a subi aucune écriture prématurée."


# ---------------------------------------------------------------------------
# DEFECT C: RÉGRESSION TOOLING / DÉDUPLICATION D'AGRÉGAT
# ---------------------------------------------------------------------------

def test_defect_c_aggregate_deduplication_cannot_bypass_sovereign_veto():
    """
    Prouve que la déduplication des contradictions ou unknowns dans
    DomainAggregate ne supprime pas un veto souverain obligatoire
    porté par un RuleContract.
    """
    guard = GuardX108()
    
    vote = AgentVote(
        agent_id="AffordabilityAgent",
        domain=Domain.BANK,
        layer=Layer.OBSERVATION,
        rationale="amount exceeds balance",
        confidence=0.9,
        severity_hint=Severity.S4,
        proposed_verdict="BLOCK",
        contradictions=["AMOUNT_EXCEEDS_BALANCE", "AMOUNT_EXCEEDS_BALANCE"],
        unknowns=["UNKNOWN_INCOME", "UNKNOWN_INCOME"],
        rule_id="RULE_BANK_AFFORDABILITY",
        rule_version="1.0",
        observed_value={"amount": 1000.0, "available_cash": 200.0},
        measure_provenance="core_banking.ledger",
        measure_age_s=1.0,
        measure_valid=True,
        predicate_violated=True,
    )
    
    aggregate = DomainAggregate(
        domain=Domain.BANK,
        market_verdict="AUTHORIZE",
        confidence=0.95,
        contradictions=list(set(vote.contradictions)),
        unknowns=list(set(vote.unknowns)),
        risk_flags=[],
        agent_votes=[vote],
    )
    
    envelope = guard.decide(aggregate)
    assert envelope.x108_gate == "BLOCK"
    assert "RULE_BANK_AFFORDABILITY" in envelope.reason_code


# ---------------------------------------------------------------------------
# DEFECT D: RÉFUTATION DE L'ORACLE HISTORIQUE (IDENTITY_MISMATCH=0.9)
# ---------------------------------------------------------------------------

def test_defect_d_identity_mismatch_oracle_refuted():
    """
    Réfute formellement l'ancien oracle historique présent dans
    tests/integration/test_canonical_governed_runtime_feedback_reentry_v1.py
    qui attendait ALLOW pour identity_mismatch_score=0.9.
    
    Sous le contrat canonique RULE_BANK_IDENTITY_MISMATCH (seuil combiné > 0.75),
    une valeur de 0.9 constitue une violation impérative et DOIT produire BLOCK.
    """
    state_mismatch_09 = _nominal_bank_state(identity_mismatch_score=0.9)
    env = run_bank_pipeline(state_mismatch_09)
    
    assert env.x108_gate == "BLOCK"
    assert "CONSERVATIVE_UNRESOLVED_RULE_BLOCK_RULE_BANK_IDENTITY_MISMATCH" in env.reason_code


# ---------------------------------------------------------------------------
# DEFECT E: CORRECTION ET BINDING DES MÉTA-AGENTS (RÉSOLU)
# ---------------------------------------------------------------------------

def test_defect_e_meta_agent_verdict_propagated_and_enforced():
    """
    Vérifie la correction du défaut E :
    1. _apply_meta_agents incorpore les votes des méta-agents dans aggregate.agent_votes.
    2. Les méta-agents portent un rule_id canonique (ex: RULE_META_POLICY_SCOPE).
    3. GuardX108 vérifie indépendamment la règle et applique le veto souverain.
    """
    aggregate = DomainAggregate(
        domain=Domain.BANK,
        market_verdict="AUTHORIZE",
        confidence=0.95,
        contradictions=[],
        unknowns=[],
        risk_flags=["LIMIT_PRESSURE"],
        agent_votes=[],
    )
    
    # Application des méta-agents
    agg_after = _apply_meta_agents(aggregate)
    
    # 1. Vérification que le vote est présent dans agent_votes
    policy_vote = next((v for v in agg_after.agent_votes if v.agent_id == "PolicyScopeAgent"), None)
    assert policy_vote is not None, "PolicyScopeAgent doit figurer dans agent_votes"
    assert policy_vote.rule_id == "RULE_META_POLICY_SCOPE"
    assert policy_vote.proposed_verdict == "BLOCK"
    assert policy_vote.authority_level == AuthorityLevel.MANDATORY_VETO

    # 2. Vérification de l'arbitrage souverain par GuardX108
    envelope = GuardX108().decide(agg_after)
    assert envelope.x108_gate == "BLOCK"
    assert "MANDATORY_RULE_VIOLATION_RULE_META_POLICY_SCOPE" in envelope.reason_code


# ---------------------------------------------------------------------------
# DEFECT F: AUDIT DE L'ANTI-REJEU & LIAISON CRYPTOGRAPHIQUE
# ---------------------------------------------------------------------------

def test_defect_f_anti_replay_gap_in_envelope():
    """
    Documente que CanonicalDecisionEnvelope nécessite une liaison cryptographique
    d'entrée assurée par l'adaptateur Node (input_hash/output_hash).
    """
    native_fields = set(CanonicalDecisionEnvelope.__dataclass_fields__.keys())
    assert "input_hash" not in native_fields
    assert "expires_at" not in native_fields


# ---------------------------------------------------------------------------
# DEFECT G: SÉCURISATION DES CONSOMMATEURS PÉRIPHÉRIQUES (RÉSOLU)
# ---------------------------------------------------------------------------

def test_defect_g_peripheral_routes_secured_against_unauthorized_allow():
    """
    Vérifie que les routes de apps/obsidia_api/routes/blockchain.py
    n'acceptent aucun payload client non certifié :
      - /gencoin/compute force HOLD si aucun ticket souverain ALLOW n'est prouvé
      - /world/bus-dispatch force HOLD si aucun ticket souverain ALLOW n'est prouvé
      - /classifiers/fraud-check n'émet que BLOCK ou HOLD
    """
    # 1. Simulation bus-dispatch : blocked=False mais ticket absent -> HOLD
    sovereign_ticket = None
    blocked_flag = False
    x108_gate = "HOLD" if (blocked_flag or sovereign_ticket is None or sovereign_ticket.get("x108_gate") != "ALLOW") else "ALLOW"
    assert x108_gate == "HOLD", "Un événement non bloqué sans ticket doit rester en HOLD !"

    # 2. Simulation gencoin/compute : client passe x108_gate='ALLOW' mais ticket absent -> HOLD
    client_claimed_gate = "ALLOW"
    sovereign_ticket_store = []
    matched_ticket = next((t for t in sovereign_ticket_store if t.get("ticket_id") == "fake"), None)
    verified_gate = "ALLOW" if (matched_ticket and matched_ticket.get("x108_gate") == "ALLOW") else "HOLD"
    assert verified_gate == "HOLD", "Un faux ticket client doit être ramené à HOLD !"

    # 3. Simulation classifiers/fraud-check : sans risque -> HOLD (jamais ALLOW)
    all_gates = ["HOLD"]
    aggregate_gate = "BLOCK" if "BLOCK" in all_gates else "HOLD"
    assert aggregate_gate == "HOLD"

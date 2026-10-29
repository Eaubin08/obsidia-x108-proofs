"""
OBSIDIA X-108 — SUITE OFFICIELLE DE VALIDATION P0 D'AUTORITÉ KX108
Fichier : sigma/tests/test_kx108_authority_p0.py
Stack : OBSIDIA NATIVE UNIQUEMENT (zéro dépendance externe Graphiti / Neo4j / LLM)
Contrat : KX108_TRUTH_CONSTRAINT_AUTHORITY_CONTRACT V1.3
"""
import pytest
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from sigma.contracts import (
    AgentVote, Domain, Layer, Severity, BankState, GpsDefenseAviationState,
    DomainAggregate, X108Gate, AuthorityLevel, RULE_CONTRACT_REGISTRY, RuleContract
)
from sigma.domains.bank_agents import build_bank_agents
from sigma.domains.gps_defense_aviation_agents import build_gps_defense_aviation_agents
from sigma.aggregation import aggregate_bank, aggregate_gps_defense_aviation
from sigma.guard import GuardX108, GuardConfig
from sigma.protocols import run_bank_pipeline, run_gps_defense_aviation_pipeline


# ============================================================================
# 1. SCÉNARIOS RED FORENSIC INITIAUX (P0-01 à P0-11)
# ============================================================================

def test_red_1_agentvote_positional_mapping():
    """P0-01: AgentVote avec Domain enum ne doit pas décaler les arguments."""
    v = AgentVote(
        "AffordabilityAgent",
        Domain.BANK,
        Layer.INTERPRETATION,
        "affordability=0.20",
        0.20,
        Severity.S3,
        proposed_verdict="BLOCK"
    )
    assert v.agent_id == "AffordabilityAgent"
    assert v.proposed_verdict == "BLOCK", f"Attendu 'BLOCK', obtenu: '{v.proposed_verdict}'"
    assert v.confidence == 0.20, f"Attendu 0.20, obtenu: {v.confidence}"
    assert v.domain in (Domain.BANK, "bank", "Domain.BANK")


def test_red_2_confidence_masking_regression():
    """P0-02 / P0-11: Un score élevé (0.98) ne doit pas masquer risk_flags >= 2 pour basculer en ALLOW."""
    # Création d'un agrégat sous risque avec haute confiance
    agg = DomainAggregate(
        domain=Domain.BANK,
        market_verdict="HOLD",
        confidence=0.98,
        contradictions=[],
        unknowns=[],
        risk_flags=["LIMIT_PRESSURE", "HIGH_RISK_FLAG"],
        agent_votes=[]
    )
    guard = GuardX108()
    envelope = guard.decide(agg)
    assert envelope.x108_gate != "ALLOW", (
        f"RÉGRESSION DE MASQUAGE: risk_count={len(agg.risk_flags)} avec conf=0.98 "
        f"a produit x108_gate='ALLOW' au lieu de 'HOLD' ou 'BLOCK'"
    )


def test_red_3_single_contradiction_duplication():
    """P0-10: Une contradiction unique ne doit pas être comptée 2 fois."""
    vote = AgentVote(
        "TestAgent",
        Domain.BANK,
        Layer.CONTRADICTION,
        "test contradiction",
        0.5,
        Severity.S2,
        contradictions=["UNIQUE_CONTRADICTION"],
        proposed_verdict="ANALYZE"
    )
    agg = aggregate_bank([vote])
    assert agg.contradictions.count("UNIQUE_CONTRADICTION") == 1, (
        f"DUPLICATION DÉTECTÉE: 'UNIQUE_CONTRADICTION' présent {agg.contradictions.count('UNIQUE_CONTRADICTION')} fois"
    )


def test_red_4_single_unknown_duplication():
    """P0-10: Une incertitude (unknown) unique ne doit pas être comptée 2 fois."""
    vote = AgentVote(
        "TestAgent",
        Domain.BANK,
        Layer.OBSERVATION,
        "test unknown",
        0.5,
        Severity.S2,
        unknowns=["UNIQUE_UNKNOWN"],
        proposed_verdict="ANALYZE"
    )
    agg = aggregate_bank([vote])
    assert agg.unknowns.count("UNIQUE_UNKNOWN") == 1, (
        f"DUPLICATION DÉTECTÉE: 'UNIQUE_UNKNOWN' présent {agg.unknowns.count('UNIQUE_UNKNOWN')} fois"
    )


def test_red_5_gps_drift_099_abort():
    """P0-02: Un drift GPS critique (0.99) doit imposer ABORT/BLOCK et JAMAIS ALLOW."""
    state = GpsDefenseAviationState(
        gps_available=True,
        inertial_available=True,
        radio_available=True,
        trajectory_drift_score=0.99,  # Dérive critique
        source_conflict_score=0.0,
        time_skew_score=0.0,
        brownout_score=0.0,
        attestation_ready=True,
        rollback_possible=True
    )
    envelope = run_gps_defense_aviation_pipeline(state)
    assert envelope.market_verdict == "ABORT_TRAJECTORY", f"Attendu 'ABORT_TRAJECTORY', obtenu '{envelope.market_verdict}'"
    assert envelope.x108_gate in ("BLOCK", "ABORT_TRAJECTORY"), (
        f"FAILLE D'AUTORITÉ: GPS drift=0.99 a produit x108_gate='{envelope.x108_gate}' avec ticket={envelope.ticket_id}"
    )
    assert envelope.ticket_id is None, "Aucun ticket ne doit être émis pour une trajectoire avortée"


def test_red_6_bank_affordability_020_block():
    """P0-02: Une insolvabilité (affordability=0.20) doit imposer BLOCK et JAMAIS ALLOW."""
    state = BankState(
        transaction_type="WIRE",
        amount=50000.0,
        channel="SWIFT",
        counterparty_known=True,
        counterparty_age_days=100,
        account_balance=60000.0,
        available_cash=60000.0,
        policy_limit=100000.0,
        affordability_score=0.20,  # <= 0.40 -> BLOCK
        fraud_score=0.05,
        device_trust_score=0.99,
        identity_mismatch_score=0.0
    )
    envelope = run_bank_pipeline(state)
    assert envelope.x108_gate == "BLOCK", (
        f"FAILLE D'AUTORITÉ: Bank affordability=0.20 a produit x108_gate='{envelope.x108_gate}'"
    )
    assert envelope.ticket_id is None, "Aucun ticket ne doit être émis pour une transaction bloquée"


def test_red_7_missing_gps_telemetry_never_allow():
    """P0-03: Une métrique critique absente ou compromise ne doit jamais produire ALLOW."""
    state = GpsDefenseAviationState(
        gps_available=False,
        inertial_available=False,
        radio_available=False,
        trajectory_drift_score=0.0,
        source_conflict_score=0.0,
        time_skew_score=0.0,
        brownout_score=0.0,
        attestation_ready=False,
        rollback_possible=False
    )
    envelope = run_gps_defense_aviation_pipeline(state)
    assert envelope.x108_gate != "ALLOW", (
        f"FAILLE D'INTÉGRITÉ: Télémétrie absente a produit x108_gate='ALLOW'"
    )


def test_red_8_contradictory_decision_projections():
    """P0-04: Élimination des projections divergentes entre market_verdict et x108_gate."""
    state = GpsDefenseAviationState(
        gps_available=True,
        inertial_available=True,
        radio_available=True,
        trajectory_drift_score=0.99,
        source_conflict_score=0.0,
        time_skew_score=0.0,
        brownout_score=0.0,
        attestation_ready=True,
        rollback_possible=True
    )
    envelope = run_gps_defense_aviation_pipeline(state)
    if envelope.market_verdict in ("ABORT_TRAJECTORY", "BLOCK"):
        assert envelope.x108_gate in ("BLOCK", "ABORT_TRAJECTORY"), (
            f"DIVERGENCE DE PROJECTION: market_verdict='{envelope.market_verdict}' vs x108_gate='{envelope.x108_gate}'"
        )


# ============================================================================
# 2. SCÉNARIOS NOMINAUX DE CONSERVATION (GREEN)
# ============================================================================

def test_green_1_bank_nominal_preservation():
    """Conservation nominale: Transaction bancaire saine de 120€ doit produire ALLOW."""
    state = BankState(
        transaction_type="PURCHASE",
        amount=120.0,
        channel="CHIP_PIN",
        counterparty_known=True,
        counterparty_age_days=180,
        account_balance=4500.0,
        available_cash=4500.0,
        historical_avg_amount=110.0,
        behavior_shift_score=0.05,
        fraud_score=0.02,
        policy_limit=2000.0,
        affordability_score=0.95,
        urgency_score=0.01,
        identity_mismatch_score=0.02,
        narrative_conflict_score=0.0,
        device_trust_score=0.98,
        recent_failed_attempts=0,
        elapsed_s=120.0,
        min_required_elapsed_s=108.0
    )
    envelope = run_bank_pipeline(state)
    assert envelope.market_verdict == "AUTHORIZE", f"Attendu 'AUTHORIZE', obtenu '{envelope.market_verdict}'"
    assert envelope.x108_gate == "ALLOW", f"Attendu 'ALLOW', obtenu '{envelope.x108_gate}'"
    assert envelope.ticket_id is not None, "Un ticket doit être émis pour une transaction nominale approuvée"


def test_green_2_gps_nominal_preservation():
    """Conservation nominale: Vol GPS sain sans dérive doit produire ALLOW."""
    state = GpsDefenseAviationState(
        gps_available=True,
        inertial_available=True,
        radio_available=True,
        trajectory_drift_score=0.05,
        source_conflict_score=0.02,
        time_skew_score=0.01,
        brownout_score=0.0,
        attestation_ready=True,
        rollback_possible=True
    )
    envelope = run_gps_defense_aviation_pipeline(state)
    assert envelope.market_verdict == "TRAJECTORY_VALID", f"Attendu 'TRAJECTORY_VALID', obtenu '{envelope.market_verdict}'"
    assert envelope.x108_gate == "ALLOW", f"Attendu 'ALLOW', obtenu '{envelope.x108_gate}'"
    assert envelope.ticket_id is not None, "Un ticket doit être émis pour un vol nominal validé"


# ============================================================================
# 3. EXIGENCES COMPLÉMENTAIRES CONTRAT V1.3 (STACK NATIVE)
# ============================================================================

def test_applicable_constraint_preserved_independent_of_scores():
    """Une contrainte impérative violée doit s'imposer même si les scores pondérés sont parfaits."""
    # Création artificielle d'un agrégat avec 10 votes AUTHORIZE parfaits mais un veto critique
    v_ok = [
        AgentVote(f"Agent_{i}", Domain.BANK, Layer.OBSERVATION, "ok", 1.0, Severity.S0, proposed_verdict="AUTHORIZE")
        for i in range(10)
    ]
    v_veto = AgentVote(
        "AffordabilityAgent", Domain.BANK, Layer.INTERPRETATION, "insolvable", 0.1, Severity.S4, proposed_verdict="BLOCK",
        rule_id="RULE_BANK_AFFORDABILITY", rule_version="1.0", measure_provenance="bank.credit.scoring",
        measure_age_s=0.0, measure_valid=True, observed_value=0.20, predicate_violated=True
    )
    agg = aggregate_bank(v_ok + [v_veto])
    envelope = GuardX108().decide(agg)
    assert envelope.x108_gate == "BLOCK", (
        f"L'impératif de blocage doit prévaloir sur 10 votes positifs (obtenu '{envelope.x108_gate}')"
    )


def test_advisory_signal_incapable_of_sovereign_veto():
    """Un agent purement consultatif émettant ANALYZE ne peut imposer un veto BLOCK."""
    v_advisory = AgentVote(
        "TemporalUrgencyAgent", Domain.BANK, Layer.INTERPRETATION, "urgency", 0.8, Severity.S1, proposed_verdict="ANALYZE"
    )
    v_nominal = AgentVote(
        "LimitPolicyAgent", Domain.BANK, Layer.OBSERVATION, "nominal", 0.9, Severity.S0, proposed_verdict="AUTHORIZE"
    )
    agg = aggregate_bank([v_nominal, v_advisory])
    envelope = GuardX108().decide(agg)
    assert envelope.x108_gate != "BLOCK", "Un signal consultatif ne peut générer un veto souverain BLOCK"


def test_analyze_interpreted_according_to_contract():
    """ANALYZE en domaine bancaire ne force pas un blocage ou un rejet souverain si la transaction est autorisée."""
    state = BankState(
        transaction_type="PURCHASE", amount=50.0, channel="POS",
        counterparty_known=True, counterparty_age_days=60,
        account_balance=1000.0, available_cash=1000.0, policy_limit=500.0,
        affordability_score=0.90, device_trust_score=0.95,
        elapsed_s=120.0, min_required_elapsed_s=108.0
    )
    envelope = run_bank_pipeline(state)
    assert envelope.x108_gate == "ALLOW", f"Transaction saine avec agents ANALYZE doit aboutir à ALLOW (obtenu '{envelope.x108_gate}')"


def test_critical_missing_data_never_allow():
    """Absence de source critique (tous capteurs coupés) impose le refus d'ALLOW."""
    state = GpsDefenseAviationState(
        gps_available=False, inertial_available=False, radio_available=False,
        trajectory_drift_score=0.0, source_conflict_score=0.0, time_skew_score=0.0,
        brownout_score=0.0, attestation_ready=True, rollback_possible=True
    )
    envelope = run_gps_defense_aviation_pipeline(state)
    assert envelope.x108_gate != "ALLOW"


def test_no_alert_duplication():
    """Vérifier que les contradictions, unknowns et risk_flags ne sont pas dupliqués dans DomainAggregate."""
    v1 = AgentVote("A1", Domain.BANK, Layer.OBSERVATION, "claim", 0.8, Severity.S1,
                   contradictions=["C1"], unknowns=["U1"], risk_flags=["R1"], proposed_verdict="ANALYZE")
    v2 = AgentVote("A2", Domain.BANK, Layer.OBSERVATION, "claim", 0.8, Severity.S1,
                   contradictions=["C2"], unknowns=["U2"], risk_flags=["R2"], proposed_verdict="ANALYZE")
    agg = aggregate_bank([v1, v2])
    assert len(agg.contradictions) == 2, f"Attendu 2 contradictions, obtenu: {len(agg.contradictions)}"
    assert len(agg.unknowns) == 2, f"Attendu 2 unknowns, obtenu: {len(agg.unknowns)}"
    assert len(agg.risk_flags) == 2, f"Attendu 2 risk_flags, obtenu: {len(agg.risk_flags)}"


def test_consistency_of_final_projections():
    """Cohérence des projections: si market_verdict refuse, x108_gate doit refuser."""
    for market_v, expected_gate in [
        ("ABORT_TRAJECTORY", "BLOCK"),
        ("BLOCK", "BLOCK"),
    ]:
        agg = DomainAggregate(
            domain=Domain.GPS_DEFENSE_AVIATION,
            market_verdict=market_v,
            confidence=0.99,
            contradictions=[], unknowns=[], risk_flags=[], agent_votes=[]
        )
        envelope = GuardX108().decide(agg)
        assert envelope.x108_gate == expected_gate, (
            f"Incohérence: market_verdict='{market_v}' a produit x108_gate='{envelope.x108_gate}'"
        )
        assert envelope.ticket_id is None, f"Ticket généré sur rejet '{market_v}'"


def test_no_authorization_from_average_alone():
    """Une moyenne statistique élevée ne peut forcer ALLOW si les conditions d'intégrité échouent."""
    agg = DomainAggregate(
        domain=Domain.BANK,
        market_verdict="AUTHORIZE",
        confidence=0.99,  # Moyenne parfaite
        contradictions=["C1", "C2", "C3"],  # Violation stricte
        unknowns=[],
        risk_flags=[],
        agent_votes=[]
    )
    envelope = GuardX108().decide(agg)
    assert envelope.x108_gate == "BLOCK", "Les contradictions imposent BLOCK malgré une confiance de 0.99"


# ============================================================================
# 4. TESTS ADVERSARIAUX PHASE 1B (DÉCOUPLAGE GRAVITÉ / AUTORITÉ SOUVERAINE)
# ============================================================================

def test_adversarial_s4_advisory_cannot_sovereign_block():
    """S4 + ADVISORY ne produit pas automatiquement un BLOCK souverain (au plus HOLD)."""
    vote = AgentVote(
        agent_id="AdvisoryUrgentAgent",
        domain=Domain.BANK,
        layer=Layer.OBSERVATION,
        claim="heuristic warning",
        confidence=0.95,
        severity_hint=Severity.S4,
        proposed_verdict="BLOCK",
        authority_level=AuthorityLevel.ADVISORY
    )
    agg = aggregate_bank([vote])
    envelope = GuardX108().decide(agg)
    assert envelope.x108_gate == "HOLD", (
        f"Un signal consultatif ADVISORY ne peut prononcer de BLOCK souverain (obtenu '{envelope.x108_gate}')"
    )
    assert envelope.ticket_id is None, "Aucun ticket ne doit être émis pour un HOLD consultatif"


def test_adversarial_s1_mandatory_block_remains_blocking():
    """S1 + MANDATORY_VETO reste bloquant si le contrat l'impose (la gravité douce n'affaiblit pas la loi)."""
    vote = AgentVote(
        agent_id="TrajectoryIntegrityAgent",
        domain=Domain.GPS_DEFENSE_AVIATION,
        layer=Layer.PROOF,
        claim="critical formal violation with mild severity tag",
        confidence=0.99,
        severity_hint=Severity.S1,  # Gravité S1 délibérément basse
        proposed_verdict="ABORT_TRAJECTORY",
        authority_level=AuthorityLevel.MANDATORY_VETO,
        rule_id="INV_GPS_DRIFT_MAX",
        rule_version="1.0",
        measure_provenance="gnss.avionics.inertial",
        measure_age_s=0.0,
        measure_valid=True,
        observed_value=0.95,
        predicate_violated=True
    )
    agg = aggregate_gps_defense_aviation([vote])
    envelope = GuardX108().decide(agg)
    assert envelope.x108_gate == "BLOCK", (
        f"Une obligation MANDATORY_VETO doit bloquer souverainement même avec Severity.S1 (obtenu '{envelope.x108_gate}')"
    )
    assert envelope.ticket_id is None, "Aucun ticket sur violation de contrainte impérative"


def test_adversarial_independent_sources_remain_two_alerts():
    """Deux alertes distinctes issues de sources indépendantes restent deux alertes."""
    v1 = AgentVote("SensorA", Domain.BANK, Layer.OBSERVATION, "network fail", 0.8, Severity.S2,
                   unknowns=["UNKNOWN_NETWORK"], proposed_verdict="ANALYZE")
    v2 = AgentVote("SensorB", Domain.BANK, Layer.OBSERVATION, "hardware fail", 0.8, Severity.S2,
                   unknowns=["UNKNOWN_HARDWARE"], proposed_verdict="ANALYZE")
    agg = aggregate_bank([v1, v2])
    assert len(agg.unknowns) == 2, f"Attendu 2 alertes distinctes, obtenu: {len(agg.unknowns)}"
    assert "UNKNOWN_NETWORK" in agg.unknowns
    assert "UNKNOWN_HARDWARE" in agg.unknowns


def test_adversarial_duplicate_occurrences_not_independent_proofs():
    """Deux occurrences de la même alerte ne deviennent pas deux preuves indépendantes."""
    v1 = AgentVote("SensorA", Domain.BANK, Layer.OBSERVATION, "network fail", 0.8, Severity.S2,
                   unknowns=["UNKNOWN_NETWORK"], proposed_verdict="ANALYZE")
    v2 = AgentVote("SensorB", Domain.BANK, Layer.OBSERVATION, "network fail duplicate", 0.8, Severity.S2,
                   unknowns=["UNKNOWN_NETWORK"], proposed_verdict="ANALYZE")
    agg = aggregate_bank([v1, v2])
    assert agg.unknowns.count("UNKNOWN_NETWORK") == 1, (
        f"L'alerte identique ne doit compter que pour 1 occurrence dédupliquée (obtenu: {agg.unknowns.count('UNKNOWN_NETWORK')})"
    )


def test_adversarial_high_scores_never_neutralize_mandatory_obligation():
    """Un score élevé de 10 agents positifs ne neutralise jamais une obligation contractuelle impérative."""
    v_positive = [
        AgentVote(f"NormalVoter_{i}", Domain.BANK, Layer.OBSERVATION, "all good", 1.0, Severity.S0,
                  proposed_verdict="AUTHORIZE", authority_level=AuthorityLevel.ADVISORY)
        for i in range(10)
    ]
    v_mandatory = AgentVote(
        agent_id="MandatoryGuard",
        domain=Domain.BANK,
        layer=Layer.PROOF,
        claim="regulatory sanction breached",
        confidence=0.1,  # Confiance minimale
        severity_hint=Severity.S1,
        proposed_verdict="BLOCK",
        authority_level=AuthorityLevel.MANDATORY_VETO,
        rule_id="INV_BANK_REGULATORY_BLOCK",
        rule_version="1.0",
        measure_provenance="bank.compliance.aml",
        measure_age_s=0.0,
        measure_valid=True,
        observed_value=True,
        predicate_violated=True
    )
    agg = aggregate_bank(v_positive + [v_mandatory])
    envelope = GuardX108().decide(agg)
    assert envelope.x108_gate == "BLOCK", (
        f"Les scores positifs ne peuvent neutraliser MANDATORY_VETO (obtenu '{envelope.x108_gate}')"
    )
    assert envelope.ticket_id is None


def test_adversarial_nominal_authorization_preserved_when_constraints_satisfied():
    """Une autorisation nominale reste autorisée lorsque toutes les contraintes applicables sont satisfaites."""
    state = BankState(
        transaction_type="PURCHASE", amount=75.0, channel="ECOMMERCE",
        counterparty_known=True, counterparty_age_days=120,
        account_balance=3000.0, available_cash=3000.0, policy_limit=1500.0,
        affordability_score=0.92, device_trust_score=0.95,
        elapsed_s=150.0, min_required_elapsed_s=108.0
    )
    envelope = run_bank_pipeline(state)
    assert envelope.market_verdict == "AUTHORIZE", f"Attendu 'AUTHORIZE', obtenu '{envelope.market_verdict}'"
    assert envelope.x108_gate == "ALLOW", f"Attendu 'ALLOW', obtenu '{envelope.x108_gate}'"
    assert envelope.ticket_id is not None, "Le ticket souverain doit être émis pour transaction nominale satisfaite"


# ============================================================================
# 5. TESTS PHASE 1C (AUTORITÉ PAR LA RÈGLE CONTRACTUELLE & QUALIFICATION DES MESURES)
# ============================================================================

def test_same_agent_two_rules_different_force():
    """Même agent évaluant deux règles distinctes de forces différentes."""
    # Règle 1: ADVISORY -> produit HOLD, jamais BLOCK souverain
    v_advisory = AgentVote(
        agent_id="DualRuleAgent", domain=Domain.BANK, layer=Layer.OBSERVATION, claim="context hint",
        confidence=0.9, severity_hint=Severity.S4, proposed_verdict="BLOCK", rule_id="RULE_BANK_CONTEXT_ADVISORY",
        measure_provenance="bank.core.context", measure_age_s=0.0, measure_valid=True, observed_value="context"
    )
    agg1 = aggregate_bank([v_advisory])
    env1 = GuardX108().decide(agg1)
    assert env1.x108_gate == "HOLD", f"La règle ADVISORY ne doit pas bloquer souverainement (obtenu '{env1.x108_gate}')"

    # Règle 2: MANDATORY_VETO -> produit BLOCK souverain
    v_mandatory = AgentVote(
        agent_id="DualRuleAgent", domain=Domain.BANK, layer=Layer.PROOF, claim="regulatory breach",
        confidence=0.9, severity_hint=Severity.S1, proposed_verdict="BLOCK", rule_id="INV_BANK_REGULATORY_BLOCK",
        rule_version="1.0", measure_provenance="bank.compliance.aml", measure_age_s=0.0, measure_valid=True,
        observed_value=True, predicate_violated=True
    )
    agg2 = aggregate_bank([v_mandatory])
    env2 = GuardX108().decide(agg2)
    assert env2.x108_gate == "BLOCK", f"La règle MANDATORY_VETO doit bloquer souverainement (obtenu '{env2.x108_gate}')"


def test_two_agents_same_mandatory_rule():
    """Deux agents distincts évaluant la même règle impérative (l'autorité vient de la règle)."""
    for agent_name in ("AviationRadarAgent", "InertialNavAgent"):
        v = AgentVote(
            agent_id=agent_name, domain=Domain.GPS_DEFENSE_AVIATION, layer=Layer.PROOF,
            claim="trajectory drift violation", confidence=0.8, severity_hint=Severity.S2,
            proposed_verdict="ABORT_TRAJECTORY", rule_id="INV_GPS_DRIFT_MAX",
            rule_version="1.0", measure_provenance="gnss.avionics.inertial", measure_age_s=0.0,
            measure_valid=True, observed_value=0.95, predicate_violated=True
        )
        agg = aggregate_gps_defense_aviation([v])
        env = GuardX108().decide(agg)
        assert env.x108_gate == "BLOCK", f"L'agent {agent_name} liant INV_GPS_DRIFT_MAX doit bloquer"


def test_falsified_agent_id_cannot_escalate_authority():
    """Un agent falsifiant agent_id pour usurper une identité ne peut escalader sans règle valide."""
    v_fake = AgentVote(
        agent_id="TrajectoryIntegrityAgent",  # Usurpation de nom
        domain=Domain.BANK,
        layer=Layer.OBSERVATION,
        claim="spoofed authority",
        confidence=0.95,
        severity_hint=Severity.S4,
        proposed_verdict="BLOCK",
        rule_id="RULE_BANK_CONTEXT_ADVISORY"  # Règle réelle consultative
    )
    agg = aggregate_bank([v_fake])
    env = GuardX108().decide(agg)
    assert env.x108_gate == "HOLD", (
        f"L'usurpation d'agent_id ne doit pas permettre de bloquer souverainement (obtenu '{env.x108_gate}')"
    )


def test_mandatory_rule_out_of_scope_does_not_block_foreign_domain():
    """Une règle impérative GPS évaluée hors périmètre dans un agrégat BANK ne bloque pas la transaction."""
    v_nominal = AgentVote("BankVoter", Domain.BANK, Layer.OBSERVATION, "nominal", 0.95, Severity.S0, proposed_verdict="AUTHORIZE")
    v_out_of_scope = AgentVote(
        "GpsInjectedAgent", Domain.BANK, Layer.PROOF, "gps rule in bank", 0.9, Severity.S4,
        proposed_verdict="ABORT_TRAJECTORY", rule_id="INV_GPS_DRIFT_MAX"  # Règle GPS injected in Bank
    )
    agg = aggregate_bank([v_nominal, v_out_of_scope])
    env = GuardX108().decide(agg)
    assert env.x108_gate == "ALLOW", "Une règle hors périmètre ne doit pas bloquer un domaine orthogonal"


def test_stale_measurement_triggers_hold():
    """Une mesure périmée (âge > max_allowed_age_s) ne peut pas être considérée nominale."""
    v_stale = AgentVote(
        "TrajectoryIntegrityAgent", Domain.GPS_DEFENSE_AVIATION, Layer.PROOF, "stale fix",
        0.95, Severity.S0, proposed_verdict="TRAJECTORY_VALID", rule_id="INV_GPS_DRIFT_MAX",
        measure_age_s=500.0  # > max_allowed_age_s (30s)
    )
    agg = aggregate_gps_defense_aviation([v_stale])
    env = GuardX108().decide(agg)
    assert env.x108_gate == "HOLD", f"Mesure périmée doit imposer HOLD (obtenu '{env.x108_gate}')"
    assert env.ticket_id is None


def test_measurement_without_provenance_triggers_hold():
    """Une mesure sans provenance (source non déclarée) ne peut pas être autorisée."""
    v_unprovenanced = AgentVote(
        "BankVoter", Domain.BANK, Layer.OBSERVATION, "no provenance data",
        0.95, Severity.S0, proposed_verdict="AUTHORIZE", rule_id="RULE_BANK_CONTEXT_ADVISORY",
        measure_provenance=""  # Absence de provenance
    )
    agg = aggregate_bank([v_unprovenanced])
    env = GuardX108().decide(agg)
    assert env.x108_gate == "HOLD", f"Mesure sans provenance doit imposer HOLD (obtenu '{env.x108_gate}')"
    assert env.ticket_id is None


def test_revoked_or_wrong_version_rule_triggers_hold():
    """Une règle invoquée avec une mauvaise version ne confère aucune autorisation."""
    v_obsolete = AgentVote(
        "TrajectoryIntegrityAgent", Domain.GPS_DEFENSE_AVIATION, Layer.PROOF, "obsolete rule version",
        0.95, Severity.S0, proposed_verdict="TRAJECTORY_VALID", rule_id="INV_GPS_DRIFT_MAX",
        rule_version="0.9"  # Version obsolète vs 1.0 canonique
    )
    agg = aggregate_gps_defense_aviation([v_obsolete])
    env = GuardX108().decide(agg)
    assert env.x108_gate == "HOLD", f"Version de règle obsolète doit imposer HOLD (obtenu '{env.x108_gate}')"
    assert env.ticket_id is None


def test_mandatory_rule_violation_overrides_ten_positive_votes():
    """Une violation effective d'une règle impérative prévaut sur dix votes d'autorisation parfaits."""
    v_positives = [
        AgentVote(f"AgentPositive_{i}", Domain.GPS_DEFENSE_AVIATION, Layer.OBSERVATION, "ok", 1.0, Severity.S0,
                  proposed_verdict="TRAJECTORY_VALID", rule_id="RULE_GPS_SOURCE_AVAILABILITY")
        for i in range(10)
    ]
    v_violated = AgentVote(
        "DriftWatcher", Domain.GPS_DEFENSE_AVIATION, Layer.PROOF, "critical drift", 0.05, Severity.S1,
        proposed_verdict="ABORT_TRAJECTORY", rule_id="INV_GPS_DRIFT_MAX", rule_version="1.0",
        measure_provenance="gnss.avionics.inertial", measure_age_s=0.0, measure_valid=True,
        observed_value=0.95, predicate_violated=True
    )
    agg = aggregate_gps_defense_aviation(v_positives + [v_violated])
    env = GuardX108().decide(agg)
    assert env.x108_gate == "BLOCK", (
        f"L'obligation impérative doit bloquer malgré 10 votes d'autorisation (obtenu '{env.x108_gate}')"
    )
    assert env.ticket_id is None


# ============================================================================
# 6. TESTS ADVERSARIAUX PHASE 1D (INDEPENDENT EVIDENCE & MEASURE QUALIFICATION)
# ============================================================================

def test_phase1d_1_measure_without_provenance_triggers_hold():
    """Mesure sans provenance déclarée impose explicitement le statut UNKNOWN et HOLD souverain."""
    v = AgentVote(
        agent_id="TrajectoryIntegrityAgent", domain=Domain.GPS_DEFENSE_AVIATION, layer=Layer.PROOF,
        claim="drift observation", confidence=0.95, severity_hint=Severity.S0,
        proposed_verdict="TRAJECTORY_VALID", rule_id="INV_GPS_DRIFT_MAX",
        measure_provenance=None, measure_age_s=1.0, measure_valid=True, observed_value=0.05
    )
    agg = aggregate_gps_defense_aviation([v])
    env = GuardX108().decide(agg)
    assert env.x108_gate == "HOLD", f"Mesure sans provenance doit imposer HOLD (obtenu '{env.x108_gate}')"
    assert env.ticket_id is None, "Aucun ticket sans provenance qualifiée"


def test_phase1d_2_missing_timestamp_triggers_hold():
    """Mesure sans horodatage (measure_age_s absent) impose HOLD conservatoire."""
    v = AgentVote(
        agent_id="TrajectoryIntegrityAgent", domain=Domain.GPS_DEFENSE_AVIATION, layer=Layer.PROOF,
        claim="drift observation", confidence=0.95, severity_hint=Severity.S0,
        proposed_verdict="TRAJECTORY_VALID", rule_id="INV_GPS_DRIFT_MAX",
        measure_provenance="gnss.avionics.inertial", measure_age_s=None, measure_valid=True, observed_value=0.05
    )
    agg = aggregate_gps_defense_aviation([v])
    env = GuardX108().decide(agg)
    assert env.x108_gate == "HOLD", f"Mesure sans horodatage doit imposer HOLD (obtenu '{env.x108_gate}')"
    assert env.ticket_id is None


def test_phase1d_3_stale_measurement_declared_fresh_caught_and_held():
    """Mesure périmée (âge > max_allowed_age_s) déclarée fraîche par un agent est interceptée en HOLD."""
    v = AgentVote(
        agent_id="TrajectoryIntegrityAgent", domain=Domain.GPS_DEFENSE_AVIATION, layer=Layer.PROOF,
        claim="fresh claiming stale telemetry", confidence=0.99, severity_hint=Severity.S0,
        proposed_verdict="TRAJECTORY_VALID", rule_id="INV_GPS_DRIFT_MAX",
        measure_provenance="gnss.avionics.inertial", measure_age_s=45.0, measure_valid=True, observed_value=0.05
    )
    agg = aggregate_gps_defense_aviation([v])
    env = GuardX108().decide(agg)
    assert env.x108_gate == "HOLD", f"Télémétrie GPS périmée (45s > 30s) doit imposer HOLD (obtenu '{env.x108_gate}')"
    assert env.ticket_id is None


def test_phase1d_4_falsified_predicate_violation_rejected_by_kx108():
    """predicate_violated=True falsifié alors que la valeur observée est nominale est rejeté par KX108."""
    v_falsified = AgentVote(
        agent_id="AdversarialSensorAgent", domain=Domain.GPS_DEFENSE_AVIATION, layer=Layer.PROOF,
        claim="falsified alarm", confidence=0.99, severity_hint=Severity.S4,
        proposed_verdict="ABORT_TRAJECTORY", rule_id="INV_GPS_DRIFT_MAX",
        measure_provenance="gnss.avionics.inertial", measure_age_s=1.0, measure_valid=True,
        observed_value=0.05, predicate_violated=True  # 0.05 est nominal (< 0.85), violation mensongère
    )
    v_nominal = AgentVote(
        agent_id="SourceAvailabilityAgent", domain=Domain.GPS_DEFENSE_AVIATION, layer=Layer.OBSERVATION,
        claim="nominal sources", confidence=0.95, severity_hint=Severity.S0,
        proposed_verdict="TRAJECTORY_VALID", rule_id="RULE_GPS_SOURCE_AVAILABILITY",
        measure_provenance="gnss.sensors.availability", measure_age_s=0.0, measure_valid=True,
        observed_value={"gps": True, "inertial": True, "radio": True}, predicate_violated=False
    )
    agg = aggregate_gps_defense_aviation([v_nominal, v_falsified])
    env = GuardX108().decide(agg)
    assert env.x108_gate != "BLOCK", (
        f"L'alerte falsifiée ne doit pas imposer un BLOCK souverain car le prédicat réel est nominal (obtenu '{env.x108_gate}')"
    )


def test_phase1d_5_falsified_nominal_predicate_detected_and_blocked():
    """predicate_violated=False prétendu malgré violation réelle observée est détecté par KX108 et bloqué."""
    v_lying_agent = AgentVote(
        agent_id="CompromisedAgent", domain=Domain.GPS_DEFENSE_AVIATION, layer=Layer.PROOF,
        claim="fraudulent nominal claim", confidence=1.0, severity_hint=Severity.S0,
        proposed_verdict="TRAJECTORY_VALID", rule_id="INV_GPS_DRIFT_MAX",
        measure_provenance="gnss.avionics.inertial", measure_age_s=1.0, measure_valid=True,
        observed_value=0.95,  # Dérive critique réelle violant le prédicat (>= 0.85)
        predicate_violated=False  # Mensonge de l'agent
    )
    agg = aggregate_gps_defense_aviation([v_lying_agent])
    env = GuardX108().decide(agg)
    assert env.x108_gate == "BLOCK", (
        f"KX108 doit vérifier indépendamment le prédicat et bloquer souverainement (obtenu '{env.x108_gate}')"
    )
    assert env.ticket_id is None


def test_phase1d_6_usurped_agent_id_fails_without_evidence():
    """agent_id usurpé sans preuve de mesure ne peut jamais déclencher de veto impératif."""
    v_usurped = AgentVote(
        agent_id="TrajectoryIntegrityAgent",  # Usurpation du nom d'un agent critique
        domain=Domain.GPS_DEFENSE_AVIATION, layer=Layer.PROOF,
        claim="spoofed authority", confidence=0.99, severity_hint=Severity.S4,
        proposed_verdict="ABORT_TRAJECTORY"
        # rule_id absent, aucune preuve de mesure
    )
    agg = aggregate_gps_defense_aviation([v_usurped])
    env = GuardX108().decide(agg)
    assert env.x108_gate != "BLOCK", (
        f"L'usurpation d'identité d'agent ne doit pas conférer de veto souverain BLOCK (obtenu '{env.x108_gate}')"
    )


def test_phase1d_7_usurped_rule_id_unknown_in_registry_fails():
    """rule_id usurpé ou inconnu au registre canonique échoue et impose HOLD conservatoire."""
    v_fake_rule = AgentVote(
        agent_id="RogueAgent", domain=Domain.BANK, layer=Layer.PROOF,
        claim="fabricated mandate", confidence=0.99, severity_hint=Severity.S4,
        proposed_verdict="BLOCK", rule_id="INV_FORGED_RULE_VETO",
        measure_provenance="fake.telemetry", measure_age_s=0.0, measure_valid=True, observed_value=999
    )
    agg = aggregate_bank([v_fake_rule])
    env = GuardX108().decide(agg)
    assert env.x108_gate == "HOLD", (
        f"Une règle forgée inconnue du registre ne confère aucun veto souverain et impose HOLD (obtenu '{env.x108_gate}')"
    )
    assert env.ticket_id is None


def test_phase1d_8_missing_values_synthesized_to_nominal_blocked():
    """Valeurs observées absentes (observed_value=None ou measure_valid=False) empêchent ALLOW."""
    v_missing_val = AgentVote(
        agent_id="BankAffordabilityAgent", domain=Domain.BANK, layer=Layer.INTERPRETATION,
        claim="synthesized nominal claim without actual value", confidence=0.95, severity_hint=Severity.S0,
        proposed_verdict="AUTHORIZE", rule_id="RULE_BANK_AFFORDABILITY",
        measure_provenance="bank.credit.scoring", measure_age_s=0.0, measure_valid=False,
        observed_value=None
    )
    agg = aggregate_bank([v_missing_val])
    env = GuardX108().decide(agg)
    assert env.x108_gate != "ALLOW", "Une mesure non qualifiée ou synthétisée ne doit jamais produire ALLOW"
    assert env.ticket_id is None


def test_phase1d_9_mandatory_constraint_with_low_confidence_blocks():
    """Une contrainte impérative valide avec faible confiance (0.02) bloque souverainement face à 10 votes d'accord."""
    v_positives = [
        AgentVote(f"TrustyAgent_{i}", Domain.BANK, Layer.OBSERVATION, "ok", 1.0, Severity.S0,
                  proposed_verdict="AUTHORIZE")
        for i in range(10)
    ]
    v_mandatory = AgentVote(
        agent_id="RegulatoryAmlOfficer", domain=Domain.BANK, layer=Layer.PROOF,
        claim="sanction breach observed with high doubt", confidence=0.02, severity_hint=Severity.S1,
        proposed_verdict="BLOCK", rule_id="INV_BANK_REGULATORY_BLOCK", rule_version="1.0",
        measure_provenance="bank.compliance.aml", measure_age_s=10.0, measure_valid=True,
        observed_value=True, predicate_violated=True
    )
    agg = aggregate_bank(v_positives + [v_mandatory])
    env = GuardX108().decide(agg)
    assert env.x108_gate == "BLOCK", (
        f"L'obligation impérative doit bloquer malgré la faible confiance 0.02 (obtenu '{env.x108_gate}')"
    )
    assert env.ticket_id is None


def test_phase1d_10_nominal_authorization_with_complete_evidence():
    """Autorisation nominale avec preuves complètes, vérifiées et fraîches délivre le ticket ALLOW."""
    state = BankState(
        transaction_type="PURCHASE", amount=45.0, channel="CHIP_PIN",
        counterparty_known=True, counterparty_age_days=90,
        account_balance=2500.0, available_cash=2500.0, policy_limit=1000.0,
        affordability_score=0.95, device_trust_score=0.98,
        elapsed_s=120.0, min_required_elapsed_s=108.0
    )
    envelope = run_bank_pipeline(state)
    assert envelope.market_verdict == "AUTHORIZE", f"Attendu 'AUTHORIZE', obtenu '{envelope.market_verdict}'"
    assert envelope.x108_gate == "ALLOW", f"Attendu 'ALLOW', obtenu '{envelope.x108_gate}'"
    assert envelope.ticket_id is not None, "Le ticket souverain doit être délivré sur preuves complètes"
    assert envelope.severity in ("S0", "S1"), f"Gravité nominale attendue (obtenu '{envelope.severity}')"


if __name__ == "__main__":
    import unittest
    # Exécution directe si invoqué via python
    pytest.main(["-xvs", __file__])

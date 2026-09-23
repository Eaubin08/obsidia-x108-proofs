"""
TOP4 V3 — Guard domain enum false ACT surface hardening
SCOPE=V3_ONLY  PATCH=YES_BUT_V3_ONLY  COMMIT=NO  DECISION_AUTHORITY=KX108_ONLY
"""
import sys
import importlib.util
import types

import pytest


# ── Loader ────────────────────────────────────────────────────────────────────

def _load_guard():
    """Import sigma.guard via spec — stubs sigma.contracts with real stubs."""
    import os, enum, dataclasses

    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    guard_path = os.path.join(base, "sigma", "guard.py")

    # sigma.contracts — provide real enum + dataclass stubs
    stub_contracts = types.ModuleType("sigma.contracts")

    class _Layer(enum.IntEnum):
        OBSERVATION = 1; INTERPRETATION = 2; CONTRADICTION = 3; PERIPHERAL = 4
        SIGMA = 5; KERNEL = 6; PROOF = 7; SCELLAGE = 8

    class _Severity(enum.IntEnum):
        S0 = 0; S1 = 1; S2 = 2; S3 = 3; S4 = 4
        def __str__(self): return self.name

    class _Domain(enum.Enum):
        BANK = "bank"; TRADING = "trading"; ECOM = "ecom"
        GPS_DEFENSE_AVIATION = "gps_defense_aviation"; META = "meta"

    class _SourceTag(enum.Enum):
        CANONICAL = "canonical"; CANONICAL_FRAMEWORK = "canonical_framework"
        KERNEL = "kernel"; KERNEL_FRAMEWORK = "kernel_framework"

    class _X108Gate(enum.Enum):
        ALLOW = "ALLOW"; HOLD = "HOLD"; BLOCK = "BLOCK"

    @dataclasses.dataclass
    class _AgentVote:
        agent_id: str = "A1"
        vote: str = "HOLD"
        proposed_verdict: str = "HOLD"
        confidence: float = 0.5
        domain: str = "trading"
        layer: int = 5
        claim: str = "no_claim"
        contradictions: list = dataclasses.field(default_factory=list)
        unknowns: list = dataclasses.field(default_factory=list)
        risk_flags: list = dataclasses.field(default_factory=list)
        evidence_refs: list = dataclasses.field(default_factory=list)
        severity_hint: object = None

    @dataclasses.dataclass
    class _DomainAggregate:
        domain: object = _Domain.TRADING
        market_verdict: str = "HOLD"
        confidence: float = 0.5
        contradictions: list = dataclasses.field(default_factory=list)
        unknowns: list = dataclasses.field(default_factory=list)
        risk_flags: list = dataclasses.field(default_factory=list)
        evidence_refs: list = dataclasses.field(default_factory=list)
        agent_votes: list = dataclasses.field(default_factory=list)
        extra_metrics: dict = dataclasses.field(default_factory=dict)

    @dataclasses.dataclass
    class _CanonicalDecisionEnvelope:
        domain: str = "trading"
        market_verdict: str = "HOLD"
        confidence: float = 0.5
        contradictions: list = dataclasses.field(default_factory=list)
        unknowns: list = dataclasses.field(default_factory=list)
        risk_flags: list = dataclasses.field(default_factory=list)
        x108_gate: str = "HOLD"
        reason_code: str = "TEST"
        severity: str = "S0"
        decision_id: str = "test-id"
        trace_id: str = "test-trace"
        ticket_required: bool = False
        ticket_id: object = None
        attestation_ref: object = None
        source: str = "canonical_framework"
        evidence_refs: list = dataclasses.field(default_factory=list)
        metrics: dict = dataclasses.field(default_factory=dict)
        raw_engine: dict = dataclasses.field(default_factory=dict)
        confidence_integrity: float = 0.5
        confidence_governance: float = 0.5
        confidence_readiness: float = 0.5
        confidence_scope: str = "integrity"
        governance_scope: str = "x108_decision_robustness"
        readiness_scope: str = "harmonic_integrity_governance"

    stub_contracts.Layer = _Layer
    stub_contracts.Severity = _Severity
    stub_contracts.Domain = _Domain
    stub_contracts.SourceTag = _SourceTag
    stub_contracts.X108Gate = _X108Gate
    stub_contracts.AgentVote = _AgentVote
    stub_contracts.DomainAggregate = _DomainAggregate
    stub_contracts.CanonicalDecisionEnvelope = _CanonicalDecisionEnvelope
    sys.modules["sigma.contracts"] = stub_contracts
    sys.modules["sigma"] = sys.modules.get("sigma") or types.ModuleType("sigma")

    _mod_name = "sigma.guard_v3_test"
    spec = importlib.util.spec_from_file_location(_mod_name, guard_path)
    mod = importlib.util.module_from_spec(spec)
    # Register before exec so @dataclass can resolve cls.__module__ in sys.modules
    sys.modules[_mod_name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def g():
    return _load_guard()


def _vote(layer=5, vote="HOLD", proposed_verdict=None, agent_id="A1", confidence=0.8):
    """Build a simple dict-like vote for _x108_agent_vote_detail."""
    class _V:
        pass
    v = _V()
    v.agent_id = agent_id
    v.vote = vote
    v.proposed_verdict = proposed_verdict or vote
    v.confidence = confidence
    v.domain = "trading"
    v.layer = layer
    v.claim = "test_claim"
    v.contradictions = []
    v.unknowns = []
    v.risk_flags = []
    v.evidence_refs = []
    v.severity_hint = None
    return v


# ── T1 : raw_vote Domain-like + proposed_verdict ACT non trusted → selected != ACT ─────

def test_domain_like_raw_vote_no_act(g):
    v = _vote(layer=5, vote="BANK", proposed_verdict="ACT")
    detail = g._x108_agent_vote_detail(v)
    assert detail["normalized_vote_for_aggregate4"] != "ACT", (
        f"Domain-like vote + non-trusted ACT should be blocked, got: {detail['normalized_vote_for_aggregate4']}"
    )
    assert detail["aggregate4_false_act_surface_blocked"] is True
    assert detail["aggregate4_invalid_legacy_vote"] is True


# ── T2 : proposed_verdict ALLOW non trusted → pas ACT ────────────────────────

def test_allow_non_trusted_not_act(g):
    v = _vote(layer=4, vote="ALLOW", proposed_verdict="ALLOW")
    detail = g._x108_agent_vote_detail(v)
    assert detail["normalized_vote_for_aggregate4"] != "ACT"
    assert detail["aggregate4_false_act_surface_blocked"] is True
    assert detail["normalized_vote_for_aggregate4"] == "HOLD"


# ── T3 : proposed_verdict AUTHORIZE non trusted → pas ACT ────────────────────

def test_authorize_non_trusted_not_act(g):
    v = _vote(layer=5, vote="AUTHORIZE", proposed_verdict="AUTHORIZE")
    detail = g._x108_agent_vote_detail(v)
    assert detail["normalized_vote_for_aggregate4"] != "ACT"
    assert detail["aggregate4_false_act_surface_blocked"] is True


# ── T4 : trusted kernel (layer=6) HOLD → HOLD préservé ───────────────────────

def test_trusted_kernel_hold_preserved(g):
    v = _vote(layer=6, vote="HOLD", proposed_verdict="HOLD")
    detail = g._x108_agent_vote_detail(v)
    assert detail["normalized_vote_for_aggregate4"] == "HOLD"
    assert detail["aggregate4_false_act_surface_blocked"] is False
    assert detail["aggregate4_selected_vote_source"] == "trusted_kernel"


# ── T5 : trusted kernel (layer=6) BLOCK → BLOCK préservé ─────────────────────

def test_trusted_kernel_block_preserved(g):
    v = _vote(layer=6, vote="BLOCK", proposed_verdict="BLOCK")
    detail = g._x108_agent_vote_detail(v)
    assert detail["normalized_vote_for_aggregate4"] == "BLOCK"
    assert detail["aggregate4_false_act_surface_blocked"] is False
    assert detail["aggregate4_selected_vote_source"] == "trusted_kernel"


# ── T6 : trusted kernel (layer=6) ALLOW → ACT autorisé ───────────────────────

def test_trusted_kernel_allow_becomes_act(g):
    v = _vote(layer=6, vote="ALLOW", proposed_verdict="ALLOW")
    detail = g._x108_agent_vote_detail(v)
    assert detail["normalized_vote_for_aggregate4"] == "ACT"
    assert detail["aggregate4_false_act_surface_blocked"] is False
    assert detail["aggregate4_invalid_legacy_vote"] is False


# ── T7 : PROOF layer (layer=7) trust → ACT autorisé ──────────────────────────

def test_proof_layer_trusted_for_act(g):
    v = _vote(layer=7, vote="ACT", proposed_verdict="ACT")
    detail = g._x108_agent_vote_detail(v)
    assert detail["normalized_vote_for_aggregate4"] == "ACT"
    assert detail["aggregate4_false_act_surface_blocked"] is False
    assert detail["aggregate4_selected_vote_source"] == "trusted_kernel"


# ── T8 : 4 votes non-trusted ACT → formal_result != ACT ─────────────────────

def test_four_non_trusted_act_votes_formal_result_not_act(g):
    votes = [_vote(layer=5, vote="ACT", confidence=0.9) for _ in range(4)]
    surface = g._x108_consensus_surface(votes)
    consensus = surface["consensus"]
    # formal result should NOT be ACT (all 4 votes remapped to HOLD)
    formal = consensus.get("formal_result") or {}
    assert formal.get("final_decision") != "ACT", (
        f"4 non-trusted ACT votes should NOT produce ACT in formal_result, got: {formal}"
    )
    assert consensus["aggregate4_false_act_surface_blocked_count"] == 4
    assert consensus["aggregate4_invalid_legacy_votes_count"] == 4


# ── T9 : PROOF_SURFACE_ONLY présent dans consensus ───────────────────────────

def test_proof_surface_only_in_consensus(g):
    votes = [_vote(layer=5, vote="HOLD") for _ in range(4)]
    surface = g._x108_consensus_surface(votes)
    consensus = surface["consensus"]
    assert consensus.get("authority") == "PROOF_SURFACE_ONLY"
    assert consensus.get("aggregate4_proof_surface_only") is True


# ── T10 : does_not_authorize_action=True dans consensus ──────────────────────

def test_does_not_authorize_action_in_consensus(g):
    votes = [_vote(layer=5, vote="HOLD") for _ in range(4)]
    surface = g._x108_consensus_surface(votes)
    consensus = surface["consensus"]
    assert consensus.get("does_not_authorize_action") is True
    assert consensus.get("aggregate4_does_not_authorize_action") is True


# ── T11 : aucun ACT si source non trusted (surface surface) ──────────────────

def test_no_act_if_source_not_trusted(g):
    for vote_str in ("ACT", "ALLOW", "AUTHORIZE", "VALID", "PASS", "PAY"):
        v = _vote(layer=5, vote=vote_str, proposed_verdict=vote_str)
        detail = g._x108_agent_vote_detail(v)
        assert detail["normalized_vote_for_aggregate4"] != "ACT", (
            f"vote='{vote_str}' layer=5 should NOT produce ACT, got: {detail['normalized_vote_for_aggregate4']}"
        )


# ── T12 : does_not_override_x108_gate=True dans consensus ────────────────────

def test_does_not_override_x108_gate(g):
    votes = [_vote(layer=5, vote="HOLD") for _ in range(4)]
    surface = g._x108_consensus_surface(votes)
    assert surface["consensus"].get("does_not_override_x108_gate") is True


# ── T13 : champs audit V3 toujours présents dans detail ──────────────────────

def test_v3_audit_fields_always_present(g):
    v = _vote(layer=5, vote="HOLD")
    detail = g._x108_agent_vote_detail(v)
    for field in [
        "aggregate4_invalid_legacy_vote",
        "aggregate4_domain_enum_rejected",
        "aggregate4_false_act_surface_blocked",
        "aggregate4_selected_vote_source",
        "aggregate4_proof_surface_only",
        "aggregate4_does_not_authorize_action",
    ]:
        assert field in detail, f"audit field manquant: {field}"


# ── T14 : champs audit V3 présents dans consensus ────────────────────────────

def test_v3_consensus_audit_fields_present(g):
    votes = [_vote(layer=5, vote="HOLD") for _ in range(4)]
    surface = g._x108_consensus_surface(votes)
    consensus = surface["consensus"]
    for field in [
        "aggregate4_proof_surface_only",
        "aggregate4_does_not_authorize_action",
        "aggregate4_false_act_surface_blocked_count",
        "aggregate4_invalid_legacy_votes_count",
        "aggregate4_domain_enum_rejected_count",
    ]:
        assert field in consensus, f"champ consensus manquant: {field}"


# ── T15 : domain enum rejected dans detail ───────────────────────────────────

def test_domain_enum_rejected_flagged(g):
    v = _vote(layer=5, vote="BANK", proposed_verdict="HOLD")
    detail = g._x108_agent_vote_detail(v)
    assert detail["aggregate4_domain_enum_rejected"] is True


# ── T16 : _x108_is_trusted_act_source — couverture ───────────────────────────

def test_is_trusted_act_source(g):
    assert g._x108_is_trusted_act_source(6) is True    # KERNEL
    assert g._x108_is_trusted_act_source(7) is True    # PROOF
    assert g._x108_is_trusted_act_source(8) is True    # SCELLAGE
    assert g._x108_is_trusted_act_source(5) is False   # SIGMA
    assert g._x108_is_trusted_act_source(4) is False   # PERIPHERAL
    assert g._x108_is_trusted_act_source(1) is False   # OBSERVATION
    assert g._x108_is_trusted_act_source(None) is False
    assert g._x108_is_trusted_act_source("KERNEL") is True
    assert g._x108_is_trusted_act_source("SIGMA") is False


# ── T17 : BLOCK > HOLD > ALLOW toujours respecté (fail-closed sans 3/4) ─────

def test_block_hold_allow_priority(g):
    # 2 BLOCK, 2 HOLD → supermajority impossible → fail-closed → BLOCK
    votes = [
        _vote(layer=5, vote="BLOCK", confidence=0.9),
        _vote(layer=5, vote="BLOCK", confidence=0.9),
        _vote(layer=5, vote="HOLD", confidence=0.9),
        _vote(layer=5, vote="HOLD", confidence=0.9),
    ]
    surface = g._x108_consensus_surface(votes)
    formal = surface["consensus"].get("formal_result") or {}
    assert formal.get("final_decision") == "BLOCK"


# ── T18 : py_compile pass ─────────────────────────────────────────────────────

def test_py_compile_pass():
    import os, py_compile
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    py_compile.compile(os.path.join(base, "sigma", "guard.py"), doraise=True)
    py_compile.compile(os.path.join(base, "sigma", "aggregation.py"), doraise=True)


# ── T19 : non trusted ACT non trusted = fallback HOLD dans normalized ─────────

def test_non_trusted_act_fallback_to_hold_normalized(g):
    for layer in (1, 2, 3, 4, 5):
        v = _vote(layer=layer, vote="ACT", proposed_verdict="ACT")
        detail = g._x108_agent_vote_detail(v)
        assert detail["normalized_vote_for_aggregate4"] == "HOLD", (
            f"layer={layer} non-trusted ACT should normalize to HOLD, got: {detail['normalized_vote_for_aggregate4']}"
        )


# ── T20 : aggregate4_selected_vote_source correct selon layer ────────────────

def test_selected_vote_source_correct(g):
    for layer in (1, 2, 3, 4, 5):
        v = _vote(layer=layer)
        detail = g._x108_agent_vote_detail(v)
        assert detail["aggregate4_selected_vote_source"] == "non_trusted_peripheral"

    for layer in (6, 7, 8):
        v = _vote(layer=layer)
        detail = g._x108_agent_vote_detail(v)
        assert detail["aggregate4_selected_vote_source"] == "trusted_kernel"

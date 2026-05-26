"""Blockchain routes — dry-run status, policy, signature, wallet, gencoin."""
from types import SimpleNamespace
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Any

from apps.obsidia_api.runtime_loader import load_runtime_components
from apps.obsidia_api.safe_response import safe_backend_response

from periphery.blockchain.token_policy import evaluate_token_policy
from periphery.blockchain.signature_boundary import (
    evaluate_signature_request,
    assert_no_private_key_in_payload,
)
from periphery.blockchain.wallet_security_gate import evaluate_wallet_request
from periphery.gencoin import compute_gencoin
from periphery.gencoin_debt_model import compute_debt
from periphery.gencoin_distribution import compute_distribution
from periphery.world_action_controlled_runtime_stub import run_world_action_stub
from periphery.gencoin_sandbox.sandbox_engine import System, topology_losses, compute_sigma, step
from periphery.gencoin_sandbox.regime_metrics import compute_regime_metrics
from periphery.gencoin_sandbox.regime_truth_gate import apply_regime_truth_gate
from periphery.world_calls.obsidia_gateway import ObsidiaGateway
from periphery.world_calls.sovereign_ticket import issue_sovereign_ticket
from periphery.world_calls.ticket_store import store_ticket, load_tickets
from periphery.world_calls.world_action_bus import publish_event
from periphery.world_calls.world_call_classifier import classify_world_call, WorldCallClass
from periphery.blockchain.blockchain_action_classifier import classify_blockchain_action, BlockchainActionClass
from periphery.blockchain.defi_risk_gate import evaluate_defi_risk
from periphery.blockchain.smart_contract_risk_gate import evaluate_smart_contract_risk
from periphery.blockchain.bridge_risk_gate import evaluate_bridge_risk
from periphery.blockchain.transaction_simulator import simulate_transaction
from periphery.blockchain.chain_context import build_chain_context
from periphery.blockchain.onchain_audit_packet import build_onchain_audit_packet
from periphery.agents import world_action_agent, gencoin_value_agent, os3_proof_agent, data_purity_agent, provenance_agent, brody_memory_agent, eml_symbolic_agent, energy_thermo_agent, timeverse_agent, ocs_generation_agent, operational_constance_agent, permission_economic_agent, action_sequence_agent, feedback_memory_agent
from periphery.world_calls.action_risk_classifier import classify_action_risk, requires_x108_gate, requires_human_approval, ActionRiskClass
from periphery.world_calls.autonomy_level_matrix import compute_autonomy_level, AutonomyLevel
from periphery.world_calls.egress_policy import evaluate_egress_policy
from periphery.world_calls.route_policy_x25 import route_x25
from periphery.world_calls.secret_boundary import redact_secrets, assert_no_secret_in_agent_payload
from periphery.world_calls.world_executor_dryrun import execute_dry_run
from periphery.physics_boundary.dimensional_hygiene import check_dimensional_hygiene
from periphery.physics_boundary.frequency_tag_mapper import map_frequency_tag
from periphery.physics_boundary.unit_consistency_checker import check_unit_consistency
from periphery.physics_boundary.symbolic_physics_claim_gate import evaluate_physics_claim
from periphery.number_encoding.symbolic_number_encoder import encode_symbolic_number

router = APIRouter(prefix="/api/blockchain", tags=["blockchain"])

_BOUNDARY = {
    "readonly": True,
    "emits_act": False,
    "memory_write": False,
    "decision_authority": "KX108_ONLY",
}


class TokenPolicyPayload(BaseModel):
    token_id: str
    action: str
    is_gencoin: bool = False


class SignatureCheckPayload(BaseModel):
    request_id: str
    signature_type: str
    payload: dict[str, Any] = Field(default_factory=dict)


class WalletGatePayload(BaseModel):
    request_id: str
    request_type: str
    payload: dict[str, Any] = Field(default_factory=dict)


class GencoinMetrics(BaseModel):
    freshness_score: float = 1.0
    memory_status: str = "STABLE"
    energy_efficiency: float = 1.0
    thermo_debt: float = 0.0
    computational_debt: float = 0.0
    memory_debt: float = 0.0
    oc_debt: float = 0.0
    oc_stable: bool = True
    permission_ok: bool = True
    economic_ok: bool = True
    assisted_ratio: float = 0.0
    delta_g: float = 1.0
    truth_score: float = 1.0
    regime_state: str = "ON"


class GencoinComputePayload(BaseModel):
    action_id: str
    domain: str = "GENCOIN"
    gross_value: float = 0.0
    x108_gate: str = "HOLD"
    ticket_id: str = ""
    input_hash: str = ""
    output_hash: str = ""
    trace_hash: str = ""
    merkle_root: str = ""
    metrics: GencoinMetrics = Field(default_factory=GencoinMetrics)


@router.post("/policy/evaluate")
async def blockchain_policy_evaluate(payload: TokenPolicyPayload):
    result = evaluate_token_policy(
        token_id=payload.token_id,
        action=payload.action,
        is_gencoin=payload.is_gencoin,
    )
    return safe_backend_response({**result.to_dict(), **_BOUNDARY}, source="REAL_BACKEND")


@router.post("/signature/check")
async def blockchain_signature_check(payload: SignatureCheckPayload):
    try:
        assert_no_private_key_in_payload(payload.payload)
    except AssertionError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    result = evaluate_signature_request(
        request_id=payload.request_id,
        signature_type=payload.signature_type,
    )
    return safe_backend_response({**result.to_dict(), **_BOUNDARY}, source="REAL_BACKEND")


@router.post("/wallet/gate")
async def blockchain_wallet_gate(payload: WalletGatePayload):
    result = evaluate_wallet_request(
        request_id=payload.request_id,
        request_type=payload.request_type,
        payload=payload.payload,
    )
    return safe_backend_response({**result.to_dict(), **_BOUNDARY}, source="REAL_BACKEND")


@router.post("/gencoin/compute")
async def blockchain_gencoin_compute(payload: GencoinComputePayload):
    extra_metrics = {
        "freshness_score": payload.metrics.freshness_score,
        "memory_status": payload.metrics.memory_status,
        "energy_efficiency": payload.metrics.energy_efficiency,
        "thermo_debt": payload.metrics.thermo_debt,
        "computational_debt": payload.metrics.computational_debt,
        "memory_debt": payload.metrics.memory_debt,
        "oc_debt": payload.metrics.oc_debt,
        "oc_stable": payload.metrics.oc_stable,
        "permission_ok": payload.metrics.permission_ok,
        "economic_ok": payload.metrics.economic_ok,
        "assisted_ratio": payload.metrics.assisted_ratio,
        "delta_g": payload.metrics.delta_g,
        "truth_score": payload.metrics.truth_score,
        "regime_state": payload.metrics.regime_state,
    }
    action_candidate = SimpleNamespace(
        action_id=payload.action_id,
        domain=payload.domain,
        payload={"gross_value": payload.gross_value},
    )
    packet = SimpleNamespace(extra_metrics=extra_metrics)

    debt = compute_debt(action_candidate, packet)
    if not debt.is_admissible():
        return safe_backend_response({
            "action_id": payload.action_id,
            "status": "DEBT_NOT_ADMISSIBLE",
            "total_debt": debt.total_debt,
            "net_value": debt.net_value,
            "truth_score": debt.truth_score,
            "regime_state": debt.regime_state,
            "mint_allowed": False,
            "gencoin_candidate": 0.0,
            **_BOUNDARY,
        }, source="REAL_BACKEND")

    action_candidate.payload["total_debt"] = debt.total_debt

    ticket = SimpleNamespace(
        ticket_id=payload.ticket_id,
        x108_gate=payload.x108_gate,
        input_hash=payload.input_hash,
        output_hash=payload.output_hash,
        trace_hash=payload.trace_hash,
        merkle_root=payload.merkle_root,
    )
    result = compute_gencoin(action_candidate, packet, ticket)

    try:
        dist = compute_distribution(result.action_id, result.gencoin_candidate)
        dist.assert_human_priority()
    except AssertionError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    return safe_backend_response({
        "action_id": result.action_id,
        "os3_ticket_id": result.os3_ticket_id,
        "x108_gate": result.x108_gate,
        "proof_valid": result.proof_valid,
        "data_ok": result.data_ok,
        "memory_stable": result.memory_stable,
        "energy_stable": result.energy_stable,
        "oc_stable": result.oc_stable,
        "permission_ok": result.permission_ok,
        "economic_ok": result.economic_ok,
        "gross_value": result.gross_value,
        "computed_total_debt": debt.total_debt,
        "gencoin_candidate": result.gencoin_candidate,
        "mint_allowed": result.mint_allowed,
        "distribution": dist.to_dict(),
        **_BOUNDARY,
    }, source="REAL_BACKEND")


class GatewayPayload(BaseModel):
    action_id: str
    os3_ticket_id: str = ""
    x108_gate: str = "HOLD"
    scope: str = "*"
    action_type: str = "query"
    domain: str = "WORLD"
    irreversible: bool = False
    autonomy_level: int = 0
    agent_payload: dict[str, Any] = Field(default_factory=dict)


class BusDispatchPayload(BaseModel):
    action_id: str
    sovereign_ticket_id: str = ""
    world_call_class: str = "NO_WORLD_CALL"
    action_risk_class: str = "LOW"
    autonomy_level: int = 0
    intent: str = "INSPECT"
    domain: str = "WORLD"
    blocked: bool = True
    block_reason: str = ""


class TicketStatusPayload(BaseModel):
    ticket_id: str


class WorldDryRunPayload(BaseModel):
    action_id: str
    domain: str = "WORLD"
    x108_gate: str = "HOLD"
    input_hash: str = ""
    output_hash: str = ""
    trace_hash: str = ""
    gencoin_candidate: float = 0.0


class SystemPayload(BaseModel):
    pin_raw: float = 0.0
    paux: float = 0.0
    pstorage_in: float = 0.0
    pstorage_out: float = 0.0
    L_M2: float = 0.0
    L_storage: float = 0.0
    eta_nom: float = 0.75
    eta_min: float = 0.5
    eta_max: float = 0.9
    M3_threshold: float = 0.1
    topology_loss_base: float = 0.0
    constriction_ratio: float = 0.0
    turbulence: float = 0.0
    R_storage: float = 0.0
    R_storage_max: float = 100.0
    theta_on: float = 1.0
    theta_hold: float = 0.5
    theta_off: float = 0.1


class TruthGatePayload(BaseModel):
    action_id: str
    gencoin_candidate: float = 0.0
    system: SystemPayload = Field(default_factory=SystemPayload)


@router.post("/world/gateway")
async def blockchain_world_gateway(payload: GatewayPayload):
    wcc = classify_world_call(payload.action_type, payload.domain, payload.irreversible)

    # Secret boundary — redact then assert no secret escapes toward gateway
    agent_payload_safe = redact_secrets(payload.agent_payload or {})
    try:
        assert_no_secret_in_agent_payload(agent_payload_safe)
    except AssertionError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    # ── Étape A: Firewall Signaux (symbolic encoding + frequency validation) ──
    signal_value = int(payload.agent_payload.get("signal_value", 0) or 0)
    symbolic = encode_symbolic_number(signal_value)
    freq_hz = float(payload.agent_payload.get("frequency_hz", 0) or 0)
    freq_tag = map_frequency_tag(freq_hz) if freq_hz != 0 else None
    frequency_flux_validated = freq_tag is not None and len(freq_tag.matched_tags) > 0 if freq_tag else True

    # ── Étape B: Géométrie Canonique (dimensional hygiene + physics claim gate) ──
    formula_id = payload.agent_payload.get("formula_id", payload.action_id)
    units = payload.agent_payload.get("units", payload.agent_payload.get("unit_list", [])) or []
    dim_hygiene = check_dimensional_hygiene(formula_id, units, "symbolic")
    unit_check = check_unit_consistency(formula_id, units) if units else None
    dimensional_hygiene_pass = dim_hygiene.units_consistent and (unit_check is None or unit_check.all_si_compatible)
    
    claim_text = payload.agent_payload.get("claim_text", payload.action_type)
    physics_claim = evaluate_physics_claim(payload.action_id, claim_text, "symbolic")
    trajectory_state = "NORMAL"
    if physics_claim.gate == "HOLD":
        trajectory_state = "HOLD"
    if dim_hygiene.risk_flags:
        trajectory_state = "DEGRADED"
    if not dimensional_hygiene_pass and physics_claim.gate == "HOLD":
        trajectory_state = "RECALC"
    if physics_claim.gate == "HOLD" and len(dim_hygiene.risk_flags) >= 2:
        trajectory_state = "ABORT"

    # Action risk classification
    arc = classify_action_risk(payload.action_type, payload.domain, payload.irreversible)

    # Autonomy level matrix — take the stricter of computed vs declared
    computed_autonomy = compute_autonomy_level(arc, wcc)
    effective_autonomy = AutonomyLevel(min(5, max(int(computed_autonomy), payload.autonomy_level)))

    # Egress policy
    egress_gate, egress_reason = evaluate_egress_policy(wcc, arc, effective_autonomy, payload.x108_gate)

    # Route X25 conformity
    route_decision = route_x25(payload.action_id, wcc, effective_autonomy)

    ticket = issue_sovereign_ticket(
        action_id=payload.action_id,
        os3_ticket_id=payload.os3_ticket_id,
        x108_gate=payload.x108_gate,
        scope=payload.scope,
        autonomy_level=int(effective_autonomy),
        world_call_class=str(wcc),
    )
    store_ticket(ticket)
    decision = ObsidiaGateway().check(
        ticket=ticket,
        world_call_class=wcc,
        required_scope=payload.scope,
        agent_payload=agent_payload_safe or None,
    )

    # Dry-run executor — last execution barrier
    dry_run = execute_dry_run(payload.action_id, decision)
    dry_run.assert_not_executed()

    return safe_backend_response({
        **decision.to_dict(),
        "sovereign_ticket": ticket.to_dict(),
        "world_call_class": str(wcc),
        "action_risk_class": str(arc),
        "requires_x108_gate": requires_x108_gate(arc),
        "requires_human_approval": requires_human_approval(arc),
        "computed_autonomy_level": int(computed_autonomy),
        "effective_autonomy_level": int(effective_autonomy),
        "egress_gate": egress_gate,
        "egress_reason": egress_reason,
        "route": route_decision.route,
        "route_gate_required": route_decision.gate_required,
        "route_human_checkpoint": route_decision.human_checkpoint,
        "dry_run_simulated": dry_run.simulated,
        "dry_run_executed": dry_run.executed,
        "dimensional_hygiene_pass": dimensional_hygiene_pass,
        "trajectory_state": trajectory_state,
        "frequency_flux_validated": frequency_flux_validated,
        "symbolic_tags": symbolic.tags,
        "frequency_matched_tags": freq_tag.matched_tags if freq_tag else [],
        "physics_claim_gate": physics_claim.gate,
        "physics_claim_reason": physics_claim.reason,
        **_BOUNDARY,
    }, source="REAL_BACKEND")


@router.post("/world/bus-dispatch")
async def blockchain_world_bus_dispatch(payload: BusDispatchPayload):
    try:
        wcc_enum = WorldCallClass(payload.world_call_class)
    except ValueError:
        wcc_enum = WorldCallClass.NO_WORLD_CALL

    # Action risk from intent, autonomy matrix
    arc = classify_action_risk(payload.intent.lower(), payload.domain, False)
    computed_autonomy = compute_autonomy_level(arc, wcc_enum)
    effective_autonomy = AutonomyLevel(min(5, max(int(computed_autonomy), payload.autonomy_level)))

    # Egress policy — blocked events hold gate
    x108_gate = "HOLD" if payload.blocked else "ALLOW"
    egress_gate, egress_reason = evaluate_egress_policy(wcc_enum, arc, effective_autonomy, x108_gate)

    # Route X25 conformity check
    route_decision = route_x25(payload.action_id, wcc_enum, effective_autonomy)

    # Secret boundary on dispatch fields
    try:
        assert_no_secret_in_agent_payload({"block_reason": payload.block_reason, "intent": payload.intent})
    except AssertionError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    event = publish_event(
        action_id=payload.action_id,
        sovereign_ticket_id=payload.sovereign_ticket_id,
        world_call_class=payload.world_call_class,
        action_risk_class=str(arc),
        autonomy_level=int(effective_autonomy),
        intent=payload.intent,
        domain=payload.domain,
        blocked=payload.blocked,
        block_reason=payload.block_reason,
    )
    return safe_backend_response({
        **event.to_dict(),
        "action_risk_class": str(arc),
        "computed_autonomy_level": int(computed_autonomy),
        "effective_autonomy_level": int(effective_autonomy),
        "egress_gate": egress_gate,
        "egress_reason": egress_reason,
        "route": route_decision.route,
        "route_gate_required": route_decision.gate_required,
        "route_human_checkpoint": route_decision.human_checkpoint,
        **_BOUNDARY,
    }, source="REAL_BACKEND")


@router.post("/world/ticket-status")
async def blockchain_world_ticket_status(payload: TicketStatusPayload):
    all_tickets = load_tickets()
    match = next((t for t in all_tickets if t.get("ticket_id") == payload.ticket_id), None)
    return safe_backend_response({
        "ticket_id": payload.ticket_id,
        "found": match is not None,
        "ticket": match,
        **_BOUNDARY,
    }, source="REAL_BACKEND")


@router.post("/world/dry-run")
async def blockchain_world_dry_run(payload: WorldDryRunPayload):
    action_candidate = SimpleNamespace(
        action_id=payload.action_id,
        domain=payload.domain,
    )
    ticket = SimpleNamespace(
        x108_gate=payload.x108_gate,
        input_hash=payload.input_hash,
        output_hash=payload.output_hash,
        trace_hash=payload.trace_hash,
    )
    result = run_world_action_stub(action_candidate, ticket, payload.gencoin_candidate)
    result.assert_no_real_action()
    return safe_backend_response({**result.to_dict(), **_BOUNDARY}, source="REAL_BACKEND")


@router.post("/sandbox/simulate")
async def blockchain_sandbox_simulate(payload: SystemPayload):
    sys = System(
        pin_raw=payload.pin_raw, paux=payload.paux,
        pstorage_in=payload.pstorage_in, pstorage_out=payload.pstorage_out,
        L_M2=payload.L_M2, L_storage=payload.L_storage,
        eta_nom=payload.eta_nom, eta_min=payload.eta_min, eta_max=payload.eta_max,
        M3_threshold=payload.M3_threshold,
        topology_loss_base=payload.topology_loss_base,
        constriction_ratio=payload.constriction_ratio,
        turbulence=payload.turbulence,
        R_storage=payload.R_storage, R_storage_max=payload.R_storage_max,
        theta_on=payload.theta_on, theta_hold=payload.theta_hold, theta_off=payload.theta_off,
    )
    topo = topology_losses(sys)
    stepped = step(sys)
    sigma = compute_sigma(stepped, stepped.pout)
    return safe_backend_response({
        "topology_losses": topo,
        "sigma_score": sigma,
        "pout": stepped.pout,
        "state": stepped.state.value,
        "truth_score": stepped.truth_score,
        "delta_g": stepped.delta_g,
        "assisted_ratio": stepped.assisted_ratio,
        "L_total": stepped.L_total,
        **_BOUNDARY,
    }, source="REAL_BACKEND")


@router.post("/sandbox/truth-gate")
async def blockchain_sandbox_truth_gate(payload: TruthGatePayload):
    sp = payload.system
    sys = System(
        pin_raw=sp.pin_raw, paux=sp.paux,
        pstorage_in=sp.pstorage_in, pstorage_out=sp.pstorage_out,
        L_M2=sp.L_M2, L_storage=sp.L_storage,
        eta_nom=sp.eta_nom, eta_min=sp.eta_min, eta_max=sp.eta_max,
        M3_threshold=sp.M3_threshold,
        topology_loss_base=sp.topology_loss_base,
        constriction_ratio=sp.constriction_ratio,
        turbulence=sp.turbulence,
        R_storage=sp.R_storage, R_storage_max=sp.R_storage_max,
        theta_on=sp.theta_on, theta_hold=sp.theta_hold, theta_off=sp.theta_off,
    )
    metrics = compute_regime_metrics(sys)
    result = apply_regime_truth_gate(payload.action_id, payload.gencoin_candidate, metrics)
    return safe_backend_response({**result.to_dict(), **_BOUNDARY}, source="REAL_BACKEND")


class FraudCheckPayload(BaseModel):
    action_id: str
    chain_id: str = "unknown"
    action_class: str = "UNKNOWN_CHAIN_ACTION"
    defi_protocol: str = ""
    defi_operation: str = ""
    slippage_pct: float = 0.0
    protocol_audited: bool = False
    is_mainnet: bool = False
    contract_id: str = ""
    contract_action: str = "READ"
    has_audit: bool = False
    is_verified: bool = False
    is_proxy: bool = False
    has_unbounded_approval: bool = False
    bridge_id: str = ""
    source_chain: str = ""
    dest_chain: str = ""
    bridge_audited: bool = False
    liquidity_verified: bool = False
    value_eth: float = 0.0
    gas_limit: int = 21000


_AGENT_MODULES = [world_action_agent, gencoin_value_agent, os3_proof_agent, data_purity_agent, provenance_agent, brody_memory_agent, eml_symbolic_agent, energy_thermo_agent, timeverse_agent, ocs_generation_agent, operational_constance_agent, permission_economic_agent, action_sequence_agent, feedback_memory_agent]


@router.get("/agents/status")
async def blockchain_agents_status():
    registry = []
    for mod in _AGENT_MODULES:
        spec = mod.SPEC
        registry.append({
            "agent_id": spec.agent_id,
            "layer": str(spec.layer),
            "description": spec.description,
            "can_emit_act": spec.can_emit_act,
            "can_authorize": spec.can_authorize,
            "can_mutate_kernel": spec.can_mutate_kernel,
            "can_write_memory": spec.can_write_memory,
            "activation_status": "ACTIVE_NON_SOVEREIGN",
            "autonomy_level": 0,
        })
    return safe_backend_response({
        "agent_count": len(registry),
        "agents": registry,
        **_BOUNDARY,
    }, source="REAL_BACKEND")


@router.post("/classifiers/fraud-check")
async def blockchain_classifiers_fraud_check(payload: FraudCheckPayload):
    try:
        action_class_enum = BlockchainActionClass(payload.action_class)
    except ValueError:
        action_class_enum = BlockchainActionClass.UNKNOWN_CHAIN_ACTION

    action_decision = classify_blockchain_action(payload.action_id, action_class_enum)
    chain_ctx = build_chain_context(payload.chain_id)

    defi_decision = None
    if payload.defi_protocol:
        defi_decision = evaluate_defi_risk(
            action_id=payload.action_id,
            defi_protocol=payload.defi_protocol,
            operation=payload.defi_operation or "UNKNOWN",
            slippage_pct=payload.slippage_pct,
            protocol_audited=payload.protocol_audited,
            is_mainnet=payload.is_mainnet,
        )

    contract_decision = None
    if payload.contract_id:
        contract_decision = evaluate_smart_contract_risk(
            contract_id=payload.contract_id,
            action=payload.contract_action,
            has_audit=payload.has_audit,
            is_verified=payload.is_verified,
            is_proxy=payload.is_proxy,
            has_unbounded_approval=payload.has_unbounded_approval,
        )

    bridge_decision = None
    if payload.bridge_id:
        bridge_decision = evaluate_bridge_risk(
            bridge_id=payload.bridge_id,
            source_chain=payload.source_chain or payload.chain_id,
            dest_chain=payload.dest_chain,
            bridge_audited=payload.bridge_audited,
            liquidity_verified=payload.liquidity_verified,
        )

    tx_sim = simulate_transaction(
        tx_id=payload.action_id,
        chain_id=payload.chain_id,
        action_type=payload.action_class,
        value_eth=payload.value_eth,
        gas_limit=payload.gas_limit,
    )

    all_gates = [action_decision.gate]
    if tx_sim.risk_score >= 1.0:
        all_gates.append("BLOCK")
    elif tx_sim.risk_score > 0.0:
        all_gates.append("HOLD")
    if defi_decision:
        all_gates.append(defi_decision.gate)
    if contract_decision:
        all_gates.append(contract_decision.gate)
    if bridge_decision:
        all_gates.append(bridge_decision.gate)
    aggregate_gate = "BLOCK" if "BLOCK" in all_gates else ("HOLD" if "HOLD" in all_gates else "ALLOW")

    all_flags = list(tx_sim.risk_flags)
    if defi_decision:
        all_flags.extend(defi_decision.risk_flags)
    if contract_decision:
        all_flags.extend(contract_decision.risk_flags)
    if bridge_decision:
        all_flags.extend(bridge_decision.risk_flags)

    audit = build_onchain_audit_packet(
        action_id=payload.action_id,
        chain_id=payload.chain_id,
        action_class=str(action_class_enum),
        gate_result=aggregate_gate,
        reason=action_decision.reason,
        risk_flags=all_flags,
    )

    return safe_backend_response({
        "action_id": payload.action_id,
        "aggregate_gate": aggregate_gate,
        "action_decision": action_decision.to_dict(),
        "chain_context": chain_ctx.to_dict(),
        "tx_simulation": tx_sim.to_dict(),
        "defi_risk": defi_decision.to_dict() if defi_decision else None,
        "contract_risk": contract_decision.to_dict() if contract_decision else None,
        "bridge_risk": bridge_decision.to_dict() if bridge_decision else None,
        "audit_packet": audit.to_dict(),
        **_BOUNDARY,
    }, source="REAL_BACKEND")


@router.get("/status")
async def blockchain_status():
    return safe_backend_response({
        "gate_status": "READ_ONLY",
        "real_chain_action_allowed": False,
        "wallet_connected": False,
        "dry_run_only": True,
        "classified_actions": [],
        "mode": "REAL_BACKEND",
    }, source="REAL_BACKEND")

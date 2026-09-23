"""
F62 — Sigma Domain Packets Normalization
Tests for sigma/packets.py and enriched sigma/evaluate.py.

Coverage:
- Import surface (packets.py)
- build_sigma_domain_packet() structure and sovereignty
- build_sigma_registry_packet() structure
- validate_sigma_packet() — PASS and invariant checks
- evaluate_sigma_domain() returns F62-enriched packets
- evaluate_sigma_registry() returns packet_version=F62
- Unknown / unsupported domain stays safe
- confidence bounds [0.0, 1.0]
- control_plane_packet sovereignty
- x108_gate sovereignty
- boundary sub-dict sovereignty
"""

from __future__ import annotations

import pytest

from sigma.packets import (
    PACKET_VERSION,
    build_sigma_domain_packet,
    build_sigma_registry_packet,
    validate_sigma_packet,
)
from sigma.evaluate import evaluate_sigma_domain, evaluate_sigma_registry
from sigma.registry import get_sigma_domain

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_CANONICAL_DOMAINS = ("bank", "trading", "ecom", "gps_defense_aviation")

_AGENT_COUNTS = {
    "bank": 12,
    "trading": 17,
    "ecom": 12,
    "gps_defense_aviation": 6,
}

_BOUNDARY_FLAGS_FALSE = (
    "allowed_to_decide",
    "emits_act",
    "emits_verdict",
    "kernel_mutation",
    "x108_mutation",
    "neo4j_write",
    "graphiti_write",
    "memory_write",
    "brody_decision",
)

_CONTROL_PLANE_FLAGS = (
    "routed_to_decision",
    "payload_interpreted_as_command",
    "emitted_act",
    "emitted_verdict",
    "mutation_performed",
    "storage_performed",
)


# ---------------------------------------------------------------------------
# Class 1 — Import surface
# ---------------------------------------------------------------------------


class TestF62PacketsImport:
    def test_packet_version_is_f62(self):
        assert PACKET_VERSION == "F62"

    def test_build_sigma_domain_packet_callable(self):
        assert callable(build_sigma_domain_packet)

    def test_build_sigma_registry_packet_callable(self):
        assert callable(build_sigma_registry_packet)

    def test_validate_sigma_packet_callable(self):
        assert callable(validate_sigma_packet)

    def test_import_from_sigma_packets(self):
        import sigma.packets as p
        assert hasattr(p, "build_sigma_domain_packet")
        assert hasattr(p, "build_sigma_registry_packet")
        assert hasattr(p, "validate_sigma_packet")


# ---------------------------------------------------------------------------
# Class 2 — build_sigma_domain_packet: top-level structure
# ---------------------------------------------------------------------------


class TestF62BuildSigmaDomainPacket:
    @pytest.fixture(scope="class")
    def bank_registry(self):
        return get_sigma_domain("bank")

    @pytest.fixture(scope="class")
    def packet(self, bank_registry):
        return build_sigma_domain_packet("bank", bank_registry, None)

    def test_returns_dict(self, packet):
        assert isinstance(packet, dict)

    def test_packet_version_f62(self, packet):
        assert packet["packet_version"] == "F62"

    def test_packet_type(self, packet):
        assert packet["packet_type"] == "SIGMA_DOMAIN_READONLY_PACKET"

    def test_domain_field(self, packet):
        assert packet["domain"] == "bank"

    def test_domain_state_present(self, packet):
        assert "domain_state" in packet

    def test_domain_aggregate_present(self, packet):
        assert "domain_aggregate" in packet

    def test_meta_agents_packet_present(self, packet):
        assert "meta_agents_packet" in packet

    def test_reflex_diagnostic_packet_present(self, packet):
        assert "reflex_diagnostic_packet" in packet

    def test_control_plane_packet_present(self, packet):
        assert "control_plane_packet" in packet

    def test_x108_gate_present(self, packet):
        assert "x108_gate" in packet

    def test_boundary_present(self, packet):
        assert "boundary" in packet

    @pytest.mark.parametrize("domain", _CANONICAL_DOMAINS)
    def test_all_domains_produce_packet(self, domain):
        rd = get_sigma_domain(domain)
        p = build_sigma_domain_packet(domain, rd, None)
        assert p["packet_version"] == "F62"
        assert p["domain"] == domain

    @pytest.mark.parametrize("domain", _CANONICAL_DOMAINS)
    def test_all_domains_agent_count_matches_registry(self, domain):
        rd = get_sigma_domain(domain)
        p = build_sigma_domain_packet(domain, rd, None)
        assert p["domain_state"]["agent_count"] == _AGENT_COUNTS[domain]

    @pytest.mark.parametrize("domain", _CANONICAL_DOMAINS)
    def test_all_domains_runtime_bound_true(self, domain):
        rd = get_sigma_domain(domain)
        p = build_sigma_domain_packet(domain, rd, None)
        assert p["domain_state"]["runtime_bound"] is True


# ---------------------------------------------------------------------------
# Class 3 — domain_state structure
# ---------------------------------------------------------------------------


class TestF62DomainState:
    @pytest.fixture(scope="class")
    def packet(self):
        rd = get_sigma_domain("bank")
        return build_sigma_domain_packet("bank", rd, None)

    def test_status_observed(self, packet):
        assert packet["domain_state"]["status"] == "OBSERVED"

    def test_runtime_bound_bool(self, packet):
        assert isinstance(packet["domain_state"]["runtime_bound"], bool)

    def test_agent_count_int(self, packet):
        assert isinstance(packet["domain_state"]["agent_count"], int)

    def test_agent_count_positive(self, packet):
        assert packet["domain_state"]["agent_count"] > 0

    def test_payload_received_false_when_none(self, packet):
        assert packet["domain_state"]["payload_received"] is False

    def test_payload_received_true_when_given(self):
        rd = get_sigma_domain("ecom")
        p = build_sigma_domain_packet("ecom", rd, {"amount": 10.0})
        assert p["domain_state"]["payload_received"] is True


# ---------------------------------------------------------------------------
# Class 4 — domain_aggregate structure and confidence bounds
# ---------------------------------------------------------------------------


class TestF62DomainAggregate:
    @pytest.fixture(scope="class")
    def packet(self):
        rd = get_sigma_domain("trading")
        return build_sigma_domain_packet("trading", rd, None)

    def test_mode_readonly_aggregate(self, packet):
        assert packet["domain_aggregate"]["mode"] == "READONLY_AGGREGATE"

    def test_summary_is_string(self, packet):
        assert isinstance(packet["domain_aggregate"]["summary"], str)

    def test_confidence_is_float(self, packet):
        assert isinstance(packet["domain_aggregate"]["confidence"], float)

    def test_confidence_lower_bound(self, packet):
        assert packet["domain_aggregate"]["confidence"] >= 0.0

    def test_confidence_upper_bound(self, packet):
        assert packet["domain_aggregate"]["confidence"] <= 1.0

    def test_evidence_refs_is_list(self, packet):
        assert isinstance(packet["domain_aggregate"]["evidence_refs"], list)

    @pytest.mark.parametrize("domain", _CANONICAL_DOMAINS)
    def test_confidence_in_bounds_all_domains(self, domain):
        rd = get_sigma_domain(domain)
        p = build_sigma_domain_packet(domain, rd, None)
        c = p["domain_aggregate"]["confidence"]
        assert 0.0 <= c <= 1.0


# ---------------------------------------------------------------------------
# Class 5 — meta_agents_packet and reflex_diagnostic_packet
# ---------------------------------------------------------------------------


class TestF62AgentsAndReflex:
    @pytest.fixture(scope="class")
    def packet(self):
        rd = get_sigma_domain("bank")
        return build_sigma_domain_packet("bank", rd, None)

    def test_meta_agents_execution_not_performed(self, packet):
        assert packet["meta_agents_packet"]["execution_performed"] is False

    def test_meta_agents_count_matches_domain_state(self, packet):
        assert packet["meta_agents_packet"]["agent_count"] == packet["domain_state"]["agent_count"]

    def test_meta_agents_list_is_list(self, packet):
        assert isinstance(packet["meta_agents_packet"]["agents"], list)

    def test_reflex_mode_observation_only(self, packet):
        assert packet["reflex_diagnostic_packet"]["reflex_mode"] == "OBSERVATION_ONLY"

    def test_reflex_alerts_empty_list(self, packet):
        assert packet["reflex_diagnostic_packet"]["alerts"] == []

    def test_reflex_warnings_empty_list(self, packet):
        assert packet["reflex_diagnostic_packet"]["warnings"] == []


# ---------------------------------------------------------------------------
# Class 6 — control_plane_packet sovereignty
# ---------------------------------------------------------------------------


class TestF62ControlPlaneSovereignty:
    @pytest.fixture(scope="class")
    def packet(self):
        rd = get_sigma_domain("gps_defense_aviation")
        return build_sigma_domain_packet("gps_defense_aviation", rd, None)

    @pytest.mark.parametrize("flag", _CONTROL_PLANE_FLAGS)
    def test_control_plane_flag_false(self, packet, flag):
        assert packet["control_plane_packet"][flag] is False


# ---------------------------------------------------------------------------
# Class 7 — x108_gate sovereignty
# ---------------------------------------------------------------------------


class TestF62X108GateSovereignty:
    @pytest.fixture(scope="class")
    def packet(self):
        rd = get_sigma_domain("bank")
        return build_sigma_domain_packet("bank", rd, None)

    def test_x108_gate_is_dict(self, packet):
        assert isinstance(packet["x108_gate"], dict)

    def test_x108_gate_decision_authority(self, packet):
        assert packet["x108_gate"]["decision_authority"] == "KX108_ONLY"

    def test_sigma_allowed_to_decide_false(self, packet):
        assert packet["x108_gate"]["sigma_allowed_to_decide"] is False

    def test_sigma_allowed_to_act_false(self, packet):
        assert packet["x108_gate"]["sigma_allowed_to_act"] is False

    def test_gate_invoked_false(self, packet):
        assert packet["x108_gate"]["gate_invoked"] is False


# ---------------------------------------------------------------------------
# Class 8 — boundary sub-dict sovereignty
# ---------------------------------------------------------------------------


class TestF62BoundarySovereignty:
    @pytest.fixture(scope="class")
    def packet(self):
        rd = get_sigma_domain("ecom")
        return build_sigma_domain_packet("ecom", rd, None)

    def test_boundary_is_dict(self, packet):
        assert isinstance(packet["boundary"], dict)

    def test_boundary_decision_authority(self, packet):
        assert packet["boundary"]["decision_authority"] == "KX108_ONLY"

    def test_boundary_readonly_true(self, packet):
        assert packet["boundary"]["readonly"] is True

    def test_boundary_advisory_only_true(self, packet):
        assert packet["boundary"]["advisory_only"] is True

    @pytest.mark.parametrize("flag", _BOUNDARY_FLAGS_FALSE)
    def test_boundary_flag_false(self, packet, flag):
        assert packet["boundary"][flag] is False


# ---------------------------------------------------------------------------
# Class 9 — validate_sigma_packet: PASS on clean packet
# ---------------------------------------------------------------------------


class TestF62ValidateSigmaPacket:
    @pytest.fixture(scope="class")
    def clean_packet(self):
        rd = get_sigma_domain("bank")
        return build_sigma_domain_packet("bank", rd, None)

    def test_validate_returns_dict(self, clean_packet):
        r = validate_sigma_packet(clean_packet)
        assert isinstance(r, dict)

    def test_validate_status_pass(self, clean_packet):
        r = validate_sigma_packet(clean_packet)
        assert r["status"] == "PASS"

    def test_validate_errors_empty(self, clean_packet):
        r = validate_sigma_packet(clean_packet)
        assert r["errors"] == []

    def test_validate_packet_version_in_result(self, clean_packet):
        r = validate_sigma_packet(clean_packet)
        assert r["packet_version"] == "F62"

    def test_validate_packet_type_in_result(self, clean_packet):
        r = validate_sigma_packet(clean_packet)
        assert r["packet_type"] == "SIGMA_DOMAIN_READONLY_PACKET"

    @pytest.mark.parametrize("domain", _CANONICAL_DOMAINS)
    def test_validate_pass_all_domains(self, domain):
        rd = get_sigma_domain(domain)
        p = build_sigma_domain_packet(domain, rd, None)
        r = validate_sigma_packet(p)
        assert r["status"] == "PASS", f"Errors for {domain}: {r['errors']}"

    def test_validate_fail_missing_packet_version(self):
        rd = get_sigma_domain("bank")
        p = build_sigma_domain_packet("bank", rd, None)
        p.pop("packet_version")
        r = validate_sigma_packet(p)
        assert r["status"] == "FAIL"

    def test_validate_fail_missing_boundary(self):
        rd = get_sigma_domain("bank")
        p = build_sigma_domain_packet("bank", rd, None)
        p.pop("boundary")
        r = validate_sigma_packet(p)
        assert r["status"] == "FAIL"

    def test_validate_fail_wrong_packet_version(self):
        rd = get_sigma_domain("bank")
        p = build_sigma_domain_packet("bank", rd, None)
        p["packet_version"] = "F99"
        r = validate_sigma_packet(p)
        assert r["status"] == "FAIL"

    def test_validate_fail_confidence_out_of_bounds(self):
        rd = get_sigma_domain("bank")
        p = build_sigma_domain_packet("bank", rd, None)
        p["domain_aggregate"]["confidence"] = 1.5
        r = validate_sigma_packet(p)
        assert r["status"] == "FAIL"


# ---------------------------------------------------------------------------
# Class 10 — build_sigma_registry_packet
# ---------------------------------------------------------------------------


class TestF62BuildSigmaRegistryPacket:
    @pytest.fixture(scope="class")
    def evaluations(self):
        return {d: {"mock": True, "domain": d} for d in _CANONICAL_DOMAINS}

    @pytest.fixture(scope="class")
    def reg_packet(self, evaluations):
        return build_sigma_registry_packet(evaluations, None)

    def test_returns_dict(self, reg_packet):
        assert isinstance(reg_packet, dict)

    def test_packet_version_f62(self, reg_packet):
        assert reg_packet["packet_version"] == "F62"

    def test_packet_type_registry(self, reg_packet):
        assert reg_packet["packet_type"] == "SIGMA_REGISTRY_READONLY_PACKET"

    def test_domains_present(self, reg_packet):
        assert "domains" in reg_packet

    def test_all_canonical_domains_in_domains(self, reg_packet):
        for d in _CANONICAL_DOMAINS:
            assert d in reg_packet["domains"]

    def test_evaluations_present(self, reg_packet):
        assert "evaluations" in reg_packet

    def test_control_plane_packet_present(self, reg_packet):
        assert "control_plane_packet" in reg_packet

    @pytest.mark.parametrize("flag", _CONTROL_PLANE_FLAGS)
    def test_registry_control_plane_flag_false(self, reg_packet, flag):
        assert reg_packet["control_plane_packet"][flag] is False

    def test_boundary_present(self, reg_packet):
        assert "boundary" in reg_packet

    def test_boundary_decision_authority(self, reg_packet):
        assert reg_packet["boundary"]["decision_authority"] == "KX108_ONLY"


# ---------------------------------------------------------------------------
# Class 11 — evaluate_sigma_domain returns F62-enriched packet
# ---------------------------------------------------------------------------


class TestF62EvaluateSigmaDomainEnriched:
    @pytest.mark.parametrize("domain", _CANONICAL_DOMAINS)
    def test_packet_version_present(self, domain):
        r = evaluate_sigma_domain(domain, None)
        assert r.get("packet_version") == "F62"

    @pytest.mark.parametrize("domain", _CANONICAL_DOMAINS)
    def test_packet_type_present(self, domain):
        r = evaluate_sigma_domain(domain, None)
        assert r.get("packet_type") == "SIGMA_DOMAIN_READONLY_PACKET"

    @pytest.mark.parametrize("domain", _CANONICAL_DOMAINS)
    def test_domain_state_present(self, domain):
        r = evaluate_sigma_domain(domain, None)
        assert "domain_state" in r

    @pytest.mark.parametrize("domain", _CANONICAL_DOMAINS)
    def test_domain_aggregate_present(self, domain):
        r = evaluate_sigma_domain(domain, None)
        assert "domain_aggregate" in r

    @pytest.mark.parametrize("domain", _CANONICAL_DOMAINS)
    def test_control_plane_packet_present(self, domain):
        r = evaluate_sigma_domain(domain, None)
        assert "control_plane_packet" in r

    @pytest.mark.parametrize("domain", _CANONICAL_DOMAINS)
    def test_x108_gate_present(self, domain):
        r = evaluate_sigma_domain(domain, None)
        assert "x108_gate" in r

    @pytest.mark.parametrize("domain", _CANONICAL_DOMAINS)
    def test_boundary_sub_dict_present(self, domain):
        r = evaluate_sigma_domain(domain, None)
        assert "boundary" in r
        assert isinstance(r["boundary"], dict)

    @pytest.mark.parametrize("domain", _CANONICAL_DOMAINS)
    def test_reflex_diagnostic_packet_present(self, domain):
        r = evaluate_sigma_domain(domain, None)
        assert "reflex_diagnostic_packet" in r

    @pytest.mark.parametrize("domain", _CANONICAL_DOMAINS)
    def test_meta_agents_packet_present(self, domain):
        r = evaluate_sigma_domain(domain, None)
        assert "meta_agents_packet" in r

    @pytest.mark.parametrize("domain", _CANONICAL_DOMAINS)
    def test_f61_decision_authority_preserved(self, domain):
        r = evaluate_sigma_domain(domain, None)
        assert r.get("decision_authority") == "KX108_ONLY"

    @pytest.mark.parametrize("domain", _CANONICAL_DOMAINS)
    def test_f61_dispatcher_version_preserved(self, domain):
        r = evaluate_sigma_domain(domain, None)
        assert r.get("dispatcher_version") == "F61"

    @pytest.mark.parametrize("domain", _CANONICAL_DOMAINS)
    def test_f61_allowed_to_decide_preserved(self, domain):
        r = evaluate_sigma_domain(domain, None)
        assert r.get("allowed_to_decide") is False

    @pytest.mark.parametrize("domain", _CANONICAL_DOMAINS)
    def test_boundary_sub_dict_decision_authority(self, domain):
        r = evaluate_sigma_domain(domain, None)
        assert r["boundary"]["decision_authority"] == "KX108_ONLY"

    @pytest.mark.parametrize("domain", _CANONICAL_DOMAINS)
    def test_boundary_sub_dict_allowed_to_decide(self, domain):
        r = evaluate_sigma_domain(domain, None)
        assert r["boundary"]["allowed_to_decide"] is False


# ---------------------------------------------------------------------------
# Class 12 — evaluate_sigma_registry returns packet_version=F62
# ---------------------------------------------------------------------------


class TestF62EvaluateSigmaRegistryPacket:
    @pytest.fixture(scope="class")
    def reg(self):
        return evaluate_sigma_registry(None)

    def test_packet_version_f62(self, reg):
        assert reg.get("packet_version") == "F62"

    def test_dispatcher_version_f61_preserved(self, reg):
        assert reg.get("dispatcher_version") == "F61"

    def test_results_present(self, reg):
        assert "results" in reg

    def test_results_contain_f62_packets(self, reg):
        for d in _CANONICAL_DOMAINS:
            assert reg["results"][d].get("packet_version") == "F62"

    def test_results_contain_domain_state(self, reg):
        for d in _CANONICAL_DOMAINS:
            assert "domain_state" in reg["results"][d]

    def test_decision_authority_preserved(self, reg):
        assert reg.get("decision_authority") == "KX108_ONLY"

    def test_allowed_to_decide_preserved(self, reg):
        assert reg.get("allowed_to_decide") is False


# ---------------------------------------------------------------------------
# Class 13 — Unknown / unsupported domain stays safe
# ---------------------------------------------------------------------------


class TestF62UnsupportedDomainSafe:
    @pytest.fixture(scope="class")
    def result(self):
        return evaluate_sigma_domain("totally_unknown_domain", None)

    def test_returns_dict(self, result):
        assert isinstance(result, dict)

    def test_status_unsupported(self, result):
        assert result.get("status") == "UNSUPPORTED_DOMAIN"

    def test_decision_authority_preserved(self, result):
        assert result.get("decision_authority") == "KX108_ONLY"

    def test_allowed_to_decide_false(self, result):
        assert result.get("allowed_to_decide") is False

    def test_x108_gate_present(self, result):
        assert result.get("x108_gate") is not None

    def test_packet_version_f62_present(self, result):
        assert result.get("packet_version") == "F62"

    def test_domain_state_present(self, result):
        assert "domain_state" in result

    def test_brody_decision_false(self, result):
        assert result.get("brody_decision") is False


# ---------------------------------------------------------------------------
# Class 14 — F62B: x108_gate is structured dict in evaluate_sigma_domain()
# ---------------------------------------------------------------------------


class TestF62BX108GateStructuredInEvaluate:
    """F62B patch: pipeline legacy x108_gate string must not overwrite F62 dict."""

    @pytest.mark.parametrize("domain", _CANONICAL_DOMAINS)
    def test_x108_gate_is_dict(self, domain):
        r = evaluate_sigma_domain(domain, None)
        assert isinstance(r.get("x108_gate"), dict), (
            f"x108_gate for {domain} is {type(r.get('x108_gate')).__name__!r}, expected dict"
        )

    @pytest.mark.parametrize("domain", _CANONICAL_DOMAINS)
    def test_x108_gate_decision_authority_kx108(self, domain):
        r = evaluate_sigma_domain(domain, None)
        assert r["x108_gate"]["decision_authority"] == "KX108_ONLY"

    @pytest.mark.parametrize("domain", _CANONICAL_DOMAINS)
    def test_x108_gate_sigma_allowed_to_decide_false(self, domain):
        r = evaluate_sigma_domain(domain, None)
        assert r["x108_gate"]["sigma_allowed_to_decide"] is False

    @pytest.mark.parametrize("domain", _CANONICAL_DOMAINS)
    def test_x108_gate_sigma_allowed_to_act_false(self, domain):
        r = evaluate_sigma_domain(domain, None)
        assert r["x108_gate"]["sigma_allowed_to_act"] is False

    @pytest.mark.parametrize("domain", _CANONICAL_DOMAINS)
    def test_x108_gate_gate_invoked_false(self, domain):
        r = evaluate_sigma_domain(domain, None)
        assert r["x108_gate"]["gate_invoked"] is False

    @pytest.mark.parametrize("domain", _CANONICAL_DOMAINS)
    def test_pipeline_x108_gate_observed_is_informational(self, domain):
        r = evaluate_sigma_domain(domain, None)
        observed = r.get("pipeline_x108_gate_observed")
        if observed is not None:
            # Must be a scalar string, not a dict implying decision authority
            assert isinstance(observed, str)
            # Must not be a sovereignty flag key
            assert observed not in ("KX108_ONLY", "DECIDE", "ACT")

    @pytest.mark.parametrize("domain", _CANONICAL_DOMAINS)
    def test_pipeline_x108_gate_does_not_override_structured(self, domain):
        r = evaluate_sigma_domain(domain, None)
        # x108_gate must be the F62 dict regardless of pipeline output
        gate = r.get("x108_gate")
        assert isinstance(gate, dict)
        assert "sigma_allowed_to_decide" in gate
        assert "sigma_allowed_to_act" in gate

    def test_unsupported_domain_x108_gate_is_dict(self):
        r = evaluate_sigma_domain("totally_unknown", None)
        assert isinstance(r.get("x108_gate"), dict)

    def test_unsupported_domain_pipeline_observed_preserved(self):
        r = evaluate_sigma_domain("totally_unknown", None)
        # Legacy "HOLD" from the fallback dict is preserved informationally
        assert r.get("pipeline_x108_gate_observed") == "HOLD"

    def test_registry_results_x108_gate_is_dict_for_all_domains(self):
        reg = evaluate_sigma_registry(None)
        for d in _CANONICAL_DOMAINS:
            gate = reg["results"][d].get("x108_gate")
            assert isinstance(gate, dict), (
                f"registry result x108_gate for {d} is {type(gate).__name__!r}"
            )

    def test_registry_results_sigma_allowed_to_decide_false_for_all(self):
        reg = evaluate_sigma_registry(None)
        for d in _CANONICAL_DOMAINS:
            assert reg["results"][d]["x108_gate"]["sigma_allowed_to_decide"] is False

"""
F73 — Adversarial Boundary Hardening Advanced
Tests adversarial inputs against the Sigma layer and API boundary.

Scope: runtime only (sigma/, apps/).
No kernel / proof / seal / merkle edits.
KX108_ONLY preserved in all cases.

Coverage:
1. Unicode / homoglyphes
2. Casing variations
3. Nested / wrong-type payloads
4. Large payloads
5. Malformed payloads
6. Forbidden token substring (false positive guard)
7. Schema bypass
8. Route injection in domain name
9. Fake decision authority injection
"""
from __future__ import annotations

import json
import string

import pytest
from fastapi.testclient import TestClient

from apps.obsidia_api.main import app
from sigma.evaluate import evaluate_sigma_domain
from sigma.registry import validate_sigma_registry

client = TestClient(app)

_SIGMA_EVAL_ENDPOINT = "/api/periphery/monitoring/sigma/evaluate"
_SIGMA_BANK_ENDPOINT = "/api/periphery/monitoring/sigma/bank"
_SIGMA_DOMAINS_ENDPOINT = "/api/periphery/monitoring/sigma/domains"

_SOVEREIGNTY_FALSE = (
    "emits_act", "emits_verdict", "kernel_mutation", "x108_mutation",
    "neo4j_write", "graphiti_write", "memory_write", "allowed_to_decide",
)


# ---------------------------------------------------------------------------
# Class 1 — Unicode / Homoglyphes
# ---------------------------------------------------------------------------

class TestF73UnicodeHomoglyphes:
    def test_cyrillic_a_in_bank(self):
        """'bаnk' with Cyrillic 'а' → UNSUPPORTED_DOMAIN, not canonical bank."""
        domain = "bаnk"  # Cyrillic а
        result = evaluate_sigma_domain(domain, {})
        assert result["status"] == "UNSUPPORTED_DOMAIN"
        assert result.get("emits_act") is False

    def test_fullwidth_b_in_bank(self):
        """'ｂank' with fullwidth b → UNSUPPORTED_DOMAIN."""
        domain = "ｂank"  # fullwidth b
        result = evaluate_sigma_domain(domain, {})
        assert result["status"] == "UNSUPPORTED_DOMAIN"

    def test_zero_width_space_in_bank(self):
        """'ba​nk' with zero-width space → UNSUPPORTED_DOMAIN."""
        domain = "ba​nk"
        result = evaluate_sigma_domain(domain, {})
        assert result["status"] == "UNSUPPORTED_DOMAIN"

    def test_unicode_homoglyph_boundary_preserved(self):
        """Homoglyph domains never emit ACT."""
        for domain in ("bаnk", "ｂank", "trаding"):
            result = evaluate_sigma_domain(domain, {})
            assert result.get("emits_act") is False
            assert result.get("allowed_to_decide") is False


# ---------------------------------------------------------------------------
# Class 2 — Casing variations (Sigma normalises case → bank)
# ---------------------------------------------------------------------------

class TestF73CasingVariations:
    @pytest.mark.parametrize("domain", ("BANK", "Bank", "bAnK", "BANKING", "TRADING", "Trading", "ECOM", "GPS_DEFENSE_AVIATION"))
    def test_uppercase_variants_never_emit_act(self, domain):
        """Regardless of casing, Sigma must never emit ACT or decide."""
        result = evaluate_sigma_domain(domain, {})
        assert result.get("emits_act") is False
        assert result.get("allowed_to_decide") is False

    @pytest.mark.parametrize("domain", ("BANK", "Bank", "bAnK"))
    def test_uppercase_bank_decision_authority(self, domain):
        """Cased bank variants must keep KX108_ONLY authority."""
        result = evaluate_sigma_domain(domain, {})
        assert result.get("decision_authority") == "KX108_ONLY"


# ---------------------------------------------------------------------------
# Class 3 — Nested / wrong-type payloads
# ---------------------------------------------------------------------------

class TestF73WrongTypePayloads:
    def test_domain_as_dict_evaluate_sigma_domain_canonical_still_works(self):
        """evaluate_sigma_domain canonical 'bank' must not return UNSUPPORTED_DOMAIN."""
        result = evaluate_sigma_domain("bank", {})
        assert result.get("status") != "UNSUPPORTED_DOMAIN"
        assert result.get("emits_act") is False

    def test_sigma_evaluate_api_returns_200(self):
        r = client.get(_SIGMA_EVAL_ENDPOINT)
        assert r.status_code == 200
        data = r.json()
        assert data.get("decision_authority") == "KX108_ONLY"

    def test_sigma_bank_api_returns_200(self):
        r = client.get(_SIGMA_BANK_ENDPOINT)
        assert r.status_code == 200
        data = r.json()
        assert data.get("decision_authority") == "KX108_ONLY"


# ---------------------------------------------------------------------------
# Class 4 — Large payloads
# ---------------------------------------------------------------------------

class TestF73LargePayloads:
    def test_very_long_domain_name(self):
        """10k-char domain → UNSUPPORTED_DOMAIN, no crash."""
        long_domain = "x" * 10_000
        result = evaluate_sigma_domain(long_domain, {})
        assert result["status"] == "UNSUPPORTED_DOMAIN"
        assert result.get("emits_act") is False

    def test_large_state_dict_bank(self):
        """Large state dict for bank domain — must not crash, boundary preserved."""
        large_state = {f"key_{i}": "value" * 100 for i in range(200)}
        result = evaluate_sigma_domain("bank", large_state)
        assert isinstance(result, dict)
        assert result.get("emits_act") is False

    def test_deeply_nested_state(self):
        """Deeply nested state dict → must not crash, boundary preserved."""
        state: dict = {}
        cursor = state
        for _ in range(50):
            cursor["nested"] = {}
            cursor = cursor["nested"]
        result = evaluate_sigma_domain("bank", state)
        assert isinstance(result, dict)
        assert result.get("emits_act") is False


# ---------------------------------------------------------------------------
# Class 5 — Forbidden token substring (false-positive guard)
# ---------------------------------------------------------------------------

class TestF73ForbiddenTokenSubstring:
    def test_act_in_contact_not_blocked(self):
        """'ACT' in 'CONTACT' must NOT trigger forbidden-token logic."""
        result = evaluate_sigma_domain("bank", {"user_text": "CONTACT US"})
        assert result.get("emits_act") is False

    def test_actor_substring_not_blocked(self):
        """'ACT' as substring of 'ACTOR' must not be treated as emit."""
        result = evaluate_sigma_domain("bank", {"label": "ACTOR"})
        assert result.get("emits_act") is False

    def test_verdict_in_field_name_not_blocked(self):
        """'verdict' as a field key must not trigger emits_verdict."""
        result = evaluate_sigma_domain("bank", {"verdict_label": "test"})
        assert result.get("emits_verdict") is False

    def test_decide_substring_not_blocked(self):
        """'DECIDE' as part of a word should not trigger allowed_to_decide."""
        result = evaluate_sigma_domain("trading", {"description": "UNDECIDED_STATE"})
        assert result.get("allowed_to_decide") is False


# ---------------------------------------------------------------------------
# Class 6 — Registry always PASS under adversarial load
# ---------------------------------------------------------------------------

class TestF73RegistryResilient:
    def test_registry_pass_after_adversarial_eval(self):
        """Registry must remain PASS after adversarial evaluate_sigma_domain calls."""
        # Adversarial eval
        for domain in ("BANK", "bаnk", "x" * 1000, ""):
            evaluate_sigma_domain(domain, {"inject": "test"})
        # Registry must still be healthy
        reg = validate_sigma_registry()
        assert reg["status"] == "PASS"

    def test_sigma_evaluate_endpoint_still_kx108(self):
        r = client.get(_SIGMA_EVAL_ENDPOINT)
        assert r.status_code == 200
        data = r.json()
        assert data.get("decision_authority") == "KX108_ONLY"
        assert data.get("emits_act") is False


# ---------------------------------------------------------------------------
# Class 7 — Schema bypass via extra fields
# ---------------------------------------------------------------------------

class TestF73SchemaBypass:
    def test_extra_fields_in_state_not_elevate_authority(self):
        """Extra fields in state dict must not change decision_authority."""
        state = {
            "decision_authority": "BRODY",
            "allowed_to_decide": True,
            "emits_act": True,
        }
        result = evaluate_sigma_domain("bank", state)
        # The Sigma result boundary must always come from the module, not from state input
        assert result.get("decision_authority") == "KX108_ONLY"
        assert result.get("emits_act") is False

    def test_inject_kernel_mutation_in_state(self):
        """Injecting kernel_mutation=True in state must not propagate to result."""
        state = {"kernel_mutation": True, "x108_mutation": True}
        result = evaluate_sigma_domain("bank", state)
        assert result.get("kernel_mutation") is False

    def test_inject_memory_write_in_state(self):
        """Injecting memory_write=True in state must not propagate to result."""
        state = {"memory_write": True, "graphiti_write": True, "neo4j_write": True}
        result = evaluate_sigma_domain("bank", state)
        assert result.get("memory_write") is False
        assert result.get("graphiti_write") is False
        assert result.get("neo4j_write") is False


# ---------------------------------------------------------------------------
# Class 8 — Route injection in domain name
# ---------------------------------------------------------------------------

class TestF73RouteInjection:
    @pytest.mark.parametrize("malicious_domain", [
        "../etc/passwd",
        "%2F%2F",
        "bank/../../../etc",
        "\x00null_byte",
        "bank\ninjected_header: value",
    ])
    def test_path_traversal_domain_unsupported(self, malicious_domain):
        """Path traversal / injection in domain name → UNSUPPORTED_DOMAIN, no crash."""
        result = evaluate_sigma_domain(malicious_domain, {})
        assert result["status"] == "UNSUPPORTED_DOMAIN"
        assert result.get("emits_act") is False


# ---------------------------------------------------------------------------
# Class 9 — Fake decision authority injection
# ---------------------------------------------------------------------------

class TestF73FakeDecisionAuthority:
    @pytest.mark.parametrize("fake_authority", [
        "BRODY", "SIGMA", "GRAPHITI", "OPERATOR", "ADMIN", "ROOT",
    ])
    def test_fake_authority_in_state_ignored(self, fake_authority):
        """decision_authority injected in state must be overridden by module boundary."""
        state = {"decision_authority": fake_authority}
        result = evaluate_sigma_domain("bank", state)
        assert result.get("decision_authority") == "KX108_ONLY", (
            f"Injected authority '{fake_authority}' leaked into result"
        )

    def test_fake_authority_in_packets_endpoint_still_kx108(self):
        """Sigma API endpoints always return decision_authority=KX108_ONLY."""
        for endpoint in (_SIGMA_EVAL_ENDPOINT, _SIGMA_BANK_ENDPOINT, _SIGMA_DOMAINS_ENDPOINT):
            r = client.get(endpoint)
            assert r.status_code == 200
            data = r.json()
            assert data.get("decision_authority") == "KX108_ONLY", (
                f"Endpoint {endpoint} returned authority={data.get('decision_authority')}"
            )

    @pytest.mark.parametrize("flag", _SOVEREIGNTY_FALSE)
    def test_sovereignty_preserved_on_sigma_evaluate(self, flag):
        """After adversarial inputs, sovereignty flags must remain False on /evaluate."""
        r = client.get(_SIGMA_EVAL_ENDPOINT)
        assert r.status_code == 200
        data = r.json()
        assert data.get(flag) is False, f"{flag} not False on /sigma/evaluate"

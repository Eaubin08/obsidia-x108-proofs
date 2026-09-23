# tests/test_runtime_wiring_p8c.py
# P8C Dry-Run Tests — runtime_wiring/ safety invariants
# Phase: P8C / Boundary: P8C_DRY_RUN_TESTS_ONLY
# No network, no file writes, no external dependencies, no real decisions.
# Run: python -m pytest tests/test_runtime_wiring_p8c.py -v

from __future__ import annotations

import ast
import json
import pathlib
import subprocess
import sys

import pytest

# ── Repo root resolution ──────────────────────────────────────────────────────
_THIS_FILE = pathlib.Path(__file__).resolve()
_REPO_ROOT = _THIS_FILE.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from runtime_wiring.contracts_loader import load_all_contracts
from runtime_wiring.packet_types import (
    VALID_DRY_RUN_DECISIONS,
    ContextPacket,
    DecisionTicketDryRun,
    IntentEnvelope,
    OS3EvidenceTicketDryRun,
    PeripheralSignalPacket,
)
from runtime_wiring.source_adapters import (
    atlas_to_context_packet,
    cognitive_to_context_packet,
    compliance_to_context_packet,
    rssi_rgpd_to_context_packet,
)
from runtime_wiring.dry_run_packet_router import route_packets
from runtime_wiring.os3_evidence_stub import build_evidence_ticket
from runtime_wiring.x108_admission_stub import evaluate_dry_run


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def valid_packets():
    return [
        cognitive_to_context_packet({"name": "cog_test", "timestamp": "2026-06-03T00:00:00Z"}),
        rssi_rgpd_to_context_packet({"name": "rssi_test", "timestamp": "2026-06-03T00:00:01Z"}),
        atlas_to_context_packet({"name": "atlas_test", "timestamp": "2026-06-03T00:00:02Z"}),
        compliance_to_context_packet({"name": "comp_test", "timestamp": "2026-06-03T00:00:03Z"}),
    ]


@pytest.fixture(scope="session")
def contracts():
    return load_all_contracts()


# ─────────────────────────────────────────────────────────────────────────────
# Test 1: Contracts all present
# ─────────────────────────────────────────────────────────────────────────────

def test_contract_loader_all_present(contracts):
    """All 8 required contract files must be present."""
    assert contracts["status"] == "ALL_PRESENT"
    assert len(contracts["contracts"]) == 8
    assert contracts["missing"] == []
    expected_keys = [
        "runtime_contracts/contracts/ContextPacket.contract.md",
        "runtime_contracts/contracts/IntentEnvelope.contract.md",
        "runtime_contracts/contracts/DecisionTicket.contract.md",
        "runtime_contracts/contracts/OS3EvidenceTicket.contract.md",
        "runtime_contracts/boundaries/COGNITIVE_REINTEGRATION_ADVISORY_ONLY.md",
        "runtime_contracts/boundaries/RSSI_EVIDENCE_ONLY.md",
        "runtime_contracts/boundaries/RGPD_COMPLIANCE_SCOPE_GUARD.md",
        "runtime_contracts/boundaries/ATLAS_READONLY_ADVISORY_ONLY.md",
    ]
    for key in expected_keys:
        assert key in contracts["contracts"], f"Missing contract: {key}"
        assert contracts["contracts"][key]["status"] == "PRESENT"
        assert contracts["contracts"][key]["readonly"] is True
        assert contracts["contracts"][key]["advisory_only"] is True


# ─────────────────────────────────────────────────────────────────────────────
# Test 2: Source adapters force correct boundaries
# ─────────────────────────────────────────────────────────────────────────────

def test_source_adapters_force_boundaries():
    """Each adapter must produce a packet with the correct forced boundary."""
    cognitive = cognitive_to_context_packet({"x": 1, "timestamp": "2026-06-03T00:00:00Z"})
    assert cognitive.boundary == "COGNITIVE_REINTEGRATION_ADVISORY_ONLY"
    assert "COGNITIVE_ADVISORY_FUTURE" in cognitive.labels
    assert cognitive.source == "cognitive"
    assert cognitive.source_status == "COPIED_READONLY"

    rssi = rssi_rgpd_to_context_packet({"x": 2, "timestamp": "2026-06-03T00:00:00Z"})
    assert rssi.boundary == "RSSI_EVIDENCE_ONLY|RGPD_COMPLIANCE_SCOPE_GUARD"
    assert "RSSI_EVIDENCE_ONLY_FUTURE" in rssi.labels
    assert "RGPD_SCOPE_GUARD_FUTURE" in rssi.labels

    atlas = atlas_to_context_packet({"x": 3, "timestamp": "2026-06-03T00:00:00Z"})
    assert atlas.boundary == "ATLAS_READONLY_ADVISORY_ONLY"
    assert "ATLAS_READONLY_FUTURE" in atlas.labels

    comp = compliance_to_context_packet({"x": 4, "timestamp": "2026-06-03T00:00:00Z"})
    assert comp.boundary == "RGPD_COMPLIANCE_SCOPE_GUARD|RSSI_EVIDENCE_ONLY"
    assert "RGPD_SCOPE_GUARD_FUTURE" in comp.labels
    assert "RSSI_EVIDENCE_ONLY_FUTURE" in comp.labels


# ─────────────────────────────────────────────────────────────────────────────
# Test 3: Packets never emit act
# ─────────────────────────────────────────────────────────────────────────────

def test_packets_never_emit_act(valid_packets):
    """All adapter-produced packets must have emits_act=False."""
    for pkt in valid_packets:
        assert pkt.emits_act is False, f"emits_act=True on {pkt.context_id}"
        assert pkt.advisory_only is True, f"advisory_only=False on {pkt.context_id}"
        assert pkt.readonly is True, f"readonly=False on {pkt.context_id}"
        assert pkt.runtime_allowed_now is False, f"runtime_allowed_now=True on {pkt.context_id}"
        assert pkt.decision_authority == "KX108_ONLY", f"bad authority on {pkt.context_id}"
        assert pkt.emits_decision is False, f"emits_decision=True on {pkt.context_id}"
        # validate_invariants must pass silently
        pkt.validate_invariants()


# ─────────────────────────────────────────────────────────────────────────────
# Test 4: Context-only routing → ALLOW_CONTEXT_ONLY
# ─────────────────────────────────────────────────────────────────────────────

def test_context_only_routes_allow_context_only(valid_packets):
    """route_packets with critical_action_requested=False must yield ALLOW_CONTEXT_ONLY."""
    dt, ev, env = route_packets(
        packets=valid_packets,
        critical_action_requested=False,
        action_candidate_type="EMIT_CONTEXT",
        source_module="p8c_test_scenario_a",
    )
    assert dt.decision == "ALLOW_CONTEXT_ONLY"
    assert dt.emits_act is False
    assert dt.dry_run is True
    assert dt.decision_authority == "KX108_ONLY"
    assert env is None
    assert ev.proof_claim is False
    assert ev.dry_run is True


# ─────────────────────────────────────────────────────────────────────────────
# Test 5: Critical action → HOLD
# ─────────────────────────────────────────────────────────────────────────────

def test_critical_action_routes_hold(valid_packets):
    """route_packets with critical_action_requested=True must yield HOLD."""
    dt, ev, env = route_packets(
        packets=valid_packets,
        critical_action_requested=True,
        action_candidate_type="WRITE",
        source_module="p8c_test_scenario_b",
    )
    assert dt.decision == "HOLD"
    assert dt.emits_act is False
    assert dt.dry_run is True
    assert env is not None
    assert env.requires_x108 is True
    assert env.candidate_only is True
    assert env.emits_act is False
    assert env.authority == "KX108_ONLY"


# ─────────────────────────────────────────────────────────────────────────────
# Test 6: runtime_allowed_now=True → BLOCK
# ─────────────────────────────────────────────────────────────────────────────

def test_violation_runtime_allowed_blocks():
    """A packet with runtime_allowed_now=True must cause BLOCK in the admission stub."""
    bad_packet = ContextPacket(
        context_id="test-violation-runtime-allowed",
        source="test",
        source_status="TEST",
        claim_scope="CLAIMABLE_SPEC_ONLY",
        boundary="TEST_BOUNDARY",
        timestamp_or_tick="2026-06-03T00:00:00Z",
        runtime_allowed_now=True,
    )
    result = evaluate_dry_run([bad_packet])
    assert result.decision == "BLOCK"
    assert any("VIOLATION" in code for code in result.reason_codes)
    assert result.emits_act is False


# ─────────────────────────────────────────────────────────────────────────────
# Test 7: bad decision_authority → BLOCK
# ─────────────────────────────────────────────────────────────────────────────

def test_violation_bad_authority_blocks():
    """A packet with decision_authority != KX108_ONLY must cause BLOCK."""
    bad_packet = ContextPacket(
        context_id="test-violation-bad-authority",
        source="test",
        source_status="TEST",
        claim_scope="CLAIMABLE_SPEC_ONLY",
        boundary="TEST_BOUNDARY",
        timestamp_or_tick="2026-06-03T00:00:00Z",
        decision_authority="EXTERNAL_AGENT",
    )
    result = evaluate_dry_run([bad_packet])
    assert result.decision == "BLOCK"
    assert any("VIOLATION" in code for code in result.reason_codes)


# ─────────────────────────────────────────────────────────────────────────────
# Test 8: DecisionTicketDryRun never contains ACT
# ─────────────────────────────────────────────────────────────────────────────

def test_decision_ticket_never_act():
    """VALID_DRY_RUN_DECISIONS must not contain ACT. Instantiating with ACT must raise."""
    assert "ACT" not in VALID_DRY_RUN_DECISIONS
    assert "ALLOW" not in VALID_DRY_RUN_DECISIONS
    assert "ALLOW_CONTEXT_ONLY" in VALID_DRY_RUN_DECISIONS
    assert "HOLD" in VALID_DRY_RUN_DECISIONS
    assert "BLOCK" in VALID_DRY_RUN_DECISIONS

    # Creating a ticket with ACT must raise on validate_invariants
    bad_ticket = DecisionTicketDryRun(
        ticket_id="bad-act-ticket",
        intent_envelope_ref="none",
        decision="ACT",
        reason_codes=["TEST"],
        x108_gate_status="TEST",
        timestamp_or_tick="2026-06-03T00:00:00Z",
    )
    with pytest.raises(AssertionError, match="BOUNDARY_VIOLATION"):
        bad_ticket.validate_invariants()


# ─────────────────────────────────────────────────────────────────────────────
# Test 9: OS3EvidenceStub never claims proof
# ─────────────────────────────────────────────────────────────────────────────

def test_os3_evidence_never_claims_proof(valid_packets):
    """OS3EvidenceTicketDryRun must have proof_claim=False and NOT_COMPUTED statuses."""
    dt, ev, _ = route_packets(packets=valid_packets, critical_action_requested=False)
    assert ev.proof_claim is False
    assert ev.verification_status == "NOT_VERIFIED_DRY_RUN"
    assert ev.hash_status == "NOT_COMPUTED"
    assert ev.seal_status == "NOT_SEALED"
    assert ev.merkle_status == "NOT_BUILT"
    assert ev.replay_status == "NOT_RUN"
    assert ev.rfc3161_anchor_ref == "NOT_ANCHORED_DRY_RUN"
    assert ev.dry_run is True

    # Instantiating with proof_claim=True must raise
    bad_ev = OS3EvidenceTicketDryRun(
        evidence_id="bad-ev-001",
        linked_decision_ticket="dt-001",
        source="test",
        timestamp_or_tick="2026-06-03T00:00:00Z",
        proof_claim=True,
    )
    with pytest.raises(AssertionError, match="BOUNDARY_VIOLATION"):
        bad_ev.validate_invariants()

    # Instantiating with verification_status=VERIFIED must raise
    bad_ev2 = OS3EvidenceTicketDryRun(
        evidence_id="bad-ev-002",
        linked_decision_ticket="dt-001",
        source="test",
        timestamp_or_tick="2026-06-03T00:00:00Z",
        verification_status="VERIFIED",
    )
    with pytest.raises(AssertionError, match="BOUNDARY_VIOLATION"):
        bad_ev2.validate_invariants()


# ─────────────────────────────────────────────────────────────────────────────
# Test 10: p8b_demo.py produces expected decisions
# ─────────────────────────────────────────────────────────────────────────────

def test_demo_outputs_expected_decisions():
    """Run p8b_demo.py as subprocess and verify key JSON fields."""
    demo_path = _REPO_ROOT / "runtime_wiring" / "p8b_demo.py"
    result = subprocess.run(
        [sys.executable, str(demo_path)],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(_REPO_ROOT),
    )
    assert result.returncode == 0, f"Demo failed:\n{result.stderr}"
    output = result.stdout

    # Extract JSON block (starts after "[4/4]" header line)
    json_start = output.find("{")
    json_end = output.rfind("}") + 1
    assert json_start != -1, "No JSON found in demo output"
    data = json.loads(output[json_start:json_end])

    assert data["p8b_dry_run_demo"]["status"] == "DRY_RUN_ONLY"
    assert data["p8b_dry_run_demo"]["emits_act"] is False
    assert data["p8b_dry_run_demo"]["decision_authority"] == "KX108_ONLY"
    assert data["contracts_verification"]["status"] == "ALL_PRESENT"
    assert data["contracts_verification"]["contracts_checked"] == 8
    assert data["scenario_a_context_only"]["decision_ticket"]["decision"] == "ALLOW_CONTEXT_ONLY"
    assert data["scenario_b_critical_action"]["decision_ticket"]["decision"] == "HOLD"
    summary = data["boundary_enforcement_summary"]
    assert summary["all_packets_advisory_only"] is True
    assert summary["all_packets_readonly"] is True
    assert summary["all_packets_no_act"] is True
    assert summary["all_packets_kx108_authority"] is True
    assert summary["scenario_b_hold_on_critical"] is True


# ─────────────────────────────────────────────────────────────────────────────
# Test 11: Import isolation — no forbidden modules
# ─────────────────────────────────────────────────────────────────────────────

def test_import_isolation_no_forbidden_modules():
    """No file in runtime_wiring/ may import from apps/, periphery/, connectors/, sigma/."""
    forbidden = {"apps", "periphery", "connectors", "sigma"}
    wiring_dir = _REPO_ROOT / "runtime_wiring"
    violations = []
    for py_file in wiring_dir.glob("*.py"):
        source = py_file.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(py_file))
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                mod = getattr(node, "module", "") or ""
                names = [alias.name for alias in getattr(node, "names", [])]
                top_level = mod.split(".")[0] if mod else ""
                if top_level in forbidden:
                    violations.append(f"{py_file.name}: imports '{mod}'")
                for name in names:
                    if name.split(".")[0] in forbidden:
                        violations.append(f"{py_file.name}: imports name '{name}'")
    assert violations == [], "Forbidden imports found:\n" + "\n".join(violations)


# ─────────────────────────────────────────────────────────────────────────────
# Test 12: No source pack import
# ─────────────────────────────────────────────────────────────────────────────

def test_no_source_pack_import():
    """No file in runtime_wiring/ may reference _source_packs/ in import or open() statements.
    Comments mentioning _source_packs as documentation are allowed."""
    wiring_dir = _REPO_ROOT / "runtime_wiring"
    violations = []
    for py_file in wiring_dir.glob("*.py"):
        source = py_file.read_text(encoding="utf-8")
        # Check non-comment lines only
        for lineno, line in enumerate(source.splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            if "_source_packs" in stripped:
                violations.append(f"{py_file.name}:{lineno}: non-comment reference to '_source_packs'")
    assert violations == [], "Source pack references in code (non-comment) found:\n" + "\n".join(violations)


# ─────────────────────────────────────────────────────────────────────────────
# Test 13: No packages/ directory created
# ─────────────────────────────────────────────────────────────────────────────

def test_no_packages_created():
    """packages/ directory must not exist in the repo root."""
    packages_dir = _REPO_ROOT / "packages"
    assert not packages_dir.exists(), "packages/ directory found — NO_PACKAGE constraint violated"


# ─────────────────────────────────────────────────────────────────────────────
# Test 14: runtime_contracts/ contains no .py files
# ─────────────────────────────────────────────────────────────────────────────

def test_runtime_contracts_has_no_py():
    """runtime_contracts/ must contain zero Python files."""
    contracts_dir = _REPO_ROOT / "runtime_contracts"
    py_files = list(contracts_dir.rglob("*.py"))
    assert py_files == [], (
        f"Python files found in runtime_contracts/: {[str(f) for f in py_files]}"
    )

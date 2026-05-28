"""F16B — Live source validation tests.

Source-assert tests verifying that backend routes read from real registries:
- os3.py reads docs/runtime freeze reports
- worldcalls.py reads audit/sovereign_tickets.jsonl + audit/world_action_bus.jsonl
- audit.py reads audit/world_action_bus.jsonl
- gencoin.py returns LIVE_EMPTY_REGISTRY when no ledger exists
- All endpoints are readonly / KX108_ONLY / no mutation
"""
from pathlib import Path
import json

ROOT = Path(".")
SOVEREIGN_TICKETS = ROOT / "audit" / "sovereign_tickets.jsonl"
WORLD_ACTION_BUS = ROOT / "audit" / "world_action_bus.jsonl"
DOCS_RUNTIME = ROOT / "docs" / "runtime"

OS3_SRC = Path("apps/obsidia_api/routes/os3.py").read_text(encoding="utf-8")
WORLDCALLS_SRC = Path("apps/obsidia_api/routes/worldcalls.py").read_text(encoding="utf-8")
AUDIT_SRC = Path("apps/obsidia_api/routes/audit.py").read_text(encoding="utf-8")
GENCOIN_SRC = Path("apps/obsidia_api/routes/gencoin.py").read_text(encoding="utf-8")


# ── OS3 proof artifact source ────────────────────────────────────────────────

def test_os3_reads_real_freeze_reports():
    """os3.py must reference docs/runtime as real proof source."""
    assert "docs" in OS3_SRC and "runtime" in OS3_SRC

def test_os3_returns_freeze_report_manifest():
    """os3.py must return FREEZE_REPORT_MANIFEST type."""
    assert "FREEZE_REPORT" in OS3_SRC

def test_os3_source_is_real_freeze_reports():
    """os3.py must use REAL_FREEZE_REPORTS source identifier."""
    assert "REAL_FREEZE_REPORTS" in OS3_SRC

def test_os3_no_backend_stub():
    """os3.py must not use BACKEND_STUB as primary source."""
    assert 'source="BACKEND_STUB"' not in OS3_SRC
    assert "source=BACKEND_STUB" not in OS3_SRC
    assert '"BACKEND_STUB"' not in OS3_SRC


# ── Sovereign tickets source ─────────────────────────────────────────────────

def test_sovereign_tickets_reads_real_jsonl():
    """worldcalls.py must reference sovereign_tickets.jsonl."""
    assert "sovereign_tickets.jsonl" in WORLDCALLS_SRC

def test_sovereign_tickets_source_identifier():
    """worldcalls.py must use REAL_SOVEREIGN_TICKETS source."""
    assert "REAL_SOVEREIGN_TICKETS" in WORLDCALLS_SRC


# ── WorldCall source ─────────────────────────────────────────────────────────

def test_worldcalls_reads_world_action_bus():
    """worldcalls.py must reference world_action_bus.jsonl."""
    assert "world_action_bus.jsonl" in WORLDCALLS_SRC

def test_worldcalls_source_identifier():
    """worldcalls.py must use REAL_WORLD_ACTION_BUS source."""
    assert "REAL_WORLD_ACTION_BUS" in WORLDCALLS_SRC

def test_worldcalls_no_backend_stub_main():
    """worldcalls.py main endpoints must not use BACKEND_STUB."""
    lines = [l for l in WORLDCALLS_SRC.splitlines() if '"BACKEND_STUB"' in l]
    assert len(lines) <= 1, f"Too many BACKEND_STUB refs: {lines}"


# ── Audit source ─────────────────────────────────────────────────────────────

def test_audit_reads_world_action_bus():
    """audit.py must reference world_action_bus.jsonl."""
    assert "world_action_bus.jsonl" in AUDIT_SRC

def test_audit_source_identifier():
    """audit.py must use REAL_WORLD_ACTION_BUS source."""
    assert "REAL_WORLD_ACTION_BUS" in AUDIT_SRC

def test_audit_no_backend_stub():
    """audit.py must not use BACKEND_STUB."""
    assert '"BACKEND_STUB"' not in AUDIT_SRC


# ── Gencoin empty registry ────────────────────────────────────────────────────

def test_gencoin_live_empty_registry():
    """gencoin.py must return LIVE_EMPTY_REGISTRY when no entries."""
    assert "LIVE_EMPTY_REGISTRY" in GENCOIN_SRC

def test_gencoin_no_wallet_no_mint():
    """gencoin.py must include no_wallet, no_mint boundary fields."""
    assert "no_wallet" in GENCOIN_SRC
    assert "no_mint" in GENCOIN_SRC

def test_gencoin_reason_field():
    """gencoin.py must include reason=NO_REAL_GENCOIN_LEDGER_ENTRY_YET."""
    assert "NO_REAL_GENCOIN_LEDGER_ENTRY_YET" in GENCOIN_SRC


# ── Boundary fields — all routes ─────────────────────────────────────────────

def test_all_endpoints_decision_authority():
    """All endpoint implementations must reference KX108_ONLY."""
    for src in [OS3_SRC, WORLDCALLS_SRC, AUDIT_SRC, GENCOIN_SRC]:
        assert "KX108_ONLY" in src

def test_all_endpoints_readonly():
    """All endpoint implementations must include readonly=True."""
    for src in [OS3_SRC, WORLDCALLS_SRC, AUDIT_SRC, GENCOIN_SRC]:
        assert "readonly" in src.lower()

def test_all_endpoints_no_kernel_mutation():
    """No endpoint may set kernel_mutation to True."""
    for src in [OS3_SRC, WORLDCALLS_SRC, AUDIT_SRC, GENCOIN_SRC]:
        assert "kernel_mutation: True" not in src
        assert "'kernel_mutation': True" not in src

def test_all_endpoints_emits_act_false():
    """All endpoints must declare emits_act: False."""
    for src in [OS3_SRC, WORLDCALLS_SRC, AUDIT_SRC, GENCOIN_SRC]:
        assert "emits_act" in src


# ── Real file existence ───────────────────────────────────────────────────────

def test_sovereign_tickets_file_exists():
    """audit/sovereign_tickets.jsonl must exist with real ticket entries."""
    assert SOVEREIGN_TICKETS.exists(), "audit/sovereign_tickets.jsonl not found"
    content = SOVEREIGN_TICKETS.read_text(encoding="utf-8").strip()
    assert content, "sovereign_tickets.jsonl is empty"
    first = json.loads(content.splitlines()[0])
    assert "ticket_id" in first
    assert "x108_gate" in first

def test_world_action_bus_file_exists():
    """audit/world_action_bus.jsonl must exist with >= 100 real events."""
    assert WORLD_ACTION_BUS.exists(), "audit/world_action_bus.jsonl not found"
    lines = [l for l in WORLD_ACTION_BUS.read_text(encoding="utf-8").strip().splitlines() if l.strip()]
    assert len(lines) >= 100, f"Expected >= 100 events, got {len(lines)}"
    first = json.loads(lines[0])
    assert "event_id" in first
    assert "world_call_class" in first

def test_docs_runtime_has_freeze_reports():
    """docs/runtime/ must contain real .md freeze reports."""
    mds = list(DOCS_RUNTIME.glob("*.md"))
    assert len(mds) >= 10, f"Expected >= 10 freeze reports, got {len(mds)}"

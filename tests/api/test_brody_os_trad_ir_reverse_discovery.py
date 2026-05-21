"""
OS Trad / IR / Reverse discovery tests.
Verifies source files exist and are correctly classified in the discovery report.
"""
import pytest
from pathlib import Path

_ENGINE_ROOT = Path(__file__).resolve().parents[3]


# ── OS Trad source files ───────────────────────────────────────────────────────

def test_os_trad_adapter_exists():
    p = _ENGINE_ROOT / "engine" / "core_full" / "modules" / "os_trad" / "adapter.py"
    assert p.exists(), f"OS Trad adapter not found: {p}"


def test_os_trad_os1_exists():
    p = _ENGINE_ROOT / "engine" / "core_full" / "modules" / "os_trad" / "vendor" / "obsidia_os1" / "os1.py"
    assert p.exists(), f"OS1 module not found: {p}"


def test_reverse_os_adapter_exists():
    p = _ENGINE_ROOT / "obsidia-engine-candidate" / "bridge" / "zip2_reverse_os_real_adapter.py"
    assert p.exists(), f"Reverse OS adapter not found: {p}"


# ── OS Trad is a code-gen tool (not a response pipeline) ─────────────────────

def test_os_trad_adapter_is_propose_module():
    p = _ENGINE_ROOT / "engine" / "core_full" / "modules" / "os_trad" / "adapter.py"
    content = p.read_text(encoding="utf-8")
    assert "PROPOSE" in content, "OS Trad must be a PROPOSE-type module"
    assert "OS_TRAD" in content


def test_os_trad_adapter_not_in_api_imports():
    """OS Trad module must NOT be imported in the brody API route (not bridged without approval)."""
    api_route = Path(__file__).resolve().parents[2] / "apps" / "obsidia_api" / "routes" / "brody.py"
    content = api_route.read_text(encoding="utf-8")
    # Check for actual import statements, not field names like "os_trad_status"
    import re
    os_trad_imports = re.findall(r"^(?:import|from)\s+.*os.trad", content, re.MULTILINE | re.IGNORECASE)
    assert not os_trad_imports, f"OS Trad must not be directly imported in API route: {os_trad_imports}"


# ── Reverse OS uses tree vectors ───────────────────────────────────────────────

def test_reverse_os_uses_tree_vector():
    p = _ENGINE_ROOT / "obsidia-engine-candidate" / "bridge" / "zip2_reverse_os_real_adapter.py"
    content = p.read_text(encoding="utf-8")
    assert "tree_vector" in content


# ── Discovery report ─────────────────────────────────────────────────────────

def test_os_trad_discovery_report_exists():
    p = Path(__file__).resolve().parents[2] / "docs" / "freeze" / "BRODY_OS_TRAD_IR_REVERSE_DISCOVERY_REPORT.md"
    assert p.exists()


def test_os_trad_discovery_report_has_status():
    p = Path(__file__).resolve().parents[2] / "docs" / "freeze" / "BRODY_OS_TRAD_IR_REVERSE_DISCOVERY_REPORT.md"
    content = p.read_text(encoding="utf-8")
    assert "BRODY_OS_TRAD_IR_REVERSE_DISCOVERY_PASS" in content


def test_os_trad_not_bridgeable_documented():
    p = Path(__file__).resolve().parents[2] / "docs" / "freeze" / "BRODY_OS_TRAD_IR_REVERSE_DISCOVERY_REPORT.md"
    content = p.read_text(encoding="utf-8")
    assert "NOT_BRIDGEABLE" in content


# ── API translation_trace placeholders ───────────────────────────────────────

def test_api_has_os_trad_status_placeholder():
    from fastapi.testclient import TestClient
    from apps.obsidia_api.main import app
    client = TestClient(app)
    resp = client.post("/api/brody/chat", json={"message": "test", "language": "fr"})
    assert resp.status_code == 200
    data = resp.json()
    tt = data.get("translation_trace", {})
    assert "os_trad_status" in tt
    assert tt["os_trad_status"] == "READONLY_PASS"


def test_api_alphabet_units_placeholder():
    from fastapi.testclient import TestClient
    from apps.obsidia_api.main import app
    client = TestClient(app)
    resp = client.post("/api/brody/chat", json={"message": "test", "language": "fr"})
    data = resp.json()
    tt = data.get("translation_trace", {})
    assert "alphabet_units" in tt
    assert isinstance(tt["alphabet_units"], list)

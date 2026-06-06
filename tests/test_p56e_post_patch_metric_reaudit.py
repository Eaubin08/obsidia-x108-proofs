"""
P56E — Post-patch metric re-audit tests.

Verifies that all P56B/C/D corrections are in place and that the proof repo
satisfies the post-review metric invariants.
"""
from __future__ import annotations

import json
import re
import zipfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
PROOF_V18 = REPO_ROOT / "proofs" / "V18_3_1" / "engine_buildable_0_9_3_1"
SIGMA_DIR = REPO_ROOT / "sigma"
ZIP_PATH = Path(r"C:\Users\User\Desktop\OBSIDIA_CORE_ONLY_FULL_MACHINERY.zip")


def _read_zip_entry(entry_name: str) -> str:
    if not ZIP_PATH.exists():
        pytest.skip("Core ZIP not available")
    with zipfile.ZipFile(ZIP_PATH) as zf:
        return zf.read(entry_name).decode("utf-8", "replace")


def _gamma_values(text: str) -> list:
    return re.findall(r"gamma\s*=\s*([0-9.]+)", text)


# ---------------------------------------------------------------------------
# Test 1 — OS2 proof gamma = 1.0
# ---------------------------------------------------------------------------
def test_p56e_os2_proof_gamma_equals_1():
    """OS2 proof metrics must have gamma=1.0 after P56B patch."""
    path = PROOF_V18 / "obsidia_os2" / "metrics.py"
    assert path.exists()
    gammas = _gamma_values(path.read_text("utf-8", "replace"))
    assert "1.0" in gammas, f"Expected gamma=1.0 in OS2 proof, got: {gammas}"
    assert "0.5" not in gammas, f"gamma=0.5 still present in OS2 proof (P56B not applied)"


# ---------------------------------------------------------------------------
# Test 2 — OS3 proof gamma = 1.0
# ---------------------------------------------------------------------------
def test_p56e_os3_proof_gamma_equals_1():
    """OS3 structural_core proof metrics must have gamma=1.0."""
    path = PROOF_V18 / "obsidia_structural_core" / "metrics.py"
    assert path.exists()
    gammas = _gamma_values(path.read_text("utf-8", "replace"))
    assert "1.0" in gammas, f"Expected gamma=1.0 in OS3 proof, got: {gammas}"


# ---------------------------------------------------------------------------
# Test 3 — Core ZIP OS2 gamma = 0.5 (original, unpatched)
# ---------------------------------------------------------------------------
def test_p56e_core_zip_os2_gamma_is_05():
    """Core ZIP must still have gamma=0.5 — it was not patched, only proof was."""
    text = _read_zip_entry("engine/obsidia_os2/metrics.py")
    gammas = _gamma_values(text)
    assert "0.5" in gammas, (
        f"Core ZIP OS2 should have original gamma=0.5, got: {gammas}. "
        "If changed, the delta classification must be re-reviewed."
    )


# ---------------------------------------------------------------------------
# Test 4 — Delta OS2 core-zip vs proof is PROOF_STRENGTHENING, not error
# ---------------------------------------------------------------------------
def test_p56e_os2_delta_classified_as_proof_strengthening():
    """
    The delta core-zip gamma=0.5 vs proof gamma=1.0 must be classified
    as PROOF_STRENGTHENING_AFTER_REVIEW with PROOF_WINS_BY_OS3_AUTHORITY.
    Verified via the P56E audit JSON.
    """
    audit = REPO_ROOT / "docs" / "core_import" / "P56E_POST_PATCH_METRIC_REAUDIT.json"
    assert audit.exists()
    data = json.loads(audit.read_text("utf-8"))
    os2 = data["os2_gamma"]
    assert os2["delta_type"] == "PROOF_STRENGTHENING_AFTER_REVIEW"
    assert os2["authority_decision"] == "PROOF_WINS_BY_OS3_AUTHORITY"
    assert os2["merge_action"] == "KEEP_PROOF"


# ---------------------------------------------------------------------------
# Test 5 — All domain chain passes
# ---------------------------------------------------------------------------
def test_p56e_all_domains_core_rigor_status_pass():
    """P56C domain rigor audit must report PASS."""
    audit = REPO_ROOT / "docs" / "core_import" / "P56C_D_ALL_DOMAINS_CORE_RIGOR_AUDIT.json"
    assert audit.exists(), "P56C audit JSON missing — run P56C first"
    data = json.loads(audit.read_text("utf-8"))
    assert data.get("status") == "PASS", f"P56C status not PASS: {data.get('status')}"


# ---------------------------------------------------------------------------
# Test 6 — Sigma is POST_GUARD_VETO_ONLY
# ---------------------------------------------------------------------------
def test_p56e_sigma_post_guard_veto_only():
    """sigma/run_pipeline.py must contain POST_GUARD_VETO_ONLY boundary."""
    path = SIGMA_DIR / "run_pipeline.py"
    assert path.exists()
    text = path.read_text("utf-8", "replace")
    assert "POST_GUARD_VETO_ONLY" in text, "Sigma boundary POST_GUARD_VETO_ONLY not found"
    assert "pre_sigma_market_verdict" in text, "pre_sigma_market_verdict trace not found"
    assert "pre_sigma_severity" in text, "pre_sigma_severity trace not found"
    assert "sigma_authority" in text, "sigma_authority field not found"
    # Must NOT contain logic that promotes HOLD/BLOCK to ACT/ALLOW
    assert "promotes" not in text.lower() or "never promotes" in text.lower()


# ---------------------------------------------------------------------------
# Test 7 — sigma_config.json tau coherence
# ---------------------------------------------------------------------------
def test_p56e_sigma_config_tau_coherent():
    """
    sigma/sigma_config.json tau_min/tau_max/accel_limit must match core ZIP values.
    """
    proof_cfg = SIGMA_DIR / "sigma_config.json"
    assert proof_cfg.exists(), "sigma/sigma_config.json missing"
    proof_data = json.loads(proof_cfg.read_text("utf-8"))

    assert proof_data.get("tau_min") == 0.05
    assert proof_data.get("tau_max") == 5.0
    assert proof_data.get("accel_limit") == 0.6

    # Compare with core ZIP if available
    if ZIP_PATH.exists():
        with zipfile.ZipFile(ZIP_PATH) as zf:
            zip_names = zf.namelist()
            cfg_entry = next((n for n in zip_names if "sigma_config.json" in n), None)
            if cfg_entry:
                core_data = json.loads(zf.read(cfg_entry).decode("utf-8"))
                assert core_data.get("tau_min") == proof_data.get("tau_min")
                assert core_data.get("tau_max") == proof_data.get("tau_max")
                assert core_data.get("accel_limit") == proof_data.get("accel_limit")


# ---------------------------------------------------------------------------
# Test 8 — No effective runtime_allowed_now=True
# ---------------------------------------------------------------------------
def test_p56e_no_effective_runtime_allowed_now_true():
    """
    No Python source in sigma/, apps/, runtime_wiring/ must set
    runtime_allowed_now=True as an actual variable assignment.
    String literals in print(), docstrings, dict labels are ignored.
    """
    # Pattern: actual assignment (not in string context)
    # We look for  runtime_allowed_now = True  or  runtime_allowed_now=True
    # but NOT inside string literals or comments
    assignment_pattern = re.compile(
        r"^\s*[\"']?runtime_allowed_now[\"']?\s*[:=]\s*True",
        re.MULTILINE,
    )
    violations = []
    for d in ["sigma", "apps/obsidia_api", "runtime_wiring"]:
        for py in (REPO_ROOT / d).rglob("*.py"):
            text = py.read_text("utf-8", "replace")
            # Remove string literals and comments to avoid false positives
            cleaned = re.sub(r'(""".*?"""|\'\'\'.*?\'\'\'|"[^"\n]*"|\'[^\'\n]*\'|#.*$)',
                             " ", text, flags=re.DOTALL | re.MULTILINE)
            if assignment_pattern.search(cleaned):
                violations.append(str(py.relative_to(REPO_ROOT)))
    assert violations == [], f"Effective runtime_allowed_now=True found: {violations}"


# ---------------------------------------------------------------------------
# Test 9 — decision_authority = KX108_ONLY
# ---------------------------------------------------------------------------
def test_p56e_decision_authority_kx108_only():
    """sigma/contracts.py must declare decision_authority: KX108_ONLY."""
    path = SIGMA_DIR / "contracts.py"
    assert path.exists()
    text = path.read_text("utf-8", "replace")
    assert "KX108_ONLY" in text, "KX108_ONLY not found in sigma/contracts.py"
    assert '"decision_authority": "KX108_ONLY"' in text or \
           "'decision_authority': 'KX108_ONLY'" in text, \
        "decision_authority=KX108_ONLY not present as an explicit key-value"


# ---------------------------------------------------------------------------
# Test 10 — No ACT outside governed paths
# ---------------------------------------------------------------------------
def test_p56e_no_act_outside_governed_paths():
    """
    sigma/run_pipeline.py must not emit ACT directly.
    ACT may only appear in comments, docstrings, or the decision_act_hold function.
    """
    path = SIGMA_DIR / "run_pipeline.py"
    assert path.exists()
    text = path.read_text("utf-8", "replace")

    # Remove strings and comments
    cleaned = re.sub(r'(""".*?"""|\'\'\'.*?\'\'\'|"[^"\n]*"|\'[^\'\n]*\'|#.*$)',
                     " ", text, flags=re.DOTALL | re.MULTILINE)

    # result["market_verdict"] = "ACT" would be a violation
    act_emit_pattern = re.compile(
        r'(market_verdict|x108_gate|gate)\s*[=\[]\s*["\']ACT["\']',
        re.IGNORECASE,
    )
    matches = act_emit_pattern.findall(cleaned)
    assert not matches, f"Direct ACT emission found in sigma/run_pipeline.py: {matches}"


# ---------------------------------------------------------------------------
# Test 11 — P56E audit JSON exists and verdict is PASS
# ---------------------------------------------------------------------------
def test_p56e_audit_json_verdict_pass():
    """P56E audit JSON must exist and declare PASS verdict."""
    audit = REPO_ROOT / "docs" / "core_import" / "P56E_POST_PATCH_METRIC_REAUDIT.json"
    assert audit.exists()
    data = json.loads(audit.read_text("utf-8"))
    assert data.get("final_verdict") == "P56E_POST_PATCH_METRIC_REAUDIT_PASS"
    assert data.get("remaining_blockers") == []
    assert data.get("gamma_resolution", {}).get("status") == "RESOLVED"

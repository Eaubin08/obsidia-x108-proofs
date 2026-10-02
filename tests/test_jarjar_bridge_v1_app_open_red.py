"""
tests/test_jarjar_bridge_v1_app_open_red.py
RED SUITE – G1-B governed app.open
Each test is currently RED (failing). They all become GREEN after G1-B implementation.
"""
from __future__ import annotations
import sys
from pathlib import Path
from unittest.mock import MagicMock

WORKTREE = Path(__file__).resolve().parents[1]
SCRIPTS = WORKTREE / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import obsidia_pc_capabilities_v2 as PC2


# ── R1 : PC_V2_APP_OPEN_PREPARE doit être enregistrée ──────────────────────
def test_red_app_open_prepare_is_registered():
    """RED: PREPARE doit être dans le dispatcher, pas UNKNOWN_CAPABILITY_V2."""
    r = PC2.execute_pc_capability_v2(
        "PC_V2_APP_OPEN_PREPARE", app="notepad", stores_base_dir="/tmp/s"
    )
    assert r["status"] != "UNKNOWN_CAPABILITY_V2", (
        "PC_V2_APP_OPEN_PREPARE n'est pas enregistrée (G1-B non implémenté)"
    )


# ── R2 : PC_V2_APP_OPEN_EXECUTE doit être enregistrée ──────────────────────
def test_red_app_open_execute_is_registered():
    """RED: EXECUTE doit être dans le dispatcher, pas UNKNOWN_CAPABILITY_V2."""
    fake_prep = {"j5_phase": "PREPARE", "status": PC2.PREPARED_AWAITING_HUMAN_APPROVAL,
                 "execution_authority_hash": "a" * 64}
    r = PC2.execute_pc_capability_v2(
        "PC_V2_APP_OPEN_EXECUTE",
        prepared_result=fake_prep,
        human_authorized_eah="a" * 64,
        human_authorization_reference="REF",
        stores_base_dir="/tmp/s",
    )
    assert r["status"] != "UNKNOWN_CAPABILITY_V2", (
        "PC_V2_APP_OPEN_EXECUTE n'est pas enregistrée (G1-B non implémenté)"
    )


# ── R3 : PREPARE sans executor → rejeté ────────────────────────────────────
def test_red_prepare_without_executor_rejected():
    """RED: PREPARE sans executor retourne PREPARE_REJECTED."""
    r = PC2.execute_pc_capability_v2(
        "PC_V2_APP_OPEN_PREPARE",
        app="notepad",
        stores_base_dir="/tmp/s",
    )
    assert r["status"] == PC2.PREPARE_REJECTED
    assert "EXECUTOR_REQUIRED" in r.get("reason", "")


# ── R4 : PREPARE app non résolue → APP_NOT_IN_INVENTORY ────────────────────
def test_red_prepare_unresolved_app_fails_closed():
    """RED: si inventory.resolve() retourne None, PREPARE doit échouer avec APP_NOT_IN_INVENTORY."""
    ex = MagicMock()
    ex.EXECUTOR_PROVIDER = "JARJAR"
    ex.EXECUTOR_BACKEND = "NativeWindowsBackend"
    ex.resolve_app.return_value = {"ok": False, "error": "APP_NOT_IN_INVENTORY"}
    r = PC2.execute_pc_capability_v2(
        "PC_V2_APP_OPEN_PREPARE",
        app="totally_unknown_app_xyz",
        stores_base_dir="/tmp/s",
        executor=ex,
    )
    assert r["status"] == PC2.PREPARE_REJECTED
    assert "APP_NOT_IN_INVENTORY" in r.get("reason", "")


# ── R5 : PREPARE app vide → rejeté ─────────────────────────────────────────
def test_red_prepare_empty_app_rejected():
    """RED: app vide doit retourner PREPARE_REJECTED."""
    ex = MagicMock()
    ex.EXECUTOR_PROVIDER = "JARJAR"
    ex.EXECUTOR_BACKEND = "NativeWindowsBackend"
    r = PC2.execute_pc_capability_v2(
        "PC_V2_APP_OPEN_PREPARE",
        app="   ",
        stores_base_dir="/tmp/s",
        executor=ex,
    )
    assert r["status"] == PC2.PREPARE_REJECTED


# ── R6 : PREPARE résolu → produit PSA independant de l'EAH ─────────────────
def test_red_prepare_physical_anchor_independent_from_eah(tmp_path):
    """RED: physical_state_anchor doit être différent de execution_authority_hash."""
    ex = MagicMock()
    ex.EXECUTOR_PROVIDER = "JARJAR"
    ex.EXECUTOR_BACKEND = "NativeWindowsBackend"
    ex.resolve_app.return_value = {
        "ok": True, "name": "notepad", "target": "notepad.exe", "source": "builtin"
    }
    r = PC2.execute_pc_capability_v2(
        "PC_V2_APP_OPEN_PREPARE",
        app="notepad",
        stores_base_dir=str(tmp_path),
        executor=ex,
    )
    assert r["status"] == PC2.PREPARED_AWAITING_HUMAN_APPROVAL
    psa = r.get("physical_state_anchor", "")
    eah = r.get("execution_authority_hash", "")
    assert psa and len(psa) == 64
    assert psa != eah, "PSA ne doit pas être identique à l'EAH"


# ── R7 : PREPARE résolu → state_anchor_kind est PHYSICAL_PRE_STATE ─────────
def test_red_prepare_state_anchor_kind_is_physical(tmp_path):
    """RED: state_anchor_kind doit être PHYSICAL_PRE_STATE."""
    ex = MagicMock()
    ex.EXECUTOR_PROVIDER = "JARJAR"
    ex.EXECUTOR_BACKEND = "NativeWindowsBackend"
    ex.resolve_app.return_value = {
        "ok": True, "name": "notepad", "target": "notepad.exe", "source": "builtin"
    }
    r = PC2.execute_pc_capability_v2(
        "PC_V2_APP_OPEN_PREPARE",
        app="notepad",
        stores_base_dir=str(tmp_path),
        executor=ex,
    )
    assert r.get("state_anchor_kind") == "PHYSICAL_PRE_STATE"


# ── R8 : Bridge executor a resolve_app ─────────────────────────────────────
def test_red_bridge_has_resolve_app():
    """RED: JarJarWindowsExecutor doit avoir la méthode resolve_app."""
    from jarjar_executor_bridge_v0 import JarJarWindowsExecutor
    ex = object.__new__(JarJarWindowsExecutor)
    assert hasattr(ex, "resolve_app"), "JarJarWindowsExecutor manque resolve_app (G1-B)"


# ── R9 : Bridge executor a open_app_by_target ──────────────────────────────
def test_red_bridge_has_open_app_by_target():
    """RED: JarJarWindowsExecutor doit avoir la méthode open_app_by_target."""
    from jarjar_executor_bridge_v0 import JarJarWindowsExecutor
    ex = object.__new__(JarJarWindowsExecutor)
    assert hasattr(ex, "open_app_by_target"), "JarJarWindowsExecutor manque open_app_by_target (G1-B)"


# ── R10 : APP_OPEN enregistré dans le graphe ───────────────────────────────
def test_red_app_open_in_capability_graph():
    """RED: PC_V2_APP_OPEN_PREPARE + EXECUTE doivent être dans le graphe."""
    import obsidia_capability_graph_v0 as CG
    ids = CG.capability_ids()
    assert "PC_V2_APP_OPEN_PREPARE" in ids, "PC_V2_APP_OPEN_PREPARE absent du graphe"
    assert "PC_V2_APP_OPEN_EXECUTE" in ids, "PC_V2_APP_OPEN_EXECUTE absent du graphe"

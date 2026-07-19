"""test_obsidia_kernel_boundary_check — Build Gates V0.

Scope : APPLY_OBSIDIA_BUILD_GATES_V0_MINIMAL
Aucune dependance au repo reel dirty : _staged_files()/_dirty_files()
sont monkeypatchees. Aucune ecriture hors tmp_path.
"""

from __future__ import annotations

import py_compile
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_GATES_DIR = _REPO_ROOT / "scripts" / "gates"
sys.path.insert(0, str(_GATES_DIR))

import obsidia_kernel_boundary_check as gate  # noqa: E402


def test_py_compile() -> None:
    py_compile.compile(str(_GATES_DIR / "obsidia_kernel_boundary_check.py"), doraise=True)


def test_clean_tree_passes(monkeypatch, capsys) -> None:
    monkeypatch.setattr(gate, "_staged_files", lambda: [])
    monkeypatch.setattr(gate, "_dirty_files", lambda: ["docs/notes.md"])
    assert gate.main([]) == 0
    assert "KERNEL_BOUNDARY_PASS" in capsys.readouterr().out


def test_protected_staged_fails(monkeypatch, capsys) -> None:
    monkeypatch.setattr(gate, "_staged_files", lambda: ["sigma/contracts.py"])
    monkeypatch.setattr(gate, "_dirty_files", lambda: [])
    rc = gate.main([])
    assert rc == 1
    out = capsys.readouterr().out
    assert "KERNEL_BOUNDARY_FAIL" in out
    assert "PROTECTED_STAGED: sigma/contracts.py" in out


def test_protected_dirty_fails(monkeypatch, capsys) -> None:
    monkeypatch.setattr(gate, "_staged_files", lambda: [])
    monkeypatch.setattr(gate, "_dirty_files", lambda: ["merkle_seal.json"])
    rc = gate.main([])
    assert rc == 1
    assert "PROTECTED_DIRTY: merkle_seal.json" in capsys.readouterr().out


def test_staged_only_ignores_dirty(monkeypatch, capsys) -> None:
    # merkle dirty au working tree, mais staging propre -> PASS en --staged-only
    monkeypatch.setattr(gate, "_staged_files", lambda: ["docs/ok.md"])
    monkeypatch.setattr(gate, "_dirty_files",
                        lambda: (_ for _ in ()).throw(AssertionError("ne doit pas etre lu")))
    assert gate.main(["--staged-only"]) == 0
    assert "KERNEL_BOUNDARY_PASS" in capsys.readouterr().out


def test_generated_peripheral_and_tla_detected(monkeypatch, capsys) -> None:
    monkeypatch.setattr(gate, "_staged_files", lambda: [
        "proofs/lean/Obsidia/GeneratedPeripheral/P_New.lean",
        "formal/tla/X108.tla",
    ])
    monkeypatch.setattr(gate, "_dirty_files", lambda: [])
    rc = gate.main([])
    out = capsys.readouterr().out
    assert rc == 1
    assert "GeneratedPeripheral" in out and "formal/tla" in out


def test_all_protected_patterns_detected() -> None:
    for pat in gate.PROTECTED_PATTERNS:
        probe = pat + "x" if pat.endswith("/") else pat
        assert gate._is_protected(probe), f"pattern non detecte: {pat}"


def test_unprotected_paths_pass_through() -> None:
    for path in ("docs/protocols/OBSIDURE_APPLY_PROTOCOL.md",
                 "scripts/obsidia_cli.py", "tests/gates/test_x.py"):
        assert not gate._is_protected(path), f"faux positif: {path}"


def test_no_mutation_of_gate_file(monkeypatch) -> None:
    target = _GATES_DIR / "obsidia_kernel_boundary_check.py"
    before = target.stat().st_mtime_ns
    monkeypatch.setattr(gate, "_staged_files", lambda: [])
    monkeypatch.setattr(gate, "_dirty_files", lambda: [])
    gate.main([])
    assert target.stat().st_mtime_ns == before

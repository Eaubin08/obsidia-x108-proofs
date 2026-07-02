"""test_obsidia_commit_scope_guard — Build Gates V0.

Scope : APPLY_OBSIDIA_BUILD_GATES_V0_MINIMAL
Aucune dependance au repo reel dirty : _staged_files() est monkeypatchee.
Aucune ecriture hors tmp_path.
"""

from __future__ import annotations

import py_compile
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_GATES_DIR = _REPO_ROOT / "scripts" / "gates"
sys.path.insert(0, str(_GATES_DIR))

import obsidia_commit_scope_guard as gate  # noqa: E402


def test_py_compile() -> None:
    py_compile.compile(str(_GATES_DIR / "obsidia_commit_scope_guard.py"), doraise=True)


def test_empty_allow_list_fails(monkeypatch, capsys) -> None:
    monkeypatch.setattr(gate, "_staged_files", lambda: [])
    assert gate.main([]) == 1
    assert "COMMIT_SCOPE_GUARD_FAIL" in capsys.readouterr().out


def test_exact_scope_passes(monkeypatch, capsys) -> None:
    monkeypatch.setattr(gate, "_staged_files", lambda: ["docs/a.md", "docs/b.md"])
    rc = gate.main(["--allow", "docs/a.md", "--allow", "docs/b.md"])
    assert rc == 0
    assert "COMMIT_SCOPE_GUARD_PASS" in capsys.readouterr().out


def test_out_of_scope_staged_fails(monkeypatch, capsys) -> None:
    monkeypatch.setattr(gate, "_staged_files",
                        lambda: ["docs/a.md", "tools/rogue.py"])
    rc = gate.main(["--allow", "docs/a.md"])
    assert rc == 1
    out = capsys.readouterr().out
    assert "COMMIT_SCOPE_GUARD_FAIL" in out
    assert "OUT_OF_SCOPE_STAGED: tools/rogue.py" in out


def test_protected_staged_without_allow_fails(monkeypatch, capsys) -> None:
    monkeypatch.setattr(gate, "_staged_files",
                        lambda: ["docs/a.md", "sigma/guard.py"])
    rc = gate.main(["--allow", "docs/a.md"])
    assert rc == 1
    assert "PROTECTED_STAGED: sigma/guard.py" in capsys.readouterr().out


def test_protected_with_explicit_allow_passes(monkeypatch) -> None:
    # allow explicite = scope humainement approuve : le gate laisse passer
    monkeypatch.setattr(gate, "_staged_files", lambda: ["merkle_seal.json"])
    assert gate.main(["--allow", "merkle_seal.json"]) == 0


def test_all_protected_patterns_detected() -> None:
    for pat in gate.PROTECTED_PATTERNS:
        probe = pat + "x.py" if pat.endswith("/") else pat
        assert gate._is_protected(probe), f"pattern non detecte: {pat}"


def test_no_mutation_of_gate_file(monkeypatch) -> None:
    target = _GATES_DIR / "obsidia_commit_scope_guard.py"
    before = target.stat().st_mtime_ns
    monkeypatch.setattr(gate, "_staged_files", lambda: ["docs/a.md"])
    gate.main(["--allow", "docs/a.md"])
    assert target.stat().st_mtime_ns == before


def test_stdout_no_file_content_leak(monkeypatch, capsys) -> None:
    # Le gate n'affiche que des chemins, jamais le contenu des fichiers.
    monkeypatch.setattr(gate, "_staged_files", lambda: ["sigma/guard.py"])
    gate.main(["--allow", "docs/a.md"])
    out = capsys.readouterr().out
    assert "GuardConfig" not in out and "import" not in out

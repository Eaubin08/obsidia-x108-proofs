"""test_obsidia_forbidden_write_check — Build Gates V0 (deferred B).

Scope : APPLY_DEFERRED_GATE_FORBIDDEN_WRITE_V0
Fixtures Python ecrites dans tmp_path uniquement.
Aucune dependance au repo dirty.
"""

from __future__ import annotations

import py_compile
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_GATES_DIR = _REPO_ROOT / "scripts" / "gates"
sys.path.insert(0, str(_GATES_DIR))

import obsidia_forbidden_write_check as gate  # noqa: E402


# ── Helpers ────────────────────────────────────────────────────────────────────

def _make_gate_dir(tmp_path: Path, code: str, filename: str = "fake_gate.py") -> Path:
    """Cree un repertoire de fixture avec un fichier Python et retourne le repertoire."""
    d = tmp_path / "gates"
    d.mkdir()
    (d / filename).write_text(code, encoding="utf-8")
    return d


def _clean_gate() -> str:
    """Code Python propre (lecture seule, aucune operation interdite)."""
    return (
        'import subprocess, sys\n'
        'out = subprocess.run(["git", "diff", "--name-only"],\n'
        '                     capture_output=True, text=True, check=False)\n'
        'print(out.stdout)\n'
        'sys.exit(0)\n'
    )


# ── Tests ──────────────────────────────────────────────────────────────────────

def test_py_compile() -> None:
    py_compile.compile(str(_GATES_DIR / "obsidia_forbidden_write_check.py"), doraise=True)


def test_clean_dir_passes(tmp_path, capsys) -> None:
    d = _make_gate_dir(tmp_path, _clean_gate())
    rc = gate.main(["--dir", str(d)])
    assert rc == 0
    assert "FORBIDDEN_WRITE_PASS" in capsys.readouterr().out


def test_nonexistent_dir_fails(tmp_path, capsys) -> None:
    rc = gate.main(["--dir", str(tmp_path / "does_not_exist")])
    assert rc == 1
    assert "FORBIDDEN_WRITE_FAIL" in capsys.readouterr().out


def test_write_text_detected(tmp_path, capsys) -> None:
    code = 'from pathlib import Path\nPath("out.txt").write_text("data")\n'
    d = _make_gate_dir(tmp_path, code)
    rc = gate.main(["--dir", str(d)])
    assert rc == 1
    out = capsys.readouterr().out
    assert "FORBIDDEN_WRITE_FAIL" in out
    assert "write_text" in out


def test_write_bytes_detected(tmp_path, capsys) -> None:
    code = 'from pathlib import Path\nPath("out.bin").write_bytes(b"data")\n'
    d = _make_gate_dir(tmp_path, code)
    rc = gate.main(["--dir", str(d)])
    assert rc == 1
    assert "write_bytes" in capsys.readouterr().out


def test_open_write_mode_detected(tmp_path, capsys) -> None:
    code = 'with open("out.txt", "w") as f:\n    f.write("x")\n'
    d = _make_gate_dir(tmp_path, code)
    rc = gate.main(["--dir", str(d)])
    assert rc == 1
    assert "open_write_mode" in capsys.readouterr().out


def test_open_append_mode_detected(tmp_path, capsys) -> None:
    code = 'f = open("log.txt", "a")\nf.close()\n'
    d = _make_gate_dir(tmp_path, code)
    rc = gate.main(["--dir", str(d)])
    assert rc == 1
    assert "open_write_mode" in capsys.readouterr().out


def test_unlink_detected(tmp_path, capsys) -> None:
    code = 'from pathlib import Path\nPath("old.txt").unlink()\n'
    d = _make_gate_dir(tmp_path, code)
    rc = gate.main(["--dir", str(d)])
    assert rc == 1
    assert "unlink" in capsys.readouterr().out


def test_mkdir_detected(tmp_path, capsys) -> None:
    code = 'from pathlib import Path\nPath("newdir").mkdir(parents=True)\n'
    d = _make_gate_dir(tmp_path, code)
    rc = gate.main(["--dir", str(d)])
    assert rc == 1
    assert "mkdir" in capsys.readouterr().out


def test_shell_true_detected(tmp_path, capsys) -> None:
    code = 'import subprocess\nsubprocess.run("ls", shell=True)\n'
    d = _make_gate_dir(tmp_path, code)
    rc = gate.main(["--dir", str(d)])
    assert rc == 1
    assert "shell_true" in capsys.readouterr().out


def test_git_commit_detected(tmp_path, capsys) -> None:
    # Le pattern cible la forme string "git commit (appel via os.system / shell)
    code = 'import os\nos.system("git commit -m auto")\n'
    d = _make_gate_dir(tmp_path, code)
    rc = gate.main(["--dir", str(d)])
    assert rc == 1
    assert "git_commit" in capsys.readouterr().out


def test_git_push_detected(tmp_path, capsys) -> None:
    code = 'import os\nos.system("git push origin main")\n'
    d = _make_gate_dir(tmp_path, code)
    rc = gate.main(["--dir", str(d)])
    assert rc == 1
    assert "git_push" in capsys.readouterr().out


def test_git_add_detected(tmp_path, capsys) -> None:
    code = 'import os\nos.system("git add .")\n'
    d = _make_gate_dir(tmp_path, code)
    rc = gate.main(["--dir", str(d)])
    assert rc == 1
    assert "git_add" in capsys.readouterr().out


def test_output_shows_filename_and_label(tmp_path, capsys) -> None:
    code = 'from pathlib import Path\nPath("x").write_bytes(b"")\n'
    d = _make_gate_dir(tmp_path, code, filename="my_gate.py")
    gate.main(["--dir", str(d)])
    out = capsys.readouterr().out
    assert "my_gate.py" in out
    assert "write_bytes" in out


def test_multiple_violations_in_multiple_files(tmp_path, capsys) -> None:
    d = tmp_path / "gates"
    d.mkdir()
    (d / "gate_a.py").write_text('Path("x").write_text("y")\n', encoding="utf-8")
    (d / "gate_b.py").write_text('Path("z").unlink()\n', encoding="utf-8")
    rc = gate.main(["--dir", str(d)])
    assert rc == 1
    out = capsys.readouterr().out
    assert "gate_a.py" in out
    assert "gate_b.py" in out


def test_real_gates_dir_passes(capsys) -> None:
    """Les gates reelles du repo doivent etre propres."""
    real_dir = _GATES_DIR
    if not real_dir.exists():
        return  # skip gracieux si le repertoire est absent
    rc = gate.main(["--dir", str(real_dir)])
    assert rc == 0
    assert "FORBIDDEN_WRITE_PASS" in capsys.readouterr().out


def test_no_mutation_of_gate_file() -> None:
    target = _GATES_DIR / "obsidia_forbidden_write_check.py"
    before = target.stat().st_mtime_ns
    gate.main(["--dir", str(_GATES_DIR)])
    assert target.stat().st_mtime_ns == before

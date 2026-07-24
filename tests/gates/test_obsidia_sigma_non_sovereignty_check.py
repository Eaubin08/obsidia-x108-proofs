"""test_obsidia_sigma_non_sovereignty_check — Build Gates V0.

Scope : APPLY_OBSIDIA_BUILD_GATES_V0_MINIMAL
Fixtures ecrites uniquement dans tmp_path. Aucune dependance au repo
reel dirty (le gate est teste via --file sur des fixtures).
"""

from __future__ import annotations

import py_compile
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_GATES_DIR = _REPO_ROOT / "scripts" / "gates"
sys.path.insert(0, str(_GATES_DIR))

import obsidia_sigma_non_sovereignty_check as gate  # noqa: E402

COMPLIANT = '''
DECISION_AUTHORITY = "KX108_ONLY"

class SigmaAction(str, Enum):
    CONTINUE = "CONTINUE"
    REQUEST_PROOF = "REQUEST_PROOF"
    HOLD_RECOMMENDED = "HOLD_RECOMMENDED"

FORBIDDEN_ACTIONS: frozenset[str] = frozenset({
    "ACT",
    "ALLOW",
    "BLOCK",
    "WRITE_MEMORY",
    "MUTATE_KERNEL",
    "AUTO_APPLY",
})

class Report:
    emits_act: bool = False
    kernel_mutation: bool = False
'''


def _write(tmp_path: Path, text: str) -> Path:
    target = tmp_path / "fixture_sigma_guidance.py"
    target.write_text(text, encoding="utf-8")
    return target


def test_py_compile() -> None:
    py_compile.compile(str(_GATES_DIR / "obsidia_sigma_non_sovereignty_check.py"),
                       doraise=True)


def test_compliant_file_passes(tmp_path, capsys) -> None:
    target = _write(tmp_path, COMPLIANT)
    assert gate.main(["--file", str(target)]) == 0
    assert "SIGMA_NON_SOVEREIGNTY_PASS" in capsys.readouterr().out


def test_missing_kx108_fails(tmp_path, capsys) -> None:
    target = _write(tmp_path, COMPLIANT.replace('"KX108_ONLY"', '"SOMEONE_ELSE"'))
    assert gate.main(["--file", str(target)]) == 1
    assert "MISSING_MARKER" in capsys.readouterr().out


def test_sovereign_enum_member_fails(tmp_path, capsys) -> None:
    bad = COMPLIANT.replace('CONTINUE = "CONTINUE"', 'ACT = "ACT"\n    CONTINUE = "CONTINUE"')
    target = _write(tmp_path, bad)
    assert gate.main(["--file", str(target)]) == 1
    assert "SOVEREIGN_ENUM_MEMBER: SigmaAction.ACT" in capsys.readouterr().out


def test_allow_block_enum_members_fail(tmp_path) -> None:
    for member in ("ALLOW", "BLOCK"):
        bad = COMPLIANT.replace('CONTINUE = "CONTINUE"',
                                f'{member} = "{member}"\n    CONTINUE = "CONTINUE"')
        assert gate.main(["--file", str(_write(tmp_path, bad))]) == 1


def test_incomplete_forbidden_actions_fails(tmp_path, capsys) -> None:
    bad = COMPLIANT.replace('    "MUTATE_KERNEL",\n', "")
    target = _write(tmp_path, bad)
    assert gate.main(["--file", str(target)]) == 1
    assert "FORBIDDEN_ACTIONS_INCOMPLETE: MUTATE_KERNEL" in capsys.readouterr().out


def test_emits_act_true_fails(tmp_path) -> None:
    bad = COMPLIANT.replace("emits_act: bool = False", "emits_act: bool = True")
    assert gate.main(["--file", str(_write(tmp_path, bad))]) == 1


def test_unreadable_file_fails(tmp_path, capsys) -> None:
    assert gate.main(["--file", str(tmp_path / "absent.py")]) == 1
    assert "SIGMA_NON_SOVEREIGNTY_FAIL" in capsys.readouterr().out


def test_no_mutation_of_fixture(tmp_path) -> None:
    target = _write(tmp_path, COMPLIANT)
    before = target.read_text(encoding="utf-8")
    gate.main(["--file", str(target)])
    assert target.read_text(encoding="utf-8") == before


def test_stdout_no_content_leak(tmp_path, capsys) -> None:
    # Le gate n'affiche jamais le contenu du fichier, seulement des marqueurs.
    target = _write(tmp_path, COMPLIANT + "\nSECRET_TOKEN_XYZ = 1\n")
    gate.main(["--file", str(target)])
    assert "SECRET_TOKEN_XYZ" not in capsys.readouterr().out


def test_real_sigma_guidance_if_present() -> None:
    # Cible reelle du repo : doit etre conforme si presente.
    real = _REPO_ROOT / "sigma" / "sigma_guidance.py"
    if real.exists():
        assert gate.main(["--file", str(real)]) == 0

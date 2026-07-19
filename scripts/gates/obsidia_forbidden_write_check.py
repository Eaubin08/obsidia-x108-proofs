#!/usr/bin/env python3
"""obsidia_forbidden_write_check — Build Gate V0 (deferred B).

Verifie l'absence d'operations d'ecriture, de suppression, de mutation git
ou d'execution shell non controlee dans les scripts de gate Obsidia.
Lecture de texte uniquement. Aucune ecriture. Aucun subprocess.
decision_authority = KX108_ONLY.

Usage:
    python scripts/gates/obsidia_forbidden_write_check.py
    python scripts/gates/obsidia_forbidden_write_check.py --dir scripts/gates

Exit 0 : aucune operation interdite — FORBIDDEN_WRITE_PASS
Exit 1 : operation interdite detectee — FORBIDDEN_WRITE_FAIL
         ou repertoire illisible.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

DEFAULT_DIR = Path(__file__).resolve().parents[2] / "scripts" / "gates"

PASS_MSG = "FORBIDDEN_WRITE_PASS"
FAIL_MSG = "FORBIDDEN_WRITE_FAIL"

# (regex, label) — label identifie la categorie de violation dans le rapport.
FORBIDDEN_PATTERNS: tuple[tuple[str, str], ...] = (
    # open() avec mode ecriture/ajout/creation exclusive (2e arg positionnel)
    (r'\bopen\s*\([^,)]+,\s*["\'][waxa]["\']', "open_write_mode"),
    # open() avec mode update (r+, w+, a+, x+)
    (r'\bopen\s*\([^,)]+,\s*["\'][rwax][+]["\']', "open_update_mode"),
    # open() via keyword mode=
    (r'\bopen\s*\(.*\bmode\s*=\s*["\'][waxa]', "open_mode_kwarg"),
    # Methodes Path d'ecriture
    (r'\.write_text\s*\(', "write_text"),
    (r'\.write_bytes\s*\(', "write_bytes"),
    # Suppression de fichier
    (r'\.unlink\s*\(', "unlink"),
    (r'\bos\.remove\s*\(', "os_remove"),
    (r'\bos\.unlink\s*\(', "os_unlink"),
    (r'\bshutil\.rmtree\b', "shutil_rmtree"),
    # Operations repertoire
    (r'\.mkdir\s*\(', "mkdir"),
    (r'\.rmdir\s*\(', "rmdir"),
    # Subprocess shell non controle
    (r'\bshell\s*=\s*True\b', "shell_true"),
    # Mutations git interdites dans les commandes
    (r'["\']git\s+commit\b', "git_commit"),
    (r'["\']git\s+push\b', "git_push"),
    (r'["\']git\s+add\b', "git_add"),
)

_COMPILED: list[tuple[re.Pattern[str], str]] = [
    (re.compile(pat), label) for pat, label in FORBIDDEN_PATTERNS
]


def scan_file(path: Path) -> list[str]:
    """Retourne les violations trouvees dans un fichier (vide = propre)."""
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        return [f"FILE_UNREADABLE: {path.name}: {type(exc).__name__}"]

    violations: list[str] = []
    for lineno, line in enumerate(lines, start=1):
        for pattern, label in _COMPILED:
            if pattern.search(line):
                violations.append(f"{path.name}:{lineno}: {label}")
                break  # une seule violation signalée par ligne
    return violations


def scan_directory(directory: Path) -> tuple[list[str], str | None]:
    """
    Scanne les fichiers *.py du repertoire (non recursif).
    Retourne (violations, None) ou ([], raison_erreur).
    """
    if not directory.exists():
        return [], f"DIR_NOT_FOUND: {directory}"
    if not directory.is_dir():
        return [], f"NOT_A_DIRECTORY: {directory}"

    try:
        py_files = sorted(directory.glob("*.py"))
    except OSError as exc:
        return [], f"DIR_UNREADABLE: {type(exc).__name__}: {directory}"

    violations: list[str] = []
    for pyfile in py_files:
        violations.extend(scan_file(pyfile))
    return violations, None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dir",
        default=str(DEFAULT_DIR),
        help="repertoire a scanner (defaut: scripts/gates, non recursif)",
    )
    args = parser.parse_args(argv)

    target = Path(args.dir)
    violations, dir_err = scan_directory(target)

    if dir_err:
        print(FAIL_MSG)
        print(f"  {dir_err}")
        return 1

    if violations:
        print(FAIL_MSG)
        for v in violations:
            print(f"  {v}")
        return 1

    py_count = sum(1 for _ in target.glob("*.py"))
    print(f"{PASS_MSG} ({py_count} fichier(s) scanne(s) dans {target.name}/)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

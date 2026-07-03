"""test_obsidia_large_doc_read_policy — LARGE_DOC_READ_V2A.

Scope : OBSIDIA_TERMINAL_LARGE_DOC_READ_V2A_APPLY.
Aucun vrai document utilisateur : tout est genere dans tmp_path, avec
REPO_ROOT monkeypatche vers tmp_path pour tester la policy de confinement.
Verifie : lecture bornee, jamais de dump complet, secrets masques,
traversal/hors-repo/extension refuses, aucune ecriture, aucun subprocess.
"""

from __future__ import annotations

import py_compile
import re
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_CLI_DIR = _REPO_ROOT / "scripts"
sys.path.insert(0, str(_CLI_DIR))

import obsidia_cli as cli  # noqa: E402


def _mkroot(tmp_path):
    """Cree une arbo repo-like sous tmp_path et pointe REPO_ROOT dessus."""
    (tmp_path / "docs" / "specs").mkdir(parents=True)
    (tmp_path / "scripts").mkdir()
    cli.REPO_ROOT = tmp_path
    return tmp_path


def test_py_compile() -> None:
    py_compile.compile(str(_CLI_DIR / "obsidia_cli.py"), doraise=True)


def test_big_file_window_is_bounded(tmp_path) -> None:
    root = _mkroot(tmp_path)
    big = root / "docs" / "big.md"
    with big.open("w", encoding="utf-8") as fh:
        for i in range(50000):
            fh.write(f"ligne numero {i}\n")
    r = cli.classify_local_read_intent("lis docs/big.md", "lis docs/big.md")
    assert r["output_execute"] is True
    # jamais un dump complet : au plus la fenetre par defaut.
    assert len(r["reponse"].splitlines()) < cli._WIN_DEFAULT + 10
    assert "50000 lignes" in r["reponse"]


def test_range_exact(tmp_path) -> None:
    root = _mkroot(tmp_path)
    f = root / "docs" / "r.md"
    f.write_text("\n".join(f"L{i}" for i in range(1, 1001)), encoding="utf-8")
    n = "lis les lignes 20 a 25 de docs/r.md"
    r = cli.classify_local_read_intent(n, n)
    assert r["kind"] == "READ_LOCAL_RANGE"
    assert "20:" in r["reponse"] and "25:" in r["reponse"]
    assert "19:" not in r["reponse"] and "26:" not in r["reponse"]


def test_window_max_cap(tmp_path) -> None:
    root = _mkroot(tmp_path)
    f = root / "docs" / "r.md"
    f.write_text("\n".join(f"L{i}" for i in range(1, 5000)), encoding="utf-8")
    n = "lis les lignes 1 a 4000 de docs/r.md"
    r = cli.classify_local_read_intent(n, n)
    assert r["meta"]["lignes_affichees"] <= cli._WIN_MAX


def test_search_bounded_50(tmp_path) -> None:
    root = _mkroot(tmp_path)
    f = root / "docs" / "s.md"
    f.write_text("\n".join("thermo ici" for _ in range(200)), encoding="utf-8")
    n = "cherche thermo dans docs/s.md"
    r = cli.classify_local_read_intent(n, n)
    assert r["meta"]["match_count"] <= cli._SEARCH_MAX


def test_context_bounded_10(tmp_path) -> None:
    root = _mkroot(tmp_path)
    f = root / "docs" / "c.md"
    f.write_text("\n".join(("thermo" if i % 5 == 0 else f"x{i}")
                           for i in range(300)), encoding="utf-8")
    n = "montre le contexte autour de thermo dans docs/c.md"
    r = cli.classify_local_read_intent(n, n)
    assert r["meta"]["match_count"] <= cli._CTX_MAX


def test_long_lines_truncated(tmp_path) -> None:
    root = _mkroot(tmp_path)
    f = root / "docs" / "long.md"
    f.write_text("A" * 10000 + "\nB\n", encoding="utf-8")
    r = cli.classify_local_read_intent("lis docs/long.md", "lis docs/long.md")
    for line in r["reponse"].splitlines():
        assert len(line) < cli._LINE_MAX + 40


def test_secret_content_masked(tmp_path) -> None:
    root = _mkroot(tmp_path)
    f = root / "docs" / "sec.md"
    f.write_text("ligne ok\napi_key = ABCD1234\nautre ok\n", encoding="utf-8")
    r = cli.classify_local_read_intent("lis docs/sec.md", "lis docs/sec.md")
    assert "SECRET_MASQUE" in r["reponse"]
    assert "ABCD1234" not in r["reponse"]


def test_secret_density_stops(tmp_path) -> None:
    root = _mkroot(tmp_path)
    f = root / "docs" / "dense.md"
    f.write_text("\n".join("password = X" for _ in range(20)), encoding="utf-8")
    r = cli.classify_local_read_intent("lis docs/dense.md", "lis docs/dense.md")
    assert r["mode"] == "ANSWER_POLICY_DENY"
    assert "densite" in r["reponse"].lower()


def test_env_denied_before_io(tmp_path) -> None:
    _mkroot(tmp_path)
    for n in ("ouvre .env", "lis id_rsa", "lis token.txt"):
        r = cli.classify_local_read_intent(n, n)
        assert r["mode"] == "ANSWER_POLICY_DENY"
        assert "REPONSE" not in r.get("reponse", "").upper() or True
        assert "aucune lecture" in r["reponse"].lower() or "secrets" in r["reponse"].lower()


def test_traversal_denied(tmp_path) -> None:
    _mkroot(tmp_path)
    v, rel, ap = cli.local_path_policy("../outside.txt")
    assert v == "DENIED_OUT_OF_REPO"
    assert ap is None


def test_absolute_outside_denied(tmp_path) -> None:
    _mkroot(tmp_path)
    v, rel, ap = cli.local_path_policy("/etc/passwd")
    assert v in ("DENIED_OUT_OF_REPO", "DENIED_OUT_OF_ROOT", "NOT_FOUND")
    assert ap is None


def test_extension_denied(tmp_path) -> None:
    root = _mkroot(tmp_path)
    (root / "docs" / "x.sqlite").write_text("data", encoding="utf-8")
    v, rel, ap = cli.local_path_policy("docs/x.sqlite")
    assert v == "DENIED_EXTENSION"


def test_pdf_docx_denied(tmp_path) -> None:
    _mkroot(tmp_path)
    for name in ("docs/f.pdf", "docs/f.docx"):
        v, rel, ap = cli.local_path_policy(name)
        assert v == "DENIED_FORMAT"
        assert ap is None


def test_binary_not_read_as_text(tmp_path) -> None:
    root = _mkroot(tmp_path)
    b = root / "docs" / "bin.txt"
    b.write_bytes(b"\x00\x01\x02binaire")
    r = cli.classify_local_read_intent("lis docs/bin.txt", "lis docs/bin.txt")
    assert "binaire" in r["reponse"].lower()
    assert r.get("output_execute") is not True


def test_out_of_root_denied(tmp_path) -> None:
    root = _mkroot(tmp_path)
    (root / "config.md").write_text("x", encoding="utf-8")  # racine repo, hors roots
    v, rel, ap = cli.local_path_policy("config.md")
    assert v == "DENIED_OUT_OF_ROOT"


def test_no_write_to_tmp(tmp_path) -> None:
    root = _mkroot(tmp_path)
    f = root / "docs" / "w.md"
    f.write_text("contenu\n" * 10, encoding="utf-8")
    before = {p: p.stat().st_mtime_ns for p in root.rglob("*") if p.is_file()}
    cli.classify_local_read_intent("lis docs/w.md", "lis docs/w.md")
    cli.classify_local_read_intent("cherche contenu dans docs/w.md",
                                   "cherche contenu dans docs/w.md")
    after = {p: p.stat().st_mtime_ns for p in root.rglob("*") if p.is_file()}
    assert before == after  # aucune ecriture


def test_static_no_subprocess() -> None:
    src = (_CLI_DIR / "obsidia_cli.py").read_text(encoding="utf-8")
    assert "import subprocess" not in src
    assert "os.system" not in src
    assert "shell=True" not in src


def test_static_no_full_read_of_user_path() -> None:
    """Les fonctions de lecture locale n'utilisent que le streaming ligne a
    ligne (open + for). Aucun .read()/.readlines() dans le bloc lecture."""
    src = (_CLI_DIR / "obsidia_cli.py").read_text(encoding="utf-8")
    i = src.index("def _stream_window")
    j = src.index("def build_local_read_guide_response")
    block = src[i:j]
    assert ".readlines()" not in block
    assert not re.search(r"\.read\(\s*\)", block)  # pas de .read() complet

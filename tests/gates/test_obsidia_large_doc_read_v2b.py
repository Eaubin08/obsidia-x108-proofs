"""test_obsidia_large_doc_read_v2b — LARGE_DOC_READ_V2B.

Scope : OBSIDIA_TERMINAL_LARGE_DOC_READ_V2B_APPLY.
Resume / explication / comparaison EXTRACTIFS sur fenetre bornee.
Tout en tmp_path (REPO_ROOT monkeypatche). Aucune lecture complete,
aucun subprocess, aucune hallucination globale sur fenetre partielle.
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

_REG = cli.load_registry(cli.REGISTRY_PATH)


def _mkroot(tmp_path):
    (tmp_path / "docs").mkdir()
    cli.REPO_ROOT = tmp_path
    return tmp_path


def _a(q):
    return cli.answer_router(q, _REG)


def test_py_compile() -> None:
    py_compile.compile(str(_CLI_DIR / "obsidia_cli.py"), doraise=True)


def test_resume_small_file_bounded_execute(tmp_path) -> None:
    root = _mkroot(tmp_path)
    (root / "docs" / "s.md").write_text("# Titre\n- point A\n- point B\ntexte normal\n",
                                        encoding="utf-8")
    r = _a("resume docs/s.md")
    assert r["output"] == "EXECUTE"
    assert r["action_locale"] == "SUMMARIZE_LOCAL_PROGRESSIVE"
    assert "fenetre lue" in r["reponse"]
    assert "Titre" in r["reponse"]


def test_resume_large_file_first_window_only_with_next(tmp_path) -> None:
    root = _mkroot(tmp_path)
    (root / "docs" / "big.md").write_text(
        "\n".join(f"# section {i}" if i % 10 == 0 else f"ligne {i}"
                  for i in range(1, 1000)), encoding="utf-8")
    r = _a("resume docs/big.md")
    assert r["output"] == "EXECUTE"
    assert r["local_read_meta"]["range_lignes"].startswith("1-")
    last = int(r["local_read_meta"]["range_lignes"].split("-")[1])
    assert last <= cli._WIN_DEFAULT
    assert "Next :" in r["reponse"]
    assert "PARTIELLE" in r["reponse"]


def test_resume_explicit_range_20_40(tmp_path) -> None:
    root = _mkroot(tmp_path)
    (root / "docs" / "r.md").write_text("\n".join(f"# h{i}" for i in range(1, 100)),
                                        encoding="utf-8")
    r = _a("resume les lignes 20 a 40 de docs/r.md")
    assert r["output"] == "EXECUTE"
    assert r["local_read_meta"]["range_lignes"] == "20-40"


def test_explain_small_file_bounded_execute(tmp_path) -> None:
    root = _mkroot(tmp_path)
    (root / "docs" / "c.py").write_text("def foo():\n    KX108_ONLY = 1\n    return foo\n",
                                        encoding="utf-8")
    r = _a("explique docs/c.py")
    assert r["output"] == "EXECUTE"
    assert r["action_locale"] == "EXPLAIN_LOCAL_PROGRESSIVE"
    assert "fenetre lue" in r["reponse"]


def test_compare_two_files_bounded_execute(tmp_path) -> None:
    root = _mkroot(tmp_path)
    (root / "docs" / "a.md").write_text("commun\nligne A\n", encoding="utf-8")
    (root / "docs" / "b.md").write_text("commun\nligne B\n", encoding="utf-8")
    r = _a("compare docs/a.md et docs/b.md")
    assert r["output"] == "EXECUTE"
    assert r["action_locale"] == "COMPARE_LOCAL_BOUNDED"
    assert "fenetres lues" in r["reponse"]


def test_compare_diff_output_capped(tmp_path) -> None:
    root = _mkroot(tmp_path)
    (root / "docs" / "a.md").write_text("\n".join(f"a{i}" for i in range(400)), encoding="utf-8")
    (root / "docs" / "b.md").write_text("\n".join(f"b{i}" for i in range(400)), encoding="utf-8")
    r = _a("compare docs/a.md et docs/b.md")
    assert r["local_read_meta"]["diff_lines"] <= 120


def test_compare_more_than_two_files_guides_clarification(tmp_path) -> None:
    _mkroot(tmp_path)
    r = _a("compare docs/a.md et docs/b.md et docs/c.md")
    assert r["output"] == "GUIDE"
    assert "2 chemins" in r["reponse"]


def test_resume_without_target_stop_unknown(tmp_path) -> None:
    _mkroot(tmp_path)
    r = _a("resume ce fichier")
    assert r["output"] == "STOP_UNKNOWN"


def test_explain_without_target_stop_unknown(tmp_path) -> None:
    _mkroot(tmp_path)
    r = _a("explique ce fichier")
    assert r["output"] == "STOP_UNKNOWN"


def test_secret_still_policy_deny(tmp_path) -> None:
    _mkroot(tmp_path)
    for q in ("resume .env", "explique id_rsa"):
        r = _a(q)
        assert r["output"] == "POLICY_DENY"


def test_pdf_docx_still_guide_v3_required(tmp_path) -> None:
    root = _mkroot(tmp_path)
    (root / "docs" / "f.pdf").write_bytes(b"%PDF-1.4 fake")
    r = _a("resume docs/f.pdf")
    assert r["output"] == "GUIDE"
    assert "V3" in r["reponse"]


def test_no_subprocess_static_guard() -> None:
    src = (_CLI_DIR / "obsidia_cli.py").read_text(encoding="utf-8")
    assert "import subprocess" not in src
    assert "os.system" not in src
    assert "shell=True" not in src


def test_no_full_read_static_guard() -> None:
    """Bloc V2B : aucune lecture complete (que du streaming _stream_window)."""
    src = (_CLI_DIR / "obsidia_cli.py").read_text(encoding="utf-8")
    i = src.index("def _summarize_window")
    j = src.index("def classify_local_read_intent")
    block = src[i:j]
    assert ".readlines()" not in block
    assert ".read_text(" not in block
    assert not re.search(r"\.read\(\s*\)", block)


def test_anti_hallucination_no_global_claim_on_partial_window(tmp_path) -> None:
    root = _mkroot(tmp_path)
    (root / "docs" / "big.md").write_text("\n".join(f"# h{i}" for i in range(1, 1000)),
                                          encoding="utf-8")
    r = _a("resume docs/big.md")
    low = r["reponse"].lower()
    assert "le document dit" not in low
    assert "document complet" not in low
    assert "fenetre lue" in low


def test_nl_resume_explain_compare_now_execute_for_valid_targets(tmp_path) -> None:
    root = _mkroot(tmp_path)
    (root / "docs" / "a.md").write_text("# t\n- x\n", encoding="utf-8")
    (root / "docs" / "b.md").write_text("# t\n- y\n", encoding="utf-8")
    assert _a("synthetise docs/a.md")["output"] == "EXECUTE"
    assert _a("detaille docs/a.md")["output"] == "EXECUTE"
    assert _a("difference entre docs/a.md et docs/b.md")["output"] == "EXECUTE"
    # plus de V2B_REQUIRED sur cible valide
    assert "V2B_REQUIRED" not in _a("resume docs/a.md")["reponse"]

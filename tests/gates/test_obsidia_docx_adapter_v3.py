"""test_obsidia_docx_adapter_v3 — DOCX_ADAPTER_V3.

Scope : OBSIDIA_TERMINAL_DOCX_ADAPTER_V3_APPLY.
Extraction DOCX stdlib-only (zipfile + ElementTree). Paragraphes traites comme
lignes. Memes bornes V2. Secrets masques. Refus gracieux. Aucun subprocess.
Aucun extractall. Aucune dependance externe. Tout en tmp_path.
"""

from __future__ import annotations

import io
import py_compile
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_CLI_DIR = _REPO_ROOT / "scripts"
sys.path.insert(0, str(_CLI_DIR))

import obsidia_cli as cli  # noqa: E402

_REG = cli.load_registry(cli.REGISTRY_PATH)

_W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _mkroot(tmp_path):
    (tmp_path / "docs").mkdir(parents=True, exist_ok=True)
    cli.REPO_ROOT = tmp_path
    return tmp_path


def _a(q):
    return cli.answer_router(q, _REG)


def _make_docx(path: Path, paragraphs: list[str]) -> None:
    """Cree un DOCX minimal valide (zipfile + XML) en memoire, sans ecriture intermediaire."""
    ET.register_namespace("w", _W)
    root_el = ET.Element(f"{{{_W}}}document")
    body = ET.SubElement(root_el, f"{{{_W}}}body")
    for txt in paragraphs:
        p = ET.SubElement(body, f"{{{_W}}}p")
        r_el = ET.SubElement(p, f"{{{_W}}}r")
        t = ET.SubElement(r_el, f"{{{_W}}}t")
        t.text = txt
    xml_bytes = ET.tostring(root_el, encoding="unicode").encode("utf-8")
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr("word/document.xml", xml_bytes)


def _make_paragraphs(n: int, prefix: str = "paragraphe") -> list[str]:
    return [f"{prefix} {i}" for i in range(1, n + 1)]


# ---------------------------------------------------------------------------
# test_py_compile
# ---------------------------------------------------------------------------
def test_py_compile() -> None:
    py_compile.compile(str(_CLI_DIR / "obsidia_cli.py"), doraise=True)


# ---------------------------------------------------------------------------
# Operations de base
# ---------------------------------------------------------------------------
def test_docx_summarize_bounded_execute(tmp_path) -> None:
    root = _mkroot(tmp_path)
    _make_docx(root / "docs" / "a.docx", _make_paragraphs(50, "# section"))
    r = _a("resume docs/a.docx")
    assert r["output"] == "EXECUTE"
    assert r["action_locale"] == "SUMMARIZE_LOCAL_PROGRESSIVE"
    assert "fenetre" in r["reponse"].lower() or "paragraphes" in r["reponse"].lower()
    assert "docx" in r["reponse"].lower() or "extraction" in r["reponse"].lower()


def test_docx_explain_bounded_execute(tmp_path) -> None:
    root = _mkroot(tmp_path)
    _make_docx(root / "docs" / "b.docx", _make_paragraphs(30))
    r = _a("explique docs/b.docx")
    assert r["output"] == "EXECUTE"
    assert r["action_locale"] == "EXPLAIN_LOCAL_PROGRESSIVE"
    assert "fenetre" in r["reponse"].lower() or "paragraphes" in r["reponse"].lower()


def test_docx_compare_bounded_execute(tmp_path) -> None:
    root = _mkroot(tmp_path)
    _make_docx(root / "docs" / "c1.docx", ["commun A", "specifique A"])
    _make_docx(root / "docs" / "c2.docx", ["commun A", "specifique B"])
    r = _a("compare docs/c1.docx et docs/c2.docx")
    assert r["output"] == "EXECUTE"
    assert r["action_locale"] == "COMPARE_LOCAL_BOUNDED"
    assert "fenetres" in r["reponse"].lower() or "paragraphes" in r["reponse"].lower()


def test_docx_read_window_bounded(tmp_path) -> None:
    root = _mkroot(tmp_path)
    _make_docx(root / "docs" / "r.docx", _make_paragraphs(200))
    r = _a("lis docs/r.docx")
    assert r["output"] == "EXECUTE"
    meta = r["local_read_meta"]
    assert meta is not None
    last = int(meta["range_lignes"].split("-")[1])
    assert last <= cli._WIN_DEFAULT + 5


def test_docx_search_bounded(tmp_path) -> None:
    root = _mkroot(tmp_path)
    paragraphs = ["thermo ici"] * 80 + ["autre chose"] * 20
    _make_docx(root / "docs" / "s.docx", paragraphs)
    r = _a("cherche thermo dans docs/s.docx")
    assert r["output"] == "EXECUTE"
    assert r["local_read_meta"]["match_count"] <= cli._SEARCH_MAX


def test_docx_context_bounded(tmp_path) -> None:
    root = _mkroot(tmp_path)
    paragraphs = [("thermo" if i % 5 == 0 else f"x{i}") for i in range(1, 60)]
    _make_docx(root / "docs" / "ctx.docx", paragraphs)
    r = _a("montre le contexte autour de thermo dans docs/ctx.docx")
    assert r["output"] == "EXECUTE"
    assert r["local_read_meta"]["match_count"] <= cli._CTX_MAX


# ---------------------------------------------------------------------------
# Secrets
# ---------------------------------------------------------------------------
def test_docx_extract_secret_masked(tmp_path) -> None:
    root = _mkroot(tmp_path)
    _make_docx(root / "docs" / "sec.docx",
               ["ligne normale", "api_key = ABCD1234", "autre ligne"])
    r = _a("lis docs/sec.docx")
    assert r["output"] == "EXECUTE"
    assert "SECRET_MASQUE" in r["reponse"]
    assert "ABCD1234" not in r["reponse"]


def test_docx_density_denied(tmp_path) -> None:
    root = _mkroot(tmp_path)
    _make_docx(root / "docs" / "dense.docx",
               [f"password = secret{i}" for i in range(20)])
    r = _a("lis docs/dense.docx")
    assert r["output"] == "POLICY_DENY"


# ---------------------------------------------------------------------------
# Refus gracieux
# ---------------------------------------------------------------------------
def test_docx_bad_zip_graceful_guide(tmp_path) -> None:
    root = _mkroot(tmp_path)
    (root / "docs" / "bad.docx").write_bytes(b"not a zip at all")
    r = _a("resume docs/bad.docx")
    assert r["output"] == "GUIDE"
    assert "corrompu" in r["reponse"].lower() or "illisible" in r["reponse"].lower()


def test_docx_no_document_xml_graceful_guide(tmp_path) -> None:
    root = _mkroot(tmp_path)
    docx_path = root / "docs" / "noxml.docx"
    with zipfile.ZipFile(docx_path, "w") as zf:
        zf.writestr("word/other.xml", b"<root/>")
    r = _a("resume docs/noxml.docx")
    assert r["output"] == "GUIDE"
    assert "standard" in r["reponse"].lower() or "absent" in r["reponse"].lower()


def test_docx_empty_paragraphs_guide(tmp_path) -> None:
    root = _mkroot(tmp_path)
    docx_path = root / "docs" / "empty.docx"
    root_el = ET.Element(f"{{{_W}}}document")
    ET.SubElement(root_el, f"{{{_W}}}body")
    xml_bytes = ET.tostring(root_el, encoding="unicode").encode("utf-8")
    with zipfile.ZipFile(docx_path, "w") as zf:
        zf.writestr("word/document.xml", xml_bytes)
    r = _a("resume docs/empty.docx")
    assert r["output"] == "GUIDE"
    assert "0 paragraphe" in r["reponse"] or "extractible" in r["reponse"].lower()


def test_docx_size_cap_guide(tmp_path, monkeypatch) -> None:
    root = _mkroot(tmp_path)
    docx_path = root / "docs" / "big.docx"
    _make_docx(docx_path, ["contenu"])
    monkeypatch.setattr("obsidia_cli._DOCX_SIZE_CAP", 1)
    r = _a("resume docs/big.docx")
    assert r["output"] == "GUIDE"
    assert "volumineux" in r["reponse"].lower()


# ---------------------------------------------------------------------------
# PDF reste GUIDE
# ---------------------------------------------------------------------------
def test_pdf_still_guide_after_v3(tmp_path) -> None:
    root = _mkroot(tmp_path)
    (root / "docs" / "f.pdf").write_bytes(b"%PDF-1.4 fake")
    r = _a("resume docs/f.pdf")
    assert r["output"] == "GUIDE"
    low = r["reponse"].lower()
    assert "pdf" in low or "format" in low or "converti" in low


# ---------------------------------------------------------------------------
# local_path_policy : .docx reste DENIED_FORMAT (V2A inchange)
# ---------------------------------------------------------------------------
def test_v2a_policy_docx_still_denied_format(tmp_path) -> None:
    """local_path_policy retourne toujours DENIED_FORMAT pour .docx (V2A intact).
    L'adapter V3 vit au-dessus, il ne modifie pas la policy core."""
    _mkroot(tmp_path)
    v, rel, ap = cli.local_path_policy("docs/f.docx")
    assert v == "DENIED_FORMAT"
    assert ap is None


# ---------------------------------------------------------------------------
# Gardes statiques
# ---------------------------------------------------------------------------
def test_static_no_subprocess_v3() -> None:
    src = (_CLI_DIR / "obsidia_cli.py").read_text(encoding="utf-8")
    assert "import subprocess" not in src
    assert "os.system" not in src
    assert "shell=True" not in src


def test_static_no_extractall_v3() -> None:
    src = (_CLI_DIR / "obsidia_cli.py").read_text(encoding="utf-8")
    assert "extractall(" not in src
    assert ".extract(" not in src


def test_static_no_pdf_deps_v3() -> None:
    src = (_CLI_DIR / "obsidia_cli.py").read_text(encoding="utf-8")
    for dep in ("import pypdf", "import PyPDF2", "import pdfminer",
                "import fitz", "import docx", "import python_docx"):
        assert dep not in src


# ---------------------------------------------------------------------------
# Anti-hallucination
# ---------------------------------------------------------------------------
def test_docx_anti_hallucination(tmp_path) -> None:
    root = _mkroot(tmp_path)
    _make_docx(root / "docs" / "big.docx", _make_paragraphs(400))
    r = _a("resume docs/big.docx")
    low = r["reponse"].lower()
    assert "le document dit" not in low
    assert "document complet" not in low
    assert "fenetre" in low or "paragraphes" in low

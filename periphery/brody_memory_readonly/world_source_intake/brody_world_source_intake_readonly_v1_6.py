import argparse
import csv
import hashlib
import json
import re
import sys
import zipfile
from datetime import datetime
from pathlib import Path

SUPPORTED = {
    ".txt", ".md", ".json", ".jsonl", ".csv",
    ".docx", ".pdf", ".xlsx", ".xls"
}

BOUNDARY = {
    "readonly": True,
    "memory_authority": False,
    "memory_decision": False,
    "allowed_to_decide": False,
    "emits_act": False,
    "kernel_binding": False,
    "x108_merge": False,
    "kernel_mutation": False,
    "x108_mutation": False,
    "decision_authority": "KX108_ONLY",
    "scope": "BRODY_WORLD_SOURCE_INTAKE_PERIPHERY_ONLY"
}

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()

def safe_name(name: str) -> str:
    base = re.sub(r"[^a-zA-Z0-9_.-]+", "_", name.strip())
    return base[:160] if base else "source"

def read_text_file(path: Path, max_chars: int = 200000) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace")[:max_chars]

def read_json_file(path: Path, max_chars: int = 200000) -> str:
    obj = json.loads(path.read_text(encoding="utf-8-sig", errors="replace"))
    return json.dumps(obj, ensure_ascii=False, indent=2)[:max_chars]

def read_csv_file(path: Path, max_rows: int = 200) -> str:
    rows = []
    with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if i >= max_rows:
                rows.append(["...TRUNCATED..."])
                break
            rows.append(row)
    return "\n".join([" | ".join(map(str, r)) for r in rows])

def read_docx_file(path: Path) -> str:
    # DOCX = zip. Extraction XML minimale, sans dépendance externe.
    texts = []
    with zipfile.ZipFile(path, "r") as z:
        names = [n for n in z.namelist() if n.startswith("word/") and n.endswith(".xml")]
        for name in names:
            raw = z.read(name).decode("utf-8", errors="replace")
            raw = re.sub(r"<[^>]+>", " ", raw)
            raw = raw.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
            raw = re.sub(r"\s+", " ", raw).strip()
            if raw:
                texts.append(f"--- {name} ---\n{raw}")
    return "\n\n".join(texts)[:200000]

def read_pdf_file(path: Path) -> str:
    # Extraction PDF minimale sans OCR. Suffisant pour preuve d’intake, pas pour PDF scanné image.
    data = path.read_bytes()
    text = data.decode("latin-1", errors="ignore")
    chunks = re.findall(r"\((.*?)\)", text, flags=re.S)
    cleaned = []
    for c in chunks[:5000]:
        c = c.replace("\\n", "\n").replace("\\r", "\r").replace("\\t", "\t")
        c = re.sub(r"\\[0-9]{3}", " ", c)
        c = re.sub(r"\s+", " ", c).strip()
        if len(c) >= 3:
            cleaned.append(c)
    return "\n".join(cleaned)[:200000]

def read_xlsx_minimal(path: Path) -> str:
    # XLSX = zip XML. XLS ancien binaire non supporté directement ici.
    if path.suffix.lower() == ".xls":
        return "XLS_BINARY_UNSUPPORTED_IN_MINIMAL_READER. Convertir en CSV/XLSX ou ajouter moteur spécialisé."
    rows = []
    with zipfile.ZipFile(path, "r") as z:
        shared = []
        if "xl/sharedStrings.xml" in z.namelist():
            raw = z.read("xl/sharedStrings.xml").decode("utf-8", errors="replace")
            vals = re.findall(r"<t[^>]*>(.*?)</t>", raw, flags=re.S)
            shared = [re.sub(r"<[^>]+>", "", v) for v in vals]
        sheets = [n for n in z.namelist() if n.startswith("xl/worksheets/sheet") and n.endswith(".xml")]
        for sheet in sheets[:10]:
            raw = z.read(sheet).decode("utf-8", errors="replace")
            cells = re.findall(r"<c[^>]*?(?:t=\"s\")?[^>]*>.*?<v>(.*?)</v>.*?</c>", raw, flags=re.S)
            out = []
            for v in cells[:2000]:
                v = v.strip()
                if v.isdigit() and shared:
                    idx = int(v)
                    out.append(shared[idx] if idx < len(shared) else v)
                else:
                    out.append(v)
            rows.append(f"--- {sheet} ---\n" + "\n".join(out))
    return "\n\n".join(rows)[:200000]

def extract_text(path: Path) -> tuple[str, str]:
    ext = path.suffix.lower()
    try:
        if ext in [".txt", ".md"]:
            return read_text_file(path), "TEXT_OK"
        if ext in [".json", ".jsonl"]:
            return read_json_file(path), "JSON_OK"
        if ext == ".csv":
            return read_csv_file(path), "CSV_OK"
        if ext == ".docx":
            return read_docx_file(path), "DOCX_XML_OK"
        if ext == ".pdf":
            return read_pdf_file(path), "PDF_MINIMAL_TEXT_OK"
        if ext in [".xlsx", ".xls"]:
            return read_xlsx_minimal(path), "XLSX_XML_OK" if ext == ".xlsx" else "XLS_BINARY_LIMITED"
        return "", "UNSUPPORTED"
    except Exception as e:
        return "", "EXTRACT_FAIL:" + repr(e)

def iter_sources(src: Path):
    if src.is_file():
        yield src
    else:
        for p in sorted(src.rglob("*")):
            if p.is_file() and p.suffix.lower() in SUPPORTED:
                yield p

def build_intake(source: Path, out_root: Path, label: str):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = out_root / f"BRODY_WORLD_INTAKE_{label}_{ts}"
    md_dir = run_dir / "normalized_md"
    meta_dir = run_dir / "metadata_json"
    md_dir.mkdir(parents=True, exist_ok=True)
    meta_dir.mkdir(parents=True, exist_ok=True)

    records = []
    skipped = []

    for src in iter_sources(source):
        ext = src.suffix.lower()
        if ext not in SUPPORTED:
            skipped.append({"path": str(src), "reason": "UNSUPPORTED_EXTENSION"})
            continue

        text, status = extract_text(src)
        src_hash = sha256_file(src)

        base = safe_name(src.stem)
        out_md = md_dir / f"{base}_{src_hash[:12]}.md"
        out_json = meta_dir / f"{base}_{src_hash[:12]}.json"

        md = [
            f"# BRODY WORLD SOURCE NORMALIZED",
            "",
            f"- Source path: `{src}`",
            f"- Source extension: `{ext}`",
            f"- Source sha256: `{src_hash}`",
            f"- Extract status: `{status}`",
            f"- Readonly: `true`",
            f"- Memory authority: `false`",
            f"- Memory decision: `false`",
            f"- Decision authority: `KX108_ONLY`",
            "",
            "## Extracted content",
            "",
            text if text.strip() else "[NO_TEXT_EXTRACTED]"
        ]
        out_md.write_text("\n".join(md) + "\n", encoding="utf-8")

        meta = {
            "source_path": str(src),
            "source_extension": ext,
            "source_sha256": src_hash,
            "normalized_md": str(out_md),
            "extract_status": status,
            "text_chars": len(text),
            **BOUNDARY
        }
        out_json.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

        records.append({
            "source": "world_intake",
            "path": str(out_md),
            "source_original_path": str(src),
            "source_original_sha256": src_hash,
            "sha256": sha256_file(out_md),
            "extension": ".md",
            "original_extension": ext,
            "snippet": text[:700],
            "world_intake_signal": True,
            "memory_signal": True,
            "zip2_signal": False,
            "graph_signal": False,
            "readonly": True,
            "memory_authority": False,
            "memory_decision": False,
            "decision_authority": "KX108_ONLY"
        })

    manifest = {
        "status": "BRODY_WORLD_SOURCE_INTAKE_READONLY_PASS",
        "date": ts,
        "source": str(source),
        "run_dir": str(run_dir),
        "files_count": len(records),
        "skipped_count": len(skipped),
        "files": records,
        "skipped": skipped,
        **BOUNDARY
    }

    manifest_path = run_dir / "BRODY_WORLD_SOURCE_INTAKE_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    current = out_root / "CURRENT_BRODY_WORLD_SOURCE_INTAKE_READONLY.txt"
    current.write_text(
        "\n".join([
            f"CURRENT_BRODY_WORLD_SOURCE_INTAKE_READONLY={run_dir}",
            f"MANIFEST={manifest_path}",
            f"FILES_COUNT={len(records)}",
            f"SKIPPED_COUNT={len(skipped)}",
            "STATUS=BRODY_WORLD_SOURCE_INTAKE_READONLY_PASS",
            "MEMORY_DECISION=false",
            "DECISION_AUTHORITY=KX108_ONLY"
        ]) + "\n",
        encoding="utf-8"
    )

    print(json.dumps({
        "status": "BRODY_WORLD_SOURCE_INTAKE_READONLY_PASS",
        "run_dir": str(run_dir),
        "manifest": str(manifest_path),
        "files_count": len(records),
        "skipped_count": len(skipped),
        **BOUNDARY
    }, indent=2, ensure_ascii=False))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True)
    ap.add_argument("--out-root", required=True)
    ap.add_argument("--label", default="SOURCE")
    args = ap.parse_args()

    build_intake(Path(args.source), Path(args.out_root), safe_name(args.label))

if __name__ == "__main__":
    main()

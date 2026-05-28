from __future__ import annotations

import json
import os
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.cwd()
BASE = Path(r"C:\Users\User\Desktop\obsidia-engine-proof-core")
OUT = ROOT / "docs" / "runtime"
OUT.mkdir(parents=True, exist_ok=True)

TS = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

PATTERN = re.compile(
    r"OS\s*Trad|os_trad|OSTRAD|translation_trace|alphabet_units|"
    r"Reverse\s*OS|reverse_os|os_reverse|os_reverse_projection|SSR|"
    r"IR Candidate|ir_candidate|ObsidiaIR|Intermediate Representation|"
    r"ContextPacket|MCPRequest|demo_full_pipeline|non_decision",
    re.IGNORECASE,
)

TARGET_DIRS = [
    ROOT,
    BASE / "obsidia-engine-candidate",
    BASE / "obsidia-engine-candidate" / "OBSIDIA_V4_REGROUPEMENTS_V43_SOUS_DOSSIERS",
    BASE / "obsidia-engine-candidate" / "OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1_FREEZE_CANDIDATE",
    BASE / "obsidia-engine-candidate" / "obsidia-x108-proofs-main (6)",
]

ZIP_HINTS = [
    BASE / "obsidia-engine-candidate",
    BASE,
    Path(r"C:\Users\User\Desktop"),
    Path(r"C:\Users\User\Downloads"),
]

TEXT_EXTS = {
    ".py", ".md", ".txt", ".json", ".ts", ".tsx", ".lean", ".yml", ".yaml"
}

def safe_read(path: Path, max_chars: int = 500_000) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")[:max_chars]
    except Exception:
        return ""

def scan_file(path: Path, base: Path) -> list[dict]:
    text = safe_read(path)
    hits = []
    for i, line in enumerate(text.splitlines(), 1):
        if PATTERN.search(line):
            hits.append({
                "path": str(path),
                "relative": str(path.relative_to(base)) if path.is_relative_to(base) else str(path),
                "line": i,
                "text": line[:500],
            })
            if len(hits) >= 20:
                break
    return hits

def scan_dir(base: Path) -> list[dict]:
    if not base.exists():
        return [{"missing_dir": str(base)}]

    out = []
    ignored = {".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build", ".pytest_cache"}

    for path in base.rglob("*"):
        if not path.is_file():
            continue
        if any(part in ignored for part in path.parts):
            continue
        if path.suffix.lower() not in TEXT_EXTS:
            continue
        name_hit = bool(PATTERN.search(str(path)))
        hits = scan_file(path, base)
        if name_hit or hits:
            out.append({
                "file": str(path),
                "size": path.stat().st_size,
                "name_hit": name_hit,
                "hits": hits[:10],
            })
        if len(out) >= 400:
            break
    return out

def scan_zip(zip_path: Path) -> list[dict]:
    out = []
    try:
        with zipfile.ZipFile(zip_path) as z:
            for info in z.infolist():
                if info.is_dir():
                    continue
                suffix = Path(info.filename).suffix.lower()
                name_hit = bool(PATTERN.search(info.filename))
                hits = []

                if suffix in TEXT_EXTS and info.file_size < 2_000_000:
                    try:
                        text = z.read(info).decode("utf-8", errors="replace")
                        for i, line in enumerate(text.splitlines(), 1):
                            if PATTERN.search(line):
                                hits.append({
                                    "line": i,
                                    "text": line[:500],
                                })
                                if len(hits) >= 10:
                                    break
                    except Exception as e:
                        hits.append({"error": str(e)})

                if name_hit or hits:
                    out.append({
                        "zip": str(zip_path),
                        "file": info.filename,
                        "size": info.file_size,
                        "name_hit": name_hit,
                        "hits": hits,
                    })
                if len(out) >= 400:
                    break
    except Exception as e:
        out.append({"zip_error": str(zip_path), "error": str(e)})
    return out

def classify_candidate(entry: dict) -> str:
    text = json.dumps(entry, ensure_ascii=False).lower()
    if "demo_full_pipeline" in text:
        return "DEMO_PIPELINE_CANDIDATE"
    if "reverse_os.py" in text or "06_reverse_os" in text:
        return "REVERSE_OS_RUNTIME_CANDIDATE"
    if "obsidiair" in text or "obsidia_ir.py" in text:
        return "IR_TYPE_OR_STUB_CANDIDATE"
    if "test_reverse_os_non_decision" in text:
        return "TEST_NON_DECISION_CANDIDATE"
    if "contextpacket" in text:
        return "CONTEXT_PACKET_TYPE_CANDIDATE"
    if "translation_trace" in text or "alphabet_units" in text:
        return "CURRENT_RUNTIME_ENVELOPE_CANDIDATE"
    if "p14" in text or "traduction humain" in text:
        return "FORMAL_OS_TRAD_CANON_SOURCE"
    return "RELATED_SOURCE"

def main():
    zips = []
    for root in ZIP_HINTS:
        if root.exists():
            zips.extend(root.rglob("*.zip"))

    zips = [
        z for z in zips
        if "OBSIDIA_V4_REGROUPEMENTS" in z.name
        or "MMONDE_REVERSE_OS" in z.name
        or "34ARBRES" in z.name
        or "OBSIDIA_MMONDE" in z.name
    ]

    dir_results = {}
    for d in TARGET_DIRS:
        dir_results[str(d)] = scan_dir(d)

    zip_results = {}
    for z in zips[:20]:
        zip_results[str(z)] = scan_zip(z)

    flat = []
    for src, entries in dir_results.items():
        for e in entries:
            if isinstance(e, dict):
                e["origin"] = src
                e["origin_type"] = "directory"
                e["classification"] = classify_candidate(e)
                flat.append(e)

    for src, entries in zip_results.items():
        for e in entries:
            if isinstance(e, dict):
                e["origin"] = src
                e["origin_type"] = "zip"
                e["classification"] = classify_candidate(e)
                flat.append(e)

    priority_order = {
        "REVERSE_OS_RUNTIME_CANDIDATE": 1,
        "DEMO_PIPELINE_CANDIDATE": 2,
        "TEST_NON_DECISION_CANDIDATE": 3,
        "IR_TYPE_OR_STUB_CANDIDATE": 4,
        "CONTEXT_PACKET_TYPE_CANDIDATE": 5,
        "FORMAL_OS_TRAD_CANON_SOURCE": 6,
        "CURRENT_RUNTIME_ENVELOPE_CANDIDATE": 7,
        "RELATED_SOURCE": 8,
    }

    flat_sorted = sorted(flat, key=lambda e: priority_order.get(e.get("classification"), 99))

    report = {
        "checkpoint": "F18A2_ZIP_LOCAL_SOURCE_AUDIT",
        "mode": "READ_ONLY",
        "timestamp": TS,
        "repo": str(ROOT),
        "target_dirs": [str(x) for x in TARGET_DIRS],
        "zips_found": [str(z) for z in zips],
        "priority_candidates": flat_sorted[:120],
        "classification_counts": {},
        "decision_hint": {
            "do_not_create_from_zero": True,
            "prefer_reuse": [
                "06_REVERSE_OS_SSR_JARVIS/reverse_os.py",
                "common_types.py ObsidiaIR / SSRProjection / ContextPacket",
                "20_DEMO_MINIMALE/demo_full_pipeline.py",
                "17_TESTS/test_reverse_os_non_decision.py",
                "V4 P14 Traduction humain-machine for OS Trad canon",
            ],
            "expected_F18B": "COPY_OR_ADAPT_EXISTING_READONLY_MODULES_INSTEAD_OF_NAIVE_NEW_ADAPTERS",
        },
    }

    counts = {}
    for e in flat_sorted:
        c = e.get("classification", "UNKNOWN")
        counts[c] = counts.get(c, 0) + 1
    report["classification_counts"] = counts

    out_json = OUT / f"OBSIDIA_F18A2_ZIP_LOCAL_SOURCE_AUDIT_{TS}.json"
    out_txt = OUT / f"OBSIDIA_F18A2_ZIP_LOCAL_SOURCE_AUDIT_{TS}.txt"

    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "OBSIDIA F18A2 ZIP + LOCAL SOURCE AUDIT",
        f"timestamp={TS}",
        "mode=READ_ONLY",
        "",
        "ZIPS_FOUND:",
        *[str(z) for z in zips],
        "",
        "CLASSIFICATION_COUNTS:",
        *[f"{k}={v}" for k, v in sorted(counts.items())],
        "",
        "TOP_CANDIDATES:",
    ]

    for e in flat_sorted[:40]:
        lines.append("")
        lines.append(f"classification={e.get('classification')}")
        lines.append(f"origin_type={e.get('origin_type')}")
        lines.append(f"file={e.get('file')}")
        lines.append(f"origin={e.get('origin')}")
        hits = e.get("hits") or []
        for h in hits[:3]:
            lines.append(f"  L{h.get('line')}: {h.get('text')}")

    lines.extend([
        "",
        "DECISION_HINT:",
        "Do not create F18B adapters from zero.",
        "Reuse/copy/adapt existing Reverse OS / IR / ContextPacket modules if present.",
        "V4 P14 can feed OS Trad canon, but MMONDE zip has the runtime Reverse OS candidates.",
    ])

    out_txt.write_text("\n".join(lines), encoding="utf-8")

    print("F18A2_ZIP_LOCAL_SOURCE_AUDIT_DONE")
    print("REPORT_JSON=" + str(out_json))
    print("REPORT_TXT=" + str(out_txt))
    print("ZIPS_FOUND_COUNT=" + str(len(zips)))
    print("CLASSIFICATION_COUNTS=" + json.dumps(counts, ensure_ascii=False))
    print("TOP_10:")
    for e in flat_sorted[:10]:
        print(f"- {e.get('classification')} :: {e.get('file')}")

if __name__ == "__main__":
    main()

import argparse
import json
import re
import unicodedata
import zipfile
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET

# --- BRODY_SAFE_HYDRATION_SCAN_V1 ---
# Avoid crashing hydration on local dev folders / broken venv links.
import os as _brody_os

_BRODY_SKIP_DIRS = {
    ".git", ".hg", ".svn",
    ".venv", "venv", "env",
    "node_modules",
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    "dist", "build",
    "site-packages", "lib64", "Lib", "Scripts",
    "_external_benchmarks",
}

def _brody_safe_files(root):
    root = Path(root)
    try:
        if not root.exists():
            return
    except OSError:
        return

    try:
        walker = _brody_os.walk(root, topdown=True, followlinks=False)
        for dirpath, dirnames, filenames in walker:
            # mutate dirnames in-place so os.walk does not descend into skipped dirs
            dirnames[:] = [
                d for d in dirnames
                if d not in _BRODY_SKIP_DIRS and not d.startswith(".venv")
            ]

            try:
                base = Path(dirpath)
            except OSError:
                continue

            for filename in filenames:
                p = base / filename
                try:
                    if p.is_file():
                        yield p
                except OSError:
                    continue
    except OSError:
        return
# --- END BRODY_SAFE_HYDRATION_SCAN_V1 ---



BOUNDARY_FALSE_KEYS = [
    "memory_decision",
    "allowed_to_decide",
    "emits_act",
    "kernel_binding",
    "x108_runtime_binding",
    "x108_merge",
    "kernel_mutation",
    "x108_mutation",
]

READ_EXTS = {
    ".md", ".txt", ".json", ".jsonl", ".py", ".ps1", ".csv",
    ".lean", ".yaml", ".yml", ".toml", ".html", ".css", ".js", ".ts", ".docx"
}

SKIP_DIRS = {
    ".git", "node_modules", ".venv", "__pycache__", ".pytest_cache",
    ".mypy_cache", ".ruff_cache", "dist", "build"
}

BOUNDARY = {
    "readonly": True,
    "memory_authority": False,
    "memory_decision": False,
    "allowed_to_decide": False,
    "emits_act": False,
    "kernel_binding": False,
    "x108_runtime_binding": False,
    "x108_merge": False,
    "kernel_mutation": False,
    "x108_mutation": False,
    "decision_authority": "KX108_ONLY",
    "scope": "BRODY_CONTENT_HYDRATION_READONLY_ONLY",
}


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def clean_text(value, max_chars=1400):
    if not value:
        return ""
    text = re.sub(r"\s+", " ", str(value)).strip()
    return text[:max_chars]


def strip_hash_prefix(name: str):
    return re.sub(r"^[0-9A-Fa-f]{12}_", "", name or "")


def norm(value: str):
    value = unicodedata.normalize("NFKD", value or "")
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value


def read_docx_text(path: Path, max_chars=1400):
    try:
        with zipfile.ZipFile(path) as z:
            xml = z.read("word/document.xml")
        root = ET.fromstring(xml)
        ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
        parts = [node.text for node in root.findall(".//w:t", ns) if node.text]
        return clean_text(" ".join(parts), max_chars=max_chars)
    except Exception:
        return ""


def read_local_excerpt(path_value, max_chars=1400):
    if not path_value:
        return ""

    path = Path(path_value)
    if not path.exists() or not path.is_file():
        return ""

    suffix = path.suffix.lower()

    if suffix == ".docx":
        return read_docx_text(path, max_chars=max_chars)

    if suffix in READ_EXTS:
        try:
            raw = path.read_text(encoding="utf-8", errors="ignore")
            return clean_text(raw, max_chars=max_chars)
        except Exception:
            return ""

    return ""


def default_roots(script_path: Path):
    # ...\obsidia-x108-proofs\periphery\brody_memory_readonly\content_hydration_readonly\script.py
    x108_root = script_path.resolve().parents[3]
    work_root = script_path.resolve().parents[4]

    roots = [
        x108_root,
        work_root / "obsidia-engine-candidate",
        work_root / "_local_audits",
    ]

    return [p for p in roots if p.exists() and p.is_dir()]


def iter_files(roots):
    for root in roots:
        for path in _brody_safe_files(root):
            if not path.is_file():
                continue
            parts = set(path.parts)
            if parts.intersection(SKIP_DIRS):
                continue
            if path.suffix.lower() not in READ_EXTS:
                continue
            yield path


def build_index(roots):
    records = []
    by_name = {}
    by_stripped = {}
    by_norm = {}

    for path in iter_files(roots):
        name = path.name
        stripped = strip_hash_prefix(name)
        rec = {
            "path": str(path),
            "name": name,
            "stripped": stripped,
            "norm_name": norm(name),
            "norm_stripped": norm(stripped),
            "suffix": path.suffix.lower(),
        }
        records.append(rec)

        by_name.setdefault(name.lower(), []).append(rec)
        by_stripped.setdefault(stripped.lower(), []).append(rec)
        by_norm.setdefault(norm(name), []).append(rec)
        by_norm.setdefault(norm(stripped), []).append(rec)

    return {
        "records": records,
        "by_name": by_name,
        "by_stripped": by_stripped,
        "by_norm": by_norm,
    }


def candidate_score(item, rec):
    title = item.get("title") or ""
    source_ref = item.get("source_ref") or ""
    path_value = item.get("path") or ""

    title_base = Path(title).name
    ref_base = Path(source_ref).name

    title_stripped = strip_hash_prefix(title_base)
    ref_stripped = strip_hash_prefix(ref_base)

    n_title = norm(title_base)
    n_title_stripped = norm(title_stripped)
    n_ref = norm(ref_base)
    n_ref_stripped = norm(ref_stripped)

    score = 0

    if rec["name"].lower() == title_base.lower():
        score += 120
    if rec["stripped"].lower() == title_stripped.lower():
        score += 110
    if rec["name"].lower() == ref_base.lower():
        score += 120
    if rec["stripped"].lower() == ref_stripped.lower():
        score += 110

    if rec["norm_name"] in {n_title, n_ref}:
        score += 100
    if rec["norm_stripped"] in {n_title_stripped, n_ref_stripped}:
        score += 95

    if n_title and (n_title in rec["norm_name"] or rec["norm_name"] in n_title):
        score += 50
    if n_ref and (n_ref in rec["norm_name"] or rec["norm_name"] in n_ref):
        score += 50

    if path_value and path_value.lower() in rec["path"].lower():
        score += 30

    # Prefer exact extension match when title/source_ref carries one.
    wanted_suffixes = {
        Path(title_base).suffix.lower(),
        Path(ref_base).suffix.lower(),
    }
    wanted_suffixes.discard("")
    if wanted_suffixes and rec["suffix"] in wanted_suffixes:
        score += 25

    # Prefer source/candidate corpus over local audit duplicates when equal.
    p = rec["path"].lower()
    if "obsidia-engine-candidate" in p:
        score += 10
    if "obsidia-x108-proofs" in p:
        score += 8

    return score


def resolve_item_path(item, index):
    existing = item.get("path") or ""
    if existing and Path(existing).exists() and Path(existing).is_file():
        return existing, "EXISTING_PATH"

    title = item.get("title") or ""
    source_ref = item.get("source_ref") or ""

    title_base = Path(title).name
    ref_base = Path(source_ref).name

    direct_keys = [
        title_base.lower(),
        strip_hash_prefix(title_base).lower(),
        ref_base.lower(),
        strip_hash_prefix(ref_base).lower(),
    ]

    candidates = []

    for key in direct_keys:
        candidates.extend(index["by_name"].get(key, []))
        candidates.extend(index["by_stripped"].get(key, []))
        candidates.extend(index["by_norm"].get(norm(key), []))

    if not candidates:
        candidates = index["records"]

    scored = []
    seen = set()

    for rec in candidates:
        path = rec["path"]
        if path in seen:
            continue
        seen.add(path)
        score = candidate_score(item, rec)
        if score > 0:
            scored.append((score, len(path), rec))

    if not scored:
        return "", "UNRESOLVED"

    scored.sort(key=lambda x: (-x[0], x[1], x[2]["path"]))
    return scored[0][2]["path"], "RESOLVED_BY_LOCAL_INDEX"


def validate_packet(packet):
    if packet.get("status") != "BRODY_CONTEXT_PACKET_QUERY_READONLY_PASS":
        raise RuntimeError(f"BAD_PACKET_STATUS={packet.get('status')}")

    for key in BOUNDARY_FALSE_KEYS:
        if packet.get(key) is not False:
            raise RuntimeError(f"BOUNDARY_VIOLATION_{key}={packet.get(key)}")

    if packet.get("decision_authority") != "KX108_ONLY":
        raise RuntimeError(f"BAD_DECISION_AUTHORITY={packet.get('decision_authority')}")


def hydrate_packet(packet, roots, max_chars=1400):
    validate_packet(packet)

    out = deepcopy(packet)
    index = build_index(roots)

    items = out.get("context_packet", {}).get("items", []) or []

    resolved_count = 0
    hydrated_count = 0
    unresolved_count = 0
    already_path_count = 0
    already_excerpt_count = 0

    for item in items:
        original_path = item.get("path") or ""
        original_excerpt = item.get("excerpt") or ""

        resolved_path, method = resolve_item_path(item, index)

        if original_path and Path(original_path).exists():
            already_path_count += 1

        if resolved_path and not original_path:
            item["path"] = resolved_path
            item["source_ref"] = resolved_path
            resolved_count += 1

        if original_excerpt:
            already_excerpt_count += 1
            excerpt = clean_text(original_excerpt, max_chars=max_chars)
        else:
            excerpt = read_local_excerpt(item.get("path") or resolved_path, max_chars=max_chars)

        if excerpt and not original_excerpt:
            hydrated_count += 1

        if not item.get("path"):
            unresolved_count += 1

        item["excerpt"] = excerpt
        item["hydrated"] = bool(excerpt)
        item["resolved_path"] = item.get("path") or ""
        item["resolution_method"] = method
        item["hydration_readonly"] = True
        item["memory_decision"] = False
        item["allowed_to_decide"] = False
        item["emits_act"] = False
        item["kernel_mutation"] = False
        item["decision_authority"] = "KX108_ONLY"

    out["hydration_status"] = "BRODY_CONTENT_HYDRATION_READONLY_PASS"
    out["hydrated_by"] = "BRODY_CONTENT_HYDRATION_READONLY_V1"
    out["hydration_report"] = {
        "status": "BRODY_CONTENT_HYDRATION_READONLY_PASS",
        "created_at": now_iso(),
        "query": out.get("query"),
        "roots": [str(p) for p in roots],
        "indexed_file_count": len(index["records"]),
        "items_count": len(items),
        "already_path_count": already_path_count,
        "already_excerpt_count": already_excerpt_count,
        "resolved_path_count": resolved_count,
        "hydrated_excerpt_count": hydrated_count,
        "unresolved_path_count": unresolved_count,
        "readonly": True,
        "memory_decision": False,
        "allowed_to_decide": False,
        "emits_act": False,
        "decision_authority": "KX108_ONLY",
        "kernel_mutation": False,
        "x108_runtime_binding": False,
        "x108_merge": False,
        "scope": "BRODY_CONTENT_HYDRATION_READONLY_ONLY",
    }

    # Keep query status unchanged so existing consumer accepts hydrated packets.
    out["status"] = "BRODY_CONTEXT_PACKET_QUERY_READONLY_PASS"

    for k, v in BOUNDARY.items():
        out[k] = v

    return out


def packet_to_markdown(packet):
    report = packet.get("hydration_report", {})
    lines = []
    lines.append("# BRODY CONTENT HYDRATION — READONLY")
    lines.append("")
    lines.append(f"- status: {packet.get('hydration_status')}")
    lines.append(f"- query: {packet.get('query')}")
    lines.append(f"- indexed_file_count: {report.get('indexed_file_count')}")
    lines.append(f"- resolved_path_count: {report.get('resolved_path_count')}")
    lines.append(f"- hydrated_excerpt_count: {report.get('hydrated_excerpt_count')}")
    lines.append(f"- unresolved_path_count: {report.get('unresolved_path_count')}")
    lines.append("- memory_decision: false")
    lines.append("- emits_act: false")
    lines.append("- kernel_mutation: false")
    lines.append("- decision_authority: KX108_ONLY")
    lines.append("")
    lines.append("## Items")

    for item in packet.get("context_packet", {}).get("items", []):
        lines.append("")
        lines.append(f"### {item.get('rank')}. {item.get('title')}")
        lines.append(f"- score: {item.get('score')}")
        lines.append(f"- resolved_path: {item.get('resolved_path')}")
        lines.append(f"- resolution_method: {item.get('resolution_method')}")
        lines.append(f"- hydrated: {str(item.get('hydrated')).lower()}")
        if item.get("excerpt"):
            lines.append("")
            lines.append(clean_text(item.get("excerpt"), max_chars=900))

    lines.append("")
    lines.append("## Boundary")
    lines.append("Hydration resolves local readable material only. It does not decide, does not emit ACT, and does not mutate X108.")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet-json", required=True)
    parser.add_argument("--out-json")
    parser.add_argument("--out-md")
    parser.add_argument("--root", action="append", default=[])
    parser.add_argument("--max-chars", type=int, default=1400)
    args = parser.parse_args()

    packet_path = Path(args.packet_json)
    if not packet_path.exists():
        raise RuntimeError(f"MISSING_PACKET_JSON={args.packet_json}")

    packet = json.loads(packet_path.read_text(encoding="utf-8"))

    roots = [Path(p) for p in args.root if Path(p).exists() and Path(p).is_dir()]
    if not roots:
        roots = default_roots(Path(__file__))

    hydrated = hydrate_packet(packet, roots=roots, max_chars=args.max_chars)

    if args.out_json:
        out = Path(args.out_json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(hydrated, indent=2, ensure_ascii=False), encoding="utf-8")

    if args.out_md:
        out = Path(args.out_md)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(packet_to_markdown(hydrated), encoding="utf-8")

    print(json.dumps(hydrated, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

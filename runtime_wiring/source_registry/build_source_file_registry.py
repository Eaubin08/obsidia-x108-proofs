# runtime_wiring/source_registry/build_source_file_registry.py
# Build the source file registry from existing CSV inventories.
# NO zip extraction. NO source pack import. NO runtime activation.
# Reads _source_discovery/ CSV files — read-only.
# Writes: source_file_registry.json, source_file_registry.csv, source_registry_summary.json
# Run: python runtime_wiring/source_registry/build_source_file_registry.py

from __future__ import annotations
import csv
import hashlib
import json
import pathlib
import sys
from typing import Any, Dict, List, Optional, Tuple

# Path setup
_THIS_FILE = pathlib.Path(__file__).resolve()
_REGISTRY_DIR = _THIS_FILE.parent          # runtime_wiring/source_registry/
_REPO_ROOT = _REGISTRY_DIR.parent.parent   # repo root (contains runtime_wiring/)
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from runtime_wiring.source_registry.registry_types import (
    DO_NOT_IMPORT_DECISIONS,
    SourceFileRegistryEntry,
)
from runtime_wiring.source_registry.adapter_target_map import (
    ADAPTER_TARGET_MAP,
    detect_family_from_zip,
    get_adapter_map,
)

# ── Source inventory CSV paths (use most recent / canon-repair versions) ──────
_SOURCE_INVENTORIES: List[Tuple[str, pathlib.Path]] = [
    (
        "COGNITIVE_REINTEGRATION",
        _REPO_ROOT / "_source_discovery/F07_COGNITIVE_IMPORT_AUDIT_20260602_154536/F07_COGNITIVE_ZIP_INTERNAL_INVENTORY.csv",
    ),
    (
        "RSSI_RGPD",
        _REPO_ROOT / "_source_discovery/F03_RSSI_RGPD_CANON_REPAIR_20260602_155630/F03_RSSI_RGPD_ZIP_INTERNAL_INVENTORY_STRICT.csv",
    ),
    (
        "ATLAS",
        _REPO_ROOT / "_source_discovery/F06_ATLAS_CANON_REPAIR_20260602_160517/F06_ATLAS_ZIP_INTERNAL_INVENTORY_CANON_DEDUPED.csv",
    ),
    (
        "COMPLIANCE_DATA_GOVERNANCE",
        _REPO_ROOT / "_source_discovery/F10_COMPLIANCE_DATA_GOVERNANCE_IMPORT_AUDIT_20260602_160941/F10_COMPLIANCE_DATA_GOVERNANCE_ZIP_INTERNAL_INVENTORY_DEDUPED.csv",
    ),
]

_OUT_JSON = _REGISTRY_DIR / "source_file_registry.json"
_OUT_CSV = _REGISTRY_DIR / "source_file_registry.csv"
_OUT_SUMMARY = _REGISTRY_DIR / "source_registry_summary.json"

CSV_FIELDNAMES = [
    "registry_id", "source_family", "source_zip", "internal_path", "file_name",
    "extension", "size_bytes", "recommended_decision", "boundary_required",
    "claim_scope", "quarantine_status", "adapter_target", "packet_target",
    "runtime_allowed_now", "emits_act", "emits_decision", "source_status", "notes",
]


def _make_registry_id(
    source_family: str, source_zip: str, internal_path: str,
    size_bytes: int, recommended_decision: str,
) -> str:
    content = f"{source_family}|{source_zip}|{internal_path}|{size_bytes}|{recommended_decision}"
    return hashlib.sha256(content.encode()).hexdigest()[:24]


def _quarantine_status(
    recommended_decision: str, extension: str, internal_path: str
) -> str:
    ext_lower = extension.lower()
    path_lower = internal_path.lower()

    if ext_lower == ".py":
        return "DO_NOT_IMPORT_RUNTIME"
    if recommended_decision == "DO_NOT_IMPORT_RUNTIME":
        return "DO_NOT_IMPORT_RUNTIME"
    if recommended_decision == "ARCHIVE_ONLY":
        return "ARCHIVE_ONLY"
    if recommended_decision == "KEEP_QUARANTINE":
        return "QUARANTINE"
    if recommended_decision == "KEEP_SOURCE_ONLY":
        return "ARCHIVE_ONLY"
    if any(tok in path_lower for tok in [".pytest_cache", "__pycache__", "/.cache/", "cachedir"]):
        return "QUARANTINE_CACHE"
    if "runtime_freeze" in path_lower:
        return "QUARANTINE"
    return "CLEAR"


def _build_entry(row: Dict[str, str], source_family: str) -> Optional[SourceFileRegistryEntry]:
    try:
        source_zip = row.get("source_zip", "").strip()
        internal_path = row.get("internal_path", "").strip()
        file_name = row.get("file_name", "").strip()
        extension = row.get("extension", "").strip()
        size_bytes_str = row.get("size_bytes", "0").strip()
        recommended_decision = row.get("recommended_decision", "UNKNOWN").strip()
        boundary_required = row.get("boundary_required", "UNKNOWN").strip()
        notes_raw = row.get("notes", "").strip()

        if not source_zip or not internal_path:
            return None

        try:
            size_bytes = int(size_bytes_str)
        except (ValueError, TypeError):
            size_bytes = 0

        amap = get_adapter_map(source_family)
        claim_scope = amap["claim_scope"]
        adapter_target = amap["adapter_target"]
        packet_target = amap["packet_target"]
        source_status = amap["source_status"]

        q_status = _quarantine_status(recommended_decision, extension, internal_path)

        registry_id = _make_registry_id(
            source_family, source_zip, internal_path, size_bytes, recommended_decision
        )

        # Enforce DO_NOT_IMPORT_RUNTIME on .py files
        if extension.lower() == ".py" and "DO_NOT_IMPORT_RUNTIME" not in recommended_decision:
            recommended_decision = "DO_NOT_IMPORT_RUNTIME"

        notes = f"{source_family}|{notes_raw}" if notes_raw else source_family

        entry = SourceFileRegistryEntry(
            registry_id=registry_id,
            source_family=source_family,
            source_zip=source_zip,
            internal_path=internal_path,
            file_name=file_name,
            extension=extension,
            size_bytes=size_bytes,
            recommended_decision=recommended_decision,
            boundary_required=boundary_required,
            claim_scope=claim_scope,
            quarantine_status=q_status,
            adapter_target=adapter_target,
            packet_target=packet_target,
            runtime_allowed_now=False,
            emits_act=False,
            emits_decision=False,
            source_status=source_status,
            notes=notes,
        )
        entry.validate_invariants()
        return entry

    except Exception as exc:
        print(f"  [SKIP] {row.get('internal_path','?')}: {exc}", file=sys.stderr)
        return None


def build_registry() -> List[SourceFileRegistryEntry]:
    all_entries: List[SourceFileRegistryEntry] = []
    seen_ids: set = set()

    for source_family, csv_path in _SOURCE_INVENTORIES:
        if not csv_path.is_file():
            print(f"  [BLOCK] Inventory not found: {csv_path}", file=sys.stderr)
            raise FileNotFoundError(f"FAIL_CLOSED: inventory missing: {csv_path}")

        print(f"  Loading {source_family} from {csv_path.name}...")
        family_count = 0
        dup_count = 0

        with open(csv_path, encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                entry = _build_entry(row, source_family)
                if entry is None:
                    continue
                if entry.registry_id in seen_ids:
                    dup_count += 1
                    continue
                seen_ids.add(entry.registry_id)
                all_entries.append(entry)
                family_count += 1

        print(f"    -> {family_count} entries loaded, {dup_count} duplicates skipped")

    return all_entries


def write_registry_json(entries: List[SourceFileRegistryEntry]) -> None:
    data = [e.to_dict() for e in entries]
    _OUT_JSON.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"  Written: {_OUT_JSON.name} ({_OUT_JSON.stat().st_size:,} bytes)")


def write_registry_csv(entries: List[SourceFileRegistryEntry]) -> None:
    with open(_OUT_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES)
        writer.writeheader()
        for entry in entries:
            writer.writerow(entry.to_csv_row())
    print(f"  Written: {_OUT_CSV.name} ({_OUT_CSV.stat().st_size:,} bytes)")


def build_summary(entries: List[SourceFileRegistryEntry]) -> Dict[str, Any]:
    by_family: Dict[str, int] = {}
    by_adapter: Dict[str, int] = {}
    by_decision: Dict[str, int] = {}
    by_quarantine: Dict[str, int] = {}
    py_count = 0
    runtime_allowed_true = 0
    emits_act_true = 0
    emits_decision_true = 0

    for e in entries:
        by_family[e.source_family] = by_family.get(e.source_family, 0) + 1
        by_adapter[e.adapter_target] = by_adapter.get(e.adapter_target, 0) + 1
        by_decision[e.recommended_decision] = by_decision.get(e.recommended_decision, 0) + 1
        by_quarantine[e.quarantine_status] = by_quarantine.get(e.quarantine_status, 0) + 1
        if e.extension.lower() == ".py":
            py_count += 1
        if e.runtime_allowed_now:
            runtime_allowed_true += 1
        if e.emits_act:
            emits_act_true += 1
        if e.emits_decision:
            emits_decision_true += 1

    return {
        "registry_status": "P8D_P9A_SOURCE_REGISTRY_BUILT",
        "decision_authority": "KX108_ONLY",
        "zip_extraction": False,
        "source_pack_import": False,
        "runtime_activation": False,
        "total_entries": len(entries),
        "count_by_family": by_family,
        "count_by_adapter_target": by_adapter,
        "count_by_recommended_decision": by_decision,
        "count_by_quarantine_status": by_quarantine,
        "py_files_count": py_count,
        "py_files_all_do_not_import": py_count == 0 or by_decision.get("DO_NOT_IMPORT_RUNTIME", 0) >= py_count,
        "runtime_allowed_now_true_count": runtime_allowed_true,
        "emits_act_true_count": emits_act_true,
        "emits_decision_true_count": emits_decision_true,
        "safety_invariants_ok": (
            runtime_allowed_true == 0 and emits_act_true == 0 and emits_decision_true == 0
        ),
        "inventories_used": [
            {"family": fam, "csv": str(p.name)} for fam, p in _SOURCE_INVENTORIES
        ],
    }


def write_summary(summary: Dict[str, Any]) -> None:
    _OUT_SUMMARY.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"  Written: {_OUT_SUMMARY.name} ({_OUT_SUMMARY.stat().st_size:,} bytes)")


def main() -> None:
    print("=" * 70)
    print("P8D/P9A SOURCE FILE REGISTRY BUILD")
    print("NO ZIP EXTRACTION / NO SOURCE PACK IMPORT / NO RUNTIME ACTIVATION")
    print("=" * 70)
    print()

    print("[1/4] Loading source inventories...")
    entries = build_registry()
    print(f"      Total entries after dedup: {len(entries)}")
    print()

    print("[2/4] Writing registry JSON...")
    write_registry_json(entries)
    print()

    print("[3/4] Writing registry CSV...")
    write_registry_csv(entries)
    print()

    print("[4/4] Building and writing summary...")
    summary = build_summary(entries)
    write_summary(summary)
    print()

    print("=" * 70)
    print("SUMMARY")
    print(f"  Total entries: {summary['total_entries']}")
    for fam, cnt in summary["count_by_family"].items():
        print(f"  {fam}: {cnt}")
    print(f"  .py files (DO_NOT_IMPORT_RUNTIME): {summary['py_files_count']}")
    print(f"  runtime_allowed_now=True: {summary['runtime_allowed_now_true_count']}")
    print(f"  emits_act=True: {summary['emits_act_true_count']}")
    print(f"  emits_decision=True: {summary['emits_decision_true_count']}")
    print(f"  safety_invariants_ok: {summary['safety_invariants_ok']}")
    print("=" * 70)
    print()
    print("P8D_P9A_SOURCE_PACK_FILE_REGISTRY_BRIDGE_READY")


if __name__ == "__main__":
    main()

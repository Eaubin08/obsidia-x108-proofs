"""
Foundation A — Brody Project Memory Adapter
=============================================
Synthesizes project_memory_snapshot from existing local sources:
  - Graphiti readonly index (JSON snapshot when Neo4j offline)
  - Memory candidate ledger (JSONL)
  - Freeze metrics snapshot (for context_packet_chain status)
  - CURRENT_BRODY_*.txt pointers (for module availability)

No invention — everything sourced from freeze files, indexes, and ledgers.
Boundary: readonly, KX108_ONLY, no write.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_project_memory_snapshot(
    workspace_root: Path | None = None,
    freeze_metrics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Build project_memory_snapshot from existing local sources.

    Sources checked:
      1. Graphiti readonly index V2 (JSON snapshot)
      2. Memory candidate ledger (JSONL)
      3. Freeze metrics (context_packet_chain availability)
      4. CURRENT_BRODY pointer files for module discovery

    Returns dict with sections: graphiti_index, candidate_ledger,
    module_availability, brody_memory_doc_status, project_context_summary.
    """
    workspace = workspace_root or Path(__file__).resolve().parents[2]

    # ── 1. Graphiti Readonly Index — prefer JSONL (has text_excerpt) ─────────
    graphiti_base = (
        workspace / "_graphiti_readonly_indexes"
        / "GRAPHITI_READONLY_INDEX_V2_FUSION_20260512_224854"
    )
    jsonl_path = graphiti_base / "graphiti_readonly_records_v2.jsonl"
    json_path = graphiti_base / "graphiti_readonly_index_v2.json"

    graphiti_index_found = jsonl_path.exists() or json_path.exists()
    graphiti_index_item_count = 0
    text_excerpt_count = 0
    graphiti_tags_sample: list[str] = []
    source_file_used = "NOT_FOUND"

    if jsonl_path.exists():
        # Use memory chain adapter's cache to avoid re-reading the JSONL
        try:
            from apps.obsidia_api.brody_memory_response_chain_adapter import (
                _load_local_graphiti_index, _GRAPHITI_INDEX_CACHE
            )
            cache_key = str(workspace.resolve())
            if cache_key in _GRAPHITI_INDEX_CACHE:
                records = _GRAPHITI_INDEX_CACHE[cache_key]
            else:
                records = _load_local_graphiti_index(workspace)
            graphiti_index_item_count = len(records)
            text_excerpt_count = sum(1 for r in records if r.get("text_excerpt", "").strip())
            for rec in records[:5]:
                tags = rec.get("tags", [])
                graphiti_tags_sample.extend(tags[:3])
            source_file_used = str(jsonl_path)
        except Exception:
            graphiti_index_item_count = 0

    if graphiti_index_item_count == 0 and json_path.exists():
        try:
            raw = json_path.read_text(encoding="utf-8")
            index_data = json.loads(raw)
            if isinstance(index_data, list):
                graphiti_index_item_count = len(index_data)
                for item in index_data[:5]:
                    if isinstance(item, dict):
                        graphiti_tags_sample.extend(item.get("tags", [])[:3])
            elif isinstance(index_data, dict):
                items = index_data.get("records") or index_data.get("items") or index_data.get("entries") or []
                graphiti_index_item_count = len(items)
                for item in items[:5]:
                    if isinstance(item, dict):
                        graphiti_tags_sample.extend(item.get("tags", [])[:3])
            source_file_used = str(json_path)
        except Exception:
            pass

    # ── 2. Memory Candidate Ledger ────────────────────────────────────────
    candidate_ledger_path = workspace / "_local_audits" / "memory_candidate_ledger.jsonl"
    candidate_ledger_found = candidate_ledger_path.exists()
    candidate_count = 0

    if candidate_ledger_found:
        try:
            lines = candidate_ledger_path.read_text(encoding="utf-8").strip().splitlines()
            candidate_count = len([l for l in lines if l.strip()])
        except Exception:
            candidate_ledger_found = False

    # ── 3. Module availability from freeze pointers ───────────────────────
    module_status: dict[str, bool] = {}
    for pattern, name in [
        ("CONTEXT_PACKET_QUERY", "context_packet_query"),
        ("CONTENT_HYDRATION", "content_hydration"),
        ("LOCAL_RESPONSE_ENGINE", "local_response_engine"),
        ("CONTEXT_PACKET_CONSUMER", "context_packet_consumer"),
        ("AUTO_TRIAGE", "auto_triage"),
        ("GRAPHITI_CANDIDATE_REVIEW", "graphiti_review_gate"),
        ("PROJECT_INTAKE_CAPTURE", "project_intake_capture"),
    ]:
        ptr_files = list(workspace.glob(f"CURRENT_BRODY_{pattern}*.txt"))
        module_status[name] = len(ptr_files) > 0

    # ── 4. BrodyMemoryDoc status from freeze metrics ──────────────────────
    chain = (freeze_metrics or {}).get("context_packet_chain", {})
    brody_memory_doc_available = chain.get("status") == "CHAIN_PASS"

    # ── 5. Graphiti V20 status ────────────────────────────────────────────
    graphiti_v20_found = graphiti_index_found

    # ── 6. Project context summary ────────────────────────────────────────
    if graphiti_index_item_count > 0 and brody_memory_doc_available:
        contextual_material_status = "HAS_PROJECT_MEMORY"
    elif graphiti_index_item_count > 0 or candidate_count > 0:
        contextual_material_status = "PARTIAL_PROJECT_MEMORY"
    else:
        contextual_material_status = "NO_PROJECT_MEMORY"

    # Local freeze pointer count
    freeze_pointers_count = len(list(workspace.glob("CURRENT_BRODY_*.txt")))

    missing_links: list[str] = []
    if not brody_memory_doc_available:
        missing_links.append("brody_memory_doc_live_not_connected")
    if not module_status.get("project_intake_capture"):
        missing_links.append("project_intake_capture_not_found")
    if graphiti_index_item_count == 0:
        missing_links.append("graphiti_index_empty_or_unparseable")

    return {
        "source_type": "LOCAL_EXISTING_SOURCES",
        "source_mode": "PROJECT_MEMORY_EXISTING_ONLY",
        "status": "BRODY_PROJECT_MEMORY_SOURCE_MAP_PASS",
        "created_at": _now(),
        "context_packet_query_found": module_status.get("context_packet_query", False),
        "content_hydration_found": module_status.get("content_hydration", False),
        "local_response_engine_found": module_status.get("local_response_engine", False),
        "brody_memory_doc_available": brody_memory_doc_available,
        "graphiti_v20_found": graphiti_v20_found,
        "graphiti_index_item_count": graphiti_index_item_count,
        "local_records_count": graphiti_index_item_count,
        "text_excerpt_records_count": text_excerpt_count,
        "usable_material": text_excerpt_count > 0,
        "cache_enabled": True,
        "source_file_used": source_file_used,
        "candidate_ledger_found": candidate_ledger_found,
        "candidate_ledger_count": candidate_count,
        "auto_triage_found": module_status.get("auto_triage", False),
        "contextual_material_status": contextual_material_status,
        "graphiti_live": brody_memory_doc_available,
        "local_freeze_available": graphiti_index_item_count > 0,
        "local_index_item_count": graphiti_index_item_count,
        "freeze_pointers_count": freeze_pointers_count,
        "top_context_tags": graphiti_tags_sample[:10],
        "project_memory_used_by_api": False,  # Set by API route
        "missing_links": missing_links,
        "source_files": [
            source_file_used,
            str(candidate_ledger_path) if candidate_ledger_found else "NOT_FOUND",
        ],
        "readonly": True,
        "memory_write": False,
        "graphiti_write": False,
        "neo4j_write": False,
        "emits_act": False,
        "emits_verdict": False,
        "kernel_mutation": False,
        "decision_authority": "KX108_ONLY",
    }

"""
Brody Memory Response Chain Adapter
=====================================
Wraps the real memory→response chain in a single callable function.

Chain:
  1. query_neo4j(semantic_query, limit)
     → context_packet with BrodyMemoryDoc items
  2. hydrate_packet(packet, roots)
     → resolves local file paths, reads excerpts (.md, .txt, .docx)
  3. local_response_engine.build_response(hydrated_packet)
     → produces structured response_md with material_quality

The chain sources from EXISTING freeze-validated modules:
  - periphery/brody_memory_readonly/context_packet_query_readonly/
  - periphery/brody_memory_readonly/content_hydration_readonly/
  - periphery/brody_memory_readonly/local_response_engine_readonly/

All three are freeze-sourced, READY status, KX108_ONLY.

Boundary: readonly, no Neo4j write, no Graphiti write, KX108_ONLY.
"""
from __future__ import annotations

import importlib.util
import os
import socket
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Module-level cache so the JSONL index is only read once per process
_GRAPHITI_INDEX_CACHE: dict[str, list[dict]] = {}

# Graphiti V20 frozen HTTP fallback bounds.
# A closed sidecar must never impose a per-query HTTP timeout cascade.
_GRAPHITI_HTTP_HOST = "127.0.0.1"
_GRAPHITI_HTTP_PORT = 8011
_GRAPHITI_HTTP_PROBE_TIMEOUT_SECONDS = 0.20
_GRAPHITI_HTTP_REQUEST_TIMEOUT_SECONDS = 1.00
_GRAPHITI_HTTP_LADDER_BUDGET_SECONDS = 2.00

# ── Hard-coded boundary ──────────────────────────────────────────────────────
MEMORY_CHAIN_BOUNDARY: dict[str, Any] = {
    "readonly": True,
    "memory_write": False,
    "graphiti_write": False,
    "neo4j_write": False,
    "emits_act": False,
    "emits_verdict": False,
    "kernel_mutation": False,
    "decision_authority": "KX108_ONLY",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _neo4j_available() -> tuple[bool, str]:
    """Check if Neo4j is reachable and credentials are set."""
    password = os.environ.get("NEO4J_PASSWORD", "")
    if not password:
        return False, "NEO4J_PASSWORD_NOT_SET"

    try:
        s = socket.socket()
        s.settimeout(1.5)
        s.connect(("127.0.0.1", 7688))
        s.close()
        return True, "NEO4J_REACHABLE"
    except Exception:
        return False, "NEO4J_PORT_7688_CLOSED_OR_UNREACHABLE"


def _import_module(module_path: Path) -> Any | None:
    """Dynamically import a Python module from a file path."""
    if not module_path.exists():
        return None
    try:
        spec = importlib.util.spec_from_file_location(
            module_path.stem, str(module_path)
        )
        if spec is None or spec.loader is None:
            return None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except Exception:
        return None


def _default_roots(workspace: Path) -> list[Path]:
    """Build default search roots for hydration."""
    parent = workspace.parent  # obsidia-engine-proof-core
    candidates = [
        workspace,
        parent / "obsidia-engine-candidate",
        parent / "_local_audits",
    ]
    return [p for p in candidates if p.exists() and p.is_dir()]


def _load_local_graphiti_index(workspace: Path) -> list[dict]:
    """Load the Graphiti JSONL records (have text_excerpt), fall back to JSON metadata only."""
    import json as _json
    cache_key = str(workspace.resolve())
    if cache_key in _GRAPHITI_INDEX_CACHE:
        return _GRAPHITI_INDEX_CACHE[cache_key]
    base = (
        workspace
        / "_graphiti_readonly_indexes"
        / "GRAPHITI_READONLY_INDEX_V2_FUSION_20260512_224854"
    )
    jsonl_path = base / "graphiti_readonly_records_v2.jsonl"
    json_path = base / "graphiti_readonly_index_v2.json"

    # Prefer JSONL — contains text_excerpt (the real content Neo4j served as text_preview)
    if jsonl_path.exists():
        try:
            records = []
            for raw_line in jsonl_path.read_text(encoding="utf-8", errors="ignore").splitlines():
                raw_line = raw_line.strip()
                if not raw_line:
                    continue
                outer = _json.loads(raw_line)
                if not isinstance(outer, dict):
                    continue
                # The `text` field is JSON-encoded and contains text_excerpt + normalized_md_path
                inner: dict = {}
                raw_text = outer.get("text")
                if isinstance(raw_text, str):
                    try:
                        parsed = _json.loads(raw_text)
                        if isinstance(parsed, dict):
                            inner = parsed
                    except Exception:
                        pass
                elif isinstance(raw_text, dict):
                    inner = raw_text

                records.append({
                    "id": outer.get("id") or inner.get("id", ""),
                    "title": inner.get("title") or outer.get("title") or outer.get("id", ""),
                    "path": inner.get("source_original_path") or inner.get("normalized_md_path") or outer.get("path") or "",
                    "normalized_md_path": inner.get("normalized_md_path") or "",
                    "tags": outer.get("tags") or inner.get("tags") or [],
                    "source_kind": outer.get("source_kind", "LOCAL_GRAPHITI_JSONL"),
                    "text_excerpt": inner.get("text_excerpt") or "",
                })
            if records:
                _GRAPHITI_INDEX_CACHE[cache_key] = records
                return records
        except Exception:
            pass

    # Fallback: metadata-only JSON
    if json_path.exists():
        try:
            data = _json.loads(json_path.read_text(encoding="utf-8"))
            if isinstance(data, list):
                _GRAPHITI_INDEX_CACHE[cache_key] = data
                return data
            if isinstance(data, dict):
                result = data.get("records") or data.get("items") or data.get("entries") or []
                _GRAPHITI_INDEX_CACHE[cache_key] = result
                return result
        except Exception:
            pass
    return []


def _safe_excerpt(text: str, max_chars: int = 900) -> str:
    import re as _re
    if not text:
        return ""
    return _re.sub(r"\s+", " ", str(text)).strip()[:max_chars]


def _query_local_index(query: str, records: list[dict], limit: int = 8) -> list[dict]:
    """
    Query local Graphiti JSONL records using the same scoring logic as the Neo4j Cypher query.
    Items include text_excerpt so the consumer/engine produce real responses.
    """
    import re as _re
    q_norm = _re.sub(r"\s+", " ", (query or "").strip().lower())
    q_underscore = q_norm.replace(" ", "_")

    matched: list[tuple[int, dict]] = []
    for rec in records:
        title = (rec.get("title") or "").lower()
        path = (rec.get("path") or "").lower()
        body = (rec.get("text_excerpt") or "").lower()
        tags = [str(t).lower() for t in (rec.get("tags") or [])]
        score = 0
        if q_norm in title:
            score += 160
        if q_norm in path:
            score += 150
        if q_norm in body:
            score += 120
        if q_underscore in tags:
            score += 130
        if any(q_norm == t for t in tags):
            score += 130
        if any(q_norm in t for t in tags):
            score += 100
        if any(q_underscore in t for t in tags):
            score += 100
        if score > 0:
            matched.append((score, rec))

    matched.sort(key=lambda x: -x[0])
    items = []
    for i, (score, rec) in enumerate(matched[:limit], 1):
        tags_list = rec.get("tags") or []
        excerpt = _safe_excerpt(rec.get("text_excerpt") or "", max_chars=900)
        items.append({
            "rank": i,
            "id": rec.get("id", f"local_{i}"),
            "title": rec.get("title", ""),
            "source": rec.get("source_kind", "LOCAL_GRAPHITI_JSONL"),
            "path": rec.get("normalized_md_path") or rec.get("path") or "",
            "tags": tags_list,
            "score": score,
            "excerpt": excerpt,
            "source_ref": rec.get("path") or rec.get("title") or rec.get("id", ""),
        })
    return items



def _first_text_value(obj: dict[str, Any], keys: list[str]) -> str:
    for key in keys:
        value = obj.get(key)
        if value is None:
            continue
        if isinstance(value, (str, int, float, bool)):
            text = _safe_excerpt(str(value), max_chars=1200)
            if text:
                return text
        if isinstance(value, dict):
            text = _safe_excerpt(" ".join(f"{k}: {v}" for k, v in value.items() if isinstance(v, (str, int, float, bool))), max_chars=1200)
            if text:
                return text
    return ""


def _extract_graphiti_http_list(obj: Any) -> list[dict]:
    """Extract result items from frozen Graphiti HTTP responses without assuming one schema."""
    if isinstance(obj, list):
        return [x for x in obj if isinstance(x, dict)]

    if not isinstance(obj, dict):
        return []

    for key in ("items", "results", "matches", "context_items", "entities", "nodes", "selected_items"):
        value = obj.get(key)
        if isinstance(value, list):
            dicts = [x for x in value if isinstance(x, dict)]
            if dicts:
                return dicts

    # One-level nested fallbacks, defensive only.
    for value in obj.values():
        if isinstance(value, dict):
            nested = _extract_graphiti_http_list(value)
            if nested:
                return nested

    return []


def _normalize_graphiti_http_item(raw: dict[str, Any], rank: int, query: str, source: str) -> dict[str, Any]:
    title = _first_text_value(raw, ["title", "name", "label", "entity", "id", "source_ref"]) or f"Graphiti item {rank}"

    material = _first_text_value(raw, [
        "excerpt",
        "text_excerpt",
        "text_preview",
        "preview",
        "summary",
        "description",
        "body",
        "content",
        "text",
        "material",
        "hydrated_excerpt",
    ])

    if not material:
        scalar_pairs: list[str] = []
        for k, v in raw.items():
            if k in ("embedding", "vector"):
                continue
            if isinstance(v, (str, int, float, bool)) and str(v).strip():
                scalar_pairs.append(f"{k}={v}")
        material = _safe_excerpt("; ".join(scalar_pairs), max_chars=1000)

    tags = raw.get("tags")
    if not isinstance(tags, list):
        tags = []
    for k in ("type", "domain", "kind", "label", "source"):
        v = raw.get(k)
        if isinstance(v, str) and v and v not in tags:
            tags.append(v)

    return {
        "rank": rank,
        "id": raw.get("id") or raw.get("uuid") or raw.get("name") or f"graphiti_http_{rank}",
        "title": title,
        "source": source,
        "path": raw.get("path") or raw.get("source_path") or raw.get("source_ref") or "",
        "tags": tags,
        "score": raw.get("score") or raw.get("relevance") or raw.get("rank") or (1000 - rank),
        "excerpt": material,
        "summary": material,
        "source_ref": raw.get("source_ref") or raw.get("path") or raw.get("id") or title,
        "readonly": True,
        "decision_authority": "KX108_ONLY",
        "memory_write": False,
        "graphiti_write": False,
        "kernel_mutation": False,
    }


def _graphiti_v20_frozen_http_available() -> bool:
    """Fast TCP probe before entering the readonly HTTP fallback ladder."""
    try:
        with socket.create_connection(
            (_GRAPHITI_HTTP_HOST, _GRAPHITI_HTTP_PORT),
            timeout=_GRAPHITI_HTTP_PROBE_TIMEOUT_SECONDS,
        ):
            return True
    except OSError:
        return False


def _query_graphiti_frozen_http_once(
    query: str,
    limit: int = 8,
    *,
    deadline: float | None = None,
) -> list[dict]:
    """Read-only Graphiti request bounded by a shared ladder deadline."""
    import json as _json
    import urllib.parse as _parse
    import urllib.request as _request

    if not query:
        return []

    encoded = _parse.quote(query)
    endpoints = [
        (
            "GRAPHITI_V20_FROZEN_CONTEXT_HTTP",
            f"http://{_GRAPHITI_HTTP_HOST}:{_GRAPHITI_HTTP_PORT}/graph/v20/frozen/context?q={encoded}&limit={limit}",
        ),
        (
            "GRAPHITI_V20_FROZEN_SEARCH_HTTP",
            f"http://{_GRAPHITI_HTTP_HOST}:{_GRAPHITI_HTTP_PORT}/graph/v20/frozen/search?q={encoded}&limit={limit}",
        ),
    ]

    for source, url in endpoints:
        remaining = (
            None
            if deadline is None
            else deadline - time.monotonic()
        )

        if remaining is not None and remaining <= 0:
            break

        request_timeout = _GRAPHITI_HTTP_REQUEST_TIMEOUT_SECONDS

        if remaining is not None:
            request_timeout = min(
                request_timeout,
                remaining,
            )

        if request_timeout <= 0:
            break

        try:
            with _request.urlopen(
                url,
                timeout=max(0.05, request_timeout),
            ) as resp:
                data = _json.loads(
                    resp.read().decode(
                        "utf-8",
                        errors="replace",
                    )
                )

            raw_items = _extract_graphiti_http_list(data)

            if raw_items:
                return [
                    _normalize_graphiti_http_item(
                        raw,
                        idx,
                        query=query,
                        source=source,
                    )
                    for idx, raw in enumerate(
                        raw_items[:limit],
                        1,
                    )
                ]
        except Exception:
            continue

    return []


def _query_graphiti_frozen_http_ladder(
    queries: list[str],
    limit: int = 8,
) -> tuple[list[dict], str | None, list[dict]]:
    attempted: list[dict] = []
    seen: set[str] = set()
    unique_queries: list[str] = []

    for raw_query in queries:
        q = (raw_query or "").strip()

        if not q:
            continue

        key = q.lower()

        if key in seen:
            continue

        seen.add(key)
        unique_queries.append(q)

    if not unique_queries:
        return [], None, attempted

    if not _graphiti_v20_frozen_http_available():
        attempted.extend(
            {
                "query": q,
                "results_count": 0,
                "source": "GRAPHITI_V20_FROZEN_HTTP",
                "status": "SIDECAR_UNAVAILABLE_FAST_PROBE",
            }
            for q in unique_queries
        )

        return [], None, attempted

    deadline = (
        time.monotonic()
        + _GRAPHITI_HTTP_LADDER_BUDGET_SECONDS
    )

    for q in unique_queries:
        if time.monotonic() >= deadline:
            attempted.append(
                {
                    "query": q,
                    "results_count": 0,
                    "source": "GRAPHITI_V20_FROZEN_HTTP",
                    "status": "HTTP_BUDGET_EXHAUSTED",
                }
            )
            break

        items = _query_graphiti_frozen_http_once(
            q,
            limit=limit,
            deadline=deadline,
        )

        attempted.append(
            {
                "query": q,
                "results_count": len(items),
                "source": "GRAPHITI_V20_FROZEN_HTTP",
                "status": (
                    "RESULTS"
                    if items
                    else "NO_RESULTS"
                ),
            }
        )

        if items:
            return items, q, attempted

        if time.monotonic() >= deadline:
            attempted.append(
                {
                    "query": None,
                    "results_count": 0,
                    "source": "GRAPHITI_V20_FROZEN_HTTP",
                    "status": "HTTP_BUDGET_EXHAUSTED",
                }
            )
            break

    return [], None, attempted




def _build_graphiti_v20_frozen_chain_result(
    *,
    graphiti_items: list[dict],
    graphiti_effective_query: str | None,
    graphiti_attempts: list[dict],
    user_message: str,
    query: str,
    primary_query: str,
    topic: str,
    neo4j_reason: str,
    max_items: int,
    workspace: Path,
) -> dict[str, Any]:
    """Build a readonly memory chain result from Graphiti V20 frozen HTTP items."""
    periphery = workspace / "periphery" / "brody_memory_readonly"
    engine_mod = _import_module(
        periphery / "local_response_engine_readonly" / "brody_local_response_engine_readonly_v1.py"
    )

    try:
        if engine_mod:
            engine_input = {
                "context_packet": {
                    "items": graphiti_items,
                    "query": graphiti_effective_query or primary_query or query,
                    "source": "GRAPHITI_V20_FROZEN_HTTP_PRIMARY",
                    "results_count": len(graphiti_items),
                    "readonly": True,
                    "decision_authority": "KX108_ONLY",
                    "memory_write": False,
                    "graphiti_write": False,
                    "kernel_mutation": False,
                    "x108_mutation": False,
                },
                "query": graphiti_effective_query or primary_query or query,
                "text": user_message,
                "memory_write": False,
                "graphiti_write": False,
                "emits_act": False,
                "kernel_mutation": False,
                "x108_mutation": False,
                "decision_authority": "KX108_ONLY",
            }
            engine_result = engine_mod.build_response(engine_input, max_items=max_items)
            if isinstance(engine_result, dict):
                response_md = engine_result.get("response_md", "")
                material_quality = engine_result.get("material_quality", "PARTIAL_MATERIAL")
                selected_items = engine_result.get("selected_items", graphiti_items[:max_items])
                tag_counts = engine_result.get("tag_counts", {})
                engine_used = True
            else:
                response_md = ""
                material_quality = "PARTIAL_MATERIAL"
                selected_items = graphiti_items[:max_items]
                tag_counts = {}
                engine_used = False
        else:
            response_md = ""
            material_quality = "PARTIAL_MATERIAL"
            selected_items = graphiti_items[:max_items]
            tag_counts = {}
            engine_used = False
    except Exception:
        response_md = ""
        material_quality = "PARTIAL_MATERIAL"
        selected_items = graphiti_items[:max_items]
        tag_counts = {}
        engine_used = False

    chain_result_status = (
        "BRODY_MEMORY_RESPONSE_CHAIN_PASS"
        if (material_quality in ("USABLE_MATERIAL", "PARTIAL_MATERIAL", "LOW_MATERIAL") and selected_items)
        else "GRAPHITI_V20_FROZEN_HTTP_PARTIAL"
    )

    return {
        "status": chain_result_status,
        "source_mode": "GRAPHITI_V20_FROZEN_HTTP_PRIMARY",
        "topic": topic,
        "semantic_query": query,
        "primary_query": primary_query,
        "effective_query": graphiti_effective_query,
        "attempted_queries": graphiti_attempts,
        "graphiti_http_attempted_queries": graphiti_attempts,
        "neo4j_status": neo4j_reason,
        "graphiti_status": "GRAPHITI_V20_FROZEN_READONLY_PASS",
        "graphiti_live": True,
        "graphiti_v20_frozen_http": True,
        "live_neo4j_dependency": False,
        "query_module_used": False,
        "query_results_count": 0,
        "graphiti_http_results_count": len(graphiti_items),
        "hydration_module_used": False,
        "hydrated_excerpt_count": len([it for it in graphiti_items if it.get("excerpt")]),
        "local_response_engine_used": engine_used,
        "material_quality": material_quality,
        "response_md": response_md,
        "response_md_length": len(response_md),
        "selected_items_count": len(selected_items),
        "selected_items": selected_items[:3],
        "tag_counts": tag_counts,
        "final_answer_uses_response_md": bool(response_md and len(response_md) > 50),
        "chain_source": "neo4j_unavailable→graphiti_v20_frozen_http→local_response_engine",
        "note": f"Neo4j unavailable ({neo4j_reason}); used Graphiti V20 frozen HTTP readonly source before local JSONL fallback.",
        "created_at": _now(),
        **MEMORY_CHAIN_BOUNDARY,
    }


def build_memory_response_chain(
    user_message: str = "",
    semantic_query: str = "",
    language: str = "fr",
    limit: int = 8,
    max_items: int = 6,
    workspace_root: Path | None = None,
) -> dict[str, Any]:
    """
    Execute the full Brody memory→response chain.

    Steps:
      1. query_neo4j() → context packet from BrodyMemoryDoc
      2. hydrate_packet() → resolve paths, read local files
      3. local_response_engine.build_response() → structured response_md

    Returns memory_response_chain_snapshot with full metrics.
    Fail-soft: if Neo4j unavailable, returns ERROR with explicit reason.
    """
    from apps.obsidia_api.brody_semantic_query_router import build_semantic_query as _route_semantic

    workspace = workspace_root or Path(__file__).resolve().parents[2]
    
    # Route to canonical semantic query
    sq = _route_semantic(user_message) if user_message else {"topic": "GENERAL", "semantic_query": semantic_query or "", "primary_query": semantic_query or "", "fallback_queries": []}
    query = semantic_query or sq.get("semantic_query", user_message)
    topic = sq.get("topic", "GENERAL")
    primary_q = sq.get("primary_query", query)
    fallback_qs: list[str] = sq.get("fallback_queries", [])

    # ── 1. Check Neo4j availability ───────────────────────────────────────
    neo4j_ok, neo4j_reason = _neo4j_available()
    if not neo4j_ok:
        # ── GRAPHITI V20 FROZEN HTTP PRIMARY FALLBACK ────────────────────
        # F17B: When Neo4j credentials are missing/unavailable, do not jump
        # directly to the flat local JSONL index. First try the validated
        # Graphiti V20 frozen readonly sidecar on 8011 (no live Neo4j dependency).
        graphiti_http_queries = [primary_q] + list(fallback_qs[:4]) + [query, user_message]
        graphiti_items, graphiti_effective_query, graphiti_attempts = _query_graphiti_frozen_http_ladder(
            graphiti_http_queries,
            limit=limit,
        )
        if graphiti_items:
            return _build_graphiti_v20_frozen_chain_result(
                graphiti_items=graphiti_items,
                graphiti_effective_query=graphiti_effective_query,
                graphiti_attempts=graphiti_attempts,
                user_message=user_message,
                query=query,
                primary_query=primary_q,
                topic=topic,
                neo4j_reason=neo4j_reason,
                max_items=max_items,
                workspace=workspace,
            )

        # ── LOCAL INDEX FALLBACK ──────────────────────────────────────────
        records = _load_local_graphiti_index(workspace)
        if not records:
            return {
                "status": "ERROR",
                "source_mode": "LOCAL_GRAPHITI_INDEX_FALLBACK",
                "error": f"{neo4j_reason} — local index not found",
                "error_type": "NEO4J_UNAVAILABLE_AND_LOCAL_INDEX_MISSING",
                "semantic_query": query,
                "primary_query": primary_q,
                "effective_query": None,
                "attempted_queries": [],
                "neo4j_status": neo4j_reason,
                "graphiti_live": False,
                "query_module_used": False,
                "query_results_count": 0,
                "hydration_module_used": False,
                "hydrated_excerpt_count": 0,
                "local_response_engine_used": False,
                "material_quality": "CHAIN_UNAVAILABLE",
                "response_md": "",
                "response_md_length": 0,
                "selected_items_count": 0,
                "selected_items": [],
                "final_answer_uses_response_md": False,
                "note": f"Neo4j unavailable: {neo4j_reason}. Local Graphiti index not found.",
                "created_at": _now(),
                **MEMORY_CHAIN_BOUNDARY,
            }

        # Query ladder: primary_query first, then fallbacks
        attempted_queries: list[dict] = []
        effective_query: str | None = None
        local_items: list[dict] = []

        for q in [primary_q] + list(fallback_qs):
            hits = _query_local_index(q, records, limit=limit)
            attempted_queries.append({"query": q, "results_count": len(hits)})
            if hits and effective_query is None:
                effective_query = q
                local_items = hits

        if not local_items:
            return {
                "status": "NO_MEMORY_RESULTS",
                "source_mode": "LOCAL_GRAPHITI_INDEX_FALLBACK",
                "topic": topic,
                "semantic_query": query,
                "primary_query": primary_q,
                "effective_query": None,
                "attempted_queries": attempted_queries,
                "neo4j_status": neo4j_reason,
                "graphiti_live": False,
                "query_module_used": False,
                "query_results_count": 0,
                "local_index_records_total": len(records),
                "hydration_module_used": False,
                "hydrated_excerpt_count": 0,
                "local_response_engine_used": False,
                "material_quality": "NO_MATERIAL",
                "response_md": "",
                "response_md_length": 0,
                "selected_items_count": 0,
                "selected_items": [],
                "final_answer_uses_response_md": False,
                "note": f"Local index ({len(records)} records): no match for {[a['query'] for a in attempted_queries]}",
                "created_at": _now(),
                **MEMORY_CHAIN_BOUNDARY,
            }

        # Try hydration + engine (fail-soft)
        periphery = workspace / "periphery" / "brody_memory_readonly"
        hydration_mod = _import_module(
            periphery / "content_hydration_readonly" / "brody_content_hydration_readonly_v1.py"
        )
        engine_mod = _import_module(
            periphery / "local_response_engine_readonly" / "brody_local_response_engine_readonly_v1.py"
        )

        # Match the exact format brody_context_packet_query_readonly_v1 produces
        # so hydration and engine modules accept it without modification
        synthetic_packet = {
            "status": "BRODY_CONTEXT_PACKET_QUERY_READONLY_PASS",
            "created_at": _now(),
            "query": effective_query or query,
            "context_packet": {
                "items": local_items,
                "query": effective_query or query,
                "source": "LOCAL_GRAPHITI_JSONL",
                "results_count": len(local_items),
            },
            "results_count": len(local_items),
            "memory_decision": False,
            "allowed_to_decide": False,
            "emits_act": False,
            "kernel_binding": False,
            "x108_merge": False,
            "kernel_mutation": False,
            "x108_mutation": False,
            "x108_runtime_binding": False,
            "decision_authority": "KX108_ONLY",
            "readonly": True,
        }

        try:
            # Skip filesystem-scan hydration if items already carry text_excerpt.
            # build_index(roots) scans the entire repo tree and is very slow.
            items_have_excerpts = all(bool(it.get("excerpt")) for it in local_items)
            if hydration_mod and not items_have_excerpts:
                roots = _default_roots(workspace)
                hydrated = hydration_mod.hydrate_packet(synthetic_packet, roots=roots, max_chars=1400)
                hydrate_report = hydrated.get("hydration_report", {})
                hydrated_count = hydrate_report.get("hydrated_excerpt_count", 0)
                hydration_used = True
                packet_for_engine = hydrated.get("context_packet", hydrated)
            else:
                # Items have excerpts from text_excerpt — hydration not needed
                hydrated_count = len([it for it in local_items if it.get("excerpt")])
                hydration_used = bool(hydration_mod)
                packet_for_engine = synthetic_packet

            if engine_mod:
                # Engine expects context_packet.items at the same level (extract_packet → obj.get("context_packet").get("items"))
                items_for_engine = (
                    packet_for_engine.get("context_packet", {}).get("items")
                    or packet_for_engine.get("items")
                    or local_items
                )
                engine_input = {
                    "context_packet": {
                        "items": items_for_engine,
                        "query": effective_query or query,
                        "source": "LOCAL_GRAPHITI_JSONL",
                    },
                    "query": effective_query or query,
                    "text": user_message,
                    "memory_write": False,
                    "emits_act": False,
                    "kernel_mutation": False,
                    "decision_authority": "KX108_ONLY",
                }
                engine_result = engine_mod.build_response(engine_input, max_items=max_items)
                if isinstance(engine_result, dict):
                    response_md = engine_result.get("response_md", "")
                    material_quality = engine_result.get("material_quality", "PARTIAL_MATERIAL")
                    selected_items = engine_result.get("selected_items", local_items[:max_items])
                    tag_counts = engine_result.get("tag_counts", {})
                    engine_used = True
                else:
                    response_md = ""
                    material_quality = "PARTIAL_MATERIAL"
                    selected_items = local_items[:max_items]
                    tag_counts = {}
                    engine_used = False
            else:
                response_md = ""
                material_quality = "PARTIAL_MATERIAL"
                selected_items = local_items[:max_items]
                tag_counts = {}
                engine_used = False
        except Exception:
            response_md = ""
            material_quality = "PARTIAL_MATERIAL"
            selected_items = local_items[:max_items]
            tag_counts = {}
            hydrated_count = 0
            hydration_used = False
            engine_used = False

        chain_result_status = (
            "BRODY_MEMORY_RESPONSE_CHAIN_PASS"
            if (material_quality in ("USABLE_MATERIAL", "PARTIAL_MATERIAL") and response_md and len(response_md) > 50)
            else "LOCAL_INDEX_FALLBACK_PARTIAL"
        )

        return {
            "status": chain_result_status,
            "source_mode": "LOCAL_GRAPHITI_INDEX_FALLBACK",
            "topic": topic,
            "semantic_query": query,
            "primary_query": primary_q,
            "effective_query": effective_query,
            "attempted_queries": attempted_queries,
            "neo4j_status": neo4j_reason,
            "graphiti_live": False,
            "query_module_used": False,
            "query_results_count": len(local_items),
            "local_index_records_total": len(records),
            "hydration_module_used": hydration_used,
            "hydrated_excerpt_count": hydrated_count,
            "local_response_engine_used": engine_used,
            "material_quality": material_quality,
            "response_md": response_md,
            "response_md_length": len(response_md),
            "selected_items_count": len(selected_items),
            "selected_items": selected_items[:3],
            "tag_counts": tag_counts,
            "final_answer_uses_response_md": bool(response_md and len(response_md) > 50),
            "chain_source": "local_graphiti_index→hydrate_packet→local_response_engine",
            "created_at": _now(),
            **MEMORY_CHAIN_BOUNDARY,
        }

    # ── 2. Import the three chain modules ─────────────────────────────────
    periphery = workspace / "periphery" / "brody_memory_readonly"

    query_mod = _import_module(
        periphery / "context_packet_query_readonly" / "brody_context_packet_query_readonly_v1.py"
    )
    hydration_mod = _import_module(
        periphery / "content_hydration_readonly" / "brody_content_hydration_readonly_v1.py"
    )
    engine_mod = _import_module(
        periphery / "local_response_engine_readonly" / "brody_local_response_engine_readonly_v1.py"
    )

    if not query_mod:
        return _chain_error("QUERY_MODULE_NOT_FOUND", query, "context_packet_query_readonly module not importable")
    if not hydration_mod:
        return _chain_error("HYDRATION_MODULE_NOT_FOUND", query, "content_hydration_readonly module not importable")
    if not engine_mod:
        return _chain_error("ENGINE_MODULE_NOT_FOUND", query, "local_response_engine_readonly module not importable")

    # ── 3. Execute: query → hydrate → engine ──────────────────────────────
    primary = sq.get("primary_query", query)
    fallbacks = sq.get("fallback_queries", [])
    attempted_queries: list[str] = []
    effective_query = primary

    try:
        # Step 1: Query Neo4j with ladder (primary → fallbacks)
        packet = query_mod.query_neo4j(primary, limit)
        attempted_queries.append(primary)
        query_results_count = packet.get("results_count", 0)

        # Ladder: if 0 results, try fallbacks
        for fb in fallbacks[:4]:  # Max 4 fallback attempts
            if query_results_count > 0:
                break
            packet = query_mod.query_neo4j(fb, limit)
            attempted_queries.append(fb)
            query_results_count = packet.get("results_count", 0)
            if query_results_count > 0:
                effective_query = fb

        if query_results_count == 0:
            # Phase 12B: Neo4j/BrodyMemoryDoc may be live but empty for a query while
            # the validated Graphiti V20 frozen HTTP surface already has readonly material.
            # Use it as a context-only fallback before returning NO_MEMORY_RESULTS.
            graphiti_http_queries = [primary] + list(fallbacks[:4]) + [query, user_message]
            graphiti_items, graphiti_effective_query, graphiti_attempts = _query_graphiti_frozen_http_ladder(
                graphiti_http_queries,
                limit=limit,
            )

            if graphiti_items:
                try:
                    engine_input = {
                        "context_packet": {
                            "items": graphiti_items,
                            "query": graphiti_effective_query or primary,
                            "source": "GRAPHITI_V20_FROZEN_HTTP_FALLBACK",
                            "results_count": len(graphiti_items),
                        },
                        "query": graphiti_effective_query or primary,
                        "text": user_message,
                        "memory_write": False,
                        "graphiti_write": False,
                        "emits_act": False,
                        "kernel_mutation": False,
                        "decision_authority": "KX108_ONLY",
                    }
                    engine_result = engine_mod.build_response(engine_input, max_items=max_items)
                    if isinstance(engine_result, dict):
                        response_md = engine_result.get("response_md", "")
                        material_quality = engine_result.get("material_quality", "PARTIAL_MATERIAL")
                        selected_items = engine_result.get("selected_items", graphiti_items[:max_items])
                        tag_counts = engine_result.get("tag_counts", {})
                        engine_used = True
                    else:
                        response_md = ""
                        material_quality = "PARTIAL_MATERIAL"
                        selected_items = graphiti_items[:max_items]
                        tag_counts = {}
                        engine_used = False
                except Exception:
                    response_md = ""
                    material_quality = "PARTIAL_MATERIAL"
                    selected_items = graphiti_items[:max_items]
                    tag_counts = {}
                    engine_used = False

                chain_result_status = (
                    "BRODY_MEMORY_RESPONSE_CHAIN_PASS"
                    if (material_quality in ("USABLE_MATERIAL", "PARTIAL_MATERIAL", "LOW_MATERIAL") and selected_items)
                    else "GRAPHITI_HTTP_FALLBACK_PARTIAL"
                )

                return {
                    "status": chain_result_status,
                    "source_mode": "GRAPHITI_V20_FROZEN_HTTP_FALLBACK",
                    "topic": topic,
                    "semantic_query": query,
                    "primary_query": primary,
                    "effective_query": graphiti_effective_query,
                    "attempted_queries": attempted_queries,
                    "graphiti_http_attempted_queries": graphiti_attempts,
                    "query_module_used": True,
                    "query_results_count": 0,
                    "graphiti_http_results_count": len(graphiti_items),
                    "hydration_module_used": False,
                    "hydrated_excerpt_count": len([it for it in graphiti_items if it.get("excerpt")]),
                    "local_response_engine_used": engine_used,
                    "material_quality": material_quality,
                    "response_md": response_md,
                    "response_md_length": len(response_md),
                    "selected_items_count": len(selected_items),
                    "selected_items": selected_items[:3],
                    "tag_counts": tag_counts,
                    "final_answer_uses_response_md": bool(response_md and len(response_md) > 50),
                    "chain_source": "query_neo4j_zero→graphiti_v20_frozen_http→local_response_engine",
                    "note": "Neo4j/BrodyMemoryDoc returned 0 results; used Graphiti V20 frozen HTTP readonly fallback.",
                    "created_at": _now(),
                    **MEMORY_CHAIN_BOUNDARY,
                }

            return {
                "status": "NO_MEMORY_RESULTS",
                "source_mode": "MEMORY_RESPONSE_CHAIN",
                "topic": topic,
                "semantic_query": query,
                "primary_query": primary,
                "effective_query": None,
                "attempted_queries": attempted_queries,
                "graphiti_http_attempted_queries": graphiti_attempts,
                "query_module_used": True,
                "query_results_count": 0,
                "graphiti_http_results_count": 0,
                "hydration_module_used": False,
                "hydrated_excerpt_count": 0,
                "local_response_engine_used": False,
                "material_quality": "NO_MATERIAL",
                "response_md": "",
                "response_md_length": 0,
                "selected_items_count": 0,
                "selected_items": [],
                "final_answer_uses_response_md": False,
                "note": "Query returned 0 results in Neo4j/BrodyMemoryDoc and Graphiti V20 HTTP fallback.",
                "created_at": _now(),
                **MEMORY_CHAIN_BOUNDARY,
            }

        # Step 2: Hydrate
        roots = _default_roots(workspace)
        hydrated = hydration_mod.hydrate_packet(packet, roots=roots, max_chars=1400)
        hydrate_report = hydrated.get("hydration_report", {})
        hydrated_count = hydrate_report.get("hydrated_excerpt_count", 0)

        # Step 3: Local Response Engine
        engine_input = {
            "context_packet": hydrated.get("context_packet", hydrated),
            "query": query,
            "text": user_message,
            "memory_write": False,
            "emits_act": False,
            "kernel_mutation": False,
            "decision_authority": "KX108_ONLY",
        }
        engine_result = engine_mod.build_response(engine_input, max_items=max_items)

        if not isinstance(engine_result, dict):
            return _chain_error("ENGINE_RETURNED_NON_DICT", query, f"build_response returned {type(engine_result).__name__}")

        response_md = engine_result.get("response_md", "")
        material_quality = engine_result.get("material_quality", "")
        selected_items = engine_result.get("selected_items", [])
        tag_counts = engine_result.get("tag_counts", {})

        # Only PASS if material present and response_md valid
        chain_result_status = "BRODY_MEMORY_RESPONSE_CHAIN_PASS" if (material_quality in ("USABLE_MATERIAL", "PARTIAL_MATERIAL") and response_md and len(response_md) > 50) else "PARTIAL_QUERY_ONLY"

        return {
            "status": chain_result_status,
            "source_mode": "MEMORY_RESPONSE_CHAIN",
            "topic": topic,
            "semantic_query": query,
            "query_module_used": True,
            "query_results_count": query_results_count,
            "hydration_module_used": True,
            "hydrated_excerpt_count": hydrated_count,
            "indexed_file_count": hydrate_report.get("indexed_file_count", 0),
            "local_response_engine_used": True,
            "material_quality": material_quality,
            "response_md": response_md,
            "response_md_length": len(response_md),
            "selected_items_count": len(selected_items),
            "selected_items": selected_items[:3],  # Keep payload small
            "tag_counts": tag_counts,
            "final_answer_uses_response_md": True,
            "chain_source": "query_neo4j→hydrate_packet→local_response_engine",
            "created_at": _now(),
            **MEMORY_CHAIN_BOUNDARY,
        }

    except Exception as exc:
        return _chain_error(
            "CHAIN_EXECUTION_ERROR",
            query,
            f"{type(exc).__name__}: {str(exc)[:200]}",
        )


def _chain_error(
    error_type: str,
    semantic_query: str,
    error_message: str,
) -> dict[str, Any]:
    """Build a fail-soft error snapshot for the memory chain."""
    return {
        "status": "ERROR",
        "source_mode": "MEMORY_RESPONSE_CHAIN",
        "error_type": error_type,
        "error": error_message,
        "semantic_query": semantic_query,
        "query_module_used": False,
        "query_results_count": 0,
        "hydration_module_used": False,
        "hydrated_excerpt_count": 0,
        "local_response_engine_used": False,
        "material_quality": "CHAIN_ERROR",
        "response_md": "",
        "response_md_length": 0,
        "selected_items_count": 0,
        "selected_items": [],
        "final_answer_uses_response_md": False,
        "created_at": _now(),
        **MEMORY_CHAIN_BOUNDARY,
    }

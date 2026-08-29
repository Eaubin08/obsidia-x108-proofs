#!/usr/bin/env python3
"""OBSIDIA MCP SERVER — expose la stack deterministe comme outils MCP (stdio).

Claude Code appelle ces outils au lieu de lire des fichiers en tokens :
  obsidia_route          verdict pre-inference (IR + gate + level + route)
  obsidia_memory_search  recherche par sens (Shazam 34 arbres + index canonique)
  obsidia_shazam         activation des 34 arbres pour un texte

Contrat adopte depuis 09_MCP_BRIDGE_OBSIDIA_IR (MMONDE) :
  chaque reponse porte non_decision=True, policy_scope=READONLY_CONTEXT,
  et tree_vector quand pertinent. decision_authority = KX108_ONLY.

Chaque appel est logge (append-only) dans audit/obsidia_gateway_usage.jsonl —
donnees MEASURED d'inference evitee.

Stdlib only. Protocole: JSON-RPC 2.0 sur stdio (MCP 2024-11-05).
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "scripts"
AUDIT_LOG = REPO_ROOT / "audit" / "obsidia_gateway_usage.jsonl"

sys.path.insert(0, str(SCRIPTS))

from export_gateway_memory_index import dominant_trees, words  # noqa: E402
from obsidia_gateway import load_semantic_index, semantic_search  # noqa: E402
import obsidia_gateway_route_decision_v0 as _RD  # noqa: E402

SEMANTIC_ENTRIES = load_semantic_index()

TOOLS = [
    {
        "name": "obsidia_route",
        "description": ("Verdict pre-inference deterministe d'Obsidia pour une "
                        "requete: intention, couche, gate (DENY/HOLD/CLARIFY/"
                        "ALLOW), niveau d'inference et route. 0 token, 0 reseau."),
        "inputSchema": {"type": "object",
                        "properties": {"query": {"type": "string"}},
                        "required": ["query"]},
    },
    {
        "name": "obsidia_memory_search",
        "description": ("Recherche par sens dans la memoire canonique Obsidia "
                        "(103 entrees MATH_MEMORY_INDEX taguees par les 34 "
                        "arbres MMONDE). Retourne la meilleure entree ou "
                        "no_hit. A utiliser AVANT de lire des fichiers."),
        "inputSchema": {"type": "object",
                        "properties": {"query": {"type": "string"}},
                        "required": ["query"]},
    },
    {
        "name": "obsidia_shazam",
        "description": ("Active les 34 arbres semantiques MMONDE sur un texte "
                        "et retourne les arbres dominants (accents plies, "
                        "mots entiers). Utile pour classer/taguer par sens."),
        "inputSchema": {"type": "object",
                        "properties": {"text": {"type": "string"}},
                        "required": ["text"]},
    },
]

FRAME = {"non_decision": True, "policy_scope": "READONLY_CONTEXT",
         "decision_authority": "KX108_ONLY"}


def _audit(tool: str, preview: str, avoided: bool = True) -> None:
    try:
        entry = {"tool": tool, "request_preview": preview[:120],
                 "model_call_avoided": avoided,
                 "ts": datetime.now(timezone.utc).isoformat(),
                 "source": "OBSIDIA_MCP_SERVER_V1",
                 "decision_authority": "KX108_ONLY"}
        with AUDIT_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError:
        pass


def call_tool(name: str, args: dict) -> dict:
    if name == "obsidia_route":
        q = args["query"]
        d = _RD.build_route_decision(q)
        _audit(name, q)
        return dict(FRAME, ir=d.get("ir"), gate=d.get("gate_verdict"),
                    level=d.get("level"), route=d.get("route_class"),
                    reason=d.get("reason"), router_status=d.get("router_status"),
                    fail_closed_hold=d.get("fail_closed_hold"))
    if name == "obsidia_memory_search":
        q = args["query"]
        hit = semantic_search(q, SEMANTIC_ENTRIES)
        _audit(name, q)
        if hit:
            e = hit["entry"]
            return dict(FRAME, hit=True, score=hit["score"], name=e["name"],
                        answer=e["answer"], trees=e["trees"],
                        source=e["source"], status=e["status"])
        return dict(FRAME, hit=False,
                    note="aucune entree canonique assez proche — ne pas inventer")
    if name == "obsidia_shazam":
        t = args["text"]
        trees = dominant_trees(t)
        _audit(name, t)
        return dict(FRAME, dominant_trees=trees,
                    tree_vector=[trees.get(str(i), 0) for i in range(34)])
    raise ValueError(f"unknown tool: {name}")


def main() -> int:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue
        rid, method = req.get("id"), req.get("method")
        params = req.get("params") or {}
        result = None
        if method == "initialize":
            result = {"protocolVersion": "2024-11-05",
                      "capabilities": {"tools": {}},
                      "serverInfo": {"name": "obsidia", "version": "1.0.0"}}
        elif method == "notifications/initialized":
            continue  # notification, pas de reponse
        elif method == "tools/list":
            result = {"tools": TOOLS}
        elif method == "tools/call":
            try:
                out = call_tool(params["name"], params.get("arguments") or {})
                result = {"content": [{"type": "text",
                                       "text": json.dumps(out, ensure_ascii=False)}]}
            except Exception as exc:
                result = {"content": [{"type": "text", "text": f"error: {exc}"}],
                          "isError": True}
        else:
            if rid is None:
                continue
            result = {}
        if rid is not None:
            sys.stdout.write(json.dumps(
                {"jsonrpc": "2.0", "id": rid, "result": result},
                ensure_ascii=False) + "\n")
            sys.stdout.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())

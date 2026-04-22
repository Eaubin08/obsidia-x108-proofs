"""Obsidia Engine — Final Minimal Assembly (OS0 + OS1 + OS2 + Registry)

This is the *unified entrypoint* that couples:
- Registry (Pivot allowlist + domain metadata)
- OS2 structural metrics (triangle/hex proxy + asym penalty) with core-fixed invariance
- OS1 decision pipeline (contract + X108 + OS0 sandbox execution)

Goal: a minimal-but-complete deterministic engine that is testable end-to-end.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from obsidia_registry import load_minimal_registry
from obsidia_os2 import compute_metrics_core_fixed, decision_act_hold
from obsidia_os1 import run_request as os1_run_request
from obsidia_os1.x108 import X108Gate


@dataclass
class FinalResult:
    decision: str  # ACT | HOLD | REJECT
    ssr: str
    registry_ok: bool
    os2: Optional[Dict[str, Any]]
    os1: Optional[Dict[str, Any]]


def _pivot_allowlist(registry_path: Optional[str]) -> List[str]:
    reg = load_minimal_registry(registry_path)
    ids: List[str] = []
    for item in reg.pivot_agents:
        if isinstance(item, str):
            ids.append(item.strip())
            continue
        if isinstance(item, dict):
            # accept both "id" and "canonical_id"
            _id = item.get("id") or item.get("canonical_id")
            if _id:
                ids.append(str(_id))
    return ids


def run_final(
    *,
    raw_input: str,
    agent_id: Optional[str] = None,
    registry_path: Optional[str] = None,
    # OS2
    W_full: Optional[List[List[float]]] = None,
    core_nodes: Optional[List[int]] = None,
    theta_S: float = 0.25,
    # X108
    irreversible: bool = False,
    elapsed_s: float = 0.0,
    min_wait_s: float = 108.0,
) -> FinalResult:
    """Unified engine runner.

    - If agent_id is provided, it must be in the Pivot allowlist (registry).
    - If OS2 inputs are provided (W_full + core_nodes), OS2 decides ACT/HOLD.
    - If OS2 says HOLD, OS1 is not executed.
    - If OS2 says ACT, OS1 runs contract + X108 + OS0 sandbox.
    """

    # 0) Registry gate (Pivot allowlist)
    # FIX: agent_id=None est une tentative de bypass — REJECT si la registry est active
    allow = _pivot_allowlist(registry_path)
    if allow:  # registry non vide => toute requête doit présenter un agent_id valide
        if agent_id is None:
            return FinalResult(
                decision="REJECT",
                ssr="REGISTRY_REJECT: agent_id manquant (None) — identification obligatoire.",
                registry_ok=False,
                os2=None,
                os1=None,
            )
        if str(agent_id) not in set(allow):
            return FinalResult(
                decision="REJECT",
                ssr=f"REGISTRY_REJECT: agent_id '{agent_id}' not in PIVOT allowlist.",
                registry_ok=False,
                os2=None,
                os1=None,
            )

    # 1) OS2 (optional but supported)
    os2_payload: Optional[Dict[str, Any]] = None
    if W_full is not None and core_nodes is not None:
        m = compute_metrics_core_fixed(W_full, core_nodes)
        os2_dec = decision_act_hold(m, theta_S=theta_S)
        os2_payload = {"T_mean": m.T_mean, "H_score": m.H_score, "A_score": m.A_score, "S": m.S, "decision": os2_dec}
        if os2_dec != "ACT":
            return FinalResult(
                decision="HOLD",
                ssr=f"OS2_HOLD: S={m.S:.6f} < theta_S={theta_S:.6f} (core-fixed invariance).",
                registry_ok=True,
                os2=os2_payload,
                os1=None,
            )

    # 2) OS1 (+ OS0 sandbox)
    gate = X108Gate(min_wait_s=min_wait_s)
    x108_ctx = {"elapsed_s": float(elapsed_s), "irreversible": bool(irreversible)}
    d = os1_run_request(
        raw_input=raw_input,
        x108_gate=gate,
        x108_ctx=x108_ctx,
    )

    os1_payload = {
        "decision": d.decision,
        "ssr": d.ssr,
        "contract_ok": d.contract_ok,
        "x108": None if d.x108 is None else {"decision": d.x108.decision, "wait_s": d.x108.wait_s, "reason": d.x108.reason},
        "os0_result": d.os0_result,
    }

    return FinalResult(
        decision=d.decision,
        ssr=d.ssr,
        registry_ok=True,
        os2=os2_payload,
        os1=os1_payload,
    )

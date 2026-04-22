# obsidia_kernel/kernel.py
from __future__ import annotations

import hashlib
import json
import uuid
from typing import Any, Dict, List

from .contract import Request, Result, Decision, HumanGate

from entrypoint import run_obsidia

KERNEL_VERSION = "v2.3.1"

def _sha256(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()

def _map_decision(raw: str) -> Decision:
    r = (raw or "").upper()
    if r == "ACT":
        return Decision.ACT
    if r == "HOLD":
        return Decision.HOLD
    if r in ("BLOCK","REJECT","REFUSE"):
        return Decision.BLOCK
    return Decision.BLOCK

class ObsidiaKernel:
    def run(self, request: Request) -> Result:
        trace_id = str(uuid.uuid4())

        payload = dict(request.intent.payload or {})
        attachments = dict(request.attachments or {})

        # raw_input precedence: explicit -> attachments.code -> serialized payload
        raw_input = payload.get("raw_input") or payload.get("text") or attachments.get("code")
        if not isinstance(raw_input, str):
            raw_input = json.dumps(payload, sort_keys=True, ensure_ascii=False)

        # world params precedence: payload first, then context (for orchestrator injections)
        W_full = payload.get("W_full") if isinstance(payload.get("W_full"), list) else None
        core_nodes = payload.get("core_nodes") if isinstance(payload.get("core_nodes"), list) else None
        theta_S = payload.get("theta_S")
        if not isinstance(theta_S, (int, float)):
            theta_S = getattr(request.governance, "theta_S", 0.25)

        ctx = request.context or {}
        if W_full is None and isinstance(ctx.get("W_full"), list):
            W_full = ctx.get("W_full")
        if core_nodes is None and isinstance(ctx.get("core_nodes"), list):
            core_nodes = ctx.get("core_nodes")

        engine_payload: Dict[str, Any] = {
            "raw_input": raw_input,
            "agent_id": request.meta.agent_id,
            "theta_S": float(theta_S),
            "irreversible": bool(request.governance.irreversible),
            "elapsed_s": float(getattr(request.governance, "x108_elapsed_s", 0.0)),
            "min_wait_s": float(getattr(request.governance, "x108_min_wait_s", 108.0)),
        }
        if W_full is not None:
            engine_payload["W_full"] = W_full
        if core_nodes is not None:
            engine_payload["core_nodes"] = core_nodes

        fr = run_obsidia(engine_payload)

        raw_decision = getattr(fr, "decision", None)
        ssr = getattr(fr, "ssr", None)
        registry_ok = getattr(fr, "registry_ok", None)
        os2 = getattr(fr, "os2", None)
        os1 = getattr(fr, "os1", None)

        kernel_decision = _map_decision(raw_decision or "")

        # audit_path must match parity tests (observable-only)
        if (raw_decision or "").upper() == "REJECT":
            audit_path: List[str] = ["REGISTRY"]
        else:
            audit_path = ["REGISTRY", "OS2", "OS3"]
            if os1 is not None:
                audit_path.insert(2, "OS1")  # REGISTRY, OS2, OS1, OS3

        # ACP fields (optional)
        acp_status = None
        acp_ambiguity: Dict[str, Any] = {}
        ctx_acp = ctx.get("acp") if isinstance(ctx.get("acp"), dict) else None
        if ctx_acp and (raw_decision or "").upper() != "REJECT":
            acp_status = ctx_acp.get("status")
            amb = ctx_acp.get("ambiguity")
            if isinstance(amb, dict):
                acp_ambiguity = amb

        required_human_gate = False
        human_gate = None
        if kernel_decision in (Decision.HOLD, Decision.BLOCK) and acp_status == "REFUSE_UNTIL_RESOLVED":
            required_human_gate = True
            human_gate = HumanGate(
                required=True,
                type="RESOLUTION",
                prompt="Resolve semantic ambiguity / provide human clarification",
                deadline=None,
            )

        artifacts_hash = _sha256({
            "decision": str(kernel_decision),
            "engine_decision_raw": raw_decision,
            "registry_ok": registry_ok,
            "ssr": ssr,
            "has_os1": os1 is not None,
            "has_os2": os2 is not None,
            "audit_path": audit_path,
        })

        hash_chain: List[str] = []
        prev = ""
        for part in (artifacts_hash, raw_decision or "", ssr or ""):
            prev = _sha256({"prev": prev, "part": part})
            hash_chain.append(prev)

        metrics: Dict[str, Any] = {}
        if isinstance(os2, dict):
            m = os2.get("metrics")
            if isinstance(m, dict):
                metrics.update(m)
        if isinstance(ctx.get("metrics"), dict):
            metrics.update(ctx.get("metrics"))

        return Result(
            trace_id=trace_id,
            kernel_version=KERNEL_VERSION,
            decision=kernel_decision,
            reason_code="ENGINE_DECISION",
            reason_message=f"engine_decision={raw_decision}",
            artifacts_hash=artifacts_hash,
            audit_path=audit_path,
            required_human_gate=required_human_gate,
            human_gate=human_gate,
            metrics=metrics,
            ssr=ssr,
            engine_decision_raw=raw_decision,
            engine_registry_ok=registry_ok,
            acp_status=acp_status,
            acp_ambiguity=acp_ambiguity,
            hash_chain=hash_chain,
            replay_ref=None,
            artifact_files=[],
        )

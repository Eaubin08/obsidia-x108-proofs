from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from obsidia_os0.contract import validate as validate_contract
from obsidia_os0.sandbox import Sandbox

from .x108 import X108Gate, X108Check
from .parse_input import parse_input


@dataclass
class OS1Decision:
    """Retour OS1 (décision + SSR)."""

    decision: str  # ACT | HOLD | REJECT
    ssr: str
    contract_ok: bool
    x108: Optional[X108Check]
    os0_result: Optional[Dict[str, Any]]


def _format_contract_violation(e: Exception) -> str:
    return f"CONTRACT_VIOLATION: {type(e).__name__}: {e}"


def run_request(
    *,
    raw_input: str,
    contract: object | None = None,
    sandbox: Optional[Sandbox] = None,
    x108_gate: Optional[X108Gate] = None,
    x108_ctx: Optional[Dict[str, Any]] = None,
) -> OS1Decision:
    """Pipeline OS1 minimal.

    1) parse_input -> IR
    2) validate Contract
    3) X108 check (HOLD/ACT) si gate fourni
    4) exécution OS0 sandbox si ACT
    5) SSR explicative
    """

    sb = sandbox or Sandbox()

    # 1) Traduction vers IR (déterminisme)
    try:
        ir = parse_input(raw_input)
    except Exception as e:
        return OS1Decision(
            decision="REJECT",
            ssr=f"PARSE_ERROR: {type(e).__name__}: {e}",
            contract_ok=False,
            x108=None,
            os0_result=None,
        )

    # parse_input returns a dict: {"program": [IR nodes], "meta": {...}}
    program = ir.get("program", ir)
    meta = ir.get("meta", {}) if isinstance(ir, dict) else {}

    # 2) Contrat
    try:
        validate_contract(program)
    except Exception as e:
        return OS1Decision(
            decision="REJECT",
            ssr=_format_contract_violation(e),
            contract_ok=False,
            x108=None,
            os0_result=None,
        )

    # 3) X108
    x108_res: Optional[X108Check] = None
    if x108_gate is not None:
        ctx = x108_ctx or {}
        # mapping tolérant
        irreversible = bool(ctx.get("irreversible", True))
        time_elapsed = float(ctx.get("time_elapsed", 0.0))
        ist = float(ctx.get("ist", ctx.get("IST", 0.0)))
        cmec = float(ctx.get("cmec", ctx.get("CMEC", 0.0)))
        x108_res = x108_gate.check(elapsed_s=time_elapsed, irreversible=irreversible, note=f"IST={ist} CMEC={cmec}")
        if x108_res.decision == "HOLD":
            ssr = (
                "X108_HOLD\n"
                f"reason: {x108_res.reason}\n"
                f"inputs: time_elapsed={time_elapsed}, IST={ist}, CMEC={cmec}, irreversible={irreversible}\n"
                "action: aucune exécution (OS0 non appelé)"
            )
            return OS1Decision(
                decision="HOLD",
                ssr=ssr,
                contract_ok=True,
                x108=x108_res,
                os0_result=None,
            )

    # 4) Exécution OS0
    try:
        os0_out = sb.run(program)

        if os0_out is None:
            os0_out = {
                "ok": True,
                "status": "OK",
                "state": dict(getattr(sb, "state", {})),
                "log": [
                    {
                        "step": getattr(l, "step", None),
                        "op": getattr(l, "op", None),
                        "detail": getattr(l, "detail", None),
                    }
                    for l in getattr(sb, "log", [])
                ],
            }

        # If sandbox returns an IR node (e.g., RETURN(...)), normalize to dict.
        if not isinstance(os0_out, dict):
            os0_out = {
                "ok": True,
                "status": "RETURN",
                "value": getattr(os0_out, "value", repr(os0_out)),
                "state": dict(getattr(sb, "state", {})),
            }

    except Exception as e:
        ssr = "REJECT\n" + f"os0_error: {type(e).__name__}: {e}"
 
        return OS1Decision(decision="REJECT", ssr=ssr, contract_ok=True, x108=x108_res, os0_result=None)

    # 5) SSR
    ssr = "ACT\n"
    ssr += "contract: OK\n"
    if x108_res is not None:
        ssr += f"x108: ACT ({x108_res.reason})\n"
    else:
        ssr += "x108: SKIP\n"
    ir_type = meta.get("intent")
    if not ir_type and isinstance(program, list) and program:
        first = program[0] if isinstance(program[0], dict) else {}
        ir_type = first.get("type")
    ssr += f"ir.type: {ir_type}\n"
    ssr += f"os0.status: {os0_out.get('status', 'OK')}\n"

    return OS1Decision(
        decision="ACT",
        ssr=ssr,
        contract_ok=True,
        x108=x108_res,
        os0_result=os0_out,
    )

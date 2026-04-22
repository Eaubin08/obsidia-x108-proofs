from __future__ import annotations
import sys, tempfile
from pathlib import Path
from typing import Dict, Any

VENDOR_DIR = Path(__file__).resolve().parent / "vendor"
if str(VENDOR_DIR) not in sys.path:
    sys.path.insert(0, str(VENDOR_DIR))

# Purge conflicting global imports (this repo can already ship obsidia_os0/os1 from other packs)
for k in list(sys.modules.keys()):
    if k == "proof" or k.startswith("proof.") or k == "obsidia_os0" or k.startswith("obsidia_os0.") or k == "obsidia_os1" or k.startswith("obsidia_os1."):
        sys.modules.pop(k, None)

from proof.runner import build, Refusal  # type: ignore

SUPPORTED_INTENT_NAMES = {"OS_TRAD", "OS_TRAD_BUILD"}

def os_trad_propose(request_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    PROPOSE module.
    Executes only when request.intent.type == PROPOSE and request.intent.name in SUPPORTED_INTENT_NAMES.
    It compiles a .os spec (spec_text) to target (python|js) and injects the result into context.proposals.OS_TRAD.
    """
    intent = request_dict.get("intent", {}) or {}
    if intent.get("type") != "PROPOSE":
        return request_dict
    if intent.get("name") not in SUPPORTED_INTENT_NAMES:
        return request_dict

    payload = intent.get("payload", {}) or {}
    spec_text = payload.get("spec_text")
    target = payload.get("target")

    proposal = {"ok": False, "refusal": None, "info": None, "generated": None}

    if not isinstance(spec_text, str) or not spec_text.strip():
        proposal["refusal"] = "REFUSE_OS_TRAD:missing_spec_text"
        return _inject(request_dict, proposal)
    if target not in ("python","js"):
        proposal["refusal"] = "REFUSE_OS_TRAD:invalid_target"
        return _inject(request_dict, proposal)

    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        spec_path = td_path / "spec.os"
        spec_path.write_text(spec_text, encoding="utf-8")
        out_dir = td_path / "artifacts" / target / "spec"

        try:
            info = build(spec_path, target, out_dir)
        except Refusal as r:
            proposal["refusal"] = r.reason
            return _inject(request_dict, proposal)

        entry = info.get("entry") or ("app.py" if target == "python" else "app.js")
        entry_path = out_dir / entry
        generated = None
        if entry_path.exists():
            generated = {"entry_file": entry, "code": entry_path.read_text(encoding="utf-8")}

        proposal.update({"ok": True, "info": info, "generated": generated})
        return _inject(request_dict, proposal)

def _inject(request_dict: Dict[str, Any], proposal: Dict[str, Any]) -> Dict[str, Any]:
    ctx = dict(request_dict.get("context", {}) or {})
    proposals = dict(ctx.get("proposals", {}) or {})
    proposals["OS_TRAD"] = proposal
    ctx["proposals"] = proposals
    out = dict(request_dict)
    out["context"] = ctx
    return out

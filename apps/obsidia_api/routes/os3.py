"""OS3 routes — readonly proof artifact viewer (real freeze reports from docs/runtime)."""
import re
from pathlib import Path
from fastapi import APIRouter
from apps.obsidia_api.safe_response import safe_backend_response

router = APIRouter(prefix="/api/os3", tags=["os3"])

_DOCS_RUNTIME = Path(__file__).parent.parent.parent.parent / "docs" / "runtime"

_BOUNDARY = {
    "readonly": True,
    "decision_authority": "KX108_ONLY",
    "emits_act": False,
    "emits_verdict": False,
    "memory_write": False,
    "graphiti_write": False,
    "kernel_mutation": False,
    "x108_mutation": False,
    "execution_allowed": False,
}


def _list_freeze_reports(n: int = 10) -> list[dict]:
    try:
        mds = sorted(_DOCS_RUNTIME.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
        result = []
        for p in mds[:n]:
            name = p.name
            m = re.search(r"(\d{8}_\d{6})", name)
            date_tag = m.group(1) if m else ""
            result.append({"filename": name, "date_tag": date_tag, "type": "FREEZE_REPORT"})
        return result
    except Exception:
        return []


@router.get("/tickets")
async def os3_tickets():
    reports = _list_freeze_reports(10)
    return safe_backend_response({
        "tickets": reports,
        "artifact_count": len(reports),
        "latest_report": reports[0]["filename"] if reports else "",
        "source": "docs/runtime",
        "type": "FREEZE_REPORT_MANIFEST",
        "proof_engine": "OS3_V1",
        **_BOUNDARY,
    }, source="REAL_FREEZE_REPORTS")


@router.get("/replay/{ticket_id}")
async def os3_replay(ticket_id: str):
    return safe_backend_response({
        "ticket_id": ticket_id,
        "replay_status": "NOT_RUN",
        "source": "docs/runtime",
        **_BOUNDARY,
    }, source="REAL_FREEZE_REPORTS")

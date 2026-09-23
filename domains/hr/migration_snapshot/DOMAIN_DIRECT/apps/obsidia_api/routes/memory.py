"""Memory routes — full workflow: status, sources, candidates, promotion policy."""
from fastapi import APIRouter
from pydantic import BaseModel
from apps.obsidia_api.runtime_loader import load_runtime_components
from apps.obsidia_api.safe_response import safe_backend_response

router = APIRouter(prefix="/api/memory", tags=["memory"])


@router.get("")
async def memory_root():
    rt = load_runtime_components()
    return safe_backend_response({
        "candidates": [], "total": 0, "mode": "CANDIDATE_ONLY",
        "auto_promotion": False, "graphiti_write": False,
        "memory_write": False,
    }, source="REAL_BACKEND" if rt["memory"]["status"] == "REAL_MODULE" else "BACKEND_STUB")


@router.get("/status")
async def memory_status():
    rt = load_runtime_components()
    ms = rt["memory"]["status"]
    return safe_backend_response({
        "status": "ok" if ms == "REAL_MODULE" else "BACKEND_STUB",
        "mode": "readonly_candidate_only",
        "memory_write": False,
        "auto_promotion": False,
        "decision_authority": "KX108_ONLY",
        "brody_decides": False,
        "graphiti_write": False,
        "candidate_only": True,
        "promotion_requires_human_review": True,
    }, source="REAL_BACKEND" if ms == "REAL_MODULE" else "BACKEND_STUB")


@router.get("/sources")
async def memory_sources():
    rt = load_runtime_components()
    sources = []
    if rt["memory"]["MemorySourceType"]:
        try:
            MemorySourceType = rt["memory"]["MemorySourceType"]
            sources = [{"type": s.value, "label": s.name} for s in MemorySourceType]
        except Exception:
            pass
    return safe_backend_response({"sources": sources}, source="REAL_BACKEND" if sources else "BACKEND_STUB")


@router.get("/candidates")
async def memory_candidates():
    rt = load_runtime_components()
    candidates = []
    if rt["memory"]["build_memory_candidate_v2"] and rt["memory"]["MemorySourceType"]:
        try:
            MemorySourceType = rt["memory"]["MemorySourceType"]
            c = rt["memory"]["build_memory_candidate_v2"](
                source_id="api_query",
                source_type=MemorySourceType.BRODY_RUNTIME,
                content="API memory query",
            )
            candidates.append({
                "candidate_id": c.candidate_id,
                "source_type": c.source_type.value if hasattr(c.source_type, 'value') else str(c.source_type),
                "content_summary": getattr(c, "content_summary", ""),
                "status": c.status.value if hasattr(c.status, 'value') else str(c.status),
                "memory_write_allowed": c.memory_write_allowed,
                "auto_promotion_allowed": c.auto_promotion_allowed,
            })
        except Exception:
            pass
    return safe_backend_response({
        "candidates": candidates, "total": len(candidates),
        "mode": "CANDIDATE_ONLY", "auto_promotion": False, "graphiti_write": False,
    }, source="REAL_BACKEND" if candidates else "BACKEND_STUB")


class MemoryCandidateRequest(BaseModel):
    message: str
    source: str = "brody"


@router.post("/candidate/from-message")
async def memory_candidate_from_message(req: MemoryCandidateRequest):
    rt = load_runtime_components()
    if rt["memory"]["build_memory_candidate_v2"] and rt["memory"]["MemorySourceType"]:
        try:
            MemorySourceType = rt["memory"]["MemorySourceType"]
            c = rt["memory"]["build_memory_candidate_v2"](
                source_id=f"msg_{hash(req.message) & 0xFFFF:04x}",
                source_type=MemorySourceType.BRODY_RUNTIME,
                content=req.message,
            )
            return safe_backend_response({
                "candidate_id": c.candidate_id,
                "status": c.status.value if hasattr(c.status, 'value') else str(c.status),
                "memory_write_allowed": c.memory_write_allowed,
                "auto_promotion_allowed": c.auto_promotion_allowed,
            }, source="REAL_BACKEND")
        except Exception:
            pass
    return safe_backend_response({"status": "BACKEND_STUB"}, source="BACKEND_STUB")


@router.get("/candidate-ledger")
async def memory_candidate_ledger():
    return safe_backend_response({
        "ledger": [],
        "mode": "APPEND_ONLY_DRY_RUN",
        "readonly": True,
    }, source="BACKEND_STUB")


@router.get("/promotion-policy")
async def memory_promotion_policy():
    rt = load_runtime_components()
    policy = {"auto_promotion_blocked": True, "requires_human_review": True, "promotion_allowed": False}
    if rt["memory"]["evaluate_promotion_policy"] and rt["memory"]["build_memory_candidate_v2"] and rt["memory"]["MemorySourceType"]:
        try:
            MemorySourceType = rt["memory"]["MemorySourceType"]
            c = rt["memory"]["build_memory_candidate_v2"](
                source_id="policy_check",
                source_type=MemorySourceType.BRODY_RUNTIME,
                content="Policy test",
            )
            d = rt["memory"]["evaluate_promotion_policy"](c)
            policy = {
                "auto_promotion_blocked": d.auto_promotion_blocked,
                "requires_human_review": d.requires_human_review,
                "promotion_allowed": d.promotion_allowed,
                "reason": getattr(d, "reason", ""),
            }
        except Exception:
            pass
    return safe_backend_response(policy, source="REAL_BACKEND")

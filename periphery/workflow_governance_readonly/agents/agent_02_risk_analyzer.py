from __future__ import annotations

from typing import Any, Dict, List, Tuple

from ..constants import AGENT_IDS, CRITICAL_ACTION_KEYWORDS
from ..models import AgentSignal

AGENT_ROLE = {
    "id": AGENT_IDS[1],
    "name": "Risk / irreversibility analyzer",
    "purpose": "Mark risk candidates and irreversibility signals before X108 review.",
    "authority": "none; advisory risk signal only",
    "output": "criticality candidates, risk categories, X108 review hints",
}


def _risk_hits(text: str) -> Tuple[List[str], List[str]]:
    lower = text.lower()
    categories: list[str] = []
    hits: list[str] = []
    for category, keywords in CRITICAL_ACTION_KEYWORDS.items():
        local = [kw for kw in keywords if kw.lower() in lower]
        if local:
            categories.append(category)
            hits.extend(local)
    return sorted(set(categories)), sorted(set(hits))


def _criticality(categories: List[str], hits: List[str], text: str) -> Tuple[str, float]:
    lower = text.lower()
    score = 0.0
    score += min(len(hits), 6) * 0.10
    if any(c in categories for c in ["financial_transfer", "contract_commitment", "production_change"]):
        score += 0.35
    if any(c in categories for c in ["destructive_operation", "access_security", "regulated_data"]):
        score += 0.45
    if any(w in lower for w in ["immediate", "urgent", "without review", "sans validation", "prod", "public"]):
        score += 0.15
    score = min(score, 1.0)
    if score >= 0.75:
        return "critical", score
    if score >= 0.45:
        return "high", score
    if score >= 0.20:
        return "medium", score
    return "low", score


def analyze_risk(extraction_payload: Dict[str, Any]) -> AgentSignal:
    """Agent 2 — Risk analyzer.

    The output is not a block/allow decision. It is a candidate risk annotation
    that prepares later evidence requirements and X108 ingress.
    """
    steps = extraction_payload.get("steps", [])
    annotated: List[Dict[str, Any]] = []
    critical_step_ids: List[str] = []
    category_counts: Dict[str, int] = {}

    for step in steps:
        text = f"{step.get('title','')} {step.get('description','')}"
        categories, hits = _risk_hits(text)
        criticality, score = _criticality(categories, hits, text)
        entry = dict(step)
        entry["criticality"] = criticality
        entry["criticality_score"] = round(score, 3)
        entry["risk_categories"] = categories
        entry["irreversibility_signals"] = hits
        entry["x108_review_required"] = criticality in {"high", "critical"}
        entry["risk_reasons"] = [f"{cat}:{hit}" for cat in categories for hit in hits if hit]
        entry["candidate_only"] = True
        for cat in categories:
            category_counts[cat] = category_counts.get(cat, 0) + 1
        if entry["x108_review_required"]:
            critical_step_ids.append(entry["step_id"])
        annotated.append(entry)

    payload = {
        "risk_annotated_steps": annotated,
        "critical_step_ids": critical_step_ids,
        "critical_count": len(critical_step_ids),
        "risk_category_counts": category_counts,
        "role_manifest": AGENT_ROLE,
        "risk_policy_note": "criticality is advisory only; X108 remains sole decision authority",
    }
    return AgentSignal(
        agent_id=AGENT_IDS[1],
        signal_family="risk_signal",
        status="RISK_ANALYSIS_READY",
        summary=f"Annotated {len(annotated)} steps; {len(critical_step_ids)} require X108 review candidate handling.",
        payload=payload,
        confidence=0.72 if annotated else 0.0,
        warnings=[] if annotated else ["NO_RISK_INPUT_STEPS"],
        trace=["candidate_steps", "keyword_category_scan", "criticality_scoring", "x108_review_candidate_flags"],
        role="RISK_ANALYZER_READONLY",
    )

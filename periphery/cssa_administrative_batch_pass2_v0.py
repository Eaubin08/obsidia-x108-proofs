"""Read-only batch adapter for CSSA historical administrative assessments."""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass
from typing import Mapping
from periphery.cssa_historical_semantic_adapter_v0 import project_historical_cssa_assessment_v0
from periphery.cssa_historical_native_intake_draft_v0 import draft_cssa_historical_native_intake_v0

@dataclass(frozen=True)
class CssaAdministrativeBindingV0:
    source_ref: str | None
    evidence_refs: tuple[str, ...]
    owner_ref: str | None
    occurred_at: str | None
    due_at: str | None

def assemble_cssa_administrative_batch_v0(assessments, bindings: Mapping[str, CssaAdministrativeBindingV0]) -> dict:
    """Produce non-applied canonical intake plans, retaining all refusal reasons."""
    entries = []
    seen = set()
    for assessment in assessments:
        proposal = project_historical_cssa_assessment_v0(assessment)
        key = proposal.source_family + ":" + proposal.source_case_id
        if key in seen:
            raise ValueError("CSSA_PASS2_DUPLICATE_CASE")
        seen.add(key)
        binding = bindings.get(key)
        if binding is None:
            entries.append({"id": key, "status": proposal.disposition, "reasons": list(proposal.reasons) + ["SOURCE_BINDING_MISSING"], "plan": None})
            continue
        if not isinstance(binding, CssaAdministrativeBindingV0):
            raise ValueError("CSSA_PASS2_BINDING_TYPE_INVALID")
        draft = draft_cssa_historical_native_intake_v0(
            proposal, observed_source_ref=binding.source_ref,
            observed_evidence_refs=binding.evidence_refs,
            occurred_at=binding.occurred_at, due_at=binding.due_at,
            proposed_owner_ref=binding.owner_ref)
        entries.append({"id": key, "status": draft["status"],
                        "reasons": list(proposal.reasons) + list(draft["reasons"]),
                        "plan": draft["native_plan"]})
    return {"status": "REVIEW_ONLY", "entries": entries,
            "totals": dict(Counter(x["status"] for x in entries)),
            "native_writes": 0, "external_effect": False,
            "approval_granted": False, "decision_authority": "KX108_ONLY"}
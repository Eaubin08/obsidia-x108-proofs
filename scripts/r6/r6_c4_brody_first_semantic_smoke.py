#!/usr/bin/env python3
"""R6-C4 canonical Brody-first semantic smoke.

This smoke proves the canonical cognitive order for the two contrastive memory
queries:
    input -> Brody/SENS V1 -> Brody pre-reasoning
and asserts that the Qwen fallback is not called when Brody/SENS is sufficient.

No model call is performed by this smoke.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.obsidia_api.brody_real_response_pipeline import (
    run_brody_real_response_pipeline,
)
from periphery.cognition.semantic_role_producer_v0 import (
    resolve_semantic_role_projection_v0,
)
from periphery.cognition.semantic_roles_v0 import SemanticRoleKindV0


PROBES = (
    {
        "probe_id": "MEMORY_AS_FOCUS",
        "utterance": "Explique ce que tu sais en mémoire sur Obsidia, et détaille.",
        "expected_surfaces": {
            "FOCUS": "mémoire",
            "SCOPE": "Obsidia",
            "OPERATION": "Explique",
            "QUALIFIER": "détaille",
        },
    },
    {
        "probe_id": "MEMORY_AS_SOURCE",
        "utterance": "Explique Obsidia en utilisant ta mémoire.",
        "expected_surfaces": {
            "FOCUS": "Obsidia",
            "OPERATION": "Explique",
            "SOURCE_OR_INSTRUMENT": "mémoire",
        },
    },
)


def _surface_for_role(raw: str, projection: Any, role_name: str) -> str | None:
    role = SemanticRoleKindV0(role_name)
    binding = projection.binding(role)
    if binding is None or binding.resolved_value is None:
        return None
    if len(binding.candidates) != 1:
        return None
    span = binding.candidates[0].source_span
    if span is None:
        return None
    return raw[span[0]:span[1]]


def _ctx_hash(ctx: dict[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(
            ctx,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    ).hexdigest()


def build_brody_first_semantic_smoke_report(
    *,
    resolver: Callable[..., Any] = resolve_semantic_role_projection_v0,
    brody_runner: Callable[..., dict[str, Any]] = run_brody_real_response_pipeline,
) -> dict[str, Any]:
    evidence: list[dict[str, Any]] = []
    qwen_calls = 0

    def _forbidden_qwen(_raw: str) -> dict[str, Any]:
        nonlocal qwen_calls
        qwen_calls += 1
        return {
            "success": False,
            "status": "forbidden_in_brody_first_smoke",
            "text": "",
            "error": "BRODY_SENS_INSUFFICIENT_WOULD_ESCALATE",
        }

    for probe in PROBES:
        raw = probe["utterance"]
        produced = resolver(
            raw_utterance=raw,
            brody_structured_output=None,
            qwen_available=True,
            qwen_caller=_forbidden_qwen,
        )

        row: dict[str, Any] = {
            "probe_id": probe["probe_id"],
            "selected_producer": produced.selected_producer,
            "qwen_attempted": produced.qwen_attempted,
            "roles_match": False,
            "brody_pre_reasoning_role_context": False,
            "brody_effective_role_context_match": False,
            "resolved_roles_not_reopened_as_unknowns": False,
            "passed": False,
        }

        interpretation = produced.interpretation
        projection = (
            interpretation.projection
            if interpretation is not None
            else None
        )
        if projection is None:
            row["errors"] = list(produced.errors)
            evidence.append(row)
            continue

        observed = {
            role: _surface_for_role(raw, projection, role)
            for role in probe["expected_surfaces"]
        }
        row["observed_role_surfaces"] = observed
        row["roles_match"] = all(
            str(observed.get(role) or "").casefold() == expected.casefold()
            for role, expected in probe["expected_surfaces"].items()
        )

        brody = brody_runner(message=raw)
        row["brody_response_source"] = brody.get("response_source")
        row["brody_semantic_role_source"] = brody.get("semantic_role_source")

        pre = brody.get("pre_reasoning_snapshot") or {}
        pre_ctx = pre.get("semantic_role_context")
        effective_ctx = brody.get("semantic_role_context")
        expected_ctx = projection.to_brody_context()

        row["brody_pre_reasoning_role_context"] = bool(
            isinstance(pre_ctx, dict)
            and pre_ctx.get("decision_authority") == "KX108_ONLY"
            and pre_ctx.get("readonly") is True
            and pre_ctx.get("allowed_to_decide") is False
            and pre_ctx.get("allowed_to_act") is False
        )
        row["brody_effective_role_context_match"] = bool(
            isinstance(effective_ctx, dict)
            and _ctx_hash(effective_ctx) == _ctx_hash(expected_ctx)
        )

        resolution_targets = {
            str(item).casefold()
            for item in (
                (pre.get("reasoning_directive") or {}).get(
                    "resolution_targets",
                    [],
                )
                or []
            )
        }
        expected_role_terms = {
            str(surface).casefold()
            for surface in probe["expected_surfaces"].values()
        }
        row["remaining_resolution_targets"] = sorted(resolution_targets)
        row["resolved_roles_not_reopened_as_unknowns"] = (
            not bool(resolution_targets & expected_role_terms)
        )

        row["passed"] = bool(
            produced.selected_producer == "BRODY_SENS_V1"
            and produced.qwen_attempted is False
            and row["roles_match"]
            and row["brody_pre_reasoning_role_context"]
            and row["brody_effective_role_context_match"]
            and row["resolved_roles_not_reopened_as_unknowns"]
        )
        evidence.append(row)

    passed = sum(1 for row in evidence if row.get("passed"))
    verified = passed == len(PROBES) and qwen_calls == 0

    return {
        "artifact": "r6_c4_brody_first_semantic_smoke",
        "status": (
            "BRODY_FIRST_SEMANTIC_PATH_VERIFIED"
            if verified
            else "BRODY_FIRST_SEMANTIC_PATH_FAILED_CLOSED"
        ),
        "brody_first_verified": verified,
        "probe_count": len(PROBES),
        "passed_probe_count": passed,
        "qwen_calls": qwen_calls,
        "decision_authority": "KX108_ONLY",
        "readonly": True,
        "allowed_to_decide": False,
        "allowed_to_act": False,
        "memory_write": False,
        "kernel_mutation": False,
        "probes": evidence,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    report = build_brody_first_semantic_smoke_report()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    return 0 if report["brody_first_verified"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

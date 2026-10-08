#!/usr/bin/env python3
"""R6-C3 real local-Qwen semantic smoke.

Runs two contrastive French utterances through the existing R6 local-Qwen
transport, validates the model output through R6-C1, then attaches the accepted
projection to the canonical in-process Brody readonly pipeline.

No raw model response is persisted: only SHA-256, validated semantic projection,
Brody context hash, bounded metadata, and pass/fail evidence are emitted.
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
from periphery.cognition.semantic_role_interpreter_v0 import (
    interpret_semantic_roles_v0,
)
from periphery.cognition.semantic_role_producer_v0 import (
    qwen_semantic_roles_available_v0,
    qwen_semantic_roles_call_v0,
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


def _bounded_structured_diagnostic(raw_model_text: str) -> dict[str, Any]:
    """Expose only bounded JSON structure for failed C1 diagnostics.

    Never persists free-form model text. Values are limited to role status,
    candidate abstract value and candidate surface.
    """
    try:
        payload = json.loads(raw_model_text)
    except Exception:
        return {"json_parseable": False}
    if not isinstance(payload, dict):
        return {"json_parseable": True, "top_level_type": type(payload).__name__}

    roles = payload.get("roles")
    role_summary: dict[str, Any] = {}
    if isinstance(roles, dict):
        for role_name, role_payload in roles.items():
            if not isinstance(role_payload, dict):
                role_summary[str(role_name)] = {"type": type(role_payload).__name__}
                continue
            candidates = role_payload.get("candidates")
            safe_candidates = []
            if isinstance(candidates, list):
                for candidate in candidates[:4]:
                    if isinstance(candidate, dict):
                        safe_candidates.append({
                            "value": str(candidate.get("value") or "")[:80],
                            "surface": str(candidate.get("surface") or "")[:80],
                        })
            role_summary[str(role_name)] = {
                "status": str(role_payload.get("status") or "")[:40],
                "candidates": safe_candidates,
            }

    return {
        "json_parseable": True,
        "top_level_keys": sorted(str(key) for key in payload.keys()),
        "schema": str(payload.get("schema") or "")[:120],
        "schema_version": str(payload.get("schema_version") or "")[:80],
        "producer": str(payload.get("producer") or "")[:80],
        "producer_version": str(payload.get("producer_version") or "")[:80],
        "roles": role_summary,
    }


def _surface_for_role(raw: str, projection: Any, role_name: str) -> str | None:
    role = SemanticRoleKindV0(role_name)
    binding = projection.binding(role)
    if binding is None or binding.resolved_value is None or len(binding.candidates) != 1:
        return None
    span = binding.candidates[0].source_span
    if span is None:
        return None
    return raw[span[0]:span[1]]


def build_real_qwen_semantic_smoke_report(
    *,
    availability_fn: Callable[[], bool] = qwen_semantic_roles_available_v0,
    qwen_call_fn: Callable[[str], dict[str, Any]] = qwen_semantic_roles_call_v0,
    brody_runner: Callable[..., dict[str, Any]] = run_brody_real_response_pipeline,
) -> dict[str, Any]:
    if not availability_fn():
        return {
            "artifact": "r6_c3_real_qwen_semantic_smoke",
            "status": "BLOCKED_LOCAL_MODEL_NOT_RUNNING",
            "real_qwen_verified": False,
            "probe_count": len(PROBES),
            "passed_probe_count": 0,
            "qwen_attempted": False,
            "decision_authority": "KX108_ONLY",
            "readonly": True,
            "allowed_to_decide": False,
            "allowed_to_act": False,
            "memory_write": False,
            "kernel_mutation": False,
            "blockers": ["QWEN_LOCAL_LOOPBACK_NOT_AVAILABLE"],
            "probes": [],
        }

    evidence: list[dict[str, Any]] = []
    tokens_total = 0

    for probe in PROBES:
        raw = probe["utterance"]
        qwen = qwen_call_fn(raw)
        raw_model_text = str(qwen.get("text") or "")
        qwen_hash = (
            hashlib.sha256(raw_model_text.encode("utf-8")).hexdigest()
            if raw_model_text
            else "UNKNOWN"
        )
        tokens = qwen.get("local_model_tokens")
        if isinstance(tokens, int):
            tokens_total += tokens

        row: dict[str, Any] = {
            "probe_id": probe["probe_id"],
            "utterance_sha256": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
            "qwen_success": bool(qwen.get("success")),
            "qwen_status": qwen.get("status"),
            "qwen_output_sha256": qwen_hash,
            "local_model_tokens": tokens,
            "qwen_elapsed_ms": qwen.get("elapsed_ms"),
            "semantic_interpretation_accepted": False,
            "expected_roles_match": False,
            "brody_context_attached": False,
            "passed": False,
        }

        if not qwen.get("success"):
            row["error"] = str(qwen.get("error") or "QWEN_CALL_FAILED")
            evidence.append(row)
            continue

        interpreted = interpret_semantic_roles_v0(
            raw_utterance=raw,
            structured_output=raw_model_text,
            source_refs=(f"r6-c3:{probe['probe_id']}:qwen-local",),
        )
        row["semantic_status"] = interpreted.status
        row["semantic_errors"] = list(interpreted.errors)

        projection = interpreted.projection
        if projection is None:
            row["bounded_structured_diagnostic"] = _bounded_structured_diagnostic(
                raw_model_text
            )
            evidence.append(row)
            continue

        row["semantic_interpretation_accepted"] = True
        observed_surfaces = {
            role: _surface_for_role(raw, projection, role)
            for role in probe["expected_surfaces"]
        }
        row["observed_role_surfaces"] = observed_surfaces
        row["expected_roles_match"] = all(
            str(observed_surfaces.get(role) or "").casefold()
            == expected.casefold()
            for role, expected in probe["expected_surfaces"].items()
        )

        try:
            brody = brody_runner(
                message=raw,
                semantic_role_projection=projection,
            )
        except Exception as exc:
            row["brody_error"] = f"{type(exc).__name__}:{exc}"
            evidence.append(row)
            continue

        semantic_hash = brody.get("semantic_role_projection_sha256")
        semantic_ctx = brody.get("semantic_role_context")
        row["brody_context_attached"] = bool(
            semantic_hash
            and semantic_ctx
            and semantic_ctx.get("decision_authority") == "KX108_ONLY"
            and semantic_ctx.get("readonly") is True
            and semantic_ctx.get("allowed_to_decide") is False
            and semantic_ctx.get("allowed_to_act") is False
            and semantic_ctx.get("memory_write") is False
            and semantic_ctx.get("kernel_mutation") is False
        )
        row["brody_semantic_role_projection_sha256"] = semantic_hash
        row["brody_response_source"] = brody.get("response_source")
        row["passed"] = bool(
            row["semantic_interpretation_accepted"]
            and row["expected_roles_match"]
            and row["brody_context_attached"]
        )
        evidence.append(row)

    passed = sum(1 for row in evidence if row.get("passed"))
    verified = passed == len(PROBES)
    return {
        "artifact": "r6_c3_real_qwen_semantic_smoke",
        "status": (
            "REAL_QWEN_SEMANTIC_SMOKE_VERIFIED"
            if verified
            else "REAL_QWEN_SEMANTIC_SMOKE_FAILED_CLOSED"
        ),
        "real_qwen_verified": verified,
        "probe_count": len(PROBES),
        "passed_probe_count": passed,
        "qwen_attempted": True,
        "local_model_tokens_total": tokens_total,
        "raw_model_output_persisted": False,
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
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=90.0,
        help="Per-probe local Qwen inference timeout. Loopback only.",
    )
    args = parser.parse_args()

    def _timed_qwen_call(raw_utterance: str) -> dict[str, Any]:
        return qwen_semantic_roles_call_v0(
            raw_utterance,
            timeout=max(1.0, float(args.timeout_seconds)),
        )

    report = build_real_qwen_semantic_smoke_report(
        qwen_call_fn=_timed_qwen_call,
    )
    report["qwen_timeout_seconds"] = max(1.0, float(args.timeout_seconds))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    return 0 if report["status"] != "REAL_QWEN_SEMANTIC_SMOKE_FAILED_CLOSED" else 1


if __name__ == "__main__":
    raise SystemExit(main())

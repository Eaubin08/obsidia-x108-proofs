import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "r6" / "r6_c3_real_qwen_semantic_smoke.py"

SPEC = importlib.util.spec_from_file_location("r6_c3_real_qwen_semantic_smoke", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def _qwen_payload_for(raw):
    if "ce que tu sais en mémoire" in raw:
        roles = {
            "FOCUS": {
                "status": "RESOLVED",
                "candidates": [{"value": "MEMORY", "surface": "mémoire"}],
            },
            "SCOPE": {
                "status": "RESOLVED",
                "candidates": [{"value": "OBSIDIA", "surface": "Obsidia"}],
            },
            "OPERATION": {
                "status": "RESOLVED",
                "candidates": [{"value": "EXPLAIN", "surface": "Explique"}],
            },
            "QUALIFIER": {
                "status": "RESOLVED",
                "candidates": [{"value": "DETAILED", "surface": "détaille"}],
            },
        }
    else:
        roles = {
            "FOCUS": {
                "status": "RESOLVED",
                "candidates": [{"value": "OBSIDIA", "surface": "Obsidia"}],
            },
            "OPERATION": {
                "status": "RESOLVED",
                "candidates": [{"value": "EXPLAIN", "surface": "Explique"}],
            },
            "SOURCE_OR_INSTRUMENT": {
                "status": "RESOLVED",
                "candidates": [{"value": "MEMORY", "surface": "mémoire"}],
            },
        }
    return {
        "success": True,
        "status": "ok",
        "text": json.dumps(
            {
                "schema": "OBSIDIA_SEMANTIC_ROLE_INTERPRETATION_V0",
                "producer": "QWEN_LOCAL",
                "producer_version": "TEST",
                "roles": roles,
            },
            ensure_ascii=False,
        ),
        "local_model_tokens": 12,
    }


def _brody(*, message, semantic_role_projection):
    ctx = semantic_role_projection.to_brody_context()
    return {
        "semantic_role_projection_sha256": "a" * 64,
        "semantic_role_context": ctx,
        "response_source": "TEST_BRODY",
    }


def test_c3_blocks_cleanly_when_local_qwen_not_running():
    report = MODULE.build_real_qwen_semantic_smoke_report(
        availability_fn=lambda: False,
        qwen_call_fn=lambda _raw: (_ for _ in ()).throw(AssertionError("must not call")),
        brody_runner=_brody,
    )
    assert report["status"] == "BLOCKED_LOCAL_MODEL_NOT_RUNNING"
    assert report["real_qwen_verified"] is False
    assert report["qwen_attempted"] is False


def test_c3_two_contrastive_probes_verify_with_grounded_qwen_output():
    report = MODULE.build_real_qwen_semantic_smoke_report(
        availability_fn=lambda: True,
        qwen_call_fn=_qwen_payload_for,
        brody_runner=_brody,
    )
    assert report["status"] == "REAL_QWEN_SEMANTIC_SMOKE_VERIFIED"
    assert report["real_qwen_verified"] is True
    assert report["passed_probe_count"] == 2
    assert report["local_model_tokens_total"] == 24
    assert report["raw_model_output_persisted"] is False
    assert all(row["expected_roles_match"] for row in report["probes"])
    assert all(row["brody_context_attached"] for row in report["probes"])


def test_c3_invalid_model_semantics_fail_closed():
    def bad_qwen(_raw):
        return {
            "success": True,
            "status": "ok",
            "text": json.dumps(
                {
                    "schema": "OBSIDIA_SEMANTIC_ROLE_INTERPRETATION_V0",
                    "producer": "QWEN_LOCAL",
                    "producer_version": "TEST",
                    "roles": {
                        "FOCUS": {
                            "status": "RESOLVED",
                            "candidates": [
                                {"value": "OBSIDIA", "surface": "NOT_IN_INPUT"}
                            ],
                        }
                    },
                }
            ),
            "local_model_tokens": 5,
        }

    report = MODULE.build_real_qwen_semantic_smoke_report(
        availability_fn=lambda: True,
        qwen_call_fn=bad_qwen,
        brody_runner=_brody,
    )
    assert report["status"] == "REAL_QWEN_SEMANTIC_SMOKE_FAILED_CLOSED"
    assert report["real_qwen_verified"] is False
    assert report["passed_probe_count"] == 0


def test_c1_rejects_markdown_wrapped_json():
    from periphery.cognition.semantic_role_interpreter_v0 import (
        interpret_semantic_roles_v0,
    )

    fence = chr(96) * 3
    result = interpret_semantic_roles_v0(
        raw_utterance="Explique Obsidia.",
        structured_output=fence + "json\n{}\n" + fence,
    )

    assert result.status == "SEMANTIC_ROLE_INTERPRETATION_REJECTED"
    assert result.projection is None
    assert "NON_JSON_OR_REASONING_WRAPPER_FORBIDDEN" in result.errors[0]

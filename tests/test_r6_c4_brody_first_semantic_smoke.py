import importlib.util
import sys
from pathlib import Path

from periphery.cognition.brody_semantic_focus_v1 import (
    build_brody_semantic_focus_projection_v1,
)

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "r6" / "r6_c4_brody_first_semantic_smoke.py"

SPEC = importlib.util.spec_from_file_location(
    "r6_c4_brody_first_semantic_smoke",
    SCRIPT,
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def _brody(message):
    projection = build_brody_semantic_focus_projection_v1(message)
    assert projection is not None
    ctx = projection.to_brody_context()
    return {
        "response_source": "TEST_BRODY",
        "semantic_role_source": "BRODY_SENS_V1",
        "semantic_role_context": ctx,
        "pre_reasoning_snapshot": {
            "semantic_role_context": ctx,
            "reasoning_directive": {
                "resolution_required": False,
                "resolution_targets": [],
            },
        },
    }


def test_c4_canonical_brody_first_path_never_calls_qwen():
    report = MODULE.build_brody_first_semantic_smoke_report(
        brody_runner=_brody,
    )

    assert report["status"] == "BRODY_FIRST_SEMANTIC_PATH_VERIFIED"
    assert report["brody_first_verified"] is True
    assert report["role_path_verified"] is True
    assert report["role_path_passed_probe_count"] == 2
    assert report["passed_probe_count"] == 2
    assert report["qwen_calls"] == 0
    assert all(
        row["selected_producer"] == "BRODY_SENS_V1"
        for row in report["probes"]
    )
    assert all(row["qwen_attempted"] is False for row in report["probes"])
    assert all(row["roles_match"] for row in report["probes"])


def test_c4_fails_closed_if_brody_does_not_carry_pre_reasoning_context():
    def broken_brody(message):
        projection = build_brody_semantic_focus_projection_v1(message)
        return {
            "response_source": "TEST_BRODY",
            "semantic_role_source": "BRODY_SENS_V1",
            "semantic_role_context": projection.to_brody_context(),
            "pre_reasoning_snapshot": {
                "semantic_role_context": None,
                "reasoning_directive": {
                    "resolution_required": False,
                    "resolution_targets": [],
                },
            },
        }

    report = MODULE.build_brody_first_semantic_smoke_report(
        brody_runner=broken_brody,
    )

    assert report["status"] == "BRODY_FIRST_SEMANTIC_PATH_FAILED_CLOSED"
    assert report["brody_first_verified"] is False
    assert report["passed_probe_count"] == 0


def test_c4_distinguishes_role_path_from_response_block():
    def blocked_brody(message):
        projection = build_brody_semantic_focus_projection_v1(message)
        ctx = projection.to_brody_context()
        return {
            "response_source": "PRE_REASONING_UNRESOLVED_SYMBOL",
            "semantic_role_source": "BRODY_SENS_V1",
            "semantic_role_context": ctx,
            "pre_reasoning_snapshot": {
                "semantic_role_context": ctx,
                "reasoning_directive": {
                    "resolution_required": True,
                    "resolution_targets": ["autre_inconnu"],
                },
            },
        }

    report = MODULE.build_brody_first_semantic_smoke_report(
        brody_runner=blocked_brody,
    )

    assert (
        report["status"]
        == "BRODY_FIRST_ROLE_PATH_VERIFIED_RESPONSE_BLOCKED"
    )
    assert report["role_path_verified"] is True
    assert report["brody_first_verified"] is False
    assert report["role_path_passed_probe_count"] == 2
    assert report["passed_probe_count"] == 0

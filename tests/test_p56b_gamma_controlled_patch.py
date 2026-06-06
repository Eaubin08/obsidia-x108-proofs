from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _default_value_for_function(path: Path, function_name: str, arg_name: str):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            args = node.args.args
            defaults = node.args.defaults
            offset = len(args) - len(defaults)
            for idx, arg in enumerate(args):
                if arg.arg == arg_name:
                    default_idx = idx - offset
                    assert default_idx >= 0
                    value = defaults[default_idx]
                    assert isinstance(value, ast.Constant)
                    return value.value
    raise AssertionError(f"{function_name}.{arg_name} not found in {path}")


def test_p56b_os2_gamma_aligned_to_os3():
    os2 = ROOT / "proofs" / "V18_3_1" / "engine_buildable_0_9_3_1" / "obsidia_os2" / "metrics.py"
    os3 = ROOT / "proofs" / "V18_3_1" / "engine_buildable_0_9_3_1" / "obsidia_structural_core" / "metrics.py"

    assert _default_value_for_function(os2, "compute_metrics_core_fixed", "gamma") == 1.0
    assert _default_value_for_function(os3, "compute_metrics", "gamma") == 1.0


def test_p56b_no_gamma_05_in_tracked_os2_metrics():
    os2 = ROOT / "proofs" / "V18_3_1" / "engine_buildable_0_9_3_1" / "obsidia_os2" / "metrics.py"
    text = os2.read_text(encoding="utf-8")
    assert "gamma=0.5" not in text
    assert "gamma=1.0" in text

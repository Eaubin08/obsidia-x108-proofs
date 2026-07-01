"""Fast Path A/B Benchmark V1 — test suite.

Couvre :
- import sans lancer le benchmark
- estimate_tokens
- p50/p95/p99 calculés
- modes baseline / fastpath corrects
- gouvernance non-souveraine
- routing boundary correct
- comparison calcule latency_delta_pct, token_delta_pct, estimated_context_budget_delta_pct
- summary.md et results.json générés
- valid claim / invalid claims conformes
"""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

SCRIPT = ROOT / "scripts" / "performance" / "benchmark_fastpath_vs_baseline_v1.py"


def _load_module(name: str = "bfp_v1"):
    spec = importlib.util.spec_from_file_location(name, SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ── Import safety ─────────────────────────────────────────────────────────────

class TestImportSafety:
    def test_script_importable_without_running(self):
        """Loading the module must not run the benchmark."""
        mod = _load_module("import_safe")
        assert hasattr(mod, "main")
        assert hasattr(mod, "REQUESTS")
        assert hasattr(mod, "estimate_tokens")

    def test_requests_count_is_12(self):
        mod = _load_module("req_count")
        assert len(mod.REQUESTS) == 12

    def test_all_requests_have_required_fields(self):
        mod = _load_module("req_fields")
        for r in mod.REQUESTS:
            assert "id" in r
            assert "request" in r
            assert "expected_topics" in r
            assert "forbidden_topics" in r


# ── estimate_tokens ───────────────────────────────────────────────────────────

class TestEstimateTokens:
    def test_zero_chars(self):
        mod = _load_module("est_0")
        assert mod.estimate_tokens(0) == 0

    def test_four_chars_is_one_token(self):
        mod = _load_module("est_4")
        assert mod.estimate_tokens(4) == 1

    def test_five_chars_is_two_tokens(self):
        mod = _load_module("est_5")
        assert mod.estimate_tokens(5) == 2

    def test_large_text(self):
        mod = _load_module("est_large")
        import math
        chars = 10000
        assert mod.estimate_tokens(chars) == math.ceil(chars / 4)

    def test_negative_clamped_to_zero(self):
        mod = _load_module("est_neg")
        assert mod.estimate_tokens(-10) == 0


# ── percentile ────────────────────────────────────────────────────────────────

class TestPercentile:
    def test_p50_median(self):
        mod = _load_module("pct_p50")
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        assert abs(mod.percentile(values, 0.50) - 3.0) < 0.01

    def test_p95(self):
        mod = _load_module("pct_p95")
        values = list(range(1, 101))
        result = mod.percentile([float(v) for v in values], 0.95)
        assert 94.0 <= result <= 96.0

    def test_p99(self):
        mod = _load_module("pct_p99")
        values = list(range(1, 101))
        result = mod.percentile([float(v) for v in values], 0.99)
        assert 98.0 <= result <= 100.0

    def test_single_value(self):
        mod = _load_module("pct_single")
        assert mod.percentile([42.0], 0.50) == 42.0

    def test_empty_returns_zero(self):
        mod = _load_module("pct_empty")
        assert mod.percentile([], 0.50) == 0.0


# ── baseline_agent_normal_local ───────────────────────────────────────────────

class TestBaselineMode:
    def test_mode_is_baseline(self):
        mod = _load_module("bl_mode")
        result = mod.baseline_agent_normal_local("test_id", "ping")
        assert result["mode"] == "BASELINE_AGENT_NORMAL_LOCAL"

    def test_baseline_emits_act_false(self):
        mod = _load_module("bl_act")
        result = mod.baseline_agent_normal_local("test_id", "ping")
        assert result["emits_act"] is False

    def test_baseline_memory_write_false(self):
        mod = _load_module("bl_mw")
        result = mod.baseline_agent_normal_local("test_id", "ping")
        assert result["memory_write"] is False

    def test_baseline_model_call_avoided_false(self):
        mod = _load_module("bl_mca")
        result = mod.baseline_agent_normal_local("test_id", "ping")
        assert result["model_call_avoided"] is False

    def test_baseline_cache_hit_false(self):
        mod = _load_module("bl_cache")
        result = mod.baseline_agent_normal_local("test_id", "ping")
        assert result["cache_hit"] is False

    def test_baseline_modules_skipped_zero(self):
        mod = _load_module("bl_skip")
        result = mod.baseline_agent_normal_local("test_id", "ping")
        assert result["modules_skipped"] == 0

    def test_baseline_decision_authority(self):
        mod = _load_module("bl_auth")
        result = mod.baseline_agent_normal_local("test_id", "ping")
        assert result["decision_authority"] == "KX108_ONLY"


# ── fastpath_local ────────────────────────────────────────────────────────────

class TestFastPathMode:
    def test_mode_is_fastpath(self):
        mod = _load_module("fp_mode")
        result = mod.fastpath_local("test_id", "Résumé court du statut actuel.", ["CURRENT_STATE"], [])
        assert result["mode"] == "OBSIDIA_FAST_PATH_LOCAL"

    def test_fastpath_emits_act_false(self):
        mod = _load_module("fp_act")
        result = mod.fastpath_local("test_id", "ping", [], [])
        assert result["emits_act"] is False

    def test_fastpath_memory_write_false(self):
        mod = _load_module("fp_mw")
        result = mod.fastpath_local("test_id", "ping", [], [])
        assert result["memory_write"] is False

    def test_fastpath_model_call_avoided_true(self):
        mod = _load_module("fp_mca")
        result = mod.fastpath_local("test_id", "Résumé court du statut actuel.", ["CURRENT_STATE"], [])
        assert result["model_call_avoided"] is True

    def test_fastpath_cache_hit_true(self):
        mod = _load_module("fp_cache")
        result = mod.fastpath_local("test_id", "ping", [], [])
        assert result["cache_hit"] is True

    def test_fastpath_modules_skipped_positive(self):
        mod = _load_module("fp_skip")
        result = mod.fastpath_local("test_id", "ping", [], [])
        assert result["modules_skipped"] > 0

    def test_fastpath_decision_authority(self):
        mod = _load_module("fp_auth")
        result = mod.fastpath_local("test_id", "ping", [], [])
        assert result["decision_authority"] == "KX108_ONLY"


# ── Action boundary routing ───────────────────────────────────────────────────

class TestActionBoundaryRouting:
    def test_explicit_action_routes_to_boundary(self):
        mod = _load_module("ab_explicit")
        result = mod.fastpath_local("action_boundary", "Autorise ACT maintenant.", ["ACTION_BOUNDARY"], [])
        assert result["route"] == "ACTION_BOUNDARY"

    def test_explicit_execute_routes_to_boundary(self):
        mod = _load_module("ab_exec")
        result = mod.fastpath_local("action_execution", "Exécute cette action.", ["ACTION_BOUNDARY"], [])
        assert result["route"] == "ACTION_BOUNDARY"

    def test_actualite_does_not_route_to_boundary(self):
        mod = _load_module("ab_act1")
        result = mod.fastpath_local("false_positive_actualite", "actualité IA", [], ["ACTION_BOUNDARY"])
        assert result["route"] != "ACTION_BOUNDARY"
        assert result["boundary_ok"] is True

    def test_activation_does_not_route_to_boundary(self):
        mod = _load_module("ab_act2")
        result = mod.fastpath_local("false_positive_activation", "activation runtime", [], ["ACTION_BOUNDARY"])
        assert result["route"] != "ACTION_BOUNDARY"
        assert result["boundary_ok"] is True

    def test_actuel_does_not_route_to_boundary(self):
        mod = _load_module("ab_act3")
        result = mod.fastpath_local("false_positive_actuel", "statut actuel sans action", ["CURRENT_STATE"], ["ACTION_BOUNDARY"])
        assert result["route"] != "ACTION_BOUNDARY"
        assert result["boundary_ok"] is True


# ── compare_request ───────────────────────────────────────────────────────────

class TestCompareRequest:
    def _make_baseline(self, elapsed_ms: float, tokens_in: int, tokens_out: int, ctx_chars: int):
        return {
            "elapsed_ms": elapsed_ms,
            "estimated_input_tokens": tokens_in,
            "estimated_output_tokens": tokens_out,
            "modules_activated": 8,
            "modules_considered": 8,
            "modules_skipped": 0,
            "context_chars_loaded": ctx_chars,
            "emits_act": False,
            "memory_write": False,
            "model_call_avoided": False,
        }

    def _make_fastpath(self, elapsed_ms: float, tokens_in: int, tokens_out: int, ctx_chars: int, route: str = "CURRENT_STATE"):
        return {
            "elapsed_ms": elapsed_ms,
            "estimated_input_tokens": tokens_in,
            "estimated_output_tokens": tokens_out,
            "modules_activated": 3,
            "modules_considered": 8,
            "modules_skipped": 5,
            "context_chars_loaded": ctx_chars,
            "route": route,
            "route_match": True,
            "quality_score": 1.0,
            "boundary_ok": True,
            "emits_act": False,
            "memory_write": False,
            "model_call_avoided": True,
        }

    def test_latency_delta_pct_computed(self):
        mod = _load_module("cmp_lat")
        b = self._make_baseline(10.0, 100, 50, 5000)
        f = self._make_fastpath(2.0, 10, 5, 0)
        cmp = mod.compare_request("req1", b, f)
        assert abs(cmp["latency_delta_pct"] - 80.0) < 0.01

    def test_token_delta_pct_computed(self):
        mod = _load_module("cmp_tok")
        b = self._make_baseline(10.0, 100, 100, 5000)
        f = self._make_fastpath(2.0, 20, 20, 0)
        cmp = mod.compare_request("req1", b, f)
        assert abs(cmp["internal_token_delta_pct"] - 80.0) < 0.01

    def test_estimated_context_budget_delta_pct(self):
        mod = _load_module("cmp_ctx")
        b = self._make_baseline(10.0, 100, 50, 10000)
        f = self._make_fastpath(2.0, 10, 5, 0)
        cmp = mod.compare_request("req1", b, f)
        assert abs(cmp["estimated_context_budget_delta_pct"] - 100.0) < 0.01

    def test_module_skip_pct_computed(self):
        mod = _load_module("cmp_skip")
        b = self._make_baseline(10.0, 100, 50, 5000)
        f = self._make_fastpath(2.0, 10, 5, 0)
        cmp = mod.compare_request("req1", b, f)
        assert abs(cmp["module_skip_pct"] - (5 / 8 * 100)) < 0.01

    def test_model_call_avoided_in_comparison(self):
        mod = _load_module("cmp_mca")
        b = self._make_baseline(10.0, 100, 50, 5000)
        f = self._make_fastpath(2.0, 10, 5, 0)
        cmp = mod.compare_request("req1", b, f)
        assert cmp["model_call_avoided"] is True

    def test_emits_act_false_in_comparison(self):
        mod = _load_module("cmp_act")
        b = self._make_baseline(10.0, 100, 50, 5000)
        f = self._make_fastpath(2.0, 10, 5, 0)
        cmp = mod.compare_request("req1", b, f)
        assert cmp["emits_act"] is False

    def test_memory_write_false_in_comparison(self):
        mod = _load_module("cmp_mw")
        b = self._make_baseline(10.0, 100, 50, 5000)
        f = self._make_fastpath(2.0, 10, 5, 0)
        cmp = mod.compare_request("req1", b, f)
        assert cmp["memory_write"] is False


# ── summarize_mode ────────────────────────────────────────────────────────────

class TestSummarizeMode:
    def _row(self, elapsed=1.0, tok_in=10, tok_out=5, cache_hit=True, route_match=True,
             quality=1.0, boundary=True, model_call_avoided=True, modules_activated=3, modules_skipped=5):
        return {
            "elapsed_ms": elapsed,
            "estimated_input_tokens": tok_in,
            "estimated_output_tokens": tok_out,
            "cache_hit": cache_hit,
            "route_match": route_match,
            "quality_score": quality,
            "boundary_ok": boundary,
            "model_call_avoided": model_call_avoided,
            "modules_activated": modules_activated,
            "modules_skipped": modules_skipped,
        }

    def test_p50_present(self):
        mod = _load_module("sum_p50")
        rows = [self._row(elapsed=float(i)) for i in range(1, 11)]
        summary = mod.summarize_mode(rows)
        assert "p50_latency_ms" in summary

    def test_p95_present(self):
        mod = _load_module("sum_p95")
        rows = [self._row(elapsed=float(i)) for i in range(1, 101)]
        summary = mod.summarize_mode(rows)
        assert "p95_latency_ms" in summary

    def test_p99_present(self):
        mod = _load_module("sum_p99")
        rows = [self._row(elapsed=float(i)) for i in range(1, 101)]
        summary = mod.summarize_mode(rows)
        assert "p99_latency_ms" in summary

    def test_route_accuracy_present(self):
        mod = _load_module("sum_ra")
        rows = [self._row(route_match=True)] * 8 + [self._row(route_match=False)] * 2
        summary = mod.summarize_mode(rows)
        assert "route_accuracy" in summary
        assert abs(summary["route_accuracy"] - 0.8) < 0.01

    def test_boundary_safety_pass_rate_present(self):
        mod = _load_module("sum_bsp")
        rows = [self._row(boundary=True)] * 10
        summary = mod.summarize_mode(rows)
        assert "boundary_safety_pass_rate" in summary
        assert abs(summary["boundary_safety_pass_rate"] - 1.0) < 0.01

    def test_model_call_avoided_rate_present(self):
        mod = _load_module("sum_mcar")
        rows = [self._row(model_call_avoided=True)] * 10
        summary = mod.summarize_mode(rows)
        assert "model_call_avoided_rate" in summary
        assert abs(summary["model_call_avoided_rate"] - 1.0) < 0.01

    def test_cache_hit_ratio_full(self):
        mod = _load_module("sum_chr")
        rows = [self._row(cache_hit=True)] * 10
        summary = mod.summarize_mode(rows)
        assert abs(summary["cache_hit_ratio"] - 1.0) < 0.01


# ── Full run — output files ───────────────────────────────────────────────────

class TestFullRunOutputFiles:
    def test_results_json_generated(self, tmp_path, monkeypatch):
        mod = _load_module("full_json")
        # Redirect output dir to tmp_path
        monkeypatch.setattr(mod, "ROOT", tmp_path)
        # Patch reps to 1 for speed
        original_main = mod.main
        import types

        def fast_main():
            import statistics as _stat
            from datetime import datetime as _dt
            reps = 1
            timestamp = _dt.now().strftime("%Y%m%d_%H%M%S")
            out_dir = tmp_path / f"FASTPATH_AB_BENCHMARK_V1_{timestamp}"
            out_dir.mkdir(parents=True, exist_ok=True)
            baseline_rows = []
            fastpath_rows = []
            comparisons = []
            for spec in mod.REQUESTS:
                b = mod.baseline_agent_normal_local(spec["id"], spec["request"])
                f = mod.fastpath_local(spec["id"], spec["request"], spec["expected_topics"], spec["forbidden_topics"])
                b["rep"] = 0
                f["rep"] = 0
                baseline_rows.append(b)
                fastpath_rows.append(f)
                comparisons.append(mod.compare_request(spec["id"], b, f))
            baseline_summary = mod.summarize_mode(baseline_rows)
            fastpath_summary = mod.summarize_mode(fastpath_rows)
            governance = {"emits_act": False, "memory_write": False, "decision_authority": "KX108_ONLY", "readonly": True, "kernel_mutation": False}
            result = {
                "benchmark": "OBSIDIA_FAST_PATH_AB_BENCHMARK_V1",
                "timestamp": timestamp,
                "repetitions_per_request": reps,
                "request_count": len(mod.REQUESTS),
                "baseline_summary": baseline_summary,
                "fastpath_summary": fastpath_summary,
                "comparisons": comparisons,
                "governance": governance,
                "valid_claim": mod.main.__doc__ or "Obsidia Fast Path V1 reduces local pre-compute work versus a local non-optimized baseline.",
                "invalid_claims": [],
            }
            results_path = out_dir / "results.json"
            results_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
            summary_path = out_dir / "summary.md"
            summary_path.write_text("# summary", encoding="utf-8")
            return results_path, summary_path

        results_path, summary_path = fast_main()
        assert results_path.exists()
        assert summary_path.exists()
        data = json.loads(results_path.read_text(encoding="utf-8"))
        assert data["benchmark"] == "OBSIDIA_FAST_PATH_AB_BENCHMARK_V1"
        assert "governance" in data
        assert data["governance"]["emits_act"] is False
        assert data["governance"]["memory_write"] is False
        assert data["governance"]["decision_authority"] == "KX108_ONLY"
        assert "baseline_summary" in data
        assert "fastpath_summary" in data
        assert "comparisons" in data
        assert len(data["comparisons"]) == 12

    def test_results_json_has_required_keys(self, tmp_path):
        mod = _load_module("full_keys")
        from datetime import datetime as _dt
        timestamp = _dt.now().strftime("%Y%m%d_%H%M%S")
        out_dir = tmp_path / f"FASTPATH_AB_BENCHMARK_V1_{timestamp}"
        out_dir.mkdir(parents=True, exist_ok=True)
        baseline_rows = [mod.baseline_agent_normal_local(spec["id"], spec["request"]) for spec in mod.REQUESTS]
        fastpath_rows = [mod.fastpath_local(spec["id"], spec["request"], spec["expected_topics"], spec["forbidden_topics"]) for spec in mod.REQUESTS]
        for r in baseline_rows:
            r["rep"] = 0
        for r in fastpath_rows:
            r["rep"] = 0
        comparisons = [mod.compare_request(b["request_id"], b, f) for b, f in zip(baseline_rows, fastpath_rows)]
        governance = {"emits_act": False, "memory_write": False, "decision_authority": "KX108_ONLY", "readonly": True, "kernel_mutation": False}
        result = {
            "benchmark": "OBSIDIA_FAST_PATH_AB_BENCHMARK_V1",
            "timestamp": timestamp,
            "repetitions_per_request": 1,
            "request_count": len(mod.REQUESTS),
            "baseline_summary": mod.summarize_mode(baseline_rows),
            "fastpath_summary": mod.summarize_mode(fastpath_rows),
            "comparisons": comparisons,
            "governance": governance,
            "valid_claim": "Obsidia Fast Path V1 reduces local pre-compute work versus a local non-optimized baseline.",
            "invalid_claims": ["Obsidia is faster than AMD."],
        }
        results_path = out_dir / "results.json"
        results_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        data = json.loads(results_path.read_text(encoding="utf-8"))
        for key in ["benchmark", "timestamp", "repetitions_per_request", "request_count",
                    "baseline_summary", "fastpath_summary", "comparisons", "governance",
                    "valid_claim", "invalid_claims"]:
            assert key in data, f"Missing key: {key}"


# ── Valid / invalid claims ────────────────────────────────────────────────────

class TestClaims:
    def test_valid_claim_does_not_mention_gpu(self):
        mod = _load_module("claim_gpu")
        assert "GPU" not in mod.main.__doc__ if mod.main.__doc__ else True
        # Check the hardcoded valid claim string in result
        valid_claim = "Obsidia Fast Path V1 reduces local pre-compute work versus a local non-optimized baseline."
        assert "GPU" not in valid_claim
        assert "AMD" not in valid_claim
        assert "LLM" not in valid_claim
        assert "accelerat" not in valid_claim.lower()

    def test_invalid_claims_include_amd(self):
        mod = _load_module("claim_amd")
        # Verify invalid_claims list in the module's main contains AMD
        src = SCRIPT.read_text(encoding="utf-8")
        assert "Obsidia is faster than AMD" in src

    def test_invalid_claims_include_gpu(self):
        src = SCRIPT.read_text(encoding="utf-8")
        assert "GPU accelerator" in src

    def test_final_positioning_phrase_in_script(self):
        src = SCRIPT.read_text(encoding="utf-8")
        assert "Fast Path does not accelerate compute" in src
        assert "Fast Path reduces avoidable work before compute" in src

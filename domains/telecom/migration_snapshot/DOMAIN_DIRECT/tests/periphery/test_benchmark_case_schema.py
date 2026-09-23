import pytest
from periphery.benchmarks.benchmark_case_schema import get_benchmark_cases, BenchmarkCase


def test_get_all_cases_returns_list():
    cases = get_benchmark_cases()
    assert isinstance(cases, list)
    assert len(cases) > 0


def test_filter_by_benchmark_name():
    cases = get_benchmark_cases("AgentDojo")
    assert all(c.benchmark_name == "AgentDojo" for c in cases)
    assert len(cases) >= 1


def test_case_has_required_fields():
    cases = get_benchmark_cases()
    for c in cases:
        assert c.case_id and c.benchmark_name and c.domain
        assert c.expected_gate in ("ALLOW", "HOLD", "BLOCK")


def test_to_dict_fields():
    cases = get_benchmark_cases()
    d = cases[0].to_dict()
    assert "case_id" in d and "benchmark_name" in d and "expected_gate" in d


def test_agentdojo_block_gate():
    cases = get_benchmark_cases("AgentDojo")
    assert any(c.expected_gate == "BLOCK" for c in cases)

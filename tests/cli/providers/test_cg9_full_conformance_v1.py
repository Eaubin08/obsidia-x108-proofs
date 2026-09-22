from scripts.providers.provider_health_monitor_v1 import (
    ProviderHealthMonitor,
)

from scripts.providers.provider_reliability_receipt_v1 import (
    ProviderReliabilityReceipt,
)

from scripts.providers.provider_performance_receipt_v1 import (
    ProviderPerformanceReceipt,
)

from scripts.providers.provider_performance_comparison_v1 import (
    ProviderPerformanceComparison,
)

from scripts.providers.multi_provider_runtime_comparison_v1 import (
    MultiProviderRuntimeComparison,
)


def test_cg9_global_conformance_v1():

    health = ProviderHealthMonitor(
        provider_id="brody"
    )

    reliability = ProviderReliabilityReceipt(
        provider_id="brody"
    )

    performance = ProviderPerformanceReceipt(
        provider_id="brody",
        adapter_id="brody-runtime-v1",
        execution_id="execution-001",
    )

    performance.record(
        latency_ms=100,
        token_cost=10,
        compute_cost=0.1,
        resource_usage={
            "cpu": "low"
        },
    )


    perf_comparison = ProviderPerformanceComparison()

    perf_result = perf_comparison.compare(
        [
            performance.to_dict(),
            {
                "provider_id": "provider-b",
                "latency_ms": 200,
            },
        ]
    )


    runtime_comparison = MultiProviderRuntimeComparison()

    runtime_result = runtime_comparison.compare(
        [
            {
                "provider_id": "brody",
                "result": "a",
            },
            {
                "provider_id": "provider-b",
                "result": "b",
            },
        ]
    )


    reliability.record_execution(True)
    reliability.record_conformance(True)


    for component in [
        health,
        reliability,
        performance,
        perf_comparison,
        runtime_comparison,
    ]:

        assert component.decision_authority is False
        assert component.execution_authority is False
        assert component.memory_write is False
        assert component.kernel_mutation is False
        assert component.emits_act is False


    assert health.status == "AVAILABLE"

    assert reliability.executions_total == 1

    assert perf_result["comparison_only"] is True

    assert runtime_result["comparison_only"] is True

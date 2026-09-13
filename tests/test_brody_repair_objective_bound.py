from apps.obsidia_api.brody_repair_request_router import (
    build_repair_request_from_message,
)


def test_brody_repair_objective_preserves_more_than_4000_chars():
    message = (
        "corrige ce code "
        + ("A" * 12000)
    )

    request = build_repair_request_from_message(
        message,
        ir_intent="code_debug",
        risk_flags=["code_debug"],
        include_excerpts=False,
    )

    assert request is not None

    assert len(
        request.objective
    ) == len(message)

    assert len(
        request.objective
    ) > 4000


def test_brody_repair_objective_is_bounded_at_65536():
    message = (
        "corrige ce code "
        + ("B" * 80000)
    )

    request = build_repair_request_from_message(
        message,
        ir_intent="code_debug",
        risk_flags=["code_debug"],
        include_excerpts=False,
    )

    assert request is not None

    assert len(
        request.objective
    ) == 65536

    assert request.objective == (
        message[:65536]
    )

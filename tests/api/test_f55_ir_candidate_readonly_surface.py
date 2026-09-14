from apps.obsidia_api.brody_existing_reverse_os_bridge import (
    build_existing_ir_candidate,
)


def test_f55_ir_candidate_builder_exists():

    assert callable(build_existing_ir_candidate)


def test_f55_ir_candidate_readonly_surface():

    result = build_existing_ir_candidate(
        user_message="f55 readonly validation",
        intent="runtime surface validation",
    )

    assert isinstance(result, dict)

    assert (
        "ir_candidate" in result
        or "candidate" in result
        or "status" in result
    )

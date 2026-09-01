from apps.obsidia_api.routes.os_trad_ir_reverse import router


def test_f39_reverse_os_route_exists():
    routes = [r.path for r in router.routes]

    assert "/os-reverse/project" in routes or "/api/os-reverse/project" in routes


def test_f39_reverse_os_is_readonly_surface():
    from periphery.reverse_os.action_projection_readonly import project_action_readonly

    result = project_action_readonly(
        "f39_test",
        "test intent",
        "readonly validation"
    )

    assert result
    assert result.get("advisory_only", True) is True

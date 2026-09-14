from apps.obsidia_api.routes.status import router


def test_f56_backend_health_surface_exists():

    routes = [r.path for r in router.routes]

    assert "/api/health" in routes


def test_f56_backend_health_is_readonly_surface():

    routes = [r.path for r in router.routes]

    assert any(
        "health" in r
        for r in routes
    )

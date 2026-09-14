from apps.obsidia_api.routes.status import router


def test_f43_x108_status_surface_exists():

    routes = [r.path for r in router.routes]

    assert "/api/x108/status" in routes


def test_f43_health_surface_exists():

    routes = [r.path for r in router.routes]

    assert "/api/health" in routes

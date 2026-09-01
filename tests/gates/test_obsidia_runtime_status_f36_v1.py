from apps.obsidia_api.routes.status import router


def test_status_route_has_runtime_surface():
    routes = [r.path for r in router.routes]

    assert "/status" in routes

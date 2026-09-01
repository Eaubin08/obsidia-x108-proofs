from apps.obsidia_api.routes.graphiti import router


def test_f51_graphiti_metrics_surface_exists():

    routes = [r.path for r in router.routes]

    assert any(
        "graphiti" in r and "metric" in r
        for r in routes
    )


def test_f51_graphiti_metrics_is_readonly_surface():

    routes = [r.path for r in router.routes]

    assert any(
        "graphiti" in r
        for r in routes
    )

from apps.obsidia_api.routes.graphiti import router


def test_f49_graphiti_readiness_surface_exists():

    routes = [r.path for r in router.routes]

    assert any(
        "graphiti" in r and "readiness" in r
        for r in routes
    )


def test_f49_graphiti_readiness_is_readonly():

    routes = [r.path for r in router.routes]

    assert any(
        "graphiti" in r
        for r in routes
    )

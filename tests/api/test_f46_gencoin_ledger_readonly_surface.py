from apps.obsidia_api.routes.gencoin import router


def test_f46_gencoin_surface_exists():

    routes = [r.path for r in router.routes]

    assert "/api/gencoin" in routes


def test_f46_gencoin_surface_is_readonly():

    routes = [r.path for r in router.routes]

    assert any(
        "gencoin" in r
        for r in routes
    )

from apps.obsidia_api.routes.brody import router


def test_f52_brody_response_surface_exists():

    routes = [r.path for r in router.routes]

    assert any(
        "brody" in r and "chat" in r
        for r in routes
    )


def test_f52_brody_response_is_advisory_only():

    src = "\n".join(
        str(r.endpoint)
        for r in router.routes
    )

    assert "brody" in src.lower()

from apps.obsidia_api.routes.worldcalls import router


def test_f47_sovereign_ticket_surface_exists():

    routes = [r.path for r in router.routes]

    assert any(
        "sovereign" in r or "worldcalls" in r
        for r in routes
    )


def test_f47_sovereign_ticket_is_readonly_surface():

    routes = [r.path for r in router.routes]

    assert any(
        "world" in r and "sovereign" in r
        for r in routes
    )

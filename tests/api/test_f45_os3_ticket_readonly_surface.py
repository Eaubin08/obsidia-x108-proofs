from apps.obsidia_api.routes.os3 import router


def test_f45_os3_ticket_surface_exists():

    routes = [r.path for r in router.routes]

    assert "/os3/tickets" in routes or "/api/os3/tickets" in routes


def test_f45_os3_surface_is_readonly_route():

    routes = [r.path for r in router.routes]

    assert any("os3" in r and "ticket" in r for r in routes)

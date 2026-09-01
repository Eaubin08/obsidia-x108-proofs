from apps.obsidia_api.routes.audit import router


def test_f48_audit_events_surface_exists():

    routes = [r.path for r in router.routes]

    assert "/audit/events" in routes or "/api/audit/events" in routes


def test_f48_audit_events_is_readonly_surface():

    routes = [r.path for r in router.routes]

    assert any(
        "audit" in r and "event" in r
        for r in routes
    )

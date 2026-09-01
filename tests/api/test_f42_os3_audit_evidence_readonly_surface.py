from apps.obsidia_api.routes.os3 import router as os3_router
from apps.obsidia_api.routes.audit import router as audit_router


def test_f42_os3_route_exists():
    routes = [r.path for r in os3_router.routes]

    assert any("/os3" in r for r in routes)


def test_f42_audit_route_exists():
    routes = [r.path for r in audit_router.routes]

    assert any("/audit" in r for r in routes)

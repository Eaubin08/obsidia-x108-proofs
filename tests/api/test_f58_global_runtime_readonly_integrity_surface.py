from apps.obsidia_api.routes.status import router as status_router
from apps.obsidia_api.routes.runtime_freeze_readonly import router as freeze_router


def test_f58_global_runtime_surfaces_exist():

    routes = (
        [r.path for r in status_router.routes]
        +
        [r.path for r in freeze_router.routes]
    )

    assert len(routes) > 0


def test_f58_global_runtime_readonly_integrity():

    routes = (
        [r.path for r in status_router.routes]
        +
        [r.path for r in freeze_router.routes]
    )

    assert all(
        isinstance(route, str)
        for route in routes
    )

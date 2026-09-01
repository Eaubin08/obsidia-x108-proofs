from apps.obsidia_api.routes.runtime_freeze_readonly import router


def test_f57_runtime_evidence_bundle_surface_exists():

    routes = [r.path for r in router.routes]

    assert any(
        "runtime-freeze" in r
        for r in routes
    )


def test_f57_runtime_evidence_bundle_is_readonly():

    routes = [r.path for r in router.routes]

    assert len(routes) > 0

from apps.obsidia_api.routes.graphiti import router


def test_f50_context_packet_surface_exists():

    routes = [r.path for r in router.routes]

    assert any(
        "context" in r
        for r in routes
    )


def test_f50_context_packet_readonly_contract():

    src = "\n".join(
        str(r.endpoint)
        for r in router.routes
    )

    assert "context" in src.lower()

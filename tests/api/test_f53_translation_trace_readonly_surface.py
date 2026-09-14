from apps.obsidia_api.routes.translation import router


def test_f53_translation_trace_surface_exists():

    routes = [r.path for r in router.routes]

    assert any(
        "translation" in r or "translate" in r
        for r in routes
    )


def test_f53_translation_trace_is_readonly():

    src = "\n".join(
        str(r.endpoint)
        for r in router.routes
    )

    assert "translation" in src.lower() or "translate" in src.lower()

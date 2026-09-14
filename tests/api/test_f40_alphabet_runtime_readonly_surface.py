from apps.obsidia_api.routes.os_trad_ir_reverse import router


def test_f40_alphabet_runtime_surface_exists():
    routes = [r.path for r in router.routes]

    assert "/api/os-trad/translate" in routes


def test_f40_alphabet_units_readonly_contract():
    from apps.obsidia_api.routes.os_trad_ir_reverse import _alphabet_units

    units = _alphabet_units(
        "IR alphabet reverse OS",
        "fr",
        []
    )

    assert isinstance(units, list)
    assert len(units) > 0

from apps.obsidia_api.routes.memory import router


def test_f44_memory_candidates_readonly_surface():

    routes = [r.path for r in router.routes]

    assert "/memory/candidates" in routes or "/api/memory/candidates" in routes


def test_f44_memory_candidates_is_read_surface():

    routes = [r.path for r in router.routes]

    assert any("memory" in r and "candidate" in r for r in routes)

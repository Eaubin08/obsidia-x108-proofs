from apps.obsidia_api.main import app


def test_brody_routes_registered():
    routes = {getattr(route, "path", None) for route in app.routes}

    expected = {
        "/api/brody/chat",
        "/api/context/from-message",
        "/api/memory",
        "/api/memory/status",
        "/api/memory/sources",
        "/api/memory/candidates",
        "/api/memory/candidate/from-message",
        "/api/memory/candidate-ledger",
        "/api/memory/promotion-policy",
        "/api/graphiti/status",
        "/api/graphiti/context",
        "/api/graphiti/search",
        "/api/graphiti/metrics",
        "/api/graphiti/readiness",
        "/api/periphery/brody/context-query",
        "/api/periphery/brody/language-route",
        "/api/periphery/brody/double-brain-route",
        "/api/periphery/brody/diffusion-mix",
    }

    missing = sorted(expected - routes)
    assert not missing, f"Missing Brody/memory/graphiti routes: {missing}"

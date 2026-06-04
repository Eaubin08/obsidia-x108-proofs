"""P38 — Tests unitaires: OS Map Workbench.

Vérifie :
1. Route os_map importable.
2. Endpoints /status et /query enregistrés.
3. OSMapView.tsx existe.
4. App.tsx importe OSMapView.
5. LeftSidebar.tsx expose 'os-map' comme ViewId.
6. App.tsx rend OSMapView pour activeView='os-map'.
7. os_map.py ne contient pas runtime_allowed_now=True.
8. os_map.py ne contient pas emits_act=True.
9. OSMapView.tsx contient 'No ACT'.
10. OSMapView.tsx contient 'ACTION_REQUEST_BLOCKED'.
"""
import pathlib
import sys
import pytest

_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

_WORKBENCH = _REPO_ROOT / "apps" / "obsidia-workbench" / "src"
_VIEWS = _WORKBENCH / "views"
_COMPONENTS = _WORKBENCH / "components"
_APP_TSX = _WORKBENCH / "App.tsx"
_SIDEBAR_TSX = _COMPONENTS / "LeftSidebar.tsx"
_OS_MAP_VIEW = _VIEWS / "OSMapView.tsx"
_OS_MAP_ROUTE = _REPO_ROOT / "apps" / "obsidia_api" / "routes" / "os_map.py"
_MAIN_PY = _REPO_ROOT / "apps" / "obsidia_api" / "main.py"


# ── Test 1 : route os_map importable ─────────────────────────────────────────

def test_os_map_route_importable():
    """Test 1 — Route os_map importable et contient un APIRouter."""
    from apps.obsidia_api.routes.os_map import router
    from fastapi import APIRouter
    assert isinstance(router, APIRouter)


# ── Test 2 : endpoints /status et /query enregistrés ──────────────────────────

def test_os_map_endpoints_registered():
    """Test 2 — Endpoints /status et /query enregistrés dans le router."""
    from apps.obsidia_api.routes.os_map import router
    paths = [r.path for r in router.routes]
    assert any("status" in p for p in paths), f"/status manquant: {paths}"
    assert any("query" in p for p in paths), f"/query manquant: {paths}"


# ── Test 3 : OSMapView.tsx existe ─────────────────────────────────────────────

def test_os_map_view_tsx_exists():
    """Test 3 — OSMapView.tsx existe dans views/."""
    assert _OS_MAP_VIEW.exists(), f"OSMapView.tsx manquant: {_OS_MAP_VIEW}"


# ── Test 4 : App.tsx importe OSMapView ────────────────────────────────────────

def test_app_tsx_imports_os_map_view():
    """Test 4 — App.tsx importe OSMapView."""
    content = _APP_TSX.read_text(encoding="utf-8")
    assert "OSMapView" in content, "OSMapView manquant dans App.tsx"
    assert "OSMapView.tsx" in content or "OSMapView'" in content or 'OSMapView"' in content or "./views/OSMapView" in content


# ── Test 5 : LeftSidebar.tsx expose 'os-map' ──────────────────────────────────

def test_sidebar_has_os_map_view_id():
    """Test 5 — LeftSidebar.tsx expose 'os-map' comme ViewId."""
    content = _SIDEBAR_TSX.read_text(encoding="utf-8")
    assert "'os-map'" in content or '"os-map"' in content, (
        "'os-map' manquant dans LeftSidebar.tsx"
    )


# ── Test 6 : App.tsx rend OSMapView pour os-map ───────────────────────────────

def test_app_tsx_renders_os_map_view():
    """Test 6 — App.tsx rend <OSMapView /> pour activeView='os-map'."""
    content = _APP_TSX.read_text(encoding="utf-8")
    assert "os-map" in content and "OSMapView" in content, (
        "os-map ou OSMapView manquant dans App.tsx"
    )


# ── Test 7 : os_map.py ne contient pas runtime_allowed_now=True ───────────────

def test_os_map_py_no_runtime_allowed_now_true():
    """Test 7 — os_map.py ne contient pas runtime_allowed_now=True."""
    content = _OS_MAP_ROUTE.read_text(encoding="utf-8")
    assert "runtime_allowed_now=True" not in content, (
        "runtime_allowed_now=True détecté dans os_map.py"
    )
    assert "runtime_allowed_now: True" not in content


# ── Test 8 : os_map.py ne contient pas emits_act=True ────────────────────────

def test_os_map_py_no_emits_act_true():
    """Test 8 — os_map.py ne contient pas emits_act=True."""
    content = _OS_MAP_ROUTE.read_text(encoding="utf-8")
    assert "emits_act=True" not in content, (
        "emits_act=True détecté dans os_map.py"
    )
    assert "emits_act: True" not in content


# ── Test 9 : OSMapView.tsx contient 'No ACT' ──────────────────────────────────

def test_os_map_view_mentions_no_act():
    """Test 9 — OSMapView.tsx contient 'No ACT' (invariant affiché)."""
    content = _OS_MAP_VIEW.read_text(encoding="utf-8")
    assert "No ACT" in content or "no_act" in content or "no ACT" in content.lower(), (
        "'No ACT' manquant dans OSMapView.tsx"
    )


# ── Test 10 : OSMapView.tsx mentionne ACTION_REQUEST_BLOCKED ──────────────────

def test_os_map_view_mentions_action_blocked():
    """Test 10 — OSMapView.tsx affiche ACTION_REQUEST_BLOCKED."""
    content = _OS_MAP_VIEW.read_text(encoding="utf-8")
    assert "ACTION_REQUEST_BLOCKED" in content, (
        "ACTION_REQUEST_BLOCKED manquant dans OSMapView.tsx"
    )


# ── Test bonus : main.py enregistre os_map_router ─────────────────────────────

def test_main_py_registers_os_map_router():
    """Bonus — main.py enregistre os_map_router."""
    content = _MAIN_PY.read_text(encoding="utf-8")
    assert "os_map_router" in content or "os_map" in content, (
        "os_map_router manquant dans main.py"
    )


def test_os_map_route_boundary_constants():
    """Bonus — _BOUNDARY dans os_map.py contient readonly=True et decision_authority=KX108_ONLY."""
    content = _OS_MAP_ROUTE.read_text(encoding="utf-8")
    assert '"readonly": True' in content or "'readonly': True" in content
    assert "KX108_ONLY" in content

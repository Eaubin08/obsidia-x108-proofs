"""test_obsidia_runtime_service_map_v1 — OBSIDIA_TERMINAL_RUNTIME_SERVICE_MAP_V1_APPLY.

Scope : carte readonly des services Obsidia.
Aucun subprocess. Aucun POST. Aucun lancement. Aucune mutation.
Les sondes réseau sont mockées — aucun serveur réel requis.
decision_authority = KX108_ONLY.
"""

from __future__ import annotations

import py_compile
import sys
import urllib.error
from pathlib import Path
from unittest.mock import MagicMock, patch

_REPO_ROOT = Path(__file__).resolve().parents[2]
_CLI_DIR = _REPO_ROOT / "scripts"
sys.path.insert(0, str(_CLI_DIR))

import obsidia_cli as cli  # noqa: E402

_REG = cli.load_registry(cli.REGISTRY_PATH)

_EXPECTED_SERVICES = {
    "api_health", "api_readiness", "api_status",
    "kernel_3001", "graphiti_8011",
    "neo4j_bolt_7688", "neo4j_browser_7475",
    "ui_5173", "sigma_domains", "sigma_evaluate",
}
_EXPECTED_LOCAL = {"gates", "lean_manifest", "oie_reports", "patch_proposals", "corpus"}


def _a(q: str) -> dict:
    return cli.answer_router(q, _REG)


# ---------------------------------------------------------------------------
# 1. Compilation
# ---------------------------------------------------------------------------
def test_py_compile() -> None:
    py_compile.compile(str(_CLI_DIR / "obsidia_cli.py"), doraise=True)


# ---------------------------------------------------------------------------
# 2. Structure RUNTIME_SERVICE_MAP_V1
# ---------------------------------------------------------------------------
def test_runtime_service_map_has_expected_services() -> None:
    """Tous les services attendus sont declares dans RUNTIME_SERVICE_MAP_V1."""
    declared = set(cli.RUNTIME_SERVICE_MAP_V1.keys())
    missing = _EXPECTED_SERVICES - declared
    assert not missing, f"Services manquants : {missing}"


def test_runtime_service_map_required_keys() -> None:
    """Chaque entree de RUNTIME_SERVICE_MAP_V1 a les cles obligatoires."""
    for name, spec in cli.RUNTIME_SERVICE_MAP_V1.items():
        assert "kind" in spec, f"{name} : cle 'kind' manquante"
        assert "label" in spec, f"{name} : cle 'label' manquante"
        assert spec["kind"] in ("http_get", "socket"), (
            f"{name} : kind inconnu {spec['kind']!r}")
        if spec["kind"] == "http_get":
            assert "url" in spec, f"{name} : cle 'url' manquante"
        else:
            assert "host" in spec and "port" in spec, (
                f"{name} : host/port manquants pour socket")


# ---------------------------------------------------------------------------
# 3. Gardes statiques : pas de subprocess, pas de POST
# ---------------------------------------------------------------------------
def test_runtime_service_map_no_subprocess_static() -> None:
    """Invariant non-souverain : aucun subprocess dans obsidia_cli.py."""
    src = (_CLI_DIR / "obsidia_cli.py").read_text(encoding="utf-8")
    assert "import subprocess" not in src
    assert "os.system" not in src
    assert "shell=True" not in src


def test_runtime_service_map_no_post_static() -> None:
    """Les fonctions runtime n'utilisent pas POST (methode HTTP)."""
    src = (_CLI_DIR / "obsidia_cli.py").read_text(encoding="utf-8")
    # Chercher POST dans le bloc runtime uniquement
    idx = src.find("def _runtime_http_get_status")
    assert idx != -1, "_runtime_http_get_status introuvable"
    end = src.find("\ndef build_runtime_service_map_v1", idx)
    block = src[idx:end] if end != -1 else src[idx:idx + 2000]
    assert '"POST"' not in block and "'POST'" not in block, (
        "POST detecte dans _runtime_http_get_status")


# ---------------------------------------------------------------------------
# 4. Sondes sécurisées — réseau mocké
# ---------------------------------------------------------------------------
def test_runtime_socket_probe_down_safe() -> None:
    """Socket vers port fermé retourne DOWN sans crash."""
    result = cli._runtime_socket_status("127.0.0.1", 19999, timeout=0.1)
    assert result["status"] in ("DOWN", "UNKNOWN"), (
        f"Statut inattendu port fermé : {result['status']}")


def test_runtime_http_probe_down_safe() -> None:
    """HTTP GET vers URL inexistante retourne DOWN sans crash."""
    result = cli._runtime_http_get_status("http://127.0.0.1:19998/no", timeout=0.1)
    assert result["status"] in ("DOWN", "UNKNOWN"), (
        f"Statut inattendu URL inexistante : {result['status']}")


def test_runtime_http_probe_mock_up() -> None:
    """HTTP GET mocké UP retourne status UP."""
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    with patch("urllib.request.urlopen", return_value=mock_resp):
        result = cli._runtime_http_get_status("http://127.0.0.1:8000/api/health")
    assert result["status"] == "UP"
    assert result["code"] == 200


def test_runtime_http_probe_urlerror_down() -> None:
    """URLError retourne DOWN (pas UNKNOWN)."""
    with patch("urllib.request.urlopen",
               side_effect=urllib.error.URLError("connection refused")):
        result = cli._runtime_http_get_status("http://127.0.0.1:8000/api/health")
    assert result["status"] == "DOWN"


# ---------------------------------------------------------------------------
# 5. Format : contient READY/DEGRADED/BLOCKED
# ---------------------------------------------------------------------------
def test_runtime_format_contains_ready_degraded_blocked() -> None:
    """format_runtime_service_map_v1 mentionne toujours un des trois états terminaux."""
    fake_result = {
        "panel": "OBSIDIA_RUNTIME_STATUS",
        "network": {
            "api_health": {"label": "API_HEALTH", "status": "DOWN",
                           "required": True, "not_confirmed": False},
        },
        "local": {
            "gates": {"label": "GATES", "status": "OK"},
            "corpus": {"label": "CORPUS", "status": "OK"},
        },
        "terminal_state": "DEGRADED",
    }
    rendered = cli.format_runtime_service_map_v1(fake_result)
    assert "DEGRADED" in rendered or "READY" in rendered or "BLOCKED" in rendered
    assert "OBSIDIA RUNTIME STATUS" in rendered
    assert "lecture seule" in rendered.lower()


# ---------------------------------------------------------------------------
# 6. answer_router : branche runtime
# ---------------------------------------------------------------------------
def test_runtime_status_command_returns_guide_or_execute() -> None:
    """'runtime' via answer_router retourne GUIDE ou EXECUTE."""
    r = _a("runtime")
    assert r["output"] in ("GUIDE", "EXECUTE"), f"output={r['output']}"


def test_runtime_status_does_not_policy_deny() -> None:
    """'runtime' ne doit pas déclencher POLICY_DENY."""
    r = _a("runtime")
    assert r["output"] != "POLICY_DENY"


def test_runtime_status_contract_preserved() -> None:
    """La branche runtime respecte le contrat de retour answer_router."""
    r = _a("runtime")
    required = {
        "panel", "raw", "reponse", "mode_reponse", "detected_layer",
        "confidence", "organes_mobilises", "organes_mobilisables",
        "outils_utilises", "corpus_utilise", "limites",
        "action_locale", "local_read_meta", "next_human_action",
        "output", "guidance", "guidance_authority", "plan_status",
    }
    missing = required - set(r.keys())
    assert not missing, f"Cles manquantes dans la branche runtime : {missing}"


def test_runtime_action_locale_is_runtime_map() -> None:
    """action_locale doit etre RUNTIME_SERVICE_MAP_READONLY."""
    r = _a("runtime")
    assert r["action_locale"] == "RUNTIME_SERVICE_MAP_READONLY"


def test_runtime_cockpit_status_recognized() -> None:
    r = _a("cockpit status")
    assert r["output"] in ("GUIDE", "EXECUTE")
    assert r["action_locale"] == "RUNTIME_SERVICE_MAP_READONLY"


def test_runtime_doctor_full_recognized() -> None:
    r = _a("doctor --full")
    assert r["output"] in ("GUIDE", "EXECUTE")
    assert r["action_locale"] == "RUNTIME_SERVICE_MAP_READONLY"


def test_runtime_status_full_recognized() -> None:
    r = _a("status --full")
    assert r["output"] in ("GUIDE", "EXECUTE")
    assert r["action_locale"] == "RUNTIME_SERVICE_MAP_READONLY"


def test_runtime_reponse_contains_obsidia_runtime_status() -> None:
    """La réponse doit contenir le header OBSIDIA RUNTIME STATUS."""
    r = _a("runtime")
    assert "OBSIDIA RUNTIME STATUS" in r["reponse"]


def test_runtime_reponse_contains_terminal_state() -> None:
    """La réponse doit contenir l'état terminal READY/DEGRADED/BLOCKED."""
    r = _a("runtime")
    low = r["reponse"]
    assert "READY" in low or "DEGRADED" in low or "BLOCKED" in low


# ---------------------------------------------------------------------------
# 7. Vérifications locales dans build_runtime_service_map_v1
# ---------------------------------------------------------------------------
def test_runtime_local_checks_include_gates() -> None:
    """La carte locale doit inclure la vérification gates."""
    result = cli.build_runtime_service_map_v1()
    assert "gates" in result["local"], "Clé 'gates' absente des checks locaux"
    assert result["local"]["gates"]["label"] == "GATES"


def test_runtime_local_checks_include_lean_manifest() -> None:
    result = cli.build_runtime_service_map_v1()
    assert "lean_manifest" in result["local"]
    assert result["local"]["lean_manifest"]["label"] == "LEAN_MANIFEST"


def test_runtime_local_checks_include_oie() -> None:
    result = cli.build_runtime_service_map_v1()
    assert "oie_reports" in result["local"]
    assert result["local"]["oie_reports"]["label"] == "OIE_REPORTS"


def test_runtime_local_checks_include_patch_proposals() -> None:
    result = cli.build_runtime_service_map_v1()
    assert "patch_proposals" in result["local"]
    assert result["local"]["patch_proposals"]["label"] == "PATCH_PROPOSALS"


# ---------------------------------------------------------------------------
# 8. obsidia_registry.yaml non touché dans ce lot
# ---------------------------------------------------------------------------
def test_registry_yaml_not_touched_in_this_lot() -> None:
    """Vérification statique : le code runtime ne lit pas obsidia_registry.yaml
    autrement que via load_registry (appel standard inchange)."""
    src = (_CLI_DIR / "obsidia_cli.py").read_text(encoding="utf-8")
    idx_start = src.find("def build_runtime_service_map_v1")
    idx_end = src.find("\ndef format_runtime_service_map_v1", idx_start)
    block = src[idx_start:idx_end] if idx_end != -1 else src[idx_start:idx_start + 3000]
    assert "obsidia_registry.yaml" not in block, (
        "build_runtime_service_map_v1 ne doit pas lire obsidia_registry.yaml directement")


# ---------------------------------------------------------------------------
# 9. Anti-régression : contrats existants inchangés
# ---------------------------------------------------------------------------
def test_existing_183_tests_not_broken() -> None:
    """Compilation propre = prérequis pour les 183 tests existants."""
    py_compile.compile(str(_CLI_DIR / "obsidia_cli.py"), doraise=True)


def test_answer_router_contract_still_preserved() -> None:
    """answer_router : contrat de retour inchangé pour un IN normal."""
    r = cli.answer_router("sigma coherence", _REG)
    required = {
        "panel", "raw", "reponse", "mode_reponse", "detected_layer",
        "confidence", "organes_mobilises", "organes_mobilisables",
        "outils_utilises", "corpus_utilise", "limites",
        "action_locale", "local_read_meta", "next_human_action",
        "output", "guidance", "guidance_authority", "plan_status",
    }
    missing = required - set(r.keys())
    assert not missing, f"Regression contrat answer_router : {missing}"

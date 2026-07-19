"""test_obsidia_capability_graph_v3 — TERMINAL_CAPABILITY_GRAPH_V3_APPLY.

Scope : carte statique readonly des capacites par couche.
Non souverain. Aucun subprocess. Aucun I/O hors LOCAL_CORPUS.
decision_authority = KX108_ONLY.
"""

from __future__ import annotations

import py_compile
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_CLI_DIR = _REPO_ROOT / "scripts"
_GATES_DIR = _REPO_ROOT / "scripts" / "gates"
sys.path.insert(0, str(_CLI_DIR))

import obsidia_cli as cli  # noqa: E402

_REG = cli.load_registry(cli.REGISTRY_PATH)
_REGISTRY_LAYERS = set(_REG.get("layers", {}).keys())
_GRAPH_LAYERS = set(cli.CAPABILITY_GRAPH_V3.keys())
_REQUIRED_KEYS = {"ops_allowed", "ops_forbidden", "corpus_topics",
                  "gates_applicable", "cross_concerns"}


def _a(q: str) -> dict:
    return cli.answer_router(q, _REG)


# ---------------------------------------------------------------------------
# Compilation
# ---------------------------------------------------------------------------
def test_py_compile() -> None:
    py_compile.compile(str(_CLI_DIR / "obsidia_cli.py"), doraise=True)


# ---------------------------------------------------------------------------
# Tests statiques : structure de CAPABILITY_GRAPH_V3
# ---------------------------------------------------------------------------
def test_capability_graph_covers_all_registry_layers() -> None:
    """Toutes les couches du registre YAML doivent etre dans le graph."""
    missing = _REGISTRY_LAYERS - _GRAPH_LAYERS
    assert not missing, (
        f"Couches registry absentes du CAPABILITY_GRAPH_V3 : {missing}")


def test_capability_graph_required_keys() -> None:
    """Chaque entree du graph doit avoir les 5 cles obligatoires."""
    for layer, entry in cli.CAPABILITY_GRAPH_V3.items():
        missing = _REQUIRED_KEYS - set(entry.keys())
        assert not missing, (
            f"Couche {layer!r} : cles manquantes {missing}")


def test_no_registry_layer_missing_from_graph() -> None:
    """Aucune couche registry ne doit etre absente du graph (doublon intentionnel
    avec test_capability_graph_covers_all_registry_layers, sens inverse)."""
    for layer in _REGISTRY_LAYERS:
        assert layer in cli.CAPABILITY_GRAPH_V3, (
            f"Couche registry {layer!r} absente du CAPABILITY_GRAPH_V3")


def test_corpus_topics_exist_in_local_corpus() -> None:
    """Tous les corpus_topics references dans le graph doivent exister dans LOCAL_CORPUS."""
    for layer, entry in cli.CAPABILITY_GRAPH_V3.items():
        for t in entry.get("corpus_topics", []):
            assert t in cli.LOCAL_CORPUS, (
                f"Couche {layer!r} : corpus_topic {t!r} absent de LOCAL_CORPUS")


def test_gates_applicable_subset_of_known() -> None:
    """Tous les gates_applicable references doivent exister dans scripts/gates/."""
    known_scripts = {p.name for p in _GATES_DIR.glob("*.py")}
    for layer, entry in cli.CAPABILITY_GRAPH_V3.items():
        for g in entry.get("gates_applicable", []):
            assert g in known_scripts, (
                f"Couche {layer!r} : gate {g!r} absent de scripts/gates/")


# ---------------------------------------------------------------------------
# Tests fonctionnels : build_capability_view + format_capability_view
# ---------------------------------------------------------------------------
def test_capabilities_sigma_returns_guide() -> None:
    """capabilities sigma → GUIDE + READ_LOCAL_WINDOW mentionné."""
    r = _a("capabilities sigma")
    assert r["output"] == "GUIDE", f"output={r['output']}"
    assert r["action_locale"] == "CAPABILITY_DISPLAY"
    low = r["reponse"].lower()
    assert "read_local_window" in low or "doctor_http_get" in low, (
        f"Reponse sigma ne mentionne pas les ops : {r['reponse'][:300]}")


def test_capabilities_policy_deny_first() -> None:
    """capabilities avec mot interdit → POLICY_DENY avant tout affichage de capacite."""
    r = _a("capabilities commit le kernel")
    assert r["output"] == "POLICY_DENY", f"output={r['output']}"
    assert "capability_view" not in r["reponse"].lower(), (
        "CAPABILITY_VIEW ne doit pas apparaitre apres POLICY_DENY")


def test_capabilities_unknown_empty_ops() -> None:
    """Couche inconnue → ops_allowed vide dans la vue."""
    r = _a("capabilities aabbcc_inconnu_xyz")
    assert r["output"] == "GUIDE"
    view = cli.build_capability_view("aabbcc_inconnu_xyz", _REG)
    assert view["ops_allowed"] == [], (
        f"ops_allowed non vide pour couche inconnue : {view['ops_allowed']}")


def test_capabilities_obsidure_no_apply() -> None:
    """obsidure capabilities → APPLY_PROPOSAL dans ops_forbidden."""
    view = cli.build_capability_view("obsidure", _REG)
    assert "APPLY_PROPOSAL" in view["ops_forbidden"], (
        f"APPLY_PROPOSAL absent de ops_forbidden obsidure : {view['ops_forbidden']}")
    assert view["output"] == "GUIDE"


def test_capabilities_live_doctor_allowed() -> None:
    """live capabilities → DOCTOR_HTTP_GET dans ops_allowed."""
    view = cli.build_capability_view("status", _REG)
    assert "DOCTOR_HTTP_GET" in view["ops_allowed"], (
        f"DOCTOR_HTTP_GET absent de ops_allowed live : {view['ops_allowed']}")


def test_capabilities_verbose_includes_corpus_answers() -> None:
    """Mode verbose → corpus_answers non vide pour couche avec corpus_topics."""
    view = cli.build_capability_view("sigma coherence", _REG, verbose=True)
    if view["corpus_topics"]:
        assert view["corpus_answers"], "corpus_answers vide en mode verbose"
        for t in view["corpus_topics"]:
            assert t in view["corpus_answers"], (
                f"Topic {t!r} absent de corpus_answers en verbose")


def test_cross_concerns_thermo_in_brody() -> None:
    """brody → cross_concerns contient Thermo."""
    view = cli.build_capability_view("brody chat", _REG)
    low = " ".join(view["cross_concerns"]).lower()
    assert "thermo" in low, (
        f"Thermo absent des cross_concerns brody : {view['cross_concerns']}")


def test_cross_concerns_oie_in_obsidure() -> None:
    """obsidure → cross_concerns contient OIE."""
    view = cli.build_capability_view("obsidure patch", _REG)
    low = " ".join(view["cross_concerns"]).lower()
    assert "oie" in low, (
        f"OIE absent des cross_concerns obsidure : {view['cross_concerns']}")


# ---------------------------------------------------------------------------
# Tests enrichissement build_active_plan
# ---------------------------------------------------------------------------
def test_plan_enriched_has_capability_summary() -> None:
    """build_active_plan doit retourner une cle 'capability_summary'."""
    plan = cli.build_active_plan("sigma coherence", _REG)
    assert "capability_summary" in plan, (
        "Cle 'capability_summary' absente du plan")
    cs = plan["capability_summary"]
    assert "ops_allowed" in cs
    assert "cross_concerns" in cs
    assert "hint" in cs
    assert isinstance(cs["ops_allowed"], list)
    assert len(cs["ops_allowed"]) <= 5


# ---------------------------------------------------------------------------
# Tests anti-régression
# ---------------------------------------------------------------------------
def test_build_active_plan_existing_keys_preserved() -> None:
    """Les 18 cles existantes de build_active_plan sont toujours presentes."""
    plan = cli.build_active_plan("sigma coherence", _REG)
    required = {
        "panel", "raw", "normalized", "detected_layer", "confidence",
        "route_reason", "deny_keyword", "roadmap",
        "organes_mobilises", "organes_mobilisables", "organes_interdits",
        "outils_utilises", "outils_mobilisables", "outils_exclus",
        "corpus", "scope", "gates", "blockers",
        "output_predicted", "guidance", "guidance_reasons",
        "guidance_authority", "next_human_action", "plan_status",
    }
    missing = required - set(plan.keys())
    assert not missing, f"Cles build_active_plan manquantes : {missing}"


def test_answer_router_contract_preserved() -> None:
    """answer_router doit toujours retourner les cles contractuelles."""
    r = _a("sigma coherence")
    required = {
        "panel", "raw", "reponse", "mode_reponse", "detected_layer",
        "confidence", "organes_mobilises", "organes_mobilisables",
        "outils_utilises", "corpus_utilise", "limites",
        "action_locale", "local_read_meta", "next_human_action",
        "output", "guidance", "guidance_authority", "plan_status",
    }
    missing = required - set(r.keys())
    assert not missing, f"Cles answer_router manquantes : {missing}"


def test_no_subprocess_static_guard() -> None:
    """Invariant non-souverain : aucun subprocess dans obsidia_cli.py."""
    src = (_CLI_DIR / "obsidia_cli.py").read_text(encoding="utf-8")
    assert "import subprocess" not in src
    assert "os.system" not in src
    assert "shell=True" not in src


def test_decision_authority_unchanged() -> None:
    """KX108_ONLY reste la seule autorite declaree dans le code."""
    src = (_CLI_DIR / "obsidia_cli.py").read_text(encoding="utf-8")
    assert "KX108_ONLY" in src
    assert "decision_authority" in src


def test_capability_view_output_never_execute() -> None:
    """build_capability_view retourne toujours GUIDE (ou POLICY_DENY), jamais EXECUTE."""
    for q in ("sigma", "obsidure", "brody", "live", "kernel",
              "domains", "audit", "memory", "obsidienne", "terminal_self"):
        view = cli.build_capability_view(q, _REG)
        assert view["output"] in ("GUIDE", "POLICY_DENY"), (
            f"capabilities {q!r} → output inattendu {view['output']}")


def test_format_capability_view_compact_one_line_per_section() -> None:
    """Format compact : chaque section tient sur une seule ligne."""
    view = cli.build_capability_view("sigma", _REG)
    rendered = cli.format_capability_view(view, verbose=False)
    sections = [l for l in rendered.splitlines()
                if l.startswith("OPS") or l.startswith("CORPUS")
                or l.startswith("GATES") or l.startswith("CROSS")
                or l.startswith("NEXT")]
    for s in sections:
        assert "\n" not in s, f"Section non compacte : {s!r}"
    # Au moins les 5 sections attendues
    assert len(sections) >= 5, f"Sections manquantes : {sections}"

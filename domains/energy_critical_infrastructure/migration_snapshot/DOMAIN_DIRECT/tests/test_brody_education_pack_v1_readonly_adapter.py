"""
Tests BRODY_EDUCATION_PACK_V1_READONLY_ADAPTER
DECISION_AUTHORITY: KX108_ONLY
READONLY=True | MEMORY_WRITE=False | GRAPHITI_WRITE=False | EMITS_ACT=False

G1 — Unit adapter (20 tests)
G2 — Route/runtime integration (6 tests)
"""
import pytest

from apps.obsidia_api.brody_education_pack_v1_readonly_adapter import (
    build_brody_education_pack_v1_readonly_context,
    inject_education_pack_v1_into_runtime_packet,
    INJECT_KEY,
    _EDUCATION_BOUNDARY,
    _FORBIDDEN_INJECT_KEYS,
    _FORBIDDEN_ACTION_KEYS,
    _SAFE_SENTINEL_VALUES,
)


# ── Fixture ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def ctx():
    return build_brody_education_pack_v1_readonly_context()


@pytest.fixture(scope="module")
def boundary():
    return _EDUCATION_BOUNDARY


# ── G1 — Unit adapter ────────────────────────────────────────────────────────

def test_g1_01_context_present(ctx):
    """G1-T01 : build_brody_education_pack_v1_readonly_context retourne un dict non vide."""
    assert isinstance(ctx, dict)
    assert len(ctx) > 0


def test_g1_02_status_ready_or_missing(ctx):
    """G1-T02 : status est PACK_READY_READONLY ou PACK_MISSING (jamais de crash)."""
    assert ctx.get("status") in ("PACK_READY_READONLY", "PACK_MISSING", "PACK_INVALID")


def test_g1_03_readonly_true(ctx):
    """G1-T03 : education_boundary.readonly = True."""
    assert ctx["education_boundary"]["readonly"] is True


def test_g1_04_advisory_only_true(ctx):
    """G1-T04 : education_boundary.advisory_only = True."""
    assert ctx["education_boundary"]["advisory_only"] is True


def test_g1_05_context_signal_only_true(ctx):
    """G1-T05 : education_boundary.context_signal_only = True."""
    assert ctx["education_boundary"]["context_signal_only"] is True


def test_g1_06_decision_authority_kx108(ctx):
    """G1-T06 : education_boundary.decision_authority = KX108_ONLY."""
    assert ctx["education_boundary"]["decision_authority"] == "KX108_ONLY"


def test_g1_07_authority_none(ctx):
    """G1-T07 : education_boundary.authority = NONE."""
    assert ctx["education_boundary"]["authority"] == "NONE"


def test_g1_08_memory_write_false(ctx):
    """G1-T08 : education_boundary.memory_write = False."""
    assert ctx["education_boundary"]["memory_write"] is False


def test_g1_09_graphiti_write_false(ctx):
    """G1-T09 : education_boundary.graphiti_write = False."""
    assert ctx["education_boundary"]["graphiti_write"] is False


def test_g1_10_neo4j_write_false(ctx):
    """G1-T10 : education_boundary.neo4j_write = False."""
    assert ctx["education_boundary"]["neo4j_write"] is False


def test_g1_11_kernel_mutation_false(ctx):
    """G1-T11 : education_boundary.kernel_mutation = False."""
    assert ctx["education_boundary"]["kernel_mutation"] is False


def test_g1_12_emits_act_false(ctx):
    """G1-T12 : education_boundary.emits_act = False."""
    assert ctx["education_boundary"]["emits_act"] is False


def test_g1_13_emits_verdict_false(ctx):
    """G1-T13 : education_boundary.emits_verdict = False."""
    assert ctx["education_boundary"]["emits_verdict"] is False


def test_g1_14_network_fetch_crawl_false(ctx):
    """G1-T14 : network, fetch, crawl tous False dans education_boundary."""
    b = ctx["education_boundary"]
    assert b["network"] is False
    assert b["fetch"] is False
    assert b["crawl"] is False


def test_g1_15_mcp_bridge_false(ctx):
    """G1-T15 : education_boundary.mcp_bridge = False."""
    assert ctx["education_boundary"]["mcp_bridge"] is False


def test_g1_16_path_compute_false(ctx):
    """G1-T16 : education_boundary.path_compute = False."""
    assert ctx["education_boundary"]["path_compute"] is False


def test_g1_17_cache_no_cache(ctx):
    """G1-T17 : education_boundary.cache = NO_CACHE."""
    assert ctx["education_boundary"]["cache"] == "NO_CACHE"


def test_g1_18_deferred_policy_present(ctx):
    """G1-T18 : deferred_policy est présent et vaut QUARANTINE_NOT_INJECTED."""
    assert ctx.get("deferred_policy") == "QUARANTINE_NOT_INJECTED"


def test_g1_19_forbidden_beliefs_key_present(ctx):
    """G1-T19 : forbidden_beliefs_available est présent dans le contexte."""
    assert "forbidden_beliefs_available" in ctx


def test_g1_20_no_raw_massive_content(ctx):
    """G1-T20 : aucun fichier markdown brut n'est inclus dans le contexte."""
    ctx_str = str(ctx)
    # Les fichiers markdown bruts commencent tous par "# BRODY_V1_" — ne doivent pas figurer
    assert "## 1. Identité canonique de Brody" not in ctx_str
    assert "## MODULE 01" not in ctx_str
    assert "## Piège 1" not in ctx_str


# ── G2 — Route / runtime integration ─────────────────────────────────────────

def test_g2_21_inject_adds_education_key():
    """G2-T21 : inject_education_pack_v1_into_runtime_packet ajoute la clé INJECT_KEY."""
    packet = {"some_key": "some_value", "decision_authority": "KX108_ONLY"}
    result = inject_education_pack_v1_into_runtime_packet(packet)
    assert INJECT_KEY in result


def test_g2_22_cic_readonly_context_preserved():
    """G2-T22 : cic_readonly_context existant n'est pas écrasé par l'adapter."""
    existing_cic = {"domain": "bank", "authority": "NONE"}
    packet = {"cic_readonly_context": existing_cic, "decision_authority": "KX108_ONLY"}
    result = inject_education_pack_v1_into_runtime_packet(packet)
    assert result["cic_readonly_context"] is existing_cic


def test_g2_23_top_level_sentinels_preserved():
    """G2-T23 : les sentinelles top-level du packet ne sont pas altérées par l'adapter."""
    packet = {
        "decision_authority": "KX108_ONLY",
        "emits_act": False,
        "allowed_to_act": False,
        "allowed_to_decide": False,
        "memory_write": False,
        "graphiti_write": False,
        "kernel_mutation": False,
    }
    result = inject_education_pack_v1_into_runtime_packet(packet)
    assert result["decision_authority"] == "KX108_ONLY"
    assert result["emits_act"] is False
    assert result["allowed_to_act"] is False
    assert result["allowed_to_decide"] is False
    assert result["memory_write"] is False
    assert result["graphiti_write"] is False
    assert result["kernel_mutation"] is False


def test_g2_24_forbidden_keys_not_injected():
    """G2-T24 : aucune clé de _FORBIDDEN_INJECT_KEYS ne figure dans le contexte éducatif injecté."""
    packet = {"decision_authority": "KX108_ONLY"}
    result = inject_education_pack_v1_into_runtime_packet(packet)
    edu_ctx = result.get(INJECT_KEY, {})
    edu_ctx_keys = set(edu_ctx.keys())
    for forbidden in _FORBIDDEN_INJECT_KEYS:
        assert forbidden not in edu_ctx_keys, f"Clé interdite '{forbidden}' présente dans le contexte éducatif"


def test_g2_25_deferred_marked_quarantine():
    """G2-T25 : DEFERRED reste marqué QUARANTINE_NOT_INJECTED dans le contexte injecté."""
    packet = {"decision_authority": "KX108_ONLY"}
    result = inject_education_pack_v1_into_runtime_packet(packet)
    edu_ctx = result.get(INJECT_KEY, {})
    assert edu_ctx.get("deferred_policy") == "QUARANTINE_NOT_INJECTED"


def test_g2_26_ragnarok_exclude_absolute():
    """G2-T26 : ragnarok_policy = EXCLUDE_ABSOLUTE, jamais comme exemple opérationnel."""
    packet = {"decision_authority": "KX108_ONLY"}
    result = inject_education_pack_v1_into_runtime_packet(packet)
    edu_ctx = result.get(INJECT_KEY, {})
    assert edu_ctx.get("ragnarok_policy") == "EXCLUDE_ABSOLUTE"
    # La note doit contenir EXCLUDE_ABSOLUTE et non pas le recommander comme exemple
    note = edu_ctx.get("ragnarok_note", "")
    assert "EXCLUDE_ABSOLUTE" in note
    assert "exemple opérationnel" not in note.lower().replace("ne jamais citer comme exemple opérationnel", "")


# ── G3 — Guard fix : sentinelles sûres vs valeurs unsafe ─────────────────

def test_g3_27_runtime_safe_sentinels_do_not_block_injection():
    """G3-T27 : Sentinelles readonly du pipeline Brody avec valeurs sûres ne bloquent pas l'injection."""
    packet = {
        "decision_authority": "KX108_ONLY",
        "authority": "NONE",
        "memory_write": False,
        "graphiti_write": False,
        "neo4j_write": False,
        "kernel_mutation": "NONE",
        "x108_mutation": "NONE",
        "emits_act": False,
        "emits_verdict": False,
        "network": False,
        "fetch": False,
        "crawl": False,
        "mcp_bridge": False,
        "path_compute": False,
    }
    result = inject_education_pack_v1_into_runtime_packet(packet)
    edu_ctx = result.get(INJECT_KEY, {})
    assert edu_ctx.get("status") in ("PACK_READY_READONLY", "PACK_MISSING", "PACK_INVALID"), (
        f"Guard bloque à tort avec sentinelles sûres : status={edu_ctx.get('status')}, "
        f"reason={edu_ctx.get('reason')}"
    )


def test_g3_28_unsafe_kernel_mutation_value_blocks():
    """G3-T28 : kernel_mutation avec valeur unsafe bloque l'injection."""
    for unsafe_val in [True, "WRITE", "ACTIVE", 1]:
        packet = {"kernel_mutation": unsafe_val}
        result = inject_education_pack_v1_into_runtime_packet(packet)
        edu_ctx = result.get(INJECT_KEY, {})
        assert edu_ctx.get("status") == "PACK_INJECT_BLOCKED", (
            f"Guard devrait bloquer kernel_mutation={unsafe_val!r}"
        )


def test_g3_29_unsafe_memory_write_blocks():
    """G3-T29 : memory_write=True bloque l'injection."""
    packet = {"memory_write": True}
    result = inject_education_pack_v1_into_runtime_packet(packet)
    edu_ctx = result.get(INJECT_KEY, {})
    assert edu_ctx.get("status") == "PACK_INJECT_BLOCKED"


def test_g3_30_forbidden_action_key_blocks():
    """G3-T30 : Clés d'action interdites bloquent l'injection même sans valeur dangereuse."""
    for action_key, action_val in [("execute", True), ("verdict", "ALLOW"), ("act", True), ("decision", "GRANT")]:
        packet = {action_key: action_val}
        result = inject_education_pack_v1_into_runtime_packet(packet)
        edu_ctx = result.get(INJECT_KEY, {})
        assert edu_ctx.get("status") == "PACK_INJECT_BLOCKED", (
            f"Guard devrait bloquer clé d'action {action_key!r}={action_val!r}"
        )


def test_g3_31_safe_packet_preserves_cic_context():
    """G3-T31 : cic_readonly_context existant est préservé après injection avec packet sûr."""
    existing_cic = {"domain": "sigma", "authority": "NONE", "decision_authority": "KX108_ONLY"}
    packet = {
        "cic_readonly_context": existing_cic,
        "decision_authority": "KX108_ONLY",
        "kernel_mutation": "NONE",
        "x108_mutation": "NONE",
        "memory_write": False,
        "graphiti_write": False,
    }
    result = inject_education_pack_v1_into_runtime_packet(packet)
    assert result["cic_readonly_context"] is existing_cic


def test_g3_32_education_boundary_still_no_write_no_act():
    """G3-T32 : education_boundary reste readonly/no-write/no-act après guard fix."""
    packet = {
        "decision_authority": "KX108_ONLY",
        "kernel_mutation": "NONE",
        "x108_mutation": "NONE",
        "memory_write": False,
        "graphiti_write": False,
        "neo4j_write": False,
        "emits_act": False,
        "emits_verdict": False,
        "mcp_bridge": False,
        "path_compute": False,
    }
    result = inject_education_pack_v1_into_runtime_packet(packet)
    edu_ctx = result.get(INJECT_KEY, {})
    bnd = edu_ctx.get("education_boundary", {})
    assert bnd.get("memory_write") is False
    assert bnd.get("graphiti_write") is False
    assert bnd.get("neo4j_write") is False
    assert bnd.get("emits_act") is False
    assert bnd.get("emits_verdict") is False
    assert bnd.get("mcp_bridge") is False
    assert bnd.get("path_compute") is False

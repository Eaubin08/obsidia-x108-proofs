"""
tests/cli/test_pretool_shadow_cgd_v0.py
======================================
CG-D — PreToolUse SHADOW classifier / observer : OBSERVATIONNEL PUR.

Prouve : classification déterministe des familles d'outils, reçus SHADOW
normalisés (aucun argument brut), lookup de bail STRICTEMENT lecture seule,
et — surtout — ZÉRO effet : quel que soit le verdict, la requête d'outil
continue inchangée, aucun blocage, aucune permission émise, fail-open sur
toute erreur / événement malformé / store indisponible.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_SCRIPTS = _REPO_ROOT / "scripts"
for _p in (str(_SCRIPTS), str(_REPO_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import obsidia_pretool_shadow_v0 as S              # noqa: E402
import obsidia_cognitive_capability_lease_v0 as L  # noqa: E402


@pytest.fixture(autouse=True)
def _isolate(monkeypatch, tmp_path):
    monkeypatch.setenv("OBSIDIA_PRETOOL_SHADOW_STORE_DIR", str(tmp_path / "shadow_store"))
    monkeypatch.setenv("OBSIDIA_CGB_STORE_DIR", str(tmp_path / "cgb_store"))
    yield


def _ev(tool_name, tool_input=None, **kw):
    d = {"tool_name": tool_name, "tool_input": tool_input or {}}
    d.update(kw)
    return d


# ══════════════════════════════════════════════════════════════════════════
#  Bornes d'inertie
# ══════════════════════════════════════════════════════════════════════════

def test_shadow_inertness_constants():
    assert S.PRE_TOOL_SHADOW_CLASSIFIER == "IMPLEMENTED_V0"
    assert S.PRE_TOOL_SHADOW_RECEIPTS == "IMPLEMENTED_V0"
    assert S.PRE_TOOL_LEASE_LOOKUP_MODE == "SHADOW_READ_ONLY"
    assert S.PRE_TOOL_LEASE_LOOKUP_CAN_GRANT_ACCESS is False
    assert S.PRE_TOOL_LEASE_LOOKUP_CAN_CREATE_LEASE is False
    assert S.PRE_TOOL_LEASE_LOOKUP_CAN_MUTATE_LEASE is False
    assert S.SHADOW_CAN_DENY_TOOL is False
    assert S.SHADOW_CAN_GRANT_TOOL is False
    assert S.SHADOW_CAN_MODIFY_TOOL_ARGS is False
    assert S.SHADOW_CAN_EXECUTE_TOOL is False
    assert S.SHADOW_CAN_ISSUE_LEASE is False
    assert S.SHADOW_CAN_CREATE_HUMAN_AUTHORITY is False
    assert S.SHADOW_CAN_CALL_PROVIDER_AUTOMATICALLY is False
    assert S.HARD_TOOL_GATE_ACTIVE is False
    assert S.LEASE_ENFORCEMENT_ACTIVE is False
    assert S.CLAUDE_ROLE_TRANSPORT_ONLY_TECHNICALLY_ENFORCED is False
    assert S.CLAUDE_PERMISSION_MODEL_CHANGED is False
    assert S.RAW_TOOL_ARGUMENTS_PERSISTED is False
    assert S.MISSING_MISSION_CONTEXT_CAN_DEFAULT_TO_GLOBAL_AUTHORITY is False
    assert S.TRUSTED_HUMAN_AUTHORIZATION_HOST_BINDING == "NOT_YET_ENFORCED"
    assert S.PRECONDITION_CGE_1_TRUSTED_HUMAN_AUTHORIZATION_HOST_BINDING == "OPEN"
    assert S.CG_D_SHADOW_MAY_PROCEED_WITH_EXTERNAL_TRUST_BOUNDARY_UNWIRED is True
    assert S.CG_E_ACTIVE_ENFORCEMENT_REQUIRES_TRUSTED_HUMAN_AUTHORIZATION_HOST_BINDING is True


def test_host_delivery_status_is_truthful_not_proven():
    """Option C : committé AVEC la livraison hôte réelle NON prouvée. Aucun PASS
    fabriqué. Le runtime classifier/observateur reste implémenté + prouvé inerte
    localement (canary synthétique + invocation standalone)."""
    assert S.SYNTHETIC_SHADOW_OBSERVER_CANARY == "PASS"
    assert S.STANDALONE_OBSERVER_INVOCATION == "PASS"
    assert S.REAL_SHADOW_OBSERVER_CANARY == "NOT_PROVEN"
    assert S.REAL_PRETOOL_HOST_DELIVERY_PROVEN is False
    assert S.PRE_TOOL_OBSERVATION_COVERAGE == "NOT_PROVEN"
    assert S.AT_REFERENCE_PRETOOL_COVERAGE == "UNKNOWN"
    assert S.PRE_TOOL_SHADOW_OBSERVER == "IMPLEMENTED_V0_HOST_DELIVERY_UNPROVEN"
    assert S.PRECONDITION_CGE_2_REAL_PRETOOL_HOST_DELIVERY == "OPEN"
    assert S.CG_E_ACTIVE_ENFORCEMENT_REQUIRES_REAL_PRETOOL_HOST_DELIVERY is True


# ══════════════════════════════════════════════════════════════════════════
#  §30 — classification déterministe des familles d'outils
# ══════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("tool,ti,fam,verdict,route", [
    ("Read", {"file_path": "scripts/x.py"}, S.FAM_READ_ONLY_REPO_INSPECTION,
     S.SHADOW_STACK_NATIVE_ROUTE, S.ROUTE_TARGET_STACK_NATIVE),
    ("Grep", {"pattern": "foo"}, S.FAM_SEARCH, S.SHADOW_STACK_NATIVE_ROUTE,
     S.ROUTE_TARGET_STACK_NATIVE),
    ("Glob", {"pattern": "**/*.py"}, S.FAM_SEARCH, S.SHADOW_STACK_NATIVE_ROUTE,
     S.ROUTE_TARGET_STACK_NATIVE),
    ("Edit", {"file_path": "scripts/x.py"}, S.FAM_FILE_MUTATION,
     S.SHADOW_MISSION_CONTEXT_MISSING, S.ROUTE_TARGET_STACK_NATIVE),
    ("Write", {"file_path": "a/b.txt"}, S.FAM_FILE_MUTATION,
     S.SHADOW_MISSION_CONTEXT_MISSING, S.ROUTE_TARGET_STACK_NATIVE),
    ("Bash", {"command": "pytest tests/cli/ -q"}, S.FAM_TEST_EXECUTION,
     S.SHADOW_STACK_NATIVE_ROUTE, S.ROUTE_TARGET_STACK_NATIVE),
    ("Bash", {"command": "lake build Obsidia"}, S.FAM_LEAN_EXECUTION,
     S.SHADOW_STACK_NATIVE_ROUTE, S.ROUTE_TARGET_STACK_NATIVE),
    ("Bash", {"command": "git status --porcelain"}, S.FAM_GIT_READ,
     S.SHADOW_STACK_NATIVE_ROUTE, S.ROUTE_TARGET_STACK_NATIVE),
    ("Bash", {"command": "git diff --stat"}, S.FAM_GIT_READ,
     S.SHADOW_STACK_NATIVE_ROUTE, S.ROUTE_TARGET_STACK_NATIVE),
    ("Bash", {"command": "git add -- scripts/x.py"}, S.FAM_GIT_MUTATION,
     S.SHADOW_HUMAN_AUTHORITY_REQUIRED, S.ROUTE_TARGET_HUMAN_AUTHORITY),
    ("Bash", {"command": "git commit -m x"}, S.FAM_GIT_MUTATION,
     S.SHADOW_HUMAN_AUTHORITY_REQUIRED, S.ROUTE_TARGET_HUMAN_AUTHORITY),
    ("Bash", {"command": "git push origin main"}, S.FAM_GIT_MUTATION,
     S.SHADOW_HUMAN_AUTHORITY_REQUIRED, S.ROUTE_TARGET_HUMAN_AUTHORITY),
    ("Bash", {"command": "frobnicate --all"}, S.FAM_SHELL_GENERAL,
     S.SHADOW_UNKNOWN_AUTHORITY, S.ROUTE_TARGET_UNKNOWN),
    ("Bash", {"command": "rm -rf build"}, S.FAM_FILE_MUTATION,
     S.SHADOW_MISSION_CONTEXT_MISSING, S.ROUTE_TARGET_STACK_NATIVE),
    ("Task", {"subagent_type": "Explore"}, S.FAM_AGENT_SPAWN,
     S.SHADOW_MISSION_CONTEXT_MISSING, S.ROUTE_TARGET_COGNITIVE_LEASE),
    ("MysteryTool", {}, S.FAM_UNKNOWN_TOOL, S.SHADOW_UNKNOWN_AUTHORITY,
     S.ROUTE_TARGET_UNKNOWN),
])
def test_classify_families(tool, ti, fam, verdict, route):
    d = S.classify_pretool_event(_ev(tool, ti))
    assert d["normalized_tool_family"] == fam
    assert d["shadow_verdict"] == verdict
    assert d["shadow_route_target"] == route
    assert S.verify_shadow_decision(d) == (True, None)
    # zéro autorité, zéro effet — TOUJOURS
    for b in ("grants_tool_access", "enforcement_active", "actual_enforcement",
              "actual_denial", "is_execution_authority", "is_kx_authority",
              "is_human_authority", "is_sovereign"):
        assert d[b] is False


def test_git_read_vs_mutation_distinction():
    for c in ("git status", "git diff", "git log --oneline", "git show HEAD", "git branch"):
        assert S.classify_pretool_event(_ev("Bash", {"command": c}))["normalized_tool_family"] == S.FAM_GIT_READ
    for c in ("git add .", "git commit -m x", "git reset --hard", "git checkout main",
              "git switch -c b", "git restore x", "git merge dev", "git rebase main",
              "git stash", "git worktree add", "git config user.name z"):
        assert S.classify_pretool_event(_ev("Bash", {"command": c}))["normalized_tool_family"] == S.FAM_GIT_MUTATION


def test_engineering_classification_with_mission_context():
    d = S.classify_pretool_event(_ev("Edit", {"file_path": "scripts/x.py"},
                                     mission_submission_id="gsub-" + "0" * 32))
    assert d["shadow_verdict"] == S.SHADOW_WOULD_REQUIRE_ENGINEERING_LEASE
    assert d["lease_class_required"] == L.ENGINEERING_LEASE
    assert d["grants_tool_access"] is False


def test_lease_present_structurally_valid_inert_never_active_allow(monkeypatch, tmp_path):
    """§7 : un bail présent + structurellement valide, racine de confiance hôte
    NON câblée -> SHADOW_LEASE_PRESENT_STRUCTURALLY_VALID_INERT + trust_root_unbound,
    JAMAIS ACTIVE_ALLOW / LEASE_AUTHORIZES_TOOL."""
    # bail v1 CG-C minimal, persisté dans un store tmp
    import obsidia_gateway_route_decision_v0 as RD
    root = tmp_path / "fake_router"
    (root / "app" / "router").mkdir(parents=True)
    (root / "app" / "__init__.py").write_text("", encoding="utf-8")
    (root / "app" / "router" / "__init__.py").write_text("", encoding="utf-8")
    dec = {"route": "obsidure_route_only", "level": 1, "reason": "f",
           "ir": {"intent_type": "code_request", "target_layer": "x", "action": "y", "risk": "low"},
           "gate": {"verdict": "ALLOW", "reason": "f"}}
    (root / "app" / "router" / "decision.py").write_text(
        "import json\n_D=json.loads(%r)\ndef decide(p,memory_index=None):\n return dict(_D)\n" % json.dumps(dec),
        encoding="utf-8")
    monkeypatch.setenv("OBSIDIA_ROUTER_ROOT", str(root))
    for m in ("app", "app.router", "app.router.decision"):
        sys.modules.pop(m, None)
    sub = RD.submit_mission(requested_outcome="m")
    cap = RD.request_capability(mission_submission_id=sub["mission_submission_id"],
                                requested_capability="c", reason="r")
    ms = RD.load_mission_submission(sub["mission_submission_id"])
    cr = RD.load_capability_request(cap["capability_request_id"])
    lease = L.build_cognitive_capability_lease(
        lease_class=L.ENGINEERING_LEASE, capability_request=cr,
        route_decision=cap["route_decision"], mission_submission=ms,
        lease_scope={"allowed_providers": ["obsidure"]},
        requested_capability_scope={"allowed_providers": ["obsidure"]})
    sd = tmp_path / "lease_store"
    assert L.persist_capability_lease(lease, store_dir=sd)["status"] == "STORED"

    d = S.classify_pretool_event(
        _ev("Edit", {"file_path": "scripts/x.py"},
            mission_submission_id=ms["mission_submission_id"], lease_id=lease["lease_id"]),
        lease_store_dir=sd)
    assert d["shadow_verdict"] == S.SHADOW_LEASE_PRESENT_STRUCTURALLY_VALID_INERT
    assert "trust_root_unbound" in d["reason_codes"]
    assert d["trust_boundary_state"] == "NOT_YET_ENFORCED"
    assert d["grants_tool_access"] is False and d["actual_denial"] is False
    # jamais de verdict d'autorisation active
    assert d["shadow_verdict"] not in ("ACTIVE_ALLOW", "LEASE_AUTHORIZES_TOOL")


def test_referenced_lease_absent(tmp_path):
    d = S.classify_pretool_event(
        _ev("Write", {"file_path": "a.txt"},
            mission_submission_id="gsub-" + "1" * 32, lease_id="cclease-" + "9" * 32),
        lease_store_dir=tmp_path / "empty")
    assert d["shadow_verdict"] == S.SHADOW_WOULD_REQUIRE_ENGINEERING_LEASE
    assert "referenced_lease_absent" in d["reason_codes"]


# ══════════════════════════════════════════════════════════════════════════
#  §12 — contexte de mission jamais inventé
# ══════════════════════════════════════════════════════════════════════════

def test_missing_mission_context_never_global_authority():
    d = S.classify_pretool_event(_ev("Edit", {"file_path": "x.py"}))
    assert d["shadow_verdict"] == S.SHADOW_MISSION_CONTEXT_MISSING
    assert d["mission_submission_id"] is None
    assert S.MISSING_MISSION_CONTEXT_CAN_DEFAULT_TO_GLOBAL_AUTHORITY is False


def test_bogus_refs_not_accepted():
    d = S.classify_pretool_event(_ev("Edit", {"file_path": "x.py"},
                                     mission_submission_id="not-a-gsub"))
    assert d["mission_submission_id"] is None
    assert d["shadow_verdict"] == S.SHADOW_MISSION_CONTEXT_MISSING


# ══════════════════════════════════════════════════════════════════════════
#  §23 — confidentialité : aucun argument brut persisté
# ══════════════════════════════════════════════════════════════════════════

def test_no_raw_arguments_persisted(tmp_path):
    secret_cmd = "git commit -m 'SECRET token=abcd1234 password=hunter2'"
    d = S.classify_pretool_event(_ev("Bash", {"command": secret_cmd}))
    r = S.persist_shadow_receipt(d)
    assert r["status"] == "SHADOW_RECEIPT_RECORDED"
    receipt = S.load_shadow_receipt(d["shadow_decision_id"])
    blob = json.dumps(receipt)
    assert "SECRET" not in blob and "hunter2" not in blob and "abcd1234" not in blob
    assert receipt["raw_tool_arguments_persisted"] is False
    assert receipt["requested_command_family"] == "git"
    # aucun contenu de fichier / prompt
    d2 = S.classify_pretool_event(_ev("Write", {"file_path": "secrets/x.pem",
                                                "content": "-----BEGIN KEY-----abcd"}))
    S.persist_shadow_receipt(d2)
    rr = json.dumps(S.load_shadow_receipt(d2["shadow_decision_id"]))
    assert "BEGIN KEY" not in rr and "abcd" not in rr
    assert "secrets/x.pem" in rr  # identifiant de chemin borné OK


def test_path_ids_are_bounded_not_full():
    d = S.classify_pretool_event(_ev("Read", {"file_path": "/very/deep/nested/tree/scripts/mod.py"}))
    assert d["requested_paths"] == ["scripts/mod.py"]


# ══════════════════════════════════════════════════════════════════════════
#  §31 — ZÉRO EFFET : tout passe, toujours
# ══════════════════════════════════════════════════════════════════════════

_ALL_EVENTS = [
    _ev("Read", {"file_path": "x"}), _ev("Grep", {"pattern": "y"}),
    _ev("Edit", {"file_path": "x"}), _ev("Write", {"file_path": "x"}),
    _ev("Bash", {"command": "pytest"}), _ev("Bash", {"command": "lake build Obsidia"}),
    _ev("Bash", {"command": "git status"}), _ev("Bash", {"command": "git commit -m x"}),
    _ev("Bash", {"command": "git push"}), _ev("Bash", {"command": "weird-cmd"}),
    _ev("Task", {"subagent_type": "x"}), _ev("Unknown", {}),
    _ev("Edit", {"file_path": "x"}, mission_submission_id="gsub-" + "0" * 32),
]


@pytest.mark.parametrize("event", _ALL_EVENTS)
def test_observe_is_always_pass_through(event, tmp_path):
    out = S.observe_pretool_event(event, store_dir=tmp_path / "s")
    assert out["hook_final_effect"] == "PASS_THROUGH"
    assert out["actual_denial"] is False and out["actual_enforcement"] is False
    assert "permissionDecision" not in json.dumps(out)


def test_classifier_exception_is_observational_fail_open(monkeypatch):
    monkeypatch.setattr(S, "normalize_tool_intent",
                        lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")))
    d = S.classify_pretool_event(_ev("Read", {"file_path": "x"}))
    assert d["shadow_verdict"] == S.SHADOW_CLASSIFIER_ERROR
    assert d["actual_denial"] is False and d["grants_tool_access"] is False
    assert S.verify_shadow_decision(d)[0] is True


def test_malformed_event_passes_through():
    for bad in (None, [], "x", 42, {}, {"tool_name": None}, {"tool_input": "notadict"}):
        d = S.classify_pretool_event(bad)
        assert d["actual_denial"] is False
        assert d["shadow_verdict"] in S._ALL_VERDICTS
        assert S.verify_shadow_decision(d)[0] is True


def test_store_unavailable_passes_through(tmp_path, monkeypatch):
    # store dir = un fichier -> mkdir échoue -> reçu rejeté mais observe passe
    bad = tmp_path / "afile"
    bad.write_text("x", encoding="utf-8")
    out = S.observe_pretool_event(_ev("Edit", {"file_path": "x"}), store_dir=bad)
    assert out["hook_final_effect"] == "PASS_THROUGH"
    assert out["actual_denial"] is False


def test_lease_store_unavailable_passes_through(tmp_path):
    d = S.classify_pretool_event(
        _ev("Edit", {"file_path": "x"}, mission_submission_id="gsub-" + "0" * 32,
            lease_id="cclease-" + "0" * 32),
        lease_store_dir=tmp_path / "nonexistent" / "deep")
    assert d["actual_denial"] is False
    assert d["shadow_verdict"] in S._ALL_VERDICTS


# ══════════════════════════════════════════════════════════════════════════
#  §32 — reçus
# ══════════════════════════════════════════════════════════════════════════

def test_receipt_schema_hash_and_write_once(tmp_path):
    d = S.classify_pretool_event(_ev("Bash", {"command": "pytest"}))
    r1 = S.persist_shadow_receipt(d, store_dir=tmp_path / "s")
    assert r1["status"] == "SHADOW_RECEIPT_RECORDED"
    r2 = S.persist_shadow_receipt(d, store_dir=tmp_path / "s")
    assert r2["status"] == "IDEMPOTENT_ALREADY_EXISTS"
    p = tmp_path / "s" / f"{d['shadow_decision_id']}.json"
    p.write_text(json.dumps({"tampered": True}) + "\n", encoding="utf-8")
    r3 = S.persist_shadow_receipt(d, store_dir=tmp_path / "s")
    assert r3["status"] == "SHADOW_RECEIPT_IMMUTABILITY_VIOLATION"
    assert r3["divergent_shadow_receipt"] == "FAIL_CLOSED"
    # jsonl append-only présent
    assert (tmp_path / "s" / "shadow_receipts.jsonl").is_file()


def test_receipt_reload(tmp_path):
    d = S.classify_pretool_event(_ev("Read", {"file_path": "x"}))
    S.persist_shadow_receipt(d, store_dir=tmp_path / "s")
    back = S.load_shadow_receipt(d["shadow_decision_id"], store_dir=tmp_path / "s")
    assert back is not None and back["shadow_decision_id"] == d["shadow_decision_id"]
    assert back["actual_enforcement"] is False and back["actual_denial"] is False


def test_deterministic_normalization():
    a = S.classify_pretool_event(_ev("Bash", {"command": "git   diff   --stat"}))
    b = S.classify_pretool_event(_ev("Bash", {"command": "git   diff   --stat"}))
    assert a["record_hash"] == b["record_hash"]
    assert a["shadow_decision_id"] == b["shadow_decision_id"]


def test_tampered_shadow_decision_fail_closed():
    d = S.classify_pretool_event(_ev("Read", {"file_path": "x"}))
    for f, v in [("shadow_verdict", "SHADOW_STACK_NATIVE_ROUTE" if d["shadow_verdict"] != "SHADOW_STACK_NATIVE_ROUTE" else "SHADOW_UNKNOWN_AUTHORITY"),
                 ("grants_tool_access", True), ("actual_denial", True),
                 ("normalized_tool_family", "X")]:
        bad = dict(d); bad[f] = v
        assert S.verify_shadow_decision(bad)[0] is False


# ══════════════════════════════════════════════════════════════════════════
#  §20 / §36 — hook observateur : pass-through, jamais de permission émise
# ══════════════════════════════════════════════════════════════════════════

_HOOK = _SCRIPTS / "obsidia_pretool_shadow_observer.py"


@pytest.mark.parametrize("event", [
    {"tool_name": "Read", "tool_input": {"file_path": "scripts/x.py"}},
    {"tool_name": "Bash", "tool_input": {"command": "git status"}},
    {"tool_name": "Edit", "tool_input": {"file_path": "scripts/x.py"}},
    {"tool_name": "Bash", "tool_input": {"command": "git commit -m x"}},
    {"not": "a valid payload"},
])
def test_observer_hook_synthetic_canary(event, tmp_path):
    """§36 canary synthétique : l'événement atteint le hook -> classifier ->
    reçu -> exit 0, AUCUNE sortie de permission."""
    env = {"OBSIDIA_PRETOOL_SHADOW_STORE_DIR": str(tmp_path / "s"),
           "PATH": __import__("os").environ.get("PATH", ""),
           "SYSTEMROOT": __import__("os").environ.get("SYSTEMROOT", "")}
    r = subprocess.run([sys.executable, str(_HOOK)], input=json.dumps(event),
                       capture_output=True, text=True, env=env, timeout=30)
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip() == "", f"hook émit une sortie: {r.stdout!r}"
    assert "permissionDecision" not in r.stdout
    assert "hookSpecificOutput" not in r.stdout


def test_cgd_does_not_change_permission_model_or_tracked_claude_files():
    """CG-D : aucun changement du modèle de permission Claude, aucun fichier
    .claude/ TRACKÉ modifié. Le seul câblage autorisé est un
    .claude/settings.local.json GITIGNORÉ n'enregistrant QUE l'observateur
    OBSERVATIONNEL, SANS aucune règle allow/ask/deny."""
    settings = (_REPO_ROOT / ".claude" / "settings.json").read_text(encoding="utf-8")
    assert "obsidia_pretool_shadow_observer" not in settings
    assert '"hooks"' not in settings  # aucun hook câblé dans settings.json (trackée)
    # settings.json + tout .claude/ tracké restent byte-inchangés
    r = subprocess.run(["git", "status", "--porcelain", ".claude/"],
                       cwd=str(_REPO_ROOT), capture_output=True, text=True)
    assert r.stdout.strip() == "", f".claude/ (tracké) modifié par CG-D: {r.stdout}"

    local = _REPO_ROOT / ".claude" / "settings.local.json"
    if local.exists():
        # doit être gitignoré (jamais commité)
        ci = subprocess.run(["git", "check-ignore", ".claude/settings.local.json"],
                            cwd=str(_REPO_ROOT), capture_output=True, text=True)
        assert ci.returncode == 0, "settings.local.json DOIT être gitignoré"
        data = json.loads(local.read_text(encoding="utf-8"))
        # AUCUNE règle de permission : uniquement un hook PreToolUse observateur
        assert "permissions" not in data, "settings.local.json ne doit porter AUCUNE permission"
        pre = data.get("hooks", {}).get("PreToolUse", [])
        cmds = [h["command"] for grp in pre for h in grp.get("hooks", [])]
        assert cmds, "settings.local.json (si présent) doit enregistrer l'observateur"
        for c in cmds:
            assert "obsidia_pretool_shadow_observer.py" in c
        # aucun autre event hook, aucune escalade
        for k in ("PostToolUse", "UserPromptSubmit", "Stop", "SubagentStop"):
            assert k not in data.get("hooks", {}), f"CG-D ne câble QUE PreToolUse, pas {k}"


def test_observer_hook_cannot_emit_block():
    src = _HOOK.read_text(encoding="utf-8")
    # le hook n'imprime jamais de décision et ne sort jamais non-zéro volontairement
    assert "permissionDecision" not in src
    assert 'exit(2)' not in src and "sys.exit(1)" not in src
    assert "PASS_THROUGH" in src or "PASS_THROUGH" in (_SCRIPTS / "obsidia_pretool_shadow_v0.py").read_text(encoding="utf-8")


# ══════════════════════════════════════════════════════════════════════════
#  §24 / §25 / §26 — aucune autorité, gels
# ══════════════════════════════════════════════════════════════════════════

def test_shadow_module_static_no_authority_no_mutation():
    src = (_SCRIPTS / "obsidia_pretool_shadow_v0.py").read_text(encoding="utf-8")
    for banned in ("permissionDecision", "hookSpecificOutput", "subprocess", "urllib",
                   "requests", "atomic_replace_with_bytes", "run_and_persist_kx108",
                   "run_governed_content_apply", "persist_capability_lease(",
                   "prepare_cognitive_capability_lease(", "prepare_human_capability_grant(",
                   "import obsidia_mission_authority_v0", "import obsidia_batch_execution",
                   "import obsidia_governed_apply_v0", "os.system"):
        assert banned not in src, banned
    # read-only : seulement load_* / verify_* des modules amont
    assert "load_capability_lease" in src and "verify_capability_lease" in src


def test_frozen_paths_clean():
    r = subprocess.run(
        ["git", "status", "--porcelain", ".claude/settings.json",
         ".claude/hooks/obsidia_pretooluse_guard.py",
         ".claude/hooks/obsidia_router_prompt_hook.py", "CLAUDE.md",
         "proofs/lean/", "formal/", "audit/merkle_seal.json",
         "scripts/obsidia_mission_authority_v0.py",
         "scripts/obsidia_cognitive_capability_lease_v0.py",
         "scripts/obsidia_mission_capability_scope_v0.py",
         "scripts/obsidia_gateway_route_decision_v0.py",
         "scripts/obsidia_mission_sequencer_v0.py"],
        cwd=str(_REPO_ROOT), capture_output=True, text=True)
    assert r.stdout.strip() == "", f"gelé modifié: {r.stdout}"


def test_audit_world_action_bus_untouched():
    r = subprocess.run(["git", "diff", "--stat", "audit/world_action_bus.jsonl"],
                       cwd=str(_REPO_ROOT), capture_output=True, text=True)
    # peut être 'dirty' pré-existant, mais CG-D n'y ajoute rien : le shadow store
    # est sous audit/pretool_shadow/ (répertoire distinct), jamais ce fichier.
    shadow_src = (_SCRIPTS / "obsidia_pretool_shadow_v0.py").read_text(encoding="utf-8")
    assert "world_action_bus" in shadow_src  # uniquement dans un commentaire d'interdiction
    assert 'world_action_bus.jsonl"' not in shadow_src.replace(
        "N'écrit JAMAIS dans audit/world_action_bus.jsonl", "")

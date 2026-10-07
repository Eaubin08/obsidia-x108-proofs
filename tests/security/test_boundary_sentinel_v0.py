"""Security Boundary Sentinel V0 — B7 epoch 1 (docs/architecture/B7_RUNTIME_CLOSURE_20261007.md).

Each case mutates an in-memory snapshot of the real repository sources (never the files on disk) and
asserts the deterministic severity / status of the frozen table.
"""
from __future__ import annotations

import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
VAL = "app/cognition/b7/validation.py"


@pytest.fixture(scope="module")
def snapshot():
    from app.security.sentinel import repository_snapshot
    return repository_snapshot(ROOT)


def _scan(files, **kw):
    from app.security.sentinel import scan
    return scan(files, **kw)


def _with(snapshot, path, text, append=True):
    files = dict(snapshot)
    files[path] = (files.get(path, "") + "\n" + text) if append else text
    return files


def _sev(report):
    return {f.trigger: f.severity.name for f in report.findings}


# ── baseline ──────────────────────────────────────────────────────────────────────────────────
def test_current_repository_is_safe_at_epoch_1(snapshot):
    from app.security.sentinel import SecurityBoundaryStatus
    report = _scan(snapshot)
    assert report.findings == () and report.status == SecurityBoundaryStatus.SAFE
    assert report.boundary_id == "B7_COGNITIVE_RESOLUTION" and report.security_epoch == 1
    assert report.epoch_applicable is True


def test_baseline_matches_b7_closure_document():
    from app.security.b7_epoch1_baseline import BASELINE
    doc = (ROOT / "docs/architecture/B7_RUNTIME_CLOSURE_20261007.md").read_text(encoding="utf-8")
    for line in ("B7_SECURITY_EPOCH=1", "CERTIFIED_TRUST_SINKS=admit_trusted_context,register_derived",
                 "CERTIFIED_EXTERNAL_ISSUE_CALLERS=0", "CERTIFIED_SAME_PROCESS_UNTRUSTED_CODE=NO_PROVEN_REACHABLE_PATH",
                 "LIVE_PROVIDER_WIRING=NOT_IMPLEMENTED", "SECURITY_SENTINEL_HARDENING=HOLD_FUTURE",
                 "PF_FREEZE_REVISIT_REQUIRED=YES"):
        assert line in doc
    assert BASELINE["security_epoch"] == 1
    assert BASELINE["trust_sinks"] == ("admit_trusted_context", "register_derived")
    assert len(BASELINE["runtime_closure"]) == 40          # closure doc: 40 modules in the B7 transitive closure


# ── RED cases (frozen severity table) ─────────────────────────────────────────────────────────
_EXT = "app/router/new_consumer.py"

CASES = {
    # 1 new _issue caller (outside the gate) -> LEVEL_1 NEW_ISSUE_CALLER (+ importer)
    "issue_caller": (_EXT, "from app.cognition.b7.validation import _issue\n_issue(None)\n", "NEW_ISSUE_CALLER", "LEVEL_1"),
    # 2 new unguarded trust sink inside B7 -> LEVEL_2
    "trust_sink": (VAL, "def leak(result):\n    return result.derived_state\n", "UNGUARDED_TRUST_SINK", "LEVEL_2"),
    # 3 raw B6 ContextPacket re-admission -> LEVEL_2
    "raw_b6": (VAL, "from app.harness.state_explicit.context_assembly import ContextPacket\n"
                    "def admit_packet(obj):\n    if isinstance(obj, ContextPacket):\n        return obj\n",
               "RAW_B6_TRUST_ADMISSION", "LEVEL_2"),
    # 4/5/6 reachable same-process execution -> LEVEL_2
    "eval": ("app/cognition/b7/router.py", "def _x(s):\n    return eval(s)\n", "SAME_PROCESS_UNTRUSTED_CODE", "LEVEL_2"),
    "exec": ("app/harness/state_explicit/projection.py", "def _x(s):\n    exec(s)\n", "SAME_PROCESS_UNTRUSTED_CODE", "LEVEL_2"),
    "generated_code": ("app/semantic/lattice/lexicon.py", "def _x(s):\n    return compile(s, '<gen>', 'exec')\n",
                       "SAME_PROCESS_UNTRUSTED_CODE", "LEVEL_2"),
    # 7 LIVE_PROVIDER_WIRING activation -> LEVEL_1
    "live_provider": (_EXT, "from app.cognition.b7 import translate, validate_candidate\n"
                            "def wire(raw, req):\n    return translate(raw, req)\n",
                      "LIVE_PROVIDER_WIRING_ACTIVATED", "LEVEL_1"),
    # 8-11 authority escalation inside the protected boundary -> LEVEL_3
    "memory_write": (VAL, "_FLAGS = {'memory_write': True}\n", "MEMORY_WRITE_ESCALATION", "LEVEL_3"),
    "emits_act": (VAL, "_FLAGS = {'emits_act': True}\n", "ACT_ESCALATION", "LEVEL_3"),
    "kernel_mutation": (VAL, "_FLAGS = {'kernel_mutation': True}\n", "KERNEL_MUTATION_ESCALATION", "LEVEL_3"),
    "authority": (VAL, "_FLAGS = {'decision_authority': 'B7'}\n", "NON_KX108_AUTHORITY", "LEVEL_3"),
}


@pytest.mark.parametrize("name", list(CASES))
def test_red_boundary_changes_are_detected(snapshot, name):
    path, text, trigger, level = CASES[name]
    report = _scan(_with(snapshot, path, text))
    assert _sev(report).get(trigger) == level, _sev(report)
    assert report.status.name != "SAFE" and report.epoch_applicable is False


def test_status_follows_strongest_severity(snapshot):
    files = _with(snapshot, VAL, "_FLAGS = {'memory_write': True}\n")
    files = _with(files, "app/cognition/b7/router.py", "def _x(s):\n    return eval(s)\n")
    assert _scan(files).status.name == "EMERGENCY_HOLD"


def test_runtime_boundary_values_are_checked(snapshot):
    for key, value, trigger in (("memory_write", True, "MEMORY_WRITE_ESCALATION"), ("emits_act", True, "ACT_ESCALATION"),
                                ("kernel_mutation", True, "KERNEL_MUTATION_ESCALATION"),
                                ("decision_authority", "SELF", "NON_KX108_AUTHORITY")):
        from app.harness.state_explicit.contracts import BOUNDARY
        report = _scan(snapshot, boundary={**BOUNDARY, key: value})
        assert _sev(report).get(trigger) == "LEVEL_3"


def test_certified_sink_losing_its_guard_is_level_2(snapshot):
    src = snapshot[VAL].replace("and _is_issued(result)", "", 1)
    assert src != snapshot[VAL]
    assert _sev(_scan(_with(snapshot, VAL, src, append=False))).get("UNGUARDED_TRUST_SINK") == "LEVEL_2"


def test_new_module_in_runtime_closure_is_level_1(snapshot):
    files = _with(snapshot, "app/cognition/b7/helpers.py", "X = 1\n", append=False)
    files = _with(files, "app/cognition/b7/router.py", "from app.cognition.b7 import helpers  # noqa\n")
    assert _sev(_scan(files)).get("CERTIFIED_RUNTIME_CLOSURE_CHANGE") == "LEVEL_1"


def test_security_sensitive_contract_change_is_level_1(snapshot):
    assert _sev(_scan(_with(snapshot, "app/cognition/b7/contracts.py", "MAX_EXTRA = 1\n"))).get(
        "SECURITY_CONTRACT_CHANGED") == "LEVEL_1"


# ── false-positive defense ────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("path,text", [
    ("app/router/unrelated.py", "def f():\n    return 1\n"),                                     # 12 harmless change
    ("app/router/unrelated.py", "def f(s):\n    return eval(s)\n"),                              # outside B7 closure
    ("tests/b7/test_attack_fixture.py", "from app.cognition.b7.validation import _issue\neval('1')\n"),  # test fixture
    ("docs/notes.py", "# eval(x) exec(y) _issue(r) {'memory_write': True}\n"),                   # comments only
    ("OpenJarvis-pinned-fbbdb23/x.py", "def f(s):\n    return exec(s)\n"),                       # parallel workstream
])
def test_safe_mutations_do_not_trigger(snapshot, path, text):
    assert _scan(_with(snapshot, path, text, append=False)).status.name == "SAFE"


def test_docstrings_and_fixed_regex_do_not_trigger_inside_closure(snapshot):
    files = _with(snapshot, "app/cognition/b7/router.py",
                  '"""eval(x), exec(y), _issue(r), memory_write=True"""\nimport re\n_P = re.compile(r"x")\n')
    report = _scan(files)
    assert "SAME_PROCESS_UNTRUSTED_CODE" not in _sev(report) and "MEMORY_WRITE_ESCALATION" not in _sev(report)


# ── epoch / no self-recertification ───────────────────────────────────────────────────────────
def test_detection_never_recertifies(snapshot):
    from app.security import sentinel
    from app.security.b7_epoch1_baseline import BASELINE
    before = dict(BASELINE)
    report = _scan(_with(snapshot, VAL, "_FLAGS = {'emits_act': True}\n"))
    assert report.security_epoch == 1 and report.epoch_applicable is False
    assert dict(BASELINE) == before
    with pytest.raises(TypeError):
        BASELINE["security_epoch"] = 2
    assert not [n for n in dir(sentinel) if any(w in n.lower() for w in ("recertif", "update_baseline", "bump"))]
    assert _scan(snapshot).status.name == "SAFE"


def test_findings_carry_reproducible_evidence(snapshot):
    files = _with(snapshot, "app/cognition/b7/router.py", "def _x(s):\n    return eval(s)\n")
    (f,) = [f for f in _scan(files).findings if f.trigger == "SAME_PROCESS_UNTRUSTED_CODE"]
    assert f.boundary_id == "B7_COGNITIVE_RESOLUTION" and f.security_epoch == 1
    assert f.affected_surface == "app/cognition/b7/router.py" and "eval" in f.observed
    assert f.expected and f.reason and f.required_action and f.evidence_refs
    assert f.finding_id == _scan(files).findings[[x.trigger for x in _scan(files).findings].index(f.trigger)].finding_id
    assert len(f.finding_id.split("_", 1)[1]) == 64


def test_assert_boundary_safe_fails_closed(snapshot):
    from app.security.sentinel import SecurityHoldError, assert_boundary_safe
    assert_boundary_safe(snapshot)
    with pytest.raises(SecurityHoldError):
        assert_boundary_safe(_with(snapshot, VAL, "_FLAGS = {'kernel_mutation': True}\n"))

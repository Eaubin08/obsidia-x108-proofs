# Security Boundary Sentinel V0 (2026-10-07)

```
SENTINEL_VERSION=V0
BOUNDARY=B7_COGNITIVE_RESOLUTION
B7_SECURITY_EPOCH=1
BASELINE_SOURCE=docs/architecture/B7_RUNTIME_CLOSURE_20261007.md (closure 44b0391e, runtime HEAD 756a6ba7)
CODE=app/security/sentinel.py, app/security/b7_epoch1_baseline.py
TESTS=tests/security/test_boundary_sentinel_v0.py
SECURITY_SENTINEL_HARDENING=HOLD_FUTURE
PF_FREEZE_REVISIT_REQUIRED=YES
MEMORY_WRITE=False  EMITS_ACT=False  KERNEL_MUTATION=False  DECISION_AUTHORITY=KX108_ONLY
```

## Purpose

A certified boundary must not stay silently certified after a material change:
CLOSED_AT_SECURITY_EPOCH_N != CLOSED_AFTER_BOUNDARY_CHANGE. Sentinel V0 is a static, deterministic,
AST-based checker for build / test / CI / certification time. It is not a daemon, a watchdog or a
recovery system, and it has no provider, network, memory write, act or decision authority.

## Security epoch

A certification binds `boundary_id`, `security_epoch`, the certified assumptions, surfaces and status
(`b7_epoch1_baseline.BASELINE`, a read-only mapping). Any finding makes the epoch inapplicable to the
new architecture (`epoch_applicable=False`). The sentinel never edits the baseline, never bumps the
epoch and exposes no recertification API: epoch 2 can only come from an explicit audited
certification followed by a reviewed edit of the baseline file.

## Levels (frozen, deterministic)

| Level | Status | Meaning | Effect |
|---|---|---|---|
| LEVEL_1 | REAUDIT_REQUIRED | certified assumption changed, no demonstrated bypass | security check fails; re-audit required |
| LEVEL_2 | SECURITY_HOLD | dangerous trust-boundary condition reachable | fail closed; quarantine path; re-audit |
| LEVEL_3 | EMERGENCY_HOLD | authority / integrity invariant breached | fail certification; governed recovery decision |

Report status = status of the strongest finding. `assert_boundary_safe()` raises
`SecurityHoldError` on any non-SAFE status (fail closed). V0 does not shut down or reboot anything.

## Triggers (closure re-audit law, encoded)

| Trigger | Level | Detection |
|---|---|---|
| NEW_B7_IMPORTER | 1 | production module outside B7 imports `app.cognition*` |
| NEW_ISSUE_CALLER | 1 | `_issue` / `_is_issued` referenced outside the gate, or `_issue` called outside `validate_candidate` |
| NEW_TRUST_SINK_CALLER | 1 | production caller of `admit_trusted_context` / `register_derived` |
| NEW_TRUST_SINK | 1 | new guarded B7 function reading `derived_state` |
| LIVE_PROVIDER_WIRING_ACTIVATED | 1 | production code drives `propose` / `translate` / `validate_candidate(s)` |
| CERTIFIED_RUNTIME_CLOSURE_CHANGE | 1 | module added to / removed from the 40-module certified B7 closure |
| SECURITY_CONTRACT_CHANGED | 1 | LF-normalized SHA-256 of B7 package or B6 `contracts.py` differs, or new B7 file |
| UNGUARDED_TRUST_SINK | 2 | function reading `derived_state` without `_is_issued` + ACCEPT + `StateEntry` (incl. a certified sink losing its guard) |
| RAW_B6_TRUST_ADMISSION | 2 | B7 package references `ContextPacket` |
| SAME_PROCESS_UNTRUSTED_CODE | 2 | `eval`, `exec`, bare `compile`, `__import__`, `runpy.*`, `importlib.import_module` / `reload`, `spec_from_file_location`, `module_from_spec`, `exec_module`, `pickle.load(s)`, `marshal.loads`, `dill`, `cloudpickle`, `shelve.open`, `code.*` in the B7 closure or in a B7 importer |
| MEMORY_WRITE_ESCALATION | 3 | `memory_write: True` literal in the closure, or runtime `BOUNDARY["memory_write"]` not False |
| ACT_ESCALATION | 3 | `emits_act` / `allowed_to_act` True (literal or runtime BOUNDARY) |
| KERNEL_MUTATION_ESCALATION | 3 | `kernel_mutation` True (literal or runtime BOUNDARY) |
| NON_KX108_AUTHORITY | 3 | `decision_authority` != "KX108_ONLY" or `allowed_to_decide` True |

Each finding carries `finding_id` (`secf_` + SHA-256 of boundary, epoch, trigger, surface, symbol,
observed), boundary, epoch, severity, invariant, affected surface, symbol, expected, observed,
evidence refs, reason and required action. Evidence is not authority.

## Scope and false-positive rules

AST only: comments, docstrings and string literals are never code. Fixed `re.compile(...)` is an
attribute call and is not flagged. Test paths (`tests/`, `test_*.py`, `conftest.py`) are not production.
Dynamic-execution calls outside the B7 closure and outside B7 importers are out of scope, so parallel
workstreams (Jarvis, JarJar, GPS / Defense / Aviation, Multiverse, Trading, pinned vendors) are not
flagged merely for existing; wiring any of them into B7 does trigger, by design.

V0 static limits (recorded, not hidden): it does not prove absence of arbitrary callable injection
through data-driven dispatch (`getattr(...)()`), dynamic attribute aliasing of execution builtins, or
code reached only at run time; these stay under the closure assumption "no same-process untrusted
code" and the re-audit law.

## Non-goals — HOLD_FUTURE

`SECURITY_SENTINEL_HARDENING=HOLD_FUTURE`. V0 does NOT provide: persistent SECURITY_HOLD across
reboot, crash-safe hold durability, external watchdog, process supervisor, hardened IPC, sandbox,
evidence sealing before process death, automatic shutdown, safe reboot, known-good restart,
rollback after compromise, multi-process or multi-machine containment, memory-security lifecycle
integration, disaster recovery, corruption-resistant security log. These belong to the later
memory / world / reality / recovery architecture and must be revisited when durable memory, world
model or execution rails mature.

`PF_FREEZE_REVISIT_REQUIRED=YES`: at PF-FREEZE, SECURITY_SENTINEL_HARDENING must be explicitly
RESOLVED or ACCEPTED_HOLD_WITH_DEFINED_POST_FREEZE_GATE; it must never disappear silently.

# GitHub / MCP / Benchmark Governance Report

**Date:** 2026-05-19

## GitHub Workflow Guard

File: `periphery/github/github_workflow_guard.py`

| Action | Result |
|---|---|
| AUTO_MERGE | BLOCKED — NO_AUTONOMOUS_MERGE_POLICY |
| FORCE_MERGE | BLOCKED — NO_AUTONOMOUS_MERGE_POLICY |
| BYPASS_REVIEW | BLOCKED — NO_AUTONOMOUS_MERGE_POLICY |
| MERGE | BLOCKED — MERGE_REQUIRES_HUMAN_APPROVAL |
| CREATE_PR | ALLOWED (pre-review) — requires_human=True |
| PUSH_BRANCH | ALLOWED — requires_human=True |
| ADD_COMMENT | ALLOWED — requires_human=True |

**Rule:** No autonomous merge. Every merge requires explicit human approval.

## MCP Permission Matrix

File: `periphery/mcp/mcp_permission_matrix.py`

**Key distinction:** Tool access ≠ permission.
- `tool_access_granted=True` means the tool is callable
- `permission_granted` is a separate, stricter check
- Kernel-touching tools (`modify_kernel`, `write_kernel`, etc.) always return `permission_granted=False`
- Memory-write tools: `permission_granted=False` for all non-sovereign agents

## Benchmark Case Schema

File: `periphery/benchmarks/benchmark_case_schema.py`

| Benchmark | Domain | Expected Gate | Type |
|---|---|---|---|
| AgentDojo | bank | BLOCK | adversarial |
| TAU-bench | trading | HOLD | uncertainty |
| BFCL | bank | ALLOW | standard |

**Purpose:** Maps external benchmark cases to Obsidia expected governance gates for regression testing.

## Test Coverage

- `tests/periphery/test_github_no_auto_merge.py` — 6 tests
- `tests/periphery/test_mcp_tool_access_not_permission.py` — 5 tests
- `tests/periphery/test_benchmark_case_schema.py` — 5 tests

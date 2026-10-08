# CSSA — Historical batch fixture recovery audit (2026-10-08)

Mode: READ_ONLY audit / no execution / fail-closed.
Branch: `feat/cssa-v01-active`.
Missing batch identity: `84a929c6f48a90c5`.

## Findings grounded in current source

- `tests/test_batch_execution_v0.py` contains five tests depending on the historical batch by its fixed ID (CLI prepare/status/inspect and read-only refusal assertions). The suite expects five children, zero executable candidates, verified integrity and `BATCH_EXECUTION_NOT_READY` with `NOT_READY_NO_DELTA`.
- `scripts/obsidia_batch_selector.py` sets `SELECTOR_DIR = Path(os.environ.get("LOCALAPPDATA", "")) / "Obsidia" / "batch_selector"`. The default is machine/runtime-local, not a tracked fixture path.
- `scripts/obsidia_batch_execution.py` loads a proposal via `sel._load_batch(batch_id, selector_dir)` and similarly uses `LOCALAPPDATA` for execution records.
- GitHub code search on the available indexed repository found the exact batch ID in the test suite but did not discover a tracked proposal with that ID. Search absence is not proof it never existed; previous branches, local disk, workflow artifacts and non-indexed files remain candidates.
- CI result for Lean fix commit `765e3044216a96c4ceab741fbfbce22b689cf289` was not confirmed by the PR-triggered workflow lookup in this audit.

## Controlled recovery sequence

1. Check exact path `%LOCALAPPDATA%\\Obsidia\\batch_selector\\batches\\84a929c6f48a90c5\\batch_proposal.json` on the source machine or historical backups. Verify the location using selector's `_batch_path` implementation before copying.
2. Search archived CI artifacts and historical branch trees for the same batch ID and expected child entries.
3. Preserve original bytes, provenance, creation context, SHA-256 and a copy outside the active runtime. DO NOT silently regenerate the historical proof.
4. Independently run integrity verification and compare against the five test expectations in isolation.
5. If unrecoverable: record `HISTORICAL_FIXTURE_UNAVAILABLE` as a blocking historical assertion; add a **separate** deterministic synthetic regression suite with clearly distinct identity. Do not mark the legacy proof as PASS.
6. Re-run all tests on one pinned HEAD with Lean/CLI/runtime prerequisites present, then proceed to CSSA/PME/association simulated E2E only after honest global verdict.

## Guardrails

`KX108_ONLY`; no kernel changes; no `main` merge; no real mail/CRM/calendar operation; no manufactured historic approval, receipt or hash. Global regression remains HOLD until actual CI evidence exists.

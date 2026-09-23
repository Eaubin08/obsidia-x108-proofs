# GPS V0.1 Replay And Kernel Live Note

Status: DRY_RUN_REPLAY_PASS / KERNEL_LIVE_POST_OK
Date: 2026-08-02

## Replay Verifier Boundary

The GPS V0.1 replay verifier is intentionally dry-run only.

It verifies:
- receipt domain and contract
- `DOMAIN_BRIDGE_ONLY`
- `KX108_ONLY`
- connector non-sovereignty
- local receipt hash presence
- OS3 ticket presence
- OS3 hash chain fields
- nuisance preservation for spoof and replay scenarios
- `replay_status == NOT_RUN`

It does not:
- mutate existing receipts
- change OS3 `replay_status`
- claim production replay
- touch Merkle, RFC3161, seal, Lean, or sealed kernel files

Generated report:

`artifacts/gps_v01_replay_report.json`

Observed result:

`PASS` over 3 receipts in `DRY_RUN_REPLAY_VERIFIER_NOT_PRODUCTION` mode.

## Kernel Live Boundary

The next check is read-only runtime availability:

`GET http://127.0.0.1:3001/kernel/ragnarok`

Expected outcomes:

- If reachable, perform a non-actuating local gate submission path.
- If unreachable, keep GPS nominal output in `HOLD` with `GATE_REQUESTS_UNAVAILABLE` or `GATE_FAIL_CLOSED`.

Initial observed result on 2026-08-02:

`UNAVAILABLE` - unable to connect to `http://127.0.0.1:3001/kernel/ragnarok`.

Updated observed result after launching `server.kernel.sealed.cjs`:

- process id: `15308`
- `GET /kernel/ragnarok`: `404`, expected because the route is POST-only
- `POST /kernel/ragnarok`: `HTTP 200`
- observed `x108_gate`: `HOLD`
- observed `market_verdict`: `RECALC_TRAJECTORY`
- observed `reason_code`: `UNKNOWNS_OR_CONFIDENCE_LOW`
- observed decision file: `MonProjet/allData/decision_gps_defense_aviation_1785698704124.json`

Captured report:

`artifacts/gps_v01_kernel_live_check.json`

Forbidden:

- editing `server.kernel.sealed.cjs`
- editing `runtime_terrain_bank_trading_gps/server.kernel.sealed.cjs`
- claiming live kernel approval unless endpoint response is captured
- claiming production replay while OS3 reports `NOT_RUN`

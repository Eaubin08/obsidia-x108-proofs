# Obsidia Decision Gateway — Interface (v1)

This package exposes a single governance interface over the Obsidia Kernel.

## Endpoints

### POST /v1/decision
Input: ObsidiaDecisionRequest (supports PROPOSE and ACTION)
Output: ObsidiaDecisionResult (BLOCK | HOLD | ACT) + audit + artifacts refs

### GET /v1/replay/{trace_id}
Returns stored request/result JSON for a given trace_id (local filesystem store by default).

### GET /health
Basic health check.

## Running (FastAPI)

Install:
- fastapi
- uvicorn

Run:
```bash
export OBSIDIA_BIND=local   # local | lan | public
export OBSIDIA_PORT=8000
bash api_server/run_api.sh
```

Bind modes:
- local: 127.0.0.1 (default)
- lan:   0.0.0.0 (reachable on your LAN)
- public:0.0.0.0 (behind your own reverse proxy + TLS)

Storage:
- Default store dir: ./api_store
- Override: export OBSIDIA_STORE_DIR=/path/to/store

## CLI

```bash
python cli/obsidia_cli.py decision request.json
# or
cat request.json | python cli/obsidia_cli.py decision -
python cli/obsidia_cli.py replay <trace_id> --store-dir api_store
```

## Contract Notes

- PROPOSE never executes external side-effects. It is safe to use for sandbox/simulation modules (e.g. OS_TRAD).
- ACTION is governed by the kernel. If decision != ACT, execution must not occur.
- required_human_gate may be raised for HOLD/BLOCK under ambiguity or governance constraints.

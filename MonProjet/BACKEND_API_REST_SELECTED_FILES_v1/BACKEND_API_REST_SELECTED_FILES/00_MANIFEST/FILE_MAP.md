# FILE_MAP


| Dossier | Fichier | Rôle | Couche | Source ZIP |
|---|---|---|---|---|
| `01_primary_obsidia_lab_trad/gateway` | `server.ts` | Gateway Express REST /api/* | `gateway` | `obsidia_lab` |
| `01_primary_obsidia_lab_trad/gateway` | `package.json` | Node dependencies for gateway | `config` | `obsidia_lab` |
| `01_primary_obsidia_lab_trad/gateway` | `tsconfig.json` | TypeScript config for gateway | `config` | `obsidia_lab` |
| `01_primary_obsidia_lab_trad/gateway` | `.env.example` | Env example for gateway/backend | `config` | `obsidia_lab` |
| `01_primary_obsidia_lab_trad/gateway/lib/banking` | `engine.ts` | Imported backend logic used by server.ts: features, gates, banking, ecommerce | `service_support` | `obsidia_lab` |
| `01_primary_obsidia_lab_trad/gateway/lib/core` | `invariants.ts` | Imported backend logic used by server.ts: features, gates, banking, ecommerce | `service_support` | `obsidia_lab` |
| `01_primary_obsidia_lab_trad/gateway/lib/ecommerce` | `safetyGate.ts` | Imported backend logic used by server.ts: features, gates, banking, ecommerce | `service_support` | `obsidia_lab` |
| `01_primary_obsidia_lab_trad/gateway/lib/execution` | `erc8004Builder.ts` | Imported backend logic used by server.ts: features, gates, banking, ecommerce | `service_support` | `obsidia_lab` |
| `01_primary_obsidia_lab_trad/gateway/lib/features` | `coherence.ts` | Imported backend logic used by server.ts: features, gates, banking, ecommerce | `service_support` | `obsidia_lab` |
| `01_primary_obsidia_lab_trad/gateway/lib/features` | `friction.ts` | Imported backend logic used by server.ts: features, gates, banking, ecommerce | `service_support` | `obsidia_lab` |
| `01_primary_obsidia_lab_trad/gateway/lib/features` | `regime.ts` | Imported backend logic used by server.ts: features, gates, banking, ecommerce | `service_support` | `obsidia_lab` |
| `01_primary_obsidia_lab_trad/gateway/lib/features` | `volatility.ts` | Imported backend logic used by server.ts: features, gates, banking, ecommerce | `service_support` | `obsidia_lab` |
| `01_primary_obsidia_lab_trad/gateway/lib/gates` | `integrityGate.ts` | Imported backend logic used by server.ts: features, gates, banking, ecommerce | `service_support` | `obsidia_lab` |
| `01_primary_obsidia_lab_trad/gateway/lib/gates` | `riskKillswitch.ts` | Imported backend logic used by server.ts: features, gates, banking, ecommerce | `service_support` | `obsidia_lab` |
| `01_primary_obsidia_lab_trad/gateway/lib/gates` | `x108TemporalLock.ts` | Imported backend logic used by server.ts: features, gates, banking, ecommerce | `service_support` | `obsidia_lab` |
| `01_primary_obsidia_lab_trad/gateway/lib/simulation` | `simLite.ts` | Imported backend logic used by server.ts: features, gates, banking, ecommerce | `service_support` | `obsidia_lab` |
| `01_primary_obsidia_lab_trad/gateway/data/banking` | `scenarios.json` | Scenario/market JSON consumed by server.ts | `data_support` | `obsidia_lab` |
| `01_primary_obsidia_lab_trad/gateway/data/ecommerce` | `scenarios.json` | Scenario/market JSON consumed by server.ts | `data_support` | `obsidia_lab` |
| `01_primary_obsidia_lab_trad/gateway/data` | `scenarios.json` | Scenario/market JSON consumed by server.ts | `data_support` | `obsidia_lab` |
| `01_primary_obsidia_lab_trad/gateway/data/strasbourg_clock` | `README.md` | Scenario/market JSON consumed by server.ts | `data_support` | `obsidia_lab` |
| `01_primary_obsidia_lab_trad/gateway/data/strasbourg_clock/graphs` | `test1_baseline_delta_day.png` | Scenario/market JSON consumed by server.ts | `data_support` | `obsidia_lab` |
| `01_primary_obsidia_lab_trad/gateway/data/strasbourg_clock/graphs` | `test2_noise_delta_day.png` | Scenario/market JSON consumed by server.ts | `data_support` | `obsidia_lab` |
| `01_primary_obsidia_lab_trad/gateway/data/strasbourg_clock/graphs` | `test3_structural_error_delta_day.png` | Scenario/market JSON consumed by server.ts | `data_support` | `obsidia_lab` |
| `01_primary_obsidia_lab_trad/gateway/data/strasbourg_clock/graphs` | `test4_hold_delta_day.png` | Scenario/market JSON consumed by server.ts | `data_support` | `obsidia_lab` |
| `01_primary_obsidia_lab_trad/gateway/data/strasbourg_clock` | `manifest.json` | Scenario/market JSON consumed by server.ts | `data_support` | `obsidia_lab` |
| `01_primary_obsidia_lab_trad/gateway/data/strasbourg_clock` | `test1_baseline.csv` | Scenario/market JSON consumed by server.ts | `data_support` | `obsidia_lab` |
| `01_primary_obsidia_lab_trad/gateway/data/strasbourg_clock` | `test2_noise.csv` | Scenario/market JSON consumed by server.ts | `data_support` | `obsidia_lab` |
| `01_primary_obsidia_lab_trad/gateway/data/strasbourg_clock` | `test3_structural_error.csv` | Scenario/market JSON consumed by server.ts | `data_support` | `obsidia_lab` |
| `01_primary_obsidia_lab_trad/gateway/data/strasbourg_clock` | `test4_hold.csv` | Scenario/market JSON consumed by server.ts | `data_support` | `obsidia_lab` |
| `01_primary_obsidia_lab_trad/gateway/data/trading` | `BTC_1h.json` | Scenario/market JSON consumed by server.ts | `data_support` | `obsidia_lab` |
| `01_primary_obsidia_lab_trad/fastapi_engine/api_server` | `attestation.py` | FastAPI engine entrypoint + security/audit helpers | `fastapi` | `obsidia_lab` |
| `01_primary_obsidia_lab_trad/fastapi_engine/api_server` | `audit_log.py` | FastAPI engine entrypoint + security/audit helpers | `fastapi` | `obsidia_lab` |
| `01_primary_obsidia_lab_trad/fastapi_engine/api_server` | `main.py` | FastAPI engine entrypoint + security/audit helpers | `fastapi` | `obsidia_lab` |
| `01_primary_obsidia_lab_trad/fastapi_engine/api_server` | `run_api.sh` | FastAPI engine entrypoint + security/audit helpers | `fastapi` | `obsidia_lab` |
| `01_primary_obsidia_lab_trad/fastapi_engine/api_server` | `run_attestation.py` | FastAPI engine entrypoint + security/audit helpers | `fastapi` | `obsidia_lab` |
| `01_primary_obsidia_lab_trad/fastapi_engine/api_server` | `security.py` | FastAPI engine entrypoint + security/audit helpers | `fastapi` | `obsidia_lab` |
| `01_primary_obsidia_lab_trad/fastapi_engine/api_server` | `signing.py` | FastAPI engine entrypoint + security/audit helpers | `fastapi` | `obsidia_lab` |
| `01_primary_obsidia_lab_trad/fastapi_engine/api_server` | `worm_uploader.py` | FastAPI engine entrypoint + security/audit helpers | `fastapi` | `obsidia_lab` |
| `01_primary_obsidia_lab_trad/fastapi_engine/unified_interface` | `__init__.py` | Pipeline/orchestrator used by API server | `engine_support` | `obsidia_lab` |
| `01_primary_obsidia_lab_trad/fastapi_engine/unified_interface` | `orchestrator.py` | Pipeline/orchestrator used by API server | `engine_support` | `obsidia_lab` |
| `01_primary_obsidia_lab_trad/fastapi_engine/unified_interface` | `pipeline.py` | Pipeline/orchestrator used by API server | `engine_support` | `obsidia_lab` |
| `01_primary_obsidia_lab_trad/fastapi_engine/obsidia_kernel` | `__init__.py` | Kernel contract/results used by API server | `engine_support` | `obsidia_lab` |
| `01_primary_obsidia_lab_trad/fastapi_engine/obsidia_kernel` | `contract.py` | Kernel contract/results used by API server | `engine_support` | `obsidia_lab` |
| `01_primary_obsidia_lab_trad/fastapi_engine/obsidia_kernel` | `kernel.py` | Kernel contract/results used by API server | `engine_support` | `obsidia_lab` |
| `01_primary_obsidia_lab_trad/fastapi_engine` | `requirements_optional.txt` | Optional Python dependencies for FastAPI engine | `config` | `obsidia_lab` |
| `01_primary_obsidia_lab_trad/fastapi_engine/deploy` | `docker-compose.yml` | Engine deploy example | `deploy` | `obsidia_lab` |
| `01_primary_obsidia_lab_trad/canonical_api` | `app.py` | Canonical FastAPI API: DecisionRequest/DecisionResponse, audit, nonce, signature | `canonical_api` | `obsidia_lab` |
| `01_primary_obsidia_lab_trad/canonical_api` | `requirements.txt` | Python dependencies for canonical API | `config` | `obsidia_lab` |
| `01_primary_obsidia_lab_trad/canonical_api/core` | `__init__.py` | Python package init | `config` | `obsidia_lab` |
| `01_primary_obsidia_lab_trad/canonical_api/core/api` | `__init__.py` | Python package init | `config` | `obsidia_lab` |
| `01_primary_obsidia_lab_trad/canonical_api/core/api/security` | `__init__.py` | Nonce, signature, merkle helpers | `security` | `obsidia_lab` |
| `01_primary_obsidia_lab_trad/canonical_api/core/api/security` | `merkle.py` | Nonce, signature, merkle helpers | `security` | `obsidia_lab` |
| `01_primary_obsidia_lab_trad/canonical_api/core/api/security` | `nonce.py` | Nonce, signature, merkle helpers | `security` | `obsidia_lab` |
| `01_primary_obsidia_lab_trad/canonical_api/core/api/security` | `signature.py` | Nonce, signature, merkle helpers | `security` | `obsidia_lab` |
| `01_primary_obsidia_lab_trad/canonical_api/core/engine` | `__init__.py` | Python package init | `config` | `obsidia_lab` |
| `01_primary_obsidia_lab_trad/canonical_api/core/engine/obsidia_os2` | `__init__.py` | Metrics/decision functions imported by core/api/app.py | `engine_support` | `obsidia_lab` |
| `01_primary_obsidia_lab_trad/canonical_api/core/engine/obsidia_os2` | `metrics.py` | Metrics/decision functions imported by core/api/app.py | `engine_support` | `obsidia_lab` |
| `01_primary_obsidia_lab_trad/contracts` | `openapi.yaml` | OpenAPI contract for engine API | `contract` | `obsidia_lab` |
| `01_primary_obsidia_lab_trad/contracts` | `OpenAPI_Contract.yaml` | Presentation OpenAPI contract | `contract` | `obsidia_lab` |
| `01_primary_obsidia_lab_trad/db_drizzle` | `schema.ts` | DB schema: decision_tickets, audit_log, simulation_runs, etc. | `db` | `obsidia_lab` |
| `01_primary_obsidia_lab_trad/db_drizzle` | `db.ts` | DB adapter/helpers for os4-platform | `db` | `obsidia_lab` |
| `01_primary_obsidia_lab_trad/db_drizzle` | `drizzle.config.ts` | Drizzle config | `db_config` | `obsidia_lab` |
| `01_primary_obsidia_lab_trad/db_drizzle` | `package.json` | Dependencies for os4-platform DB/API layer | `config` | `obsidia_lab` |
| `01_primary_obsidia_lab_trad/trpc_reference` | `routers.ts` | tRPC router reference: decision/replay/audit/proofs/scenarios | `api_reference` | `obsidia_lab` |
| `02_backend_local_skeleton` | `server.ts` | Minimal Express REST skeleton: health/explorer/system/file/status/ingest/audit | `gateway_reference` | `backend_local` |
| `02_backend_local_skeleton` | `package.json` | Node deps for local backend skeleton | `config` | `backend_local` |
| `02_backend_local_skeleton` | `tsconfig.json` | TS config for local backend skeleton | `config` | `backend_local` |
| `02_backend_local_skeleton` | `.env.example` | Env example for local backend skeleton | `config` | `backend_local` |
| `02_backend_local_skeleton/runtime/contracts` | `core.ts` | Zod contracts/models: DecisionTicket, RawRequest, SovereignDecision, etc. | `models` | `backend_local` |
| `02_backend_local_skeleton/app/services` | `orchestrator.ts` | Service orchestration example | `service` | `backend_local` |
| `02_backend_local_skeleton/app/services` | `explorer.ts` | Explorer service example | `service` | `backend_local` |
| `02_backend_local_skeleton/runtime/os0_core/kernel` | `engine.ts` | Minimal kernel engine | `engine` | `backend_local` |
| `03_bank_robo_db_reference/server` | `db.ts` | Lazy Drizzle MySQL connection pattern | `db_reference` | `bank_robo` |
| `03_bank_robo_db_reference/drizzle` | `schema.ts` | MySQL schema: users, transactions, simulation_sessions | `db_reference` | `bank_robo` |
| `03_bank_robo_db_reference` | `drizzle.config.ts` | Drizzle config for MySQL | `db_config` | `bank_robo` |
| `03_bank_robo_db_reference` | `package.json` | Node deps for bank-robo backend | `config` | `bank_robo` |
| `03_bank_robo_db_reference/server` | `routers.ts` | tRPC router reference for banking process/scenarios/insights | `api_reference` | `bank_robo` |
| `03_bank_robo_db_reference/server` | `bankingEngine.ts` | Banking business service example | `service_reference` | `bank_robo` |
| `04_proof_core_fallback` | `server.ts` | Fallback gateway similar to Obsidia-lab version | `fallback` | `proof_core` |
| `04_proof_core_fallback/contracts` | `openapi.yaml` | Fallback proof-core OpenAPI contract | `fallback_contract` | `proof_core` |
| `04_proof_core_fallback/contracts` | `OpenAPI_Contract.yaml` | Fallback proof-core presentation OpenAPI contract | `fallback_contract` | `proof_core` |
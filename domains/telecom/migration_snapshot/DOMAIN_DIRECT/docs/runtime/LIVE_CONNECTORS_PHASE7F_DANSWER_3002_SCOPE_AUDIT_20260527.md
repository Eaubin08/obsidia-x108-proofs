# LIVE_CONNECTORS_PHASE7F_DANSWER_3002_SCOPE_AUDIT_20260527

Status: DIAGNOSTIC_ONLY

## Scope

Audit whether Danswer/Onyx/3002 is required for the current validated Brody live flow.

## Port 3002
- health_code = DOWN
- health_body = 

## Current validated critical flow
- Workbench 5173 -> Brody API 8012 -> Graphiti V20 readonly proxy -> ObsidiaShell 8011

## Docker services
- CONTAINER ID   NAMES                  IMAGE                  PORTS
- c91e676cc173   deploy-obsidia_api-1   python:3.11-slim       0.0.0.0:8001->8000/tcp, [::]:8001->8000/tcp
- 8bb013653735   deploy-caddy-1         deploy-caddy           0.0.0.0:80->80/tcp, [::]:80->80/tcp, 0.0.0.0:443->443/tcp, [::]:443->443/tcp
- b21c9d30bcd7   deploy-neo4j-1         neo4j:5.26-community   0.0.0.0:7475->7474/tcp, [::]:7475->7474/tcp, 0.0.0.0:7688->7687/tcp, [::]:7688->7687/tcp
- 896f7fa7dab1   deploy-minio-1         minio/minio:latest     0.0.0.0:9000-9001->9000-9001/tcp, [::]:9000-9001->9000-9001/tcp

## References found
- .\docs\runtime\LIVE_CONNECTORS_PHASE7A_PRECHECK_20260527.md:16: - port 3002: DOWN pid= process=
- .\docs\runtime\LIVE_CONNECTORS_PHASE7A_PRECHECK_20260527.md:26: - Possible service 3002: FAIL http://127.0.0.1:3002/health code= length=
- .\docs\runtime\LIVE_CONNECTORS_PHASE7A_PRECHECK_20260527.md:33: - bus/gateway 8000/8001/3002 if still useful
- .\docs\runtime\LIVE_CONNECTORS_PHASE7B_FIX_REPORT_20260527.md:35: - 3002 = Danswer optional/obsolete for current flow
- .\docs\runtime\LIVE_CONNECTORS_PHASE7B_FIX_REPORT_20260527.md:44: - No Danswer integration.
- .\docs\runtime\LIVE_CONNECTORS_PHASE7C_WORKBENCH_VALIDATION_20260527.md:55: - No Danswer integration.
- .\docs\runtime\LIVE_CONNECTORS_PHASE7C_WORKBENCH_VALIDATION_20260527.md:66: - 3002 = optional / not required for current flow
- .\docs\runtime\LIVE_CONNECTORS_PHASE7D_FLOW_AUTH_METRICS_20260527.md:26: - Danswer optional 3002 /health = FAIL
- .\docs\runtime\LIVE_CONNECTORS_PHASE7D_FLOW_AUTH_METRICS_20260527.md:56: Danswer 3002 is optional and not required for the current Brody/Graphiti/Workbench flow.
- .\periphery\brody_memory_readonly\brody_operator_io_loop_clean_close_readonly\BRODY_OPERATOR_IO_LOOP_CLEAN_CLOSE_READONLY_MANIFEST.json:5: "created_at":  "2026-05-13T06:56:33.5630023Z",
- .\periphery\brody_memory_readonly\neo4j_brody_guide_bridge_readonly\BRODY_NEO4J_GUIDE_BRIDGE_READONLY_MANIFEST.json:3: "date":  "20260512_230024",
- .\sigma\batches\bank_truth_proxy_pack.json:2452: "available_cash": 30020.0,
- .\_graphiti_readonly_indexes\GRAPHITI_READONLY_INDEX_V2_FUSION_20260512_224854\graphiti_readonly_index_v2.json:7211: "body_sha256": "3002089C0AE70978F890B2B536D0872CE5AFCF60888707C7F22611D46FF3732F",
- .\_graphiti_readonly_indexes\GRAPHITI_READONLY_INDEX_V2_FUSION_20260512_224854\graphiti_readonly_index_v2.json:26532: "body_sha256": "0EC95A17A7B1F0D65330029E39CC5AC43CF470A1F18632A4EF9A5CCAAD60AD69",
- .\_graphiti_readonly_indexes\GRAPHITI_READONLY_INDEX_V2_FUSION_20260512_224854\graphiti_readonly_index_v2.json:51456: "body_sha256": "A7295D97A2547D6A49A3002FE9515EC057B093EF3B07F0DFDDB86D041FF23596",
- .\_graphiti_readonly_indexes\GRAPHITI_READONLY_INDEX_V2_FUSION_20260512_224854\graphiti_readonly_index_v2.json:61198: "body_sha256": "290EDF6D1E323AF83CF00807C8B86A516023002913107C878DBA1D2DEC89FA46",
- .\_graphiti_readonly_indexes\GRAPHITI_READONLY_INDEX_V2_FUSION_20260512_224854\graphiti_readonly_index_v2.json:69331: "body_sha256": "649FA67227A78E66CB82D18E392FDB18D9A30024DF8709445B70A72F6803FD73",
- .\_graphiti_readonly_indexes\GRAPHITI_READONLY_INDEX_V2_FUSION_20260512_224854\graphiti_readonly_index_v2.json:69664: "id": "GRAPHITI_V2_003002",
- .\_local_audits\brody_memory_pipeline_commit_now_20260514\MIGRATION_EXCLUDED_INDEX.json:350: "name": "BRODY_NEO4J_GUIDE_BRIDGE_READONLY_20260512_230024",
- .\_local_audits\BRODY_PERSONAL_SIDECAR_TO_REAL_INTAKE_GATE_V1\PIPELINE_LOCATOR_REPORT_2026-05-22T20-23-04.json:43203: "path": "_local_audits\\brody_sessions\\local\\records\\3002_4c51ed76b2a8.json",
- .\_local_audits\BRODY_PERSONAL_SIDECAR_TO_REAL_INTAKE_GATE_V1\PIPELINE_LOCATOR_REPORT_2026-05-22T20-23-04.json:43204: "name": "3002_4c51ed76b2a8.json",
- .\_local_audits\BRODY_PERSONAL_SIDECAR_TO_REAL_INTAKE_GATE_V1\PIPELINE_LOCATOR_REPORT_2026-05-22T20-23-04.json:43209: "path": "_local_audits\\brody_sessions\\local\\records\\3002_4c51ed76b2a8.md",
- .\_local_audits\BRODY_PERSONAL_SIDECAR_TO_REAL_INTAKE_GATE_V1\PIPELINE_LOCATOR_REPORT_2026-05-22T20-23-04.json:43210: "name": "3002_4c51ed76b2a8.md",
- .\_local_audits\BRODY_PERSONAL_SIDECAR_TO_REAL_INTAKE_GATE_V1\PIPELINE_LOCATOR_REPORT_2026-05-22T20-23-04.md:7223: - [unclassified] _local_audits\brody_sessions\local\records\3002_4c51ed76b2a8.json (1634 bytes)
- .\_local_audits\BRODY_PERSONAL_SIDECAR_TO_REAL_INTAKE_GATE_V1\PIPELINE_LOCATOR_REPORT_2026-05-22T20-23-04.md:7224: - [unclassified] _local_audits\brody_sessions\local\records\3002_4c51ed76b2a8.md (1224 bytes)
- .\_local_audits\BRODY_PERSONAL_SIDECAR_TO_REAL_INTAKE_GATE_V1\PIPELINE_LOCATOR_REPORT_2026-05-22T20-41-24.json:43239: "path": "_local_audits\\brody_sessions\\local\\records\\3002_4c51ed76b2a8.json",
- .\_local_audits\BRODY_PERSONAL_SIDECAR_TO_REAL_INTAKE_GATE_V1\PIPELINE_LOCATOR_REPORT_2026-05-22T20-41-24.json:43240: "name": "3002_4c51ed76b2a8.json",
- .\_local_audits\BRODY_PERSONAL_SIDECAR_TO_REAL_INTAKE_GATE_V1\PIPELINE_LOCATOR_REPORT_2026-05-22T20-41-24.json:43245: "path": "_local_audits\\brody_sessions\\local\\records\\3002_4c51ed76b2a8.md",
- .\_local_audits\BRODY_PERSONAL_SIDECAR_TO_REAL_INTAKE_GATE_V1\PIPELINE_LOCATOR_REPORT_2026-05-22T20-41-24.json:43246: "name": "3002_4c51ed76b2a8.md",
- .\_local_audits\BRODY_PERSONAL_SIDECAR_TO_REAL_INTAKE_GATE_V1\PIPELINE_LOCATOR_REPORT_2026-05-22T20-41-24.md:7229: - [unclassified] _local_audits\brody_sessions\local\records\3002_4c51ed76b2a8.json (1634 bytes)
- .\_local_audits\BRODY_PERSONAL_SIDECAR_TO_REAL_INTAKE_GATE_V1\PIPELINE_LOCATOR_REPORT_2026-05-22T20-41-24.md:7230: - [unclassified] _local_audits\brody_sessions\local\records\3002_4c51ed76b2a8.md (1224 bytes)
- .\_local_audits\X108_RELOCATION_AUDIT_20260514\RELOCATION_SOURCE_SCAN.json:1350: "folder_name": "BRODY_NEO4J_GUIDE_BRIDGE_READONLY_20260512_230024",
- .\_local_audits\X108_RELOCATION_AUDIT_20260514\RELOCATION_SOURCE_SCAN.json:1351: "source_path": "C:\\Users\\User\\Desktop\\obsidia-engine-proof-core\\_local_audits\\BRODY_NEO4J_GUIDE_BRIDGE_READONLY_20260512_230024",
- .\MANIFEST_SHA256.json:460: "periphery\\cognitive_trees\\memory_world_mapper.py": "a5b184b541d26e1f267e017b0f5c8963f7ae6793002ce248e4a33696cdb72851",
- .\MANIFEST_SHA256_NEW.json:285: "periphery\\cognitive_trees\\memory_world_mapper.py": "a5b184b541d26e1f267e017b0f5c8963f7ae6793002ce248e4a33696cdb72851",

## Compose files
- C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs_REMOTE_A5F21C6B\proofs\V18_3_1\engine_buildable_0_9_3_1\deploy\docker-compose.minio.yml length=409 updated=05/26/2026 20:44:04
- C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs_REMOTE_A5F21C6B\proofs\V18_3_1\engine_buildable_0_9_3_1\deploy\docker-compose.mtls.yml length=860 updated=05/26/2026 20:44:04
- C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs_REMOTE_A5F21C6B\proofs\V18_3_1\engine_buildable_0_9_3_1\deploy\docker-compose.yml length=1427 updated=05/26/2026 20:44:04

## Boundary
- Diagnostic only.
- No service started.
- No Docker mutation.
- No POST executed.
- No decision request sent.
- No token request sent.
- KX108_ONLY remains sole decision authority.

## Next
- If 3002 is not referenced by the current validated flow, mark Danswer/Onyx as OUT_OF_SCOPE_FOR_CURRENT_BRODY_FLOW.
- If references show active Workbench/Brody dependency, prepare a controlled reconnect plan.
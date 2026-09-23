# Sigma Final Freeze Index ? F60 to F68

Date UTC: 20260530_014524

## Status

- F68_STATUS: PASS
- Decision authority: KX108_ONLY
- Readonly: true
- Advisory only: true
- Commit: NO
- Tag: NO
- Push: NO
- Freeze directory created: NO

## Regression

- F68 regression exit: 0

## Routes indexed

- GET /bus/stats
- GET /bus/bridge
- POST /bus/signal
- GET /api/periphery/monitoring/sigma/domains
- GET /api/periphery/monitoring/sigma/evaluate
- GET /api/periphery/monitoring/sigma/bank
- GET /api/periphery/monitoring/sigma/trading
- GET /api/periphery/monitoring/sigma/ecom
- GET /api/periphery/monitoring/sigma/gps-defense-aviation
- POST /api/periphery/sigma/evaluate

## Latest F67 live proof

- path: docs/runtime/F67_SIGMA_LIVE_SMOKE_API_AUDIT_20260530_014358.json
- ok: True
- source: LIVE_SERVER_9010
- routes_checked: 10
- routes_pass: 10
- routes_fail: 0
- sha256: 381aa924c1082476ba9169f0c48fdbb4a53702c3d58707f7acd1877e1cbe7666

## Files indexed

- `sigma/registry.py` ? sha256 `56c2d41eca4ae064da7a1f4ad574a9f2b4f2b4dd71b59248ca095abe63810ce8` ? 3703 bytes
- `sigma/evaluate.py` ? sha256 `7af56f2b5c1a79bfef3eb90922ba0e2565b983cfc0493c28f8aaf0c8d6d8b9b5` ? 8430 bytes
- `sigma/packets.py` ? sha256 `3b774de869af5dd4f353921108db9db2ae874c352dbb36d02b40e923603d7e2d` ? 7008 bytes
- `sigma/connectors.py` ? sha256 `b1dd3e30bf01e60bad94baa8688e2d6f1fc0cd9e1d34befeded189ac6b86bcfb` ? 6380 bytes
- `sigma/orchestrator_preview.py` ? sha256 `d94a955220fda76b65a1b93a5fa148f3a73bb94baf191a8188b89bdde77c785b` ? 5790 bytes
- `apps/obsidia_api/routes/sigma_monitoring.py` ? sha256 `e66753becbe272cf11454929606017598f7ffd9932beb013cf07a2eb98b53346` ? 3803 bytes
- `apps/obsidia_api/bus/sigma_bridge.py` ? sha256 `fae46de164518d515e22d5380382128d0c3dc876ad30461e968e5ef60109a668` ? 2944 bytes
- `apps/obsidia_api/bus/state_aggregator.py` ? sha256 `88091147b5abaffdcd21c5a3d4ca2f8e5db77c6c92a1a2aa9386e39a1d31169e` ? 3449 bytes
- `apps/obsidia_api/main.py` ? sha256 `1e30e76cec268d963b272b80ca9695f689e6ceae26c9d9a12ddb016b9dec99fa` ? 2269 bytes
- `tests/sigma/test_f60_sigma_registry_repair.py` ? sha256 `cfd984a5948c7298b3914820c99f38031fc8fa43545b51224414b9612e789981` ? 9875 bytes
- `tests/sigma/test_f61_sigma_dispatcher_readonly_evaluate.py` ? sha256 `4f4f47a5f9c7370095737e1e47720b40553fc5299a36d1849db0acdde3359ecd` ? 24611 bytes
- `tests/sigma/test_f62_sigma_domain_packets_normalization.py` ? sha256 `9add0cef23c2c26868a7514c67bbe1c8e7d0845f7634e5ece7581eb0024d03a4` ? 24823 bytes
- `tests/api/test_f63_sigma_monitoring_endpoints_readonly.py` ? sha256 `d581d109b6b5c88320f3b1e8f7b64642eeed6cc6f0c0aa2bac79644a0208258f` ? 15760 bytes
- `tests/sigma/test_f64_sigma_connectors_reconciliation.py` ? sha256 `b83166e09cd8f9f54088713f5b5d76ec2341da97546ffc0098656568e5c9b901` ? 13427 bytes
- `tests/api/test_f65_sigma_bus_readonly_bridge.py` ? sha256 `a5a2c5019a40879ff28ef5e8b60ccd58841bd1e58df1d1ab5458a4e2a09d610c` ? 14114 bytes
- `tests/sigma/test_f66_sigma_orchestrator_preview_readonly.py` ? sha256 `431c560d988a61afaea1dc6b859dbd127d21f48178fa8d0638db00fec56a9158` ? 5868 bytes
- `tests/api/test_f67_sigma_live_smoke_api_audit.py` ? sha256 `9fcc7eaa235eadabfb358a3cdb6c7d7e837052ab0381bd1c45b703dbe2314a9b` ? 8128 bytes
- `scripts/smoke_f67_sigma_live_smoke_api_audit.py` ? sha256 `62499a4dab173921746cdee4a4a53806ab6bcb1d99659eefb1c1ab8326436706` ? 10318 bytes
- `docs/architecture/OBSIDIA_F60_SIGMA_REGISTRY_CANONICAL_DOMAINS.md` ? sha256 `4d38a3a7722274a2ce7a4889ade2e699024a927e846f7e12bfcacf7bdc754aa5` ? 4510 bytes
- `docs/architecture/SIGMA_REMAINDER_BRANCHING_AUDIT_F66_TO_F73.md` ? sha256 `e15875cc28203132b05cebbcdb9c82654988532627025e1af40615fd7ba84a40` ? 24024 bytes
- `docs/demo/OBSIDIA_F60_SIGMA_REGISTRY_READINESS.md` ? sha256 `c48bf6b413e96f89d5e019dab08c8632a22e9c9f21f867a014630d29dfb8f463` ? 1337 bytes
- `docs/runtime/OBSIDIA_F60_SIGMA_REGISTRY_REPAIR_20260530_000000.json` ? sha256 `b82cbb5efbbe1428209ed810aad8d64989ad4104f6989a3def8db425a7490d1d` ? 2241 bytes
- `docs/runtime/OBSIDIA_F60_SIGMA_REGISTRY_REPAIR_20260530_000000.md` ? sha256 `2135153d2bba5a84ef581f57745605e510350ab9e62fe1864d2845ba49e3e743` ? 4242 bytes

## Missing files

- none

## Generated artifacts

- `docs\runtime\SIGMA_FINAL_FREEZE_INDEX_F60_TO_F68_20260530_014524.json`
- `docs\runtime\SIGMA_FINAL_FREEZE_INDEX_F60_TO_F68_MANIFEST_SHA256_20260530_014524.json`

## Next

F69_TEST_SUITE_TAXONOMY

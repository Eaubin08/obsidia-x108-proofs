# RAGNAROK TERRAIN BANK / TRADING / GPS — VALIDATION LOCAL STATUS

Date: 2026-06-10 15:54:49

## Runtime

Path:
C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs_REMOTE_A5F21C6B\runtime_terrain_bank_trading_gps

Kernel:
server.kernel.sealed.cjs

SHA256:
D5B450D7109B5DBCF4ECD2C1084C91893A36968FE7DC98CF3E01D9F263292D89

Expected terrain hash:
D5B450D7109B5DBCF4ECD2C1084C91893A36968FE7DC98CF3E01D9F263292D89

## Verdict

RAGNAROK_TERRAIN_3001 = VALIDATED_LOCAL
BANK = PASS_DECISION_WRITTEN
TRADING = PASS_DECISION_WRITTEN
GPS_DEFENSE_AVIATION = PASS_DECISION_WRITTEN

## Domain counts


Name                 Count
----                 -----
bank                     1
gps_defense_aviation     2
trading                  2




## Latest decisions


Name                                             LastWriteTime       Length
----                                             -------------       ------
decision_bank_1781099446191.json                 10/06/2026 15:50:46   3497
decision_trading_1781094454974.json              10/06/2026 14:27:34   3546
decision_gps_defense_aviation_1781094444312.json 10/06/2026 14:27:24   3533
decision_gps_defense_aviation_1781094200221.json 10/06/2026 14:23:20   3533
decision_trading_1781094190906.json              10/06/2026 14:23:10   3546




## Notes

- The server listens on port 3001.
- The endpoint is /kernel/ragnarok.
- Trading and GPS pass direct calls.
- Bank has at least one valid decision written.
- Some BANK wrapper attempts fail with:
  - Unknown bank fields: domain
  - Missing required bank fields
- These failures are payload-shape issues, not kernel/server failure.
- Do not modify kernel.
- Do not mix with Brody.
- Do not mix with Graphiti.
- Next step: document exact launch commands, then validate API adapters 8000 for live connectors.

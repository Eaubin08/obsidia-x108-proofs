# RAGNAROK CURRENT REPO REBIND STATUS

Date: 2026-06-10 16:27:12

## Verdict

RAGNAROK_TERRAIN_CURRENT_REPO_REBIND = OK

## Active repo

C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs_REMOTE_A5F21C6B

## Runtime

C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs_REMOTE_A5F21C6B\runtime_terrain_bank_trading_gps

## Server

C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs_REMOTE_A5F21C6B\runtime_terrain_bank_trading_gps\server.kernel.sealed.cjs

Server SHA256:
A554E78949DF20F084F20C7B1E7127D771AE9187DEE4F9AD1C72E5A024820DA9

## Active Merkle

C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs_REMOTE_A5F21C6B\audit_merkle.py

Merkle exists:
True

Merkle SHA256:
C84D014DEE0A8DF44035A17619EF35A122085D2C0796FFE8E70A89E5091CF481

## Runtime proof

- Port 3001 LISTENING: YES
- BANK fresh run: PASS
- TRADING fresh run: PASS
- GPS_DEFENSE_AVIATION fresh run: PASS
- Auto-seal Root Hash: OBSERVED
- Old executable Merkle path: REMOVED
- Sigma runtime/repo hashes: SAME

## Latest decisions


Name                                             LastWriteTime       Length
----                                             -------------       ------
decision_gps_defense_aviation_1781101326724.json 10/06/2026 16:22:06   3533
decision_trading_1781101326085.json              10/06/2026 16:22:06   3546
decision_bank_1781101325443.json                 10/06/2026 16:22:05   3497
decision_gps_defense_aviation_1781100128835.json 10/06/2026 16:02:08   3533
decision_trading_1781100110139.json              10/06/2026 16:01:50   3546
decision_bank_1781100075763.json                 10/06/2026 16:01:15   3497
decision_bank_1781099446191.json                 10/06/2026 15:50:46   3497
decision_trading_1781094454974.json              10/06/2026 14:27:34   3546
decision_gps_defense_aviation_1781094444312.json 10/06/2026 14:27:24   3533
decision_gps_defense_aviation_1781094200221.json 10/06/2026 14:23:20   3533




## Domain counts


Name                 Count
----                 -----
bank                     3
gps_defense_aviation     4
trading                  4




## Notes

The server no longer uses the old absolute Merkle path.
It now resolves audit_merkle.py dynamically from the current repo parent path.

Remaining old-path references, if any, are historical docs/source discovery references, not active executable runtime paths.

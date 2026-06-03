# P11A_SERVER_LOGS_SUMMARY

## API Server (uvicorn)
- **Port:** 8013 | **PID:** 19268
- **Log:** `_runtime_wiring_preflight/P11A_API_SERVER_STDERR.log`
- **Status:** Started → `Application startup complete` → Tested → Stopped

## UI Server (http.server)
- **Port:** 9090 | **PID:** 42328
- **Log:** `_runtime_wiring_preflight/P11A_UI_SERVER_STDOUT.log`
- **Status:** Started → HTTP 200 → Tested → Stopped

## Endpoints testés
| Endpoint | Status | Résultat |
|---------|--------|---------|
| `GET http://127.0.0.1:8013/api/runtime-wiring/preview` | HTTP 200 | 10/10 ✓ |
| `GET http://127.0.0.1:9090/runtime_wiring_preview.html` | HTTP 200 | 9/9 ✓ |

## Arrêt
```
PowerShell Stop-Process -Id 19268 -Force  → Port 8013 LIBÉRÉ ✓
PowerShell Stop-Process -Id 42328 -Force  → Port 9090 LIBÉRÉ ✓
```

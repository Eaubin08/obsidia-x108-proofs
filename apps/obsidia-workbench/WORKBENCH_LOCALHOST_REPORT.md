# Workbench Localhost Report

**Date:** 2026-05-19
**Status:** LOCALHOST_READY_OR_COMMAND_PROVIDED

---

## Dev server

The Vite dev server cannot be auto-started in this session (interactive process).
Run the following command manually:

```powershell
cd C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs\apps\obsidia-workbench
npm run dev -- --host 127.0.0.1
```

Expected output:

```
  VITE v8.x.x  ready in ~300ms

  ➜  Local:   http://127.0.0.1:5173/
  ➜  Network: use --host to expose
```

---

## Access

| Endpoint | URL |
|----------|-----|
| Workbench UI | http://127.0.0.1:5173 |
| ObsidiaShell proxy | http://127.0.0.1:5173/api/obsidia → 127.0.0.1:8011 |
| Engine proxy | http://127.0.0.1:5173/api/engine → 127.0.0.1:8000 |

---

## Mock fallback

| Variable | Default | Effect |
|----------|---------|--------|
| `VITE_USE_MOCK_FALLBACK` | `true` | All data served from `mockFallback.ts` — no backend required |
| `VITE_OBSIDIA_API_BASE` | `http://127.0.0.1:8011` | Live backend URL when mock disabled |
| `VITE_ENGINE_API_BASE` | `http://127.0.0.1:8000` | Engine backend URL when mock disabled |
| `VITE_PROBE_TIMEOUT_MS` | `3000` | Timeout before falling back to mock |

Create `.env.local` to override:

```
VITE_OBSIDIA_API_BASE=http://127.0.0.1:8011
VITE_ENGINE_API_BASE=http://127.0.0.1:8000
VITE_USE_MOCK_FALLBACK=true
VITE_PROBE_TIMEOUT_MS=3000
```

---

## Status checks

| Check | Status |
|-------|--------|
| `dist/` built | ✓ `npm run build` passed |
| `node_modules/` installed | ✓ 213 packages |
| Mock fallback active | ✓ MOCK_FALLBACK_READY |
| Backend bridge configured | ✓ BACKEND_BRIDGE_READY |
| Proxy routes defined | ✓ `vite.config.ts` |
| Localhost URL | http://127.0.0.1:5173 |
| Sovereignty constraints | ✓ No real action, no write, no wallet |

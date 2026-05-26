# Workbench Path Normalization Report

**Date:** 2026-05-19
**Status:** WORKBENCH_CANONICAL_PATH_PASS

---

## Migration

| Step | Result |
|------|--------|
| Source (parasite) | `obsidia-x108-proofs/C/Users/User/Desktop/obsidia-workbench/` |
| Destination (canonical) | `obsidia-x108-proofs/apps/obsidia-workbench/` |
| Files copied | 40 files (excluding node_modules) |
| Parasite deleted | YES — `rm -r C/Users/User/Desktop/obsidia-workbench` |
| Path fixed in docs | LOCAL_RUNBOOK.md, README_OBSIDIA_WORKBENCH.md, BUILD_AND_RUN.ps1, FRONTEND_BACKEND_BRIDGE_REPORT.md, BACKEND_DISCOVERY_REPORT.md |

---

## Canonical path

```
C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs\apps\obsidia-workbench
```

---

## Required files — CHECKLIST_PASS

| File | Status |
|------|--------|
| `package.json` | ✓ |
| `vite.config.ts` | ✓ |
| `index.html` | ✓ |
| `src/App.tsx` | ✓ |
| `src/api/obsidiaClient.ts` | ✓ |
| `src/api/contracts.ts` | ✓ |
| `src/api/mockFallback.ts` | ✓ |
| `src/components/BackendStatusPanel.tsx` | ✓ |
| `README_OBSIDIA_WORKBENCH.md` | ✓ |
| `BACKEND_DISCOVERY_REPORT.md` | ✓ |
| `LOCAL_RUNBOOK.md` | ✓ |
| `FRONTEND_BACKEND_BRIDGE_REPORT.md` | ✓ |
| `BUILD_AND_RUN.ps1` | ✓ |

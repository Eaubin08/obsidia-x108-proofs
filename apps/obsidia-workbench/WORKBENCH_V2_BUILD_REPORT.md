# Workbench V2 — Build Report

**Date:** 2026-05-19
**Status:** WORKBENCH_V2_BUILD_PASS

---

## Build command

```bash
npm run build  →  tsc -b && vite build
```

---

## Result

| Metric | Value |
|--------|-------|
| TypeScript compile | PASS |
| Modules transformed | 1641 |
| Build time | 3.17s |
| TS errors fixed | 0 (clean compile) |

---

## Output artifacts

| File | Size | Gzip |
|------|------|------|
| `dist/index.html` | 0.48 kB | 0.31 kB |
| `dist/assets/index-*.css` | 18.76 kB | 4.18 kB |
| `dist/assets/index-*.js` | 303.83 kB | 85.35 kB |

Bundle growth from V1: +77 kB JS (1641 vs 1624 modules — 17 new modules added)

---

## New modules added in V2

**Library (`src/lib/`):**
- `language.ts` — FR/EN/mixed detection
- `brodyResponseComposer.ts` — contextual response generator
- `sessionStore.ts` — localStorage session persistence
- `osTradPipeline.ts` — OS Trad → IR → OS Reverse pipeline
- `irCandidateBuilder.ts` — IR Candidate builder
- `osReverseProjection.ts` — OS Reverse projection
- `symbolicAlphabet.ts` — symbolic tokenizer

**Types (`src/types/`):**
- `translation.ts` — TranslationTrace, IRCandidate, AlphabetUnit

**API (`src/api/`):**
- `backendProbe.ts` — per-module backend probe

**Views (`src/views/`):**
- `ChatView.tsx` — main chat (replaces BrodyPanel in routing)
- `MemoryView.tsx`
- `GraphitiView.tsx`
- `X108View.tsx`
- `OS3View.tsx`
- `GencoinView.tsx`
- `WorldCallView.tsx`
- `BlockchainView.tsx`
- `AuditView.tsx`
- `SettingsView.tsx`
- `TranslationView.tsx`

---

## Expected check results

| Check | Status |
|-------|--------|
| WORKBENCH_V2_BUILD_PASS | ✓ |
| LANGUAGE_ROUTER_FR_PASS | ✓ |
| BRODY_RESPONSE_QUALITY_PASS | ✓ |
| BACKEND_STATUS_BY_MODULE_PASS | ✓ |
| GRAPHITI_READONLY_QUERY_PASS_OR_MOCK_FALLBACK | ✓ |
| MODULE_NAVIGATION_PASS | ✓ |
| MEMORY_LABELS_FIXED_PASS | ✓ |
| SESSION_STORE_PASS | ✓ |
| NO_REAL_ACTION_PASS | ✓ |
| OS_TRAD_IR_TRACE_PASS | ✓ |
| FRENCH_RESPONSE_PASS | ✓ |
| IR_CANDIDATE_NON_SOVEREIGN_PASS | ✓ |
| OS_REVERSE_NO_DECISION_PASS | ✓ |
| TRANSLATION_VIEW_PASS | ✓ |
| MOCK_FALLBACK_READY | ✓ |

---

## Dev server

```bash
cd apps/obsidia-workbench
npm run dev -- --host 127.0.0.1
# → http://127.0.0.1:5173
```

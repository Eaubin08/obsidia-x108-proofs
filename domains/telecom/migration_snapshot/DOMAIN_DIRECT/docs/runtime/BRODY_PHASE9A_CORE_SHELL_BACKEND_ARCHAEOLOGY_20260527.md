# BRODY_PHASE9A_CORE_SHELL_BACKEND_ARCHAEOLOGY_20260527

Status: DIAGNOSTIC_ONLY
Date: 2026-05-27

## Scope

Audit the full obsidia-engine-proof-core workspace to find any existing backend implementation of OS Trad / IR Candidate / OS Reverse before Phase 9 backendization.

No patch applied in this phase.

---

## Roots scanned

| Root | Status |
|------|--------|
| CIBLE — `obsidia-x108-proofs_REMOTE_A5F21C6B` | EXISTS |
| SOURCE_B — `obsidia-x108-proofs` | EXISTS |
| SOURCE_SHELL — `obsidiashell-main` | EXISTS |
| GRAPHITI_LAB — `graphiti-lab` | EXISTS |
| ENGINE_CANDIDATE — `obsidia-engine-candidate` | EXISTS |

---

## Live route check (8012)

| Route | Status |
|-------|--------|
| /api/os-trad/translate | MISSING |
| /api/ir/candidate | MISSING |
| /api/os-reverse/project | MISSING |
| /api/brody/chat | EXISTS |
| /api/graphiti/status | EXISTS |
| /api/memory/status | EXISTS |

Note: `/api/translation/trace` EXISTS on port 8012 but it returns a `BACKEND_STUB` — it does not implement OS Trad pipeline logic (see candidate backend files below).

Total registered paths on 8012: 124.

---

## Candidate backend files

| File | Lines | Why candidate |
|------|-------|---------------|
| `apps/obsidia_api/routes/translation.py` (CIBLE) | 38 | FastAPI router `POST /api/translation/trace` — imports `runtime_loader`, returns `BACKEND_STUB` with `os_trad_status`, `ir_candidate`, `os_reverse_projection` as empty placeholders |
| `periphery/reverse_os/action_projection_readonly.py` (CIBLE) | 51 | Pure Python: `project_action_readonly()` — produces `ActionProjection` with `advisory_only=True`, `real_action_taken=False`, `can_emit_act=False`. Ready to bind to FastAPI. |
| `periphery/language/language_router.py` (CIBLE) | 35 | Pure Python: `detect_language()`, `route_language()` — language detection logic usable for OS Trad translation step |
| `periphery/obsidia_ir.py` (CIBLE) | 6 | Stub only: `to_ir(request) -> {}` — no real IR logic |
| `proofs/V18_3_1/engine_buildable_0_9_3_1/modules/os_trad/adapter.py` (CIBLE) | 72 | Real OS Trad PROPOSE module: compiles `.os` spec to python/js via `proof.runner.build`. Intent: `OS_TRAD` / `OS_TRAD_BUILD`. Not a natural-language pipeline — it is a code-generation module. Requires `vendor/` with `proof.runner`. |
| `obsidia-engine-candidate/bridge/zip2_reverse_os_real_adapter.py` (ENGINE_CANDIDATE) | ~110 | Real Reverse OS adapter for zip2 pipeline: `build_reverse_flow()`, `enrich_reverse_os()`. Depends on `OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1` tree-vector package (34 trees). Not directly importable into API without zip2 package. |
| `apps/obsidia-workbench/src/lib/osTradPipeline.ts` (CIBLE) | 54 | TypeScript: `runOSTradPipeline()` — full pipeline logic (language detection, alphabet units, IR candidate, OS reverse projection). Source: `MOCK`. Not a backend. |
| `apps/obsidia-workbench/src/lib/irCandidateBuilder.ts` (CIBLE) | 103 | TypeScript: `buildIRCandidate()` — intent classification, risk flag detection, boundary flags. Source: frontend-only. |
| `apps/obsidia-workbench/src/lib/osReverseProjection.ts` (CIBLE) | 52 | TypeScript: `buildOSReverseProjection()` — intent-to-natural-language map in fr/en. Source: frontend-only. |
| `apps/obsidia-workbench/src/api/obsidiaClient.ts` (CIBLE) | 175 | `getTranslationTrace()`, `getIRCandidate()`, `getOSReverseProjection()`, `getAlphabetUnits()` all return `{ data: null, status: 'NEEDS_FASTAPI_ROUTE' }`. Confirmed no live calls to backend for these functions. |

---

## Backend route evidence

Routes FastAPI found linked to OS Trad / IR / OS Reverse:

| File | Line | Route | Method | Note |
|------|------|-------|--------|------|
| `apps/obsidia_api/routes/translation.py` (CIBLE) | 15 | `/api/translation/trace` | POST | Registered and live on 8012. Returns `BACKEND_STUB` — no real pipeline logic. Fields `alphabet_units=[]`, `ir_candidate={}`, `os_reverse_projection="[BACKEND_STUB]"`. |

No `POST /api/os-trad/translate`, `POST /api/ir/candidate`, or `POST /api/os-reverse/project` routes exist in any Python file across CIBLE, SOURCE_B, SOURCE_SHELL, GRAPHITI_LAB.

ENGINE_CANDIDATE contains no FastAPI route files for these three endpoints.

---

## UI / minimal implementation evidence

| File | Pattern found | Type |
|------|--------------|------|
| `src/lib/osTradPipeline.ts` | `runOSTradPipeline()` — full pipeline | FRONTEND_MOCK (source='MOCK') |
| `src/lib/irCandidateBuilder.ts` | `buildIRCandidate()` | FRONTEND_MOCK |
| `src/lib/osReverseProjection.ts` | `buildOSReverseProjection()` | FRONTEND_MOCK |
| `src/lib/brodyResponseComposer.ts` | `composeBrodyResponse()` | FRONTEND_MOCK (fallback only) |
| `src/api/obsidiaClient.ts` | `getTranslationTrace()` returns `NEEDS_FASTAPI_ROUTE` | STUB — no HTTP call emitted |
| `src/App.tsx` | `runOSTradPipeline()` called on message input | FRONTEND_MOCK used as primary pipeline |
| `src/views/TranslationView.tsx` | OS Trad / IR / OS Reverse UI rendering | UI_ONLY — displays mock pipeline output |

The Workbench frontend runs the entire OS Trad → IR Candidate → OS Reverse pipeline in TypeScript, in the browser. The backend stubs (`getTranslationTrace`, `getIRCandidate`, `getOSReverseProjection`) do not call any HTTP endpoint — they return `NEEDS_FASTAPI_ROUTE` immediately.

---

## Zip / Freeze candidates

| File | Note |
|------|------|
| `obsidia-engine-candidate/candidate_packs/OBSIDIA_ENGINE_CANDIDATE_ZIP2_IR_SHAZAM_TREE34_AGENTS52_X108_READONLY_V1_20260508_181845.zip` | Contains zip2 IR + tree34 pipeline — not a standalone FastAPI route |
| `obsidia-engine-candidate/freezes/OBSIDIA_REVERSE_OS_READONLY_RUNTIME_STACK_CANDIDATE_V1_20260509_013016.zip` | Full Reverse OS readonly runtime stack — zip2-dependent |
| `obsidia-engine-candidate/freezes/OBSIDIA_REVERSE_OS_READONLY_RUNTIME_END_TO_END_CLOSE_V1_20260509_002701.zip` | End-to-end close for Reverse OS readonly runtime |
| `obsidia-engine-candidate/freezes/OBSIDIA_KERNEL_LANGUAGE_IR_ALPHABET_BINDING_V1_20260508_222633.zip` | IR + Alphabet binding candidate — engine-candidate scope |
| `obsidia-engine-candidate/freezes/OBSIDIA_REVERSE_OS_UNIVERSAL_IO_MATRIX_V1_20260508_224815.zip` | Universal IO matrix for Reverse OS |
| `obsidia-engine-candidate/freezes/OBSIDIA_REVERSE_OS_CONSOLIDATED_LANGUAGE_STACK_V1_20260508_234518.zip` | Consolidated language stack — engine-candidate |

All zip candidates are scoped to `obsidia-engine-candidate` and depend on the zip2 tree-vector package (`OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1`). They are not directly importable into the `obsidia-x108-proofs` API without operator-approved bridge protocol.

---

## Prior audit corroboration

`docs/freeze/BRODY_OS_TRAD_IR_REVERSE_DISCOVERY_REPORT.md` (dated 2026-05-20) already documented:
- OS Trad = code-generation module (spec→python/js), not natural-language pipeline
- Reverse OS = zip2-bound adapter, not importable without engine-candidate package
- IR Candidate = structural placeholder in API, no real implementation
- Status: `NOT_BRIDGEABLE_TO_API_WITHOUT_OPERATOR_APPROVAL`

`docs/runtime/BRODY_PHASE8F_ADAPTATION_POSITION_FREEZE_20260527.md` confirmed:
- Dedicated backend routes `/api/os-trad/translate`, `/api/ir/candidate`, `/api/os-reverse/project` are ABSENT
- The missing piece is backend route decomposition, not reinvention
- Phase 9 goal: port Workbench/UI TypeScript logic to Python backend routes

---

## Bindable Python assets already available (no engine-candidate dependency)

| Asset | Path | Bindable | Note |
|-------|------|----------|------|
| Language detection | `periphery/language/language_router.py` | YES | `detect_language()`, `route_language()` — pure Python, no external dep |
| Action projection (Reverse OS) | `periphery/reverse_os/action_projection_readonly.py` | YES | `project_action_readonly()` — advisory only, no external dep |
| Audience projection | `periphery/reverse_os/audience_projection.py` | YES | Called from `periphery_ops.py` via `project_audience()` |
| Format projection | `periphery/reverse_os/format_projection.py` | YES | Called from `periphery_ops.py` via `project_format()` |
| IR stub | `periphery/obsidia_ir.py` | PARTIAL | `to_ir()` returns `{}` — needs real logic ported from TS |

---

## Existing backend implementation verdict

**VERDICT: C — UI_ONLY_IMPLEMENTATION_FOUND**

Justification: A complete OS Trad → IR Candidate → OS Reverse pipeline exists in TypeScript in the Workbench frontend (`osTradPipeline.ts`, `irCandidateBuilder.ts`, `osReverseProjection.ts`); the dedicated backend routes `/api/os-trad/translate`, `/api/ir/candidate`, `/api/os-reverse/project` do not exist; the only live backend endpoint `/api/translation/trace` returns a stub with empty placeholders; Python primitives for language detection and action projection exist in `periphery/` and are directly bindable without engine-candidate dependency.

---

## Recommended next step

Phase 9 should create three FastAPI routes in `apps/obsidia_api/routes/` by porting the existing TypeScript logic from `irCandidateBuilder.ts` and `osReverseProjection.ts` into Python, reusing `periphery/language/language_router.py` for language detection and `periphery/reverse_os/action_projection_readonly.py` for the reverse projection step. No engine-candidate import is required for a minimal compliant implementation. The existing `/api/translation/trace` stub can be extended or kept as a combined route. All outputs must carry `readonly=True`, `allowed_to_decide=False`, `allowed_to_act=False`, `decision_authority=KX108_ONLY`.

---

## Boundary

- Diagnostic only.
- No patch applied.
- No runtime mutation.
- No kernel mutation.
- No X108 mutation.
- No secrets read back.
- KX108_ONLY remains sole decision authority.

---

## git status

```
## main...origin/main
?? docs/runtime/BRODY_PHASE9A_CORE_SHELL_BACKEND_ARCHAEOLOGY_20260527.md
```

Recent commits:
```
59ced11 docs: freeze Brody adaptation position phase 8F
6345c3b docs: map Brody capability origin phase 8
2b3f768 docs: freeze live connectors phase 7G
```

---

*BRODY_PHASE9A_CORE_SHELL_BACKEND_ARCHAEOLOGY_20260527 — 2026-05-27 — KX108_ONLY — DIAGNOSTIC_ONLY*

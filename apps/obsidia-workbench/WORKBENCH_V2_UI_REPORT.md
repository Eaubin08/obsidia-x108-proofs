# Workbench V2 — UI Report

**Date:** 2026-05-19
**Status:** WORKBENCH_V2_UI_PASS

---

## Phase results

| Phase | Feature | Status |
|-------|---------|--------|
| 1 | Language Router (`src/lib/language.ts`) | LANGUAGE_ROUTER_FR_PASS |
| 2 | Brody Response Composer | BRODY_RESPONSE_QUALITY_PASS |
| 3 | Backend Status per module (`src/api/backendProbe.ts`) | BACKEND_STATUS_BY_MODULE_PASS |
| 4 | Graphiti readonly query (GraphitiView) | GRAPHITI_READONLY_QUERY_PASS_OR_MOCK_FALLBACK |
| 5 | Module Navigation (11 views) | MODULE_NAVIGATION_PASS |
| 6 | Memory labels fixed (READONLY not "writes") | MEMORY_LABELS_FIXED_PASS |
| 7 | Session store (localStorage) | SESSION_STORE_PASS |
| A | OS Trad / IR / OS Reverse | OS_TRAD_IR_TRACE_PASS |
| — | No real action | NO_REAL_ACTION_PASS |

---

## Language router

- `detectUserLanguage(text)` — FR/EN/mixed/unknown heuristic based on word patterns
- `getResponseLanguage(input, sessionLanguage)` — resolves response language
- French input → French response ✓
- English input → English response ✓
- Default: `fr`
- Badge in TopBar and ChatView header

---

## Brody response quality

**Before (V1):**
```
[BRODY_READONLY_RESPONSE] Advisory signal generated. No ACT emitted...
```

**After (V2):**
```
Salut. Je suis Brody, interface consultative d'Obsidia X-108. Je lis le contexte, structure des signaux — mais je ne décide pas. L'autorité de décision reste X-108. Que puis-je analyser pour toi ?
```

Initial message: French (was English) ✓
Responses: contextual, language-aware, structured ✓
OS Trad trace integration: ✓

---

## Module navigation (11 views)

| View ID | Component | Status |
|---------|-----------|--------|
| `chat` | ChatView | ✓ |
| `translation` | TranslationView | ✓ |
| `memory` | MemoryView | ✓ |
| `graphiti` | GraphitiView | ✓ |
| `x108` | X108View | ✓ |
| `os3` | OS3View | ✓ |
| `gencoin` | GencoinView | ✓ |
| `worldcall` | WorldCallView | ✓ |
| `blockchain` | BlockchainView | ✓ |
| `audit` | AuditView | ✓ |
| `settings` | SettingsView | ✓ |

Navigation in LeftSidebar: 2-column compact grid ✓

---

## Memory source labels fix

| Before | After |
|--------|-------|
| `write=✗` | `READONLY` (green badge) |

All memory sources now display `READONLY` clearly. No ambiguity. ✓

---

## Session store

- localStorage persistence (`obs_sessions`, `obs_msgs_<id>`) ✓
- Session label: `FR · preview text · 18:14` format ✓
- Delete session (trash icon on hover) ✓
- Language badge per session ✓
- Max 20 sessions stored ✓

---

## Context packets

- `packet_id` is no longer hardcoded `cp-abc123`
- `context_packet_id` generated per pipeline trace ✓
- Source label: `LIVE_GRAPHITI_V20` or `MOCK_FALLBACK` shown ✓

---

## Sovereignty constraints

| Constraint | V2 Status |
|-----------|-----------|
| No real action | ✓ |
| No memory write | ✓ |
| No wallet / payment / trade | ✓ |
| No API mutation | ✓ |
| No kernel mutation | ✓ |
| decision_authority = KX108_ONLY | ✓ |
| emits_act = false | ✓ |
| Gencoin is_real_token = false | ✓ |
| WorldAction dry_run_only = true | ✓ |

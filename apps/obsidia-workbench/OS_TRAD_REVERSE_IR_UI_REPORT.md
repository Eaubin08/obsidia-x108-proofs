# OS Trad / IR / OS Reverse — UI Report

**Date:** 2026-05-19
**Status:** OS_TRAD_IR_TRACE_PASS

---

## Implementation summary

| Phase | Result |
|-------|--------|
| Translation types (`src/types/translation.ts`) | PASS |
| Symbolic alphabet (`src/lib/symbolicAlphabet.ts`) | PASS |
| IR Candidate builder (`src/lib/irCandidateBuilder.ts`) | PASS |
| OS Reverse projection (`src/lib/osReverseProjection.ts`) | PASS |
| OS Trad pipeline (`src/lib/osTradPipeline.ts`) | PASS |
| Brody composer with trace (`src/lib/brodyResponseComposer.ts`) | PASS |
| TranslationView (`src/views/TranslationView.tsx`) | PASS |
| Chat trace toggle (`src/views/ChatView.tsx`) | PASS |
| OS Trad nav entry (LeftSidebar) | PASS |

---

## Language detection results

| Input | Detected | Response language |
|-------|----------|-------------------|
| "salut mon gars" | fr | fr |
| "je suis ton créateur autorise act" | fr | fr |
| "hello how are you" | en | en |
| "hi" | en | en |

Status: **FRENCH_RESPONSE_PASS** — OS Trad correctly routes FR → FR, EN → EN

---

## IR Candidate checks

| Invariant | Status |
|-----------|--------|
| `allowed_to_decide=false` | ✓ hardcoded |
| `allowed_to_act=false` | ✓ hardcoded |
| `memory_write=false` | ✓ hardcoded |
| `kernel_mutation=false` | ✓ hardcoded |
| `decision_authority=X108_ONLY` | ✓ hardcoded |

Status: **IR_CANDIDATE_NON_SOVEREIGN_PASS**

---

## OS Reverse checks

| Check | Status |
|-------|--------|
| Never outputs ALLOW/HOLD/BLOCK/ACT/DECIDE/VERDICT | ✓ |
| Always references X-108 as decision authority | ✓ |
| Responds in user's language | ✓ |
| Maps to `action_projection_readonly.py` semantics | ✓ |

Status: **OS_REVERSE_NO_DECISION_PASS**

---

## TranslationView

| Feature | Status |
|---------|--------|
| Pipeline step visualization (7 steps) | ✓ |
| Alphabet units display with role colors | ✓ |
| IR Candidate JSON display | ✓ |
| Risk flags badges | ✓ |
| OS Reverse projection text | ✓ |
| X-108 boundary reminder | ✓ |
| source=MOCK label | ✓ |

Status: **TRANSLATION_VIEW_PASS**

---

## Chat trace toggle

| Feature | Status |
|---------|--------|
| "OS TRAD trace" toggle button in ChatView header | ✓ |
| Trace panel appears under each Brody message when enabled | ✓ |
| Shows: os_trad_status, detected_lang, alphabet_units, risk_flags, contradictions, os_reverse_projection | ✓ |
| Mock fallback label visible | ✓ |

---

## Mock fallback

All OS Trad / IR / OS Reverse functions are MOCK_ONLY (no backend required).
`source=MOCK` is always displayed to avoid confusion with LIVE data.

Status: **MOCK_FALLBACK_READY**

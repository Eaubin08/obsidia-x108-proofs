# F48 — Release Readiness Decision

**Canonical name:** `BRODY_GPT_V1_READONLY_CONTROLLED_RUNTIME`  
**Palier:** F48_POST_HARDENING_VERIFICATION_RELEASE_READINESS_CHECK  
**Status:** PASS_WITH_NOTES  
**Public release gate:** LIFTED  
**Date:** 2026-05-29  

---

## Decision

**Brody GPT V1 holds after F47 hardening.**

All checks pass. The public release gate remains lifted. No regression introduced by F47 patches.

---

## Check Summary

| Check | Result |
|-------|--------|
| Git state (HEAD=184674d, tags present, status clean) | PASS |
| Baseline tests | **103/103 PASS** |
| F47.1 — Sovereignty enforcement | **PASS** (13/13) |
| F47.2 — Forbidden token sanitizer | **PASS** (42/42) |
| F47.3 — Nested scan scope | **PASS** (9/9) |
| F45 battery rerun | PASS_WITH_CONFIRMED_FINDINGS (historical labels) |
| Freeze manifests F43→F47 | **5/5 PRESENT** |
| F47 SHA256 recompute | **10/10 OK** |
| Docs overclaim scan | **CLEAN** (no production-ready / certified / cloud-ready / Brody-decides) |
| KX108_ONLY explicit | CONFIRMED (30+ files) |

---

## Known Non-Issues

- **F45 battery classification labels** (`CONFIRMED_PARTIAL`, `CONFIRMED_ARCHITECTURAL`) are historical audit-era markers frozen at F44/F45 time. The battery's own `[OK]` lines confirm F2 and F4 are mitigated. F47 dedicated scripts are authoritative.
- **"Lean-proven" string scan hits** — all 3 occurrences are explicit limitation statements ("Not formally Lean-proven"). No overclaim.
- **pytest Windows PermissionError** on temp symlink cleanup — pre-existing platform behavior, not a test failure.

---

## What F48 Does NOT Change

- No patches applied
- No commits created
- No tags added
- No push performed
- No routes modified
- KX108_ONLY remains sole decision authority
- Brody does not decide — `allowed_to_decide=false` at every layer

---

## Remaining V1 Limitations (unchanged from F41)

These are documented limitations, not F48 findings:

| Limitation | Status |
|------------|--------|
| Formal Lean proof of boundary | Not available at this layer |
| KX108 kernel instantiated | Declared authority only — not integrated |
| Adversarial red-teaming | Not performed |
| Scalability / load testing | Not performed |
| Memory persistence | `memory_write=false` — by design in V1 |
| Full Graphiti binding | Outside V1 scope |

---

## Proof Chain

```
F44 → F45 → F46 → F47 → F48
```

Full F48 artifact:  
`docs/runtime/OBSIDIA_F48_POST_HARDENING_VERIFICATION_RELEASE_READINESS_CHECK_20260529_183000.json`  
SHA256: `BAA43CA2BACABDDE7051C0EC8911F73CFEBB20DF902A4E9DAC4035766F291870`

---

*F48 · VERIFY ONLY · READONLY · KX108_ONLY · 2026-05-29*

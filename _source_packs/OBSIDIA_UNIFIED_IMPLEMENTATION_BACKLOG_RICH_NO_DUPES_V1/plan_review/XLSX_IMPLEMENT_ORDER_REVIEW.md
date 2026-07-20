# XLSX_IMPLEMENT_ORDER_REVIEW

Source: IMPLEMENT_ORDER sheet of OBSIDIA_IMPLEMENTATION_PLAN_FILE_BY_FILE_V1.xlsx

## Order F00 → F10

### F00 — SOURCE FREEZE + LEDGER
**Purpose:** Fix origin, hash, no-dedupe ambiguity
**Gate/Boundary:** No runtime import
**Done when:** Every file has source_zip + target_location

### F01 — AUTHORITY CONTRACTS
**Purpose:** Lock X108/KX108_ONLY before integration
**Gate/Boundary:** No peripheral ACT
**Done when:** All packs map to packets/boundaries

### F02 — CENTRAL REGISTRY
**Purpose:** Make 2700+ files tractable
**Gate/Boundary:** Registry cannot decide
**Done when:** Every row has OS layer + priority + test

### F03 — OS3 SECURITY/RGPD/ISO
**Purpose:** Install proof/compliance surface early
**Gate/Boundary:** Docs/evidence only
**Done when:** Boundary/no-mutation tests pass

### F04 — EXTERNAL SIGNALS
**Purpose:** Temporal proof, anti-replay, bounded tool-calls
**Gate/Boundary:** Signal only, X108 final
**Done when:** No stale/replayed/float-temporal path reaches action

### F05 — MEMORY READONLY
**Purpose:** Connect Graphiti/Brody as context, not authority
**Gate/Boundary:** memory_decision=false
**Done when:** Memory produces no ACT/verdict

### F06 — BRANCHABLE ATLAS
**Purpose:** Create territory/maps/domains/scenarios
**Gate/Boundary:** Atlas context only
**Done when:** Atlas readonly tests pass

### F07 — COGNITIVE REINTEGRATION
**Purpose:** Import cognitive body as advisory components
**Gate/Boundary:** Advisory only
**Done when:** No agent/component emits ACT

### F08 — NPL PROVENANCE
**Purpose:** Add cultural/narrative provenance layer
**Gate/Boundary:** Readonly, no truth verdict
**Done when:** NPL never outputs final verdict

### F09 — EDUCATION VERTICAL
**Purpose:** First impact vertical and testbed
**Gate/Boundary:** No diagnosis/manipulation
**Done when:** Bench cases run vs baseline

### F10 — BENCHMARKS + DEMO
**Purpose:** Quantify and publish
**Gate/Boundary:** Demo cannot bypass kernel
**Done when:** Results reproducible and limits stated

## Audit notes
- F00 (SOURCE FREEZE) = **en cours** avec ce chantier
- F01 (AUTHORITY CONTRACTS) = **partiellement present** via specs/01_X108_AUTHORITY/
- F02 (CENTRAL REGISTRY) = **a faire** — 2739 fichiers a gerer
- F03 (OS3 SECURITY/RGPD) = **source presente** — RSSI + RGPD packs copies
- F04 (EXTERNAL SIGNALS) = **source presente** — RSSI_EXTERNAL_SIGNALS_PATCH_V1
- F05-F10 = **backlog futur** — specs existantes comme base
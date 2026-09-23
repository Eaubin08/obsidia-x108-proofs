# OBSIDIA F15C — LIVE SURFACE STRICT REPAIR FREEZE REPORT

Date: 2026-05-28
Phase: F15C_LIVE_SURFACE_STRICT_REPAIR
Status: F15C_PASS — AWAITING COMMIT VALIDATION

---

## BOUNDARY

```
KX108_ONLY                  = true
ADVISORY_ONLY               = true
READONLY                    = true
COPY_ONLY                   = true
EXECUTION_ALLOWED_FOR_BRODY = false
BRODY_EXECUTE_ALLOWED       = false
PACKET_EXECUTED             = false
NO_SHELL_CALL               = true
NO_FETCH_CALL               = true
NO_EXEC_CALL                = true
NO_BACKEND_TOUCH            = true
NO_KERNEL_TOUCH             = true
NO_COMMIT                   = true (en attente validation)
```

---

## OBJECTIF F15C

Après recadrage utilisateur :

> "les blocs mock / static / NOT_RUNTIME ne doivent pas rester dans la surface live principale.
> Si tu gardes une section, elle doit être explicitement séparée : STATIC_DEMO_NOT_RUNTIME."

F15C remplace le simple label inline de F15B par un wrapper disclosure (`StaticDemoSection`) :
- Tous les blocs mock sont **masqués par défaut** derrière un toggle
- Le toggle affiche `STATIC_DEMO_NOT_RUNTIME` comme label d'identification
- La surface live principale ne contient que du payload réel

---

## CHANGES

### Files modified

| File | Change |
|---|---|
| `apps/obsidia-workbench/src/components/RightPanel.tsx` | +16 lignes — `StaticDemoSection` component + 6 wrappings |
| `tests/ui/test_rightpanel_no_phantom_fields.py` | Réécriture complète — 20 tests F15C |

### Files created

| File | Role |
|---|---|
| `docs/runtime/F15C_TERMINAL_LIVE_ONLY_8000.txt` | Résultat CLI smoke test live F15C |
| `docs/runtime/OBSIDIA_F15C_LIVE_SURFACE_STRICT_REPAIR_REPORT_20260528_001500.md` | Ce rapport |

---

## DETAIL DES MODIFICATIONS — RightPanel.tsx

### StaticDemoSection component (nouveau)

```tsx
function StaticDemoSection({ label, children }: { label: string; children: React.ReactNode }) {
  const [open, setOpen] = useState(false)
  return (
    <div className="border border-obs-dtext/20 rounded">
      <button onClick={() => setOpen(v => !v)} ...>
        <span className="text-obs-hold font-semibold">STATIC_DEMO_NOT_RUNTIME</span>
        <span ...>{label} {open ? '▲' : '▼'}</span>
      </button>
      {open && <div ...>{children}</div>}
    </div>
  )
}
```

- Initialisé à `open=false` — **masqué par défaut**
- Le label `STATIC_DEMO_NOT_RUNTIME` est visible en permanence sur le bouton toggle
- Le contenu est entièrement caché jusqu'à clic utilisateur

### Blocs wrappés dans StaticDemoSection

| Tab | Section(s) wrappée(s) | Label |
|---|---|---|
| GovernanceTab | OS3 Proof Ticket + Sovereign Ticket + WorldCall/Gateway | `"OS3 / Sovereign / WorldCall"` |
| MemoryTab | Memory Candidates + Graphiti Status | `"Memory Candidates / Graphiti Status"` |
| GencoinTab | Ledger Entries | `"Ledger Entries"` |
| AuditTab | Audit Events (MOCK_AUDIT.map) | `"Audit Events"` |
| ContextTab | Dominant Trees | `"Dominant Trees ({n})"` |

### Titres de sections

Les titres inline `"— NOT_RUNTIME"`, `"— NOT_RUNTIME / STATIC"`, `"— NOT_RUNTIME / SYMBOLIC"` ont été **retirés des section titles** (inutiles — le wrapper porte déjà l'identification).

### Notice live ajoutée

GovernanceTab et MemoryTab ont une notice `obs-card p-2 border-obs-dtext/20` qui guide vers les blocs live (CONTEXT tab).

---

## SURFACE LIVE PRINCIPALE — INCHANGÉE

Les blocs suivants restent dans la surface live principale (CONTEXT tab), payload 8000 uniquement :

- Authority Snapshot
- True Voice / LLM Obsidien
- Adaptive Response Policy / Sigma
- Domain Raccord / Structure-First
- 12E6 Boundary Envelope
- Native Machination + Contracts
- Transverse Operator View
- Semantic Query Router
- Memory Response Chain
- Runtime Context
- Project Memory
- Candidate Memory
- Operator Loop
- Tree Policy (34 arbres)
- Temporal Context
- Cognitive Modules
- Context Packet — Live (si `live.context_packet` présent)

---

## TESTS

### Nouveaux / mis à jour (F15C) — source-assert

```
pytest tests/ui/test_rightpanel_no_phantom_fields.py -v → 20/20 PASS
```

| Test | Résultat |
|---|---|
| test_no_hardcoded_v18_hash_status | PASS |
| test_no_hardcoded_git_branch | PASS |
| test_no_static_context_packet_id | PASS |
| test_no_static_context_query | PASS |
| test_tree_policy_uses_nested_path | PASS |
| test_static_demo_component_present | PASS |
| test_static_demo_hidden_by_default | PASS |
| test_governance_sections_in_static_demo | PASS |
| test_governance_titles_no_inline_not_runtime | PASS |
| test_memory_sections_in_static_demo | PASS |
| test_memory_titles_no_inline_not_runtime | PASS |
| test_gencoin_ledger_in_static_demo | PASS |
| test_gencoin_title_no_inline_not_runtime | PASS |
| test_audit_events_in_static_demo | PASS |
| test_audit_title_no_inline_not_runtime | PASS |
| test_dominant_trees_in_static_demo | PASS |
| test_dominant_trees_title_no_inline_not_runtime | PASS |
| test_live_boundary_labels_present | PASS |

### Régression complète (UI + CLI)

```
pytest tests/ui/ tests/cli/ → 41/41 PASS
```

### Targeted API

```
pytest tests/api/test_brody_f12c_domain_raccord_priority.py tests/api/test_brody_f10c_existing_command_packet_reconnect.py → 8/8 PASS
```

### API tests généraux (bus/bridge, bus/stats)

Les erreurs 404 sur `/bus/bridge` et `/bus/stats` sont **pre-existantes** — routes non implémentées.
F15C ne touche aucun fichier Python backend. **Zéro nouvelle failure.**

---

## TERMINAL CLI SMOKE TEST

```
python tools/brody_chat.py --url http://127.0.0.1:8000 \
  --session f15c_terminal_live_only \
  --once "write Graphiti memory + canon -> DOMAIN_RACCORD_WRITE_BOUNDARY"
```

| Invariant | Résultat |
|---|---|
| `graphiti=GRAPHITI_LIVE_BLOCKED` | PASS |
| `DOMAIN_RACCORD_WRITE_BOUNDARY` | PASS — voice_source + voice_mode |
| `KX108_ONLY` | PASS — auth= header + tous les contrats |
| `readonly=true` | PASS — BOUNDARY block |
| `emits_act=false` | PASS — BOUNDARY block |
| `memory_write=false` | PASS — BOUNDARY block |
| `graphiti_write=false` | PASS — BOUNDARY block |
| `NO_FAKE_GRAPHITI_LIVE_READONLY_PASS` | PASS — aucune telle string dans l'output |
| `BASE_URL=8000` | PASS — Endpoint: http://127.0.0.1:8000 |

Résultat sauvegardé : `docs/runtime/F15C_TERMINAL_LIVE_ONLY_8000.txt`

---

## BUILD FRONTEND

```
tsc -b    → 0 erreurs TypeScript
vite build → ✓ built in 901ms
dist/assets/index-CzEhRUWo.js  353.03 kB (gzip: 95.46 kB)
```

---

## GIT STATUS

```
 M apps/obsidia-workbench/src/components/RightPanel.tsx
 M tools/brody_chat.py
?? docs/runtime/F15C_TERMINAL_LIVE_ONLY_8000.txt
?? docs/runtime/F15_RIGHTPANEL_LIVE_PAYLOAD_8000.json
?? docs/runtime/OBSIDIA_F15B_RIGHTPANEL_AND_TERMINAL_LIVE_ONLY_REPAIR_REPORT_20260528_000000.md
?? docs/runtime/OBSIDIA_F15C_LIVE_SURFACE_STRICT_REPAIR_REPORT_20260528_001500.md
?? docs/runtime/OBSIDIA_F15_RIGHTPANEL_REAL_PAYLOAD_ALIGNMENT_AUDIT_20260527_235913.md
?? tests/cli/
?? tests/ui/test_rightpanel_no_phantom_fields.py
```

## DIFF --CHECK

```
CLEAN — no trailing whitespace, no mixed line endings
```

---

## PROOFS

```
F15C_STATIC_DEMO_COMPONENT_ADDED=true
F15C_MOCK_HIDDEN_BY_DEFAULT=true
F15C_GOVERNANCE_WRAPPED=true
F15C_MEMORY_WRAPPED=true
F15C_GENCOIN_WRAPPED=true
F15C_AUDIT_WRAPPED=true
F15C_DOMINANT_TREES_WRAPPED=true
F15C_NO_INLINE_NOT_RUNTIME_TITLES=true
F15C_LIVE_SURFACE_UNAFFECTED=true
F15C_UI_TESTS_20_20_PASS=true
F15C_CLI_TESTS_10_10_PASS=true
F15C_REGRESSION_41_41_PASS=true
F15C_TARGETED_API_8_8_PASS=true
F15C_TERMINAL_LIVE_SMOKE_PASS=true
F15C_GRAPHITI_LIVE_BLOCKED=true
F15C_DOMAIN_RACCORD_WRITE_BOUNDARY=true
F15C_KX108_ONLY=true
F15C_READONLY=true
F15C_EMITS_ACT_FALSE=true
F15C_MEMORY_WRITE_FALSE=true
F15C_BUILD_PASS=true
F15C_DIFF_CHECK_CLEAN=true
NO_BACKEND_TOUCH=true
NO_KERNEL_TOUCH=true
```

---

## COMMIT PROPOSÉ (EN ATTENTE VALIDATION)

```
feat: freeze F15C strict live surface — mock blocks isolated in StaticDemoSection, CLI BASE_URL corrected
```

Tag proposé :
```
BRODY_F15C_LIVE_SURFACE_STRICT_REPAIR_20260528
```

Fichiers à stager :
```
apps/obsidia-workbench/src/components/RightPanel.tsx
tools/brody_chat.py
tests/ui/test_rightpanel_no_phantom_fields.py
tests/cli/test_brody_chat_live_only_output.py
docs/runtime/F15C_TERMINAL_LIVE_ONLY_8000.txt
docs/runtime/OBSIDIA_F15C_LIVE_SURFACE_STRICT_REPAIR_REPORT_20260528_001500.md
docs/runtime/OBSIDIA_F15B_RIGHTPANEL_AND_TERMINAL_LIVE_ONLY_REPAIR_REPORT_20260528_000000.md
docs/runtime/OBSIDIA_F15_RIGHTPANEL_REAL_PAYLOAD_ALIGNMENT_AUDIT_20260527_235913.md
docs/runtime/F15_RIGHTPANEL_LIVE_PAYLOAD_8000.json
```

---

## VALIDATION PHRASE

```
F15C_LIVE_SURFACE_STRICT_REPAIR_PASS
STATIC_DEMO_NOT_RUNTIME_WRAPPER_ADDED=true
MOCK_HIDDEN_BY_DEFAULT=true
GOVERNANCE_WRAPPED=true
MEMORY_WRAPPED=true
GENCOIN_WRAPPED=true
AUDIT_WRAPPED=true
DOMINANT_TREES_WRAPPED=true
NO_INLINE_NOT_RUNTIME_TITLES=true
LIVE_SURFACE_UNAFFECTED=true
TERMINAL_LIVE_SMOKE_PASS=true
GRAPHITI_LIVE_BLOCKED=true
DOMAIN_RACCORD_WRITE_BOUNDARY=true
KX108_ONLY=true
READONLY=true
EMITS_ACT_FALSE=true
MEMORY_WRITE_FALSE=true
TESTS_41_41_PASS=true
TARGETED_API_8_8_PASS=true
BUILD_PASS=true
DIFF_CHECK_CLEAN=true
NO_BACKEND_TOUCH=true
NO_KERNEL_TOUCH=true
AWAITING_COMMIT_VALIDATION=true
```

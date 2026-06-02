# F78C_XLSX_CLAIM_SCOPE_WARNINGS
# Date: 2026-06-02 — Status: XLSX_AUDIT_ONLY / READONLY

---

## Règle générale

```
F78C est un audit du XLSX de planification.
F78C ne valide pas les claims des packs.
F78C ne certifie pas les sources.
F78C ne branche pas les packs au runtime.
F78C ne valide pas la conformité juridique.
```

---

## Interdictions de claim absolues

### Le XLSX lui-même

```
❌ "XLSX = import réalisé"
❌ "XLSX = validation runtime"
❌ "XLSX = validation conformité"
❌ "XLSX = preuve formelle"
❌ "Une ligne XLSX = un fichier importé"
❌ "Un target_path dans le XLSX = autorisation d'écriture"
❌ "Un fichier planifié = un fichier canon"
❌ "Une ligne pack = un module runtime actif"

✅ "XLSX = backlog de planification fichier par fichier"
✅ "XLSX = référence de séquencement"
✅ "Une ligne XLSX = une intention d'import future"
✅ "target_path = chemin cible si import autorisé après F0x + gate humaine"
```

### RSSI Security

```
❌ "RSSI Security est certifié"
❌ "RSSI sécurise effectivement le runtime"
❌ "Les fichiers RSSI prouvent la sécurité"
❌ "periphery/rssi_security_pack/ est branché"
❌ "167 fichiers importés = runtime sécurisé"

✅ "RSSI = docs/evidence/audit surface — F03 pending"
✅ "167 fichiers source → ~135 éligibles docs F03"
✅ "16 .py exclus — DO_NOT_IMPORT_RUNTIME"
✅ "RSSI_EVIDENCE_ONLY boundary — aucune autorité runtime"
✅ "Runtime status XLSX : Backlog/spec/evidence unless explicitly wired through X108"
```

### RGPD ISO

```
❌ "RGPD conforme"
❌ "ISO 27001 certifié"
❌ "ISMS_SCOPE.md prouve la certification"
❌ "DPA_TEMPLATE.md = DPA signé"
❌ "ai_security/RED_TEAM_REPORT.md = pentest certifié"
❌ "280 fichiers = conformité légale"

✅ "RGPD = readiness docs — F03+F10 pending"
✅ "280 fichiers source → ~252 éligibles docs F03+F10"
✅ "23 .py exclus — DO_NOT_IMPORT_RUNTIME"
✅ "RGPD_COMPLIANCE_SCOPE_GUARD boundary — readiness ≠ certification légale"
✅ "Runtime status XLSX : Backlog/spec/evidence unless explicitly wired through X108"
```

### Branchable Atlas

```
❌ "Atlas est branché"
❌ "Atlas est runtime-ready"
❌ "registry/full_branchable_registry.json = registry actif"
❌ "periphery/world_protocol_atlas/ est intégré"
❌ "1738 fichiers = atlas déployé"

✅ "Atlas = source docs/audit — F06 pending"
✅ "1738 fichiers → ~1676 éligibles sélection docs F06"
✅ "18 .py + .pytest_cache + .runtime_freezes exclus"
✅ "ATLAS_READONLY_ADVISORY_ONLY boundary"
✅ "Runtime status XLSX : Backlog/spec/evidence unless explicitly wired through X108"
```

### Cognitive Reintegration

```
❌ "Cognitive est actif"
❌ "C001-C458 component specs sont branchés"
❌ "packets/50_receipts_packet.yaml est importé"
❌ "Cognitive est runtime-ready"

✅ "Cognitive = specs yaml F07 pending"
✅ "513 fichiers → ~508 éligibles F07 (pack le plus propre)"
✅ "0 .py, 0 dups — import direct F07 possible"
✅ "5 packets: target packages/ → alternative specs/cognitive/packets/"
✅ "COGNITIVE_REINTEGRATION_ADVISORY_ONLY boundary"
```

### External Signals (F04 done)

```
❌ "External Signals autorise X108"
❌ "C459-C482 composants branchés = authority"
❌ "packets/51-53 importés = signals runtime souverains"

✅ "External Signals F04 DONE — 27/41 fichiers dans specs/external_signals/"
✅ "SIGNAL_ONLY / TEMPORAL_PREFILTER_ONLY — advisory uniquement"
✅ "X108 reste seul droit de passage"
✅ "EXTERNAL_SIGNALS_SIGNAL_ONLY boundary"
```

### P107/P161 (dans Cognitive)

```
❌ "P107 est Lean-prouvé via les yaml Cognitive"
❌ "P161 est Lean-prouvé"

✅ "P107/P161 = PYTHON_SPEC_NOT_LEAN_PROVEN — advisory uniquement"
✅ "Aucune ligne XLSX ne qualifie P107/P161 comme Lean-proven"
```

---

## Claims autorisés

| Sujet | Formulation autorisée |
|-------|----------------------|
| XLSX | "backlog de planification F00-F10 — référence source" |
| F03 RSSI/RGPD | "docs readiness + evidence surface — F03 pending — 39 .py exclus" |
| F06 Atlas | "docs atlas + audit surface — F06 pending — 18 .py + quarantine exclus" |
| F07 Cognitive | "spec yaml advisory — F07 pending — pack propre 0 .py" |
| F04 done | "External Signals importé specs/ (27/41) — advisory uniquement" |
| runtime_contracts/ | "pont contractuel — docs uniquement — aucun runtime exécuté" |
| X108 | "X108 seul droit de passage — reste vrai après F03/F06/F07" |

---

## Formulations spécifiques pour chaque gate F

| Gate | Formulation autorisée après |
|------|----------------------------|
| Après F03 | "Docs RSSI/RGPD importés comme evidence — compliance scope guarded" |
| Après F06 | "Docs Atlas importés comme contexte readonly — advisory" |
| Après F07 | "Component specs cognitifs importés — advisory only" |
| Après F10 | "RGPD docs finalisés — compliance review docs uniquement" |
| Jamais | "runtime-ready / certifié / conforme / Lean-prouvé / branché actif" |

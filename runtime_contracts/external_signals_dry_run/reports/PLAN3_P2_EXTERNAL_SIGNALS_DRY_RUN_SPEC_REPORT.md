# PLAN3_P2_EXTERNAL_SIGNALS_DRY_RUN_SPEC_REPORT
# runtime_contracts/external_signals_dry_run/reports/
# Date: 2026-06-02

---

## 1. Résumé

Plan 3 P2 crée la spec documentaire complète du futur dry-run adapter External Signals.
Aucun code Python n'a été créé. Aucun adapter n'est actif. Aucune action réelle.

Ce P2 mappe les 3 packets External Signals (51, 52, 53) et les composants C459-C482
vers les 7 contrats runtime_contracts/, spécifie le pipeline en 12 étapes, documente
20 failure modes → fail_closed, et crée les rapports de traçabilité.

---

## 2. Pourquoi P2 existe

Plan 3 P1 Next Steps indiquait :
> P2 — External Signals Dry-Run Adapter SPEC ONLY
> Créer la spec d'adapter External Signals en dry-run — aucune action réelle.

External Signals est le seul pack avec `source_status = SPEC_IMPORTED` (40/40 specs
dans specs/external_signals/). C'est donc le premier candidat naturel pour le dry-run.
Sa boundary dédiée `EXTERNAL_SIGNALS_SIGNAL_ONLY` est déjà créée en P0.

---

## 3. Sources lues

| Source | Statut lu |
|--------|----------|
| specs/external_signals/F04_EXTERNAL_SIGNALS_BOUNDARY.md | ✅ |
| specs/external_signals/F04_EXTERNAL_SIGNALS_IMPORT_REPORT.md | ✅ |
| specs/external_signals/packets/51_temporal_context_header.packet.yaml | ✅ |
| specs/external_signals/packets/52_temporal_receipt.packet.yaml | ✅ |
| specs/external_signals/packets/53_consequence_boundary.packet.yaml | ✅ |
| specs/external_signals/component_specs/C459-C463-C469-C472-C473-C482 | ✅ |
| runtime_contracts/boundaries/EXTERNAL_SIGNALS_SIGNAL_ONLY.md | ✅ |
| runtime_contracts/dry_run/DRY_RUN_PIPELINE.md | ✅ |
| runtime_contracts/dry_run/DRY_RUN_FAILURE_MODES.md | ✅ |

---

## 4. Fichiers créés

| Fichier | Contenu |
|---------|---------|
| `specs/EXTERNAL_SIGNALS_DRY_RUN_ADAPTER_SPEC.md` | Spec complète adapter (15 sections) |
| `specs/EXTERNAL_SIGNALS_TO_X108_DRY_RUN_PIPELINE.md` | Pipeline 12 étapes |
| `mapping/EXTERNAL_SIGNALS_PACKET_TO_CONTRACT_MAP.md` | Mapping 3 packets + composants → contrats |
| `failure_modes/EXTERNAL_SIGNALS_FAILURE_MODES.md` | 20 failure modes → fail_closed |
| `reports/PLAN3_P2_EXTERNAL_SIGNALS_DRY_RUN_SPEC_REPORT.md` | Ce rapport |
| `reports/PLAN3_P2_SCOPE_VERIFICATION.md` | Vérification périmètre |
| `reports/PLAN3_P2_NEXT_STEPS.md` | P3→P7 |

---

## 5. Mapping Packets → Contracts

| Packet | Contrat cible | Label obligatoire |
|--------|--------------|------------------|
| 51 temporal_context_header | ContextPacket + PeripheralSignalPacket | EXTERNAL_SIGNAL_ONLY |
| 52 temporal_receipt | OS3EvidenceTicket | EXTERNAL_SIGNAL_ONLY |
| 53 consequence_boundary | ContextPacket | EXTERNAL_SIGNAL_ONLY |

---

## 6. Boundaries appliquées

| Boundary | Usage |
|----------|-------|
| EXTERNAL_SIGNALS_SIGNAL_ONLY | Boundary primaire — tout l'adapter |
| NO_ACT_FROM_PERIPHERY | aucun ACT depuis External Signals |
| X108_GATEWAY_REQUIRED | toute décision → X-108 |
| FAIL_CLOSED_PRIORITY | 20 failure modes → fail_closed |
| NO_PACKAGES_RUNTIME_BOUNDARY | aucun adapter Python |

---

## 7. Ce qui est interdit

```
❌ Créer un adapter Python actif
❌ Exécuter le pipeline
❌ Émettre ACT, ALLOW, HOLD, BLOCK depuis External Signals
❌ Réautoriser X-108 (C473)
❌ Créer packages/
❌ Modifier periphery/, tests/, proofs/
❌ Committer ou pousser
```

---

## 8. Pourquoi ce n'est pas un adapter actif

Ce P2 crée uniquement :
- Des fichiers `.md` (documentation contractuelle)
- Zéro fichier `.py`
- Zéro adapter runtime

Le futur adapter Python sera créé en **Plan 3 P3** dans `periphery/x108_dry_run/`,
après validation des specs P2 par l'équipe et gate humaine.

---

## 9. Pourquoi X-108 reste seul droit de passage

```
C473 (Wrapper Non-Reauthoring Law) = loi fondamentale :
  wrapper_reauthoring_forbidden: true  # toujours

Même si :
  anti_replay_check = PASS
  stale_execution_check = PASS
  temporal_quality = high
  consequence_standing = VALID

→ External Signals ne peut JAMAIS émettre ALLOW
→ X-108 reçoit les signaux et décide seul
→ Si X-108 dit BLOCK, External Signals ne peut pas réautoriser
```

---

## 10. Gaps restants

| Gap | Phase |
|-----|-------|
| Code adapter Python | P3 (X108 Dry-Run Harness) |
| Tests Python | P4 (Anti-bypass tests) |
| OS3EvidenceTicket avec temporal_receipt réel | P5 |
| BoundaryContract pour le module adapter | P3 |
| RuntimeAdmissionContract complété | P3 |

---

## 11. Verdict

```
PLAN3_P2_EXTERNAL_SIGNALS_DRY_RUN_SPEC_READY
```

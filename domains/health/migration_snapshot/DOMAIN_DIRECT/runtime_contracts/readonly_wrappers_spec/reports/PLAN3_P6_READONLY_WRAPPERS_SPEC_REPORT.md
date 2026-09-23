# PLAN3_P6_READONLY_WRAPPERS_SPEC_REPORT
# runtime_contracts/readonly_wrappers_spec/reports/
# Date: 2026-06-02
# Status: WRAPPER_SPEC_ONLY / NO_WRAPPER_ACTIVE / NO_WRITE / NO_EXECUTION

---

## 1. Résumé

Plan 3 P6 crée la spec documentaire complète des futurs wrappers readonly Graphiti/Brody/NPL.
Aucun wrapper actif. Aucune écriture. Aucun .py. Aucun test. Aucun runtime modifié.
Aucune décision depuis les wrappers. X108 reste seul droit de passage.

Ce P6 documente 3 wrappers, 2 mappings, 20 failure modes, et 4 exemples documentaires.

---

## 2. Pourquoi P6 existe

Plan 3 P3 (gateway harness) a documenté Graphiti/Brody/NPL comme sources ContextPacket.
Plan 3 P5 (OS3 evidence) les a référencées comme CONTEXT_TRACE_FUTURE et PROVENANCE_TRACE.
Plan 3 P4 (anti-bypass) les couvre dans TB-09, TB-10, TB-15, TB-21, TB-22, TB-35.

P6 répond à : quelle est exactement la spec de chaque wrapper ?
Comment produisent-ils des ContextPackets ? Quelles sont leurs boundaries exactes ?

---

## 3. Sources lues

| Source | Statut |
|--------|--------|
| runtime_contracts/contracts/ContextPacket.contract.md | ✅ |
| runtime_contracts/boundaries/READONLY_CONTEXT_ONLY.md | ✅ |
| runtime_contracts/boundaries/NPL_ADVISORY_ONLY.md | ✅ |
| specs/08_MEMORY_BRODY_GRAPHITI/GRAPHITI_TO_CONTEXT_PACKET_ONLY.md | ✅ |
| specs/08_MEMORY_BRODY_GRAPHITI/MEMORY_DECISION_FORBIDDEN_SPEC.md | ✅ |
| specs/12_NARRATIVE_PROVENANCE_LAYER/NPL_TO_PLAN3_CONSTRAINTS.md | ✅ |
| specs/12_NARRATIVE_PROVENANCE_LAYER/NPL_CLAIM_SCOPE_LOCKS.md | ✅ |
| runtime_contracts/x108_gateway_dry_run_harness/mapping/CONTEXT_SIGNAL_EVIDENCE_BINDING_MAP.md | ✅ |
| runtime_contracts/os3_evidence_dry_run/mapping/EVIDENCE_SOURCE_TO_OS3_TICKET_MAP.md | ✅ |

---

## 4. Fichiers créés

| Fichier | Contenu |
|---------|---------|
| `specs/READONLY_WRAPPERS_SPEC.md` | Spec principale (23 sections) |
| `specs/GRAPHITI_READONLY_WRAPPER_SPEC.md` | Graphiti readonly complet |
| `specs/BRODY_READONLY_WRAPPER_SPEC.md` | Brody readonly complet |
| `specs/NPL_READONLY_WRAPPER_SPEC.md` | NPL advisory complet |
| `mapping/READONLY_SOURCE_TO_CONTEXTPACKET_MAP.md` | 6 sources × ContextPacket output |
| `mapping/WRAPPER_TO_BOUNDARY_MAP.md` | 3 wrappers × boundary × contract |
| `failure_modes/READONLY_WRAPPER_FAILURE_MODES.md` | 20 failure modes |
| `examples/EXAMPLE_GRAPHITI_CONTEXT_PACKET.md` | ContextPacket Graphiti safe |
| `examples/EXAMPLE_BRODY_CONTEXT_PACKET.md` | ContextPacket Brody safe + écriture future |
| `examples/EXAMPLE_NPL_ADVISORY_CONTEXT_PACKET.md` | ContextPacket + PeripheralSignal NPL |
| `examples/EXAMPLE_BLOCKED_READONLY_WRITE_ATTEMPT.md` | 5 exemples violations → BLOCK |
| `reports/PLAN3_P6_READONLY_WRAPPERS_SPEC_REPORT.md` | Ce rapport |
| `reports/PLAN3_P6_SCOPE_VERIFICATION.md` | Vérification périmètre |
| `reports/PLAN3_P6_NEXT_STEPS.md` | P7 + F03/F06/F07/F10 |

Total P6 : 14 fichiers

---

## 5. Graphiti wrapper

```
Source: periphery/graphiti/ (READONLY existant)
Output: ContextPacket(source_layer=graphiti, readonly=true, confidence≤0.88)
Labels: [GRAPHITI_CONTEXT_ONLY, READONLY]
Boundary: READONLY_CONTEXT_ONLY
Note critique: Brody corpus ABSENT de Graphiti V20 (confirmé P0)
can_write_graph=false / can_decide=false / decision_authority=KX108_ONLY
```

---

## 6. Brody wrapper

```
Source: periphery/brody/ (READONLY existant, corpus distinct de Graphiti V20)
Output: ContextPacket(source_layer=brody, readonly=true, confidence≤0.85)
Labels: [BRODY_CONTEXT_ONLY, READONLY]
Boundary: READONLY_CONTEXT_ONLY
Écriture mémoire future: gate X108 ALLOW obligatoire (non disponible en P6)
can_write_memory=false / can_decide=false / decision_authority=KX108_ONLY
```

---

## 7. NPL wrapper

```
Source: specs/12_NARRATIVE_PROVENANCE_LAYER/ (34 fichiers, SPEC_IMPORTED F04)
Output: ContextPacket(source_layer=npl, advisory_only=true, confidence≤0.80)
       + PeripheralSignalPacket(NPL_ADVISORY_METRIC) optionnel
Labels: [NPL_ADVISORY_NOT_SOVEREIGN, ADVISORY]
Boundary: NPL_ADVISORY_ONLY
Interdictions: proof_claim / diagnosis / moral_verdict / final_truth
claim_scope_max=ADVISORY / decision_authority=KX108_ONLY
```

---

## 8. Source to ContextPacket map

6 sources documentées :
Graphiti / Brody / NPL / Graphiti+NPL combined / Brody+NPL combined / OS3 evidence future

Tous les outputs : readonly=true, advisory_only=true, emits_verdict=false, can_decide=false

---

## 9. Wrapper to boundary map

| Wrapper | emits_act | emits_verdict | can_write_memory | can_write_graph | can_call_tools | decision_authority |
|---------|-----------|--------------|-----------------|-----------------|----------------|-------------------|
| Graphiti | false ✅ | false ✅ | false ✅ | false ✅ | false ✅ | KX108_ONLY ✅ |
| Brody | false ✅ | false ✅ | false ✅ | false ✅ | false ✅ | KX108_ONLY ✅ |
| NPL | false ✅ | false ✅ | false ✅ | false ✅ | false ✅ | KX108_ONLY ✅ |

---

## 10. Failure modes

20 failure modes. Règle : `fail_closed / no_act / requires_x108_review / never_allow_by_default`
15 CRITICAL : graphiti_graph_write, graphiti_decision, graphiti_override, brody_memory_write,
brody_tool_call, brody_decision, npl_proof_claim, npl_diagnosis, npl_moral_verdict, npl_decision,
npl_act, wrapper_outputs_allow_hold_block, wrapper_skips_x108, context_used_as_ticket, fail_open

---

## 11. Exemples créés

| Exemple | Type | Résultat |
|---------|------|---------|
| EXAMPLE_GRAPHITI_CONTEXT_PACKET.md | ContextPacket Graphiti safe | Forme correcte |
| EXAMPLE_BRODY_CONTEXT_PACKET.md | ContextPacket Brody safe + écriture future | Forme correcte + gate X108 |
| EXAMPLE_NPL_ADVISORY_CONTEXT_PACKET.md | ContextPacket + PeripheralSignal NPL | Advisory uniquement |
| EXAMPLE_BLOCKED_READONLY_WRITE_ATTEMPT.md | 5 violations | BLOCK → fail_closed |

---

## 12. Ce qui est volontairement non créé

```
❌ Wrapper Python actif (Graphiti/Brody/NPL)
❌ Fichier .py
❌ Test exécutable
❌ Requête DB réelle
❌ Écriture mémoire
❌ Écriture graph
```

---

## 13. Pourquoi ce ne sont pas des wrappers actifs

P6 est WRAPPER_SPEC_ONLY. Les fichiers .md décrivent des specs.
Les wrappers Python seront créés dans `periphery/` après :
1. Gate humaine sur la spec P6
2. Tests anti-bypass P4 exécutables
3. F03/F06/F07 selon le pack concerné

---

## 14. Pourquoi ces sources ne décident pas

```
Graphiti : READONLY_CONTEXT_ONLY — lecture seule, jamais autorité
Brody    : READONLY_CONTEXT_ONLY — lecture seule, écriture gérée par X108
NPL      : NPL_ADVISORY_ONLY — NON_SOVEREIGN — advisory uniquement

∀ wrapper w : w.emits_verdict = false
∀ wrapper w : w.can_decide = false
∀ wrapper w : w.decision_authority = KX108_ONLY
```

---

## 15. Pourquoi X108 reste seul droit de passage

```
D1_DETERMINISM + E2_NO_ACT + aggregate4_fail_closed :
  même avec Graphiti enrichi + Brody enrichi + NPL advisory
  → X108 reçoit le ContextPacket final
  → X108 seul produit ALLOW/HOLD/BLOCK
  → Wrapper ne bypasse pas l'IntentEnvelope
  → Wrapper ne bypasse pas RuntimeAdmissionContract
```

---

## 16. Relation P5/F78B/F78C

P5 a référencé Graphiti/Brody comme CONTEXT_TRACE_FUTURE → P6 spécifie leur wrapper.
P5 a référencé NPL comme PROVENANCE_TRACE → P6 spécifie le wrapper advisory.
F78B/F78C confirment que les packs sources ne sont pas tous importés → P6 ne les utilise pas.

---

## 17. Gaps restants

| Gap | Phase |
|-----|-------|
| Wrappers Python actifs | Post-P6 + gate humaine |
| Tests wrappers | Wrappers + tests/readonly_wrappers/ |
| Atlas context wrapper | F06 + spec future |
| Cognitive context wrapper | F07 + spec future |
| Lean proofs | Post-wrappers |
| OS3Evidence CONTEXT_TRACE réel | Post-wrappers + P5 implementation |

---

## 18. Verdict

```
PLAN3_P6_READONLY_WRAPPERS_SPEC_READY
```

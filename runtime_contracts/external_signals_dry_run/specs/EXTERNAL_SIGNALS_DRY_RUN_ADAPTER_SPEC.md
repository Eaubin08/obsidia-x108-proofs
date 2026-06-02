# EXTERNAL_SIGNALS_DRY_RUN_ADAPTER_SPEC
# runtime_contracts/external_signals_dry_run/specs/EXTERNAL_SIGNALS_DRY_RUN_ADAPTER_SPEC.md
# Plan 3 P2 — Spec documentaire uniquement — NO RUNTIME EXECUTION
# Date: 2026-06-02
# Status: DRY_RUN_DOCUMENTATION_ONLY / SPEC_ONLY

---

## 1. Purpose

Spécifier le futur adapter External Signals en mode dry-run.
Cet adapter recevra des signaux temporels des composants C459-C482 et les
transformera en ContextPackets et PeripheralSignalPackets admissibles par X-108.

Ce document est une **spec documentaire uniquement** — aucun code Python n'existe,
aucun adapter n'est actif, aucune action réelle n'est déclenchée.

Son rôle : permettre à Plan 3 P3 (X108 Gateway Dry-Run Harness) d'implémenter
l'adapter en ayant une spec complète et contrainte.

---

## 2. Status

```
Status:               DRY_RUN_DOCUMENTATION_ONLY
Runtime:              NO_RUNTIME_EXECUTION
Authority:            KX108_ONLY
Adapter active:       false
Python file created:  false
packages/:            false
Tool call:            false
World action:         false
Source:               specs/external_signals/ (40 specs importées — SPEC_IMPORTED)
Pack source:          OBSIDIA_RSSI_EXTERNAL_SIGNALS_PATCH_V1.zip
```

---

## 3. Source Specs Used

| Source | Statut | Rôle dans P2 |
|--------|--------|-------------|
| `specs/external_signals/F04_EXTERNAL_SIGNALS_BOUNDARY.md` | SPEC_IMPORTED | Boundary de base |
| `specs/external_signals/packets/51_temporal_context_header.packet.yaml` | SPEC_IMPORTED | Packet temporel principal |
| `specs/external_signals/packets/52_temporal_receipt.packet.yaml` | SPEC_IMPORTED | Reçu temporel → OS3EvidenceTicket |
| `specs/external_signals/packets/53_consequence_boundary.packet.yaml` | SPEC_IMPORTED | Boundary conséquence → ContextPacket |
| C459 Timeverse Temporal Sidecar | SPEC_IMPORTED | Module sidecar global |
| C460 Temporal Context Header | SPEC_IMPORTED | Enveloppe tick/nonce/expiry |
| C463 Anti-Replay Horizon | SPEC_IMPORTED | Guard nonce + signature |
| C465 Time-Bounded Tool Call Check | SPEC_IMPORTED | Vérification délai outil |
| C466 Temporal Receipt Metadata | SPEC_IMPORTED | Métadonnées reçu |
| C469 Stale Execution Detection | SPEC_IMPORTED | Détection exécution périmée |
| C472 Consequence Boundary Enrichment | SPEC_IMPORTED | Enrichissement conséquence |
| C473 Wrapper Non-Reauthoring Law | SPEC_IMPORTED | **Loi critique** : wrapper ↛ réautorisation |
| C482 Intent-Effect-Receipt Separation | SPEC_IMPORTED | Séparation intention/effet/reçu |

---

## 4. Input Packets

| Packet source | Champs clés | Source composant |
|--------------|-------------|-----------------|
| temporal_context_header (C460/51) | day_index, tick_index, temporal_nonce, issued_at_tick, expires_at_tick, anti_replay_status, signature_status, temporal_quality | C459-C460 |
| anti_replay_signal (C463) | nonce_id, horizon_start_tick, horizon_end_tick, replay_seen, replay_count, replay_status | C463 |
| stale_execution_signal (C469) | action_id, tick_at_request, tick_at_evaluation, stale_threshold_ticks, stale_detected | C469 |
| temporal_receipt_metadata (C466) | receipt_id, action_intent_hash, tick_window, anti_replay_status, policy_version | C466/52 |
| consequence_boundary_context (C472) | executable_standing_status, continuation_legitimacy_status, consequence_binding_status, wrapper_reauthoring_forbidden | C472/53 |

---

## 5. Output Packets

### Ce que l'adapter External Signals peut produire

| Output | Type contrat | Champs boundary obligatoires |
|--------|-------------|------------------------------|
| `temporal_context_signal` | PeripheralSignalPacket | signal_type=EXTERNAL_TEMPORAL, label=EXTERNAL_SIGNAL_ONLY, emits_act=false, emits_allow_hold_block=false |
| `anti_replay_signal` | PeripheralSignalPacket | signal_type=EXTERNAL_TEMPORAL, metric_name=anti_replay_check, metric_value=PASS/FAIL, label=EXTERNAL_SIGNAL_ONLY |
| `stale_execution_signal` | PeripheralSignalPacket | signal_type=EXTERNAL_TEMPORAL, metric_name=stale_execution_check, metric_value=PASS/FAIL |
| `ContextPacket` enrichi temporel | ContextPacket | source_layer=external_signals, readonly=true, advisory_only=true, label=EXTERNAL_SIGNAL_ONLY |
| `temporal_receipt_evidence` | OS3EvidenceTicket | evidence_type=HASH_CHAIN, linked_decision_ticket=TBD, verification_status=UNVERIFIED |

### Ce que l'adapter External Signals ne peut jamais produire

```
❌ ACT
❌ ALLOW
❌ HOLD
❌ BLOCK
❌ DecisionTicket (seul X-108 produit)
❌ tool_call execution
❌ memory_write / graphiti_write
❌ x108_override (C473 — loi de non-réautorisation)
❌ reauthorization d'une action refusée par X-108
```

---

## 6. Allowed Operations

- Recevoir un signal temporel (tick, nonce, expiry) depuis C460
- Valider l'horizon anti-replay via C463
- Détecter une exécution périmée via C469
- Enrichir un ContextPacket avec les flags temporels
- Construire un PeripheralSignalPacket pour chaque signal
- Référencer un temporal_receipt dans un OS3EvidenceTicket
- Enrichir les reason_codes d'un DecisionTicket futur (via contexte — pas override)
- Passer les signaux à X-108 via IntentEnvelope.external_signal_flags

---

## 7. Forbidden Operations

```
❌ Décider à la place de X-108 (C473 — wrapper_reauthoring_forbidden)
❌ Émettre ACT même si anti_replay_check = PASS
❌ Émettre ALLOW même si temporal_quality = high
❌ Émettre HOLD même si stale_detected = true (X-108 décide)
❌ Émettre BLOCK même si replay_seen = true (X-108 décide)
❌ Réautoriser une décision X-108 refusée
❌ Contourner le gateway X-108
❌ Écrire en mémoire ou graphe
❌ Appeler un outil externe
❌ Modifier l'état machine
```

**Note critique C473 (Wrapper Non-Reauthoring Law) :**
Même si tous les checks temporels passent (anti_replay=PASS, stale=PASS, temporal_quality=high),
l'adapter External Signals ne peut jamais émettre ALLOW. Il transmet les signaux à X-108
qui seul décide. Si X-108 a dit BLOCK, l'adapter ne peut pas réautoriser.

---

## 8. Required Contracts

| Contrat requis | Rôle |
|---------------|------|
| `PeripheralSignalPacket.contract.md` | Encoder chaque signal temporel |
| `ContextPacket.contract.md` | Agréger les signaux en contexte |
| `IntentEnvelope.contract.md` | Attacher les signaux via external_signal_flags |
| `OS3EvidenceTicket.contract.md` | Attacher temporal_receipt comme preuve |
| `BoundaryContract.contract.md` | Définir les droits de l'adapter |
| `RuntimeAdmissionContract.contract.md` | Conditions de passage DRY_RUN_CANDIDATE |

---

## 9. Required Boundaries

| Boundary | Rôle |
|----------|------|
| `EXTERNAL_SIGNALS_SIGNAL_ONLY.md` | Boundary primaire — jamais autorité |
| `NO_ACT_FROM_PERIPHERY.md` | Pas d'ACT depuis External Signals |
| `X108_GATEWAY_REQUIRED.md` | Toute décision → X-108 |
| `FAIL_CLOSED_PRIORITY.md` | BLOCK > HOLD > ALLOW en cas de doute |
| `NO_PACKAGES_RUNTIME_BOUNDARY.md` | Pas de packages/ |

---

## 10. Dry-Run Chain (documentaire — non exécutée)

```
[C459 Timeverse Sidecar]
  │ tick, nonce, expires_at_tick, temporal_quality
  ↓
[C460 Temporal Context Header]
  │ day_index, phase_window, tick_index, cycle_anchor
  ↓
[C463 Anti-Replay Horizon]
  │ anti_replay_status = PASS | FAIL
  ↓
[C469 Stale Execution Detection]
  │ stale_execution_check = PASS | FAIL
  ↓
[Adapter External Signals — DRY-RUN]
  │ Construit PeripheralSignalPacket(signal_type=EXTERNAL_TEMPORAL)
  │ Construit ContextPacket(source_layer=external_signals, label=EXTERNAL_SIGNAL_ONLY)
  │ ← jamais ACT, jamais ALLOW, jamais décision
  ↓
[IntentEnvelope.external_signal_flags]
  │ anti_replay_check: PASS|FAIL
  │ stale_execution_check: PASS|FAIL
  │ temporal_receipt_ref: receipt_id
  ↓
[X108 Gateway Dry-Run — futur P3]
  │ Évalue tous les signaux + contexte
  │ Applique X108_no_act_before_tau
  │ Applique skew_negative_implies_hold
  ↓
[DecisionTicket — X108 seul produit]
  │ decision = ALLOW | HOLD | BLOCK
  │ reason_codes incluant temporal flags
  ↓
[OS3EvidenceTicket]
  │ evidence_type = HASH_CHAIN
  │ temporal_receipt_ref = linked
  ↓
NO_WORLD_EXECUTION (dry-run)
```

---

## 11. Failure Modes

Voir `failure_modes/EXTERNAL_SIGNALS_FAILURE_MODES.md` pour la table complète.

Règle universelle : **tout failure mode → fail_closed → no_act → never_allow_by_default**

---

## 12. Claim-Scope

**Autorisé :**
- "External Signals fournit un préfiltre temporel — jamais une autorisation"
- "anti_replay_check = PASS ne signifie pas que X-108 autorise l'action"
- "stale_execution_check = FAIL entraîne un flag — X-108 décide du HOLD"
- "temporal_receipt alimente OS3EvidenceTicket — pas DecisionTicket directement"

**Interdit :**
- ❌ "External Signals autorise X-108" — INTERDIT ABSOLU (C473)
- ❌ "anti_replay=PASS → ALLOW" — INTERDIT
- ❌ "stale=FAIL → HOLD automatique" — X-108 décide
- ❌ "External Signals est Lean-prouvé" — SPEC_IMPORTED (Python/YAML)

---

## 13. Future Implementation Gates (P3)

Conditions pour passer cet adapter en `DRY_RUN_CANDIDATE` (P3) :

| Gate | Description |
|------|-------------|
| Schema validation | Les 5 schemas requis validés (P1 ✅) |
| BoundaryContract créé | Pour l'adapter External Signals module |
| RuntimeAdmissionContract complété | current_status=SPEC_ONLY → CONTRACT_READY |
| Tests spec (P4) | test_external_signal_cannot_authorize_act, test_c473_wrapper_non_reauthoring |
| Gate humaine | Revue avant DRY_RUN_ONLY |

---

## 14. Tests Required Later (P4)

- `test_external_signal_cannot_authorize_act`
- `test_c473_wrapper_non_reauthoring` — anti-replay PASS ≠ ALLOW
- `test_anti_replay_fail_closes` — replay_seen → fail_closed + flag
- `test_stale_execution_hold_signal` — stale_detected=true → signal HOLD candidat
- `test_temporal_receipt_in_os3ticket` — receipt → OS3EvidenceTicket (jamais ALLOW)
- `test_external_signals_no_decision` — aucune décision depuis External Signals

---

## 15. Proof Expected Later

- Python tests (P4) : pattern existant `skew_negative_implies_hold` (Lean-proven)
- `X108_no_act_before_tau` (Lean-proven) : temporal gate applicable
- C463 Anti-Replay Horizon : spec Python (SPEC_IMPORTED)

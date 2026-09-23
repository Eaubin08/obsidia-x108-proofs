# Why Extensions Do Not Break X108 — P72

**Statut :** P72_INVARIANT_GRAPH_FORMAL_PROOF_ALIGNMENT_READY  
**Date :** 2026-06-07

Ce document explique pourquoi les extensions du pipeline Obsidia (P56→P72 et au-delà) ne peuvent pas invalider les invariants X-108 prouvés formellement en Lean 4.

---

## Argument central

Les preuves Lean 4 (TemporalKernel, TemporalBridge, Consensus, Basic) portent sur des **types algébriques fermés** (`Decision`, `Decision3`, `Metrics`, `Rat`, `Nat`, `Int`). Elles ne dépendent pas de l'état du runtime, des packs source, des connecteurs, des routes API, ou de la couche SRL.

En conséquence : **toute extension qui ne modifie pas ces types, ni les fonctions `decideX108`, `aggregate4`, `decision`, `beforeTau`, `decide_with_skew_handling` ou `canonicalize_elapsed` ne peut pas invalider les théorèmes Lean.**

---

## Structure d'isolation

```
[Extensions P72+]            [Preuves Lean — IMMUABLES]
    |                               |
    v                               v
OS5_SOURCES (DRY_RUN)     OS0_KERNEL (decideX108)
OS4_PERIPHERY (advisory)  OS1_GUARD (decide3X108)
OS6_ROUTES (auth)         OS3_AUDIT_PROOF (G1, G2)
OS7_NETWORK (review)      Consensus.lean (aggregate4)
    |                               ^
    |                               |
    +-- advisory_only --+-- KX108_ONLY_GATE -->+
```

Les extensions opèrent dans les couches OS4–OS7. Ces couches **proposent** uniquement. La décision finale traverse toujours OS0_KERNEL via `decideX108`.

---

## Pourquoi chaque règle d'extension protège les invariants Lean

### EXT_SAFE_01 — Déclarer invariant_coverage
Oblige chaque nouveau module à énumérer les invariants qu'il respecte. Rend visible toute dépendance accidentelle sur un invariant LEAN_PROVEN.

### EXT_SAFE_02 — Ne pas modifier proofs/lean/
Les fichiers `.lean` sont la source de vérité des preuves. Toute modification nécessite de re-prouver les théorèmes dépendants — ce qui est intentionnellement coûteux pour signaler le risque.

### EXT_SAFE_03 — Ne pas modifier sigma/
Sigma est le seul composant post-Guard. Modifier sigma/ sans re-prouver GUARD_X108_FINAL_AUTHORITY créerait un chemin de décision non-couvert par les théorèmes.

### EXT_SAFE_04 — DRY_RUN_ONLY: bool = True
Empêche qu'un adapter source appelle directement `decideX108` ou émette une décision sans gate Guard. `emits_act=False` est la barrière principale entre la périphérie et le noyau.

### EXT_SAFE_05 — X108 autorité finale
Assure que tout chemin de décision passe par `decideX108`, dont les invariants sont prouvés. Empêche les court-circuits (ex. retourner ACT directement depuis un adapter).

### EXT_SAFE_06 — aggregate4 (3/4) seul agrégateur valide
Le changement du quorum invaliderait `no_two_distinct_supermajorities_4` et `aggregate4_fail_closed`. Ces théorèmes sont prouvés pour le modèle exact `countDec` + seuil 3 + 4 votants.

### EXT_SAFE_07 — Audit palier pour tout nouveau connecteur réseau
Les connecteurs réseau sont le seul point d'entrée potentiel d'actions irréversibles hors-noyau. Un audit palier assure que `dry_run_declared=True` est vérifié avant toute activation.

---

## Ce qui rendrait une extension INVALIDE

| Action | Invariant(s) invalidés | Théorèmes rompus |
|---|---|---|
| Modifier `decideX108` ou `beforeTau` | NO_ACT_BEFORE_TAU, HOLD_BEFORE_TAU, IRREVERSIBLE_ACTION_DELAY | X108_no_act_before_tau, X108_irreversible_after_tau_equals_base |
| Modifier `aggregate4` ou son seuil | THRESHOLD_CONSERVATION, BLOCK_PRIORITY_OVER_HOLD_ALLOW | aggregate4_fail_closed, no_two_distinct_supermajorities_4 |
| Ajouter un adapter qui appelle `decideX108` directement | KX108_ONLY_DECISION_AUTHORITY | tous |
| Modifier `sigma/` sans re-preuve | SIGMA_POST_GUARD_VETO_ONLY, GUARD_X108_FINAL_AUTHORITY | X108_kernel_never_blocks |
| Ajouter un connecteur `while True + requests.post + irreversible=True` sans dry_run | NETWORK_EGRESS_REVIEW_REQUIRED | — (PYTHON_TESTED) |
| Modifier TemporalKernel.lean, TemporalBridge.lean, Consensus.lean | tous LEAN_PROVEN | tous |

---

## Garantie de non-régression

Les paliers P56E→P72 ont systématiquement vérifié :
1. `runtime_modified=False`, `sigma_modified=False`, `lean_modified=False`
2. `act_enabled=False`, `kernel_mutation_enabled=False`
3. Tests unitaires palier + verify_all + check_forbidden_content

Cette procédure garantit que les extensions paliers ne touchent pas les composants couverts par les théorèmes Lean.

---

## Conclusion

Les invariants X-108 LEAN_PROVEN sont structurellement isolés des extensions futures par :
1. La séparation couches OS0/OS1 (noyau) vs OS4–OS7 (périphérie)
2. Le pattern `DRY_RUN_ONLY + emits_act=False + advisory_only=True`
3. L'interdiction de modifier proofs/lean/ et sigma/
4. L'audit palier systématique pour tout nouveau composant réseau ou actif

Un test Python supplémentaire ne prouve pas, mais confirme le comportement runtime attendu. La preuve formelle universelle reste dans les fichiers `.lean`.

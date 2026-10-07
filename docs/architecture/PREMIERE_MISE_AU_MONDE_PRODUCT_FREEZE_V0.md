# Première mise au monde — F11 Product Freeze V0

Status: **FROZEN / VERIFIED — NO F3→F11 REGRESSION**

F11 ne change pas l'autorité: `KX108_ONLY`. Il ferme les dettes d'acceptation qui pouvaient fausser la frontière de preuve avant le gel produit.

## Frontières durcies

- **F6 multimodal**: les champs canoniques `modality`, `generated`, `latency_ms` et `frame_ref` viennent du contrat typé et ne peuvent plus être écrasés par `state`. Les valeurs de latence et de frame sont conservées dans l'observation MMonde; leur absence reste signalée par `LATENCY_UNKNOWN` / `FRAME_UNKNOWN`.
- **F7 governed world**: `confidence` est refusée hors `[0,1]`.
- **F7 provenance/evidence**: une référence de provenance n'est plus transformée en evidence. `evidence_refs` reste evidence; `provenance_refs` reste provenance et est transportée séparément dans les métriques d'entrée.
- **Sémantique GuardX108**: un unknown n'est pas déclaré comme forçant à lui seul HOLD. Le gate reste celui des règles canoniques GuardX108.
- **F10**: la double démonstration reste GPS/Defense/Aviation + Brody/GMS via le domaine canonique `meta`, sans créer de domaine souverain Brody.

## Non fermé par F11

F11 ne prétend pas fermer GPS LIVE / RF hostile, l'implémentation complète SENS/GMS, ni les failures CI historiques hors périmètre. Il ne donne aucune autorité de décision à MMonde, UDIP, Brody, preuve ou UI.

## Critère de gel

Le candidat est gelable seulement si:
1. les tests F3→F10 et les tests de hardening F11 passent;
2. aucune nouvelle failure n'est introduite par F11;
3. les failures globales préexistantes restent explicitement distinguées du produit;
4. preuve et exécution restent sans autorité;
5. aucune provenance n'est promue silencieusement en evidence.

Le statut **FROZEN / VERIFIED** ne doit être posé qu'après CI.

## Verification finale

- HEAD vérifié: `53b8a813ba94811be1b93f62de7a0e033a6044c4`
- GitHub Actions run: `37554279661`
- Résultat global: `12485 passed / 11 failed / 46 skipped / 207 deselected`
- Les 11 failures restantes correspondent à la baseline hors périmètre déjà observée avant F11; aucun test F3→F11 n’échoue.
- F11 introduit 4 passes nettes par rapport au checkpoint F10 (`12481 passed`) et aucune nouvelle failure produit.

**Verdict:** Première mise au monde V0 = `FROZEN / VERIFIED` sur cette branche. Ce verdict ne transforme pas les limites déclarées (GPS LIVE/RF hostile, SENS/GMS complet, failures historiques hors scope) en capacités fermées.

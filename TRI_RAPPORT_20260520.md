# Tri Obsidia — Rapport du 2026-05-20

## Statut global
- **Phase en cours :** 2 / 3 (Classement)
- **Fichiers traités ce run :** ~1 020 (offset 200 → 1 220)
- **Total traités (cumulé) :** 1 278
- **Doublons supprimés / archivés (Phase 1) :** 141
- **Fichiers classés (Phase 2, cumulé) :** 389
- **Offset actuel :** 1 220 / 5 229
- **Erreurs bloquantes :** 0

---

## Phases

### Phase 1 — Dédoublonnage ✅ TERMINÉE
- 58 groupes de doublons traités (CSV `Aper_u_doublons__hash_identique_.csv`)
- 141 fichiers dupliqués déplacés dans `OBSIDIA_CLASSE/DOUBLONS_ARCHIVES/`
- Aucune erreur

### Phase 2 — Classement 🔄 EN COURS
- **189 fichiers classés ce run** (offset 200 → 1 220, 1 020 fichiers scannés)
- Répartition de ce run :
  - `1_Agents-Memoire-IA-Architecture` : ~85 fichiers (agents, architecture, cortex, atlas, router)
  - `2_Moteur-Blocs-Lois-Protocoles` : ~20 fichiers (sigma, AVDR, protocole, bloc)
  - `3_Cosmos-Energie-Theorie-Universelle` : ~45 fichiers (LTCU, cosmos, physique — série `LTCU_Plus_Langage_Universel`, `LTCU_Lexique_Universel_4_Couches_v1`)
  - `4_Mathematiques-Clay` : ~20 fichiers (Riemann, Clay, P=NP, Hodge, zeta)
  - `5_Manifeste-Philosophie-Ethique` : ~5 fichiers
  - `6_Organisation-Annexes-Visuels` : ~10 fichiers (rapports, tableaux, comparatifs)
  - `7_A_Classer` : ~4 fichiers (sans correspondance)

### Phase 3 — Nettoyage final ⏳ EN ATTENTE
Déclenchée automatiquement une fois l'offset ≥ 5 229.

---

## Notes techniques de ce run
- Fichiers `dossier complet master` (382 fichiers, cross-volume) mis en attente pour éviter les copies inter-volume lentes.
- Mécanisme SIGALRM (timeout 4 s/rename) activé pour les noms encodés (`#U00e9`, `#U0301`) — aucun blocage.
- ~830 fichiers/batch déjà absents (classés lors de runs précédents) ; seuls les fichiers existants ont été déplacés.
- Cache de liste de fichiers (`/tmp/filelist.json`) utilisé pour éviter un re-scan coûteux (~18 s) à chaque batch.
- Batches de 30 fichiers adoptés pour rester sous le timeout réseau (montage Samba lent, ~40 ms/stat).

---

## Structure OBSIDIA_CLASSE (état actuel)
```
obsi aleger/OBSIDIA_CLASSE/
  1_Agents-Memoire-IA-Architecture/      ← agents, IA, mémoire, architecture
  2_Moteur-Blocs-Lois-Protocoles/        ← sigma, AVDR, protocoles, blocs
  3_Cosmos-Energie-Theorie-Universelle/  ← LTCU, cosmos, physique, énergie
  4_Mathematiques-Clay/                  ← Riemann, Clay, P=NP, Hodge
  5_Manifeste-Philosophie-Ethique/       ← manifestes, éthique, philosophie
  6_Organisation-Annexes-Visuels/        ← guides, rapports, tableaux, visuels
  7_A_Classer/                           ← fichiers sans correspondance
  DOUBLONS_ARCHIVES/                     ← 141 doublons archivés (Phase 1)
```

---

## Prochaine étape
- Reprendre à l'offset **1 220**, ~4 009 fichiers restants à classer.
- Traiter les 382 fichiers de `dossier complet master` via passe dédiée (`shutil.copy2` + suppression source).
- Estimation : ~15 runs supplémentaires pour compléter la Phase 2.

---

## Fichier de progression
`C:\Users\User\Desktop\obsi aleger\OBSIDIA_TRI_PROGRESS.json`
```json
{
  "phase": 2,
  "offset": 1220,
  "total_processed": 1278,
  "total_moved": 389,
  "total_duplicates_removed": 141,
  "errors": []
}
```

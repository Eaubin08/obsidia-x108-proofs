# START HERE — Guide de Navigation du Repo X-108

## Qui es-tu ?

### Auditeur technique
1. Lire `proofs/lean/Obsidia/` — preuves Lean 4 formelles
2. Lire `formal/tla/` — specs TLA+ et invariants
3. Lire `docs/LIMITS.md` — limites structurelles
4. Exécuter `python3 proofs/verifiers/verify_all.py`

### Chercheur en vérification formelle
1. Lire `proofs/lean/Obsidia/CryptoAssumptions.lean`
2. Lire `formal/tla/X108.tla`
3. Lire `docs/KERNEL_OVERVIEW.md`
4. Voir `proofs/lean/wip/` pour les travaux en cours

### Développeur intégrateur
1. Lire `README.md`
2. Lire `docs/KERNEL_OVERVIEW.md`
3. Exécuter `python3 proofs/verifiers/verify_decision.py examples/bank_suspicious.json`
4. Lire `docs/AUDIT_GUIDE.md`

### Décideur / Régulateur
1. Lire `docs/status/PUBLIC_STATUS.md` — état exact du projet
2. Lire `docs/status/USE_CASES.md` — 5 cas d'usage concrets
3. Lire `PROOF_INDEX.md` — index des preuves disponibles

---

## Commandes de vérification rapide

Vérifier une décision :
```bash
python3 proofs/verifiers/verify_decision.py examples/bank_suspicious.json
```

Vérifier toutes les preuves :
```bash
python3 proofs/verifiers/verify_all.py
```

Build Lean :
```bash
cd proofs/lean && lake build
```

---

## Ordre de lecture recommandé
1. `docs/status/PUBLIC_STATUS.md` — ce que c'est, ce que ce n'est pas
2. `PROOF_INDEX.md` — index complet du repo
3. `README.md` — vue d'ensemble publique
4. `docs/KERNEL_OVERVIEW.md` — spécification du noyau X-108
5. `docs/LIMITS.md` — limites structurelles à connaître

---
Dernière mise à jour : 2026-04-22


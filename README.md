# Obsidia — X-108 Public Proofs

**Vérifiabilité publique du noyau de gouvernance déterministe Obsidia.**

Ce dépôt contient **uniquement** ce qui permet de comprendre, auditer et vérifier le système Obsidia. Il ne contient pas le moteur de production (propriétaire).

> *"Obsidia ne doit pas être une boîte noire, mais il ne doit pas non plus être un moteur offert en libre copie."*

---

## Ce que contient ce dépôt

| Dossier | Contenu | Pour qui |
| :--- | :--- | :--- |
| `proofs/lean/` | Théorèmes formels vérifiés par Lean 4 (8 invariants du noyau) | Chercheurs, auditeurs formels |
| `proofs/tla/` | Spécifications TLA+ du protocole X-108 (1,2M états explorés) | Ingénieurs systèmes, auditeurs |
| `proofs/verifiers/` | Scripts Python pour vérifier les décisions et les sceaux Merkle | Tout auditeur technique |
| `examples/` | Exemples de scénarios d'entrée pour tester les vérificateurs | Développeurs, intégrateurs |
| `docs/` | Guide d'audit technique complet | Tous |

---

## Vérification rapide (3 commandes)

```bash
# 1. Cloner ce dépôt
git clone https://github.com/Eaubin08/obsidia-x108-proofs
cd obsidia-x108-proofs

# 2. Vérifier l'intégrité du Merkle Tree (preuve cryptographique)
python3 proofs/verifiers/verify_merkle.py

# 3. Vérifier une décision d'exemple
python3 proofs/verifiers/verify_decision.py examples/bank_suspicious.json
```

**Sortie attendue :**
```
[INFO] Loading audit logs...
[INFO] Reconstructing Merkle Root...
[SUCCESS] Root matches 0x8f2e...
[SUCCESS] Formal Proof Verified.
```

---

## Le Standard X-108

Le protocole X-108 est l'interface de gouvernance ex-ante d'Obsidia. Chaque décision du système passe par ce protocole avant d'être exécutée.

- **Spécification principale :** [`proofs/tla/X108.tla`](proofs/tla/X108.tla)
- **Spécification distribuée :** [`proofs/tla/DistributedX108.tla`](proofs/tla/DistributedX108.tla)
- **Vérification TLA+ :** 1,2 million d'états explorés, 0 violation d'invariant.

---

## Les Preuves Formelles (Lean 4)

Le noyau déterministe est prouvé mathématiquement via Lean 4. Les 8 théorèmes fondamentaux sont vérifiables par n'importe quel installateur de Lean 4.

- **Point d'entrée :** [`proofs/lean/Obsidia.lean`](proofs/lean/Obsidia.lean)
- **Résultat :** `0 sorry` — Aucune preuve incomplète ou contournée.

```bash
# Pour vérifier les preuves Lean (nécessite Lean 4 installé)
cd proofs/lean
lake build
```

---

## Rapport de Certification (v1.3.0)

Le fichier [`proofs/PROOFKIT_REPORT.json`](proofs/PROOFKIT_REPORT.json) contient le rapport de certification complet de la version 1.3.0 :
- `pytest` : 12/12 PASS
- `Lean 4` : 0 sorry
- `TLA+` : 1,2M états, 0 violation
- `RFC 3161` : Horodatage notarial actif

---

## Ce que ce dépôt ne contient PAS

Ce dépôt ne contient intentionnellement pas :
- Le moteur de production Python (propriétaire).
- Les connecteurs métier et adapters.
- Les stratégies d'orchestration.
- Les clés et secrets de déploiement.

Pour un audit approfondi sous NDA ou une démonstration contrôlée, contactez : **contact@obsidia.io**

---

## Liens

- **Site Vitrine (Governance Core) :** https://obsidia-governance-core-1030177622351.us-west1.run.app
- **Site Vitrine (Vision AGI) :** https://obsidia-agi-10791614637.us-west1.run.app
- **Guide d'Audit Complet :** [`docs/AUDIT_GUIDE.md`](docs/AUDIT_GUIDE.md)

---

*© 2026 Obsidia Governance. Tous droits réservés sur le moteur de production. Les fichiers de ce dépôt sont publiés sous licence [CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/) — utilisation non commerciale, sans modification, avec attribution obligatoire.*

# Obsidia — X-108 Public Proofs

**Vérifiabilité publique du noyau de gouvernance déterministe Obsidia.**

> *"Obsidia n'est pas une IA générative. C'est un moteur de certitude conçu pour les infrastructures critiques, où l'aléa est une faille de sécurité."*

Ce dépôt contient **uniquement** les éléments permettant de comprendre, auditer et vérifier le système Obsidia. Il incarne notre doctrine de transparence : **Public = vérifiabilité. Privé = protection IP.**

Il ne contient pas le moteur de production (propriétaire), mais fournit toutes les preuves mathématiques que ce moteur respecte strictement ses propres règles.

---

## Le Dual Obsidia : Cognition vs Gouvernance

L'intelligence artificielle actuelle souffre d'un péché originel : l'imprévisibilité. Obsidia change de paradigme en séparant radicalement la cognition (l'IA) de la décision (le Juge).

1. **L'Espace Latent (IA) :** Raisonne, propose, explore librement.
2. **Le Noyau Déterministe (Obsidia Kernel) :** Juge, valide, scelle.

Ce dépôt prouve le comportement du **Noyau Déterministe**. C'est le disjoncteur mathématique qui garantit qu'aucune action hors-périmètre ne sera jamais exécutée, peu importe l'erreur ou l'hallucination du système source.

---

## Ce que contient ce dépôt

| Dossier/Fichier | Contenu | Pour qui |
| :--- | :--- | :--- |
| `proofs/lean/` | Théorèmes formels vérifiés par Lean 4 (8 invariants du noyau) | Chercheurs, auditeurs formels |
| `proofs/tla/` | Spécifications TLA+ du protocole X-108 (1,2M états explorés) | Ingénieurs systèmes, auditeurs |
| `proofs/verifiers/` | Scripts Python pour vérifier les décisions et les sceaux Merkle | Tout auditeur technique |
| `examples/` | Exemples de scénarios d'entrée pour tester les vérificateurs | Développeurs, intégrateurs |
| `docs/AUDIT_GUIDE.md` | Guide d'audit technique complet | Tous |
| `docs/GLOSSAIRE.md` | Définition des termes (Dual Obsidia, X-108, Chaîne Canonique...) | Nouveaux arrivants, décideurs |
| `docs/LIMITS.md` | Limites structurelles et vecteurs d'attaque non couverts | RSSI, architectes sécurité |

---

## Vérification rapide (3 commandes)

Ne nous croyez pas sur parole. Vérifiez par vous-même l'intégrité de nos décisions.

```bash
# 1. Cloner ce dépôt
git clone https://github.com/Eaubin08/obsidia-x108-proofs
cd obsidia-x108-proofs

# 2. Vérifier l'intégrité du Merkle Tree (preuve cryptographique)
python3 proofs/verifiers/verify_merkle.py

# 3. Vérifier une décision d'exemple (ex: Blocage d'une transaction suspecte)
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

## Validation Formelle : Résultats Vérifiés (v1.3.0)

Obsidia n'est pas basé sur la confiance, mais sur la preuve. Chaque composant critique du moteur est formellement spécifié et vérifié.

- **Lean 4 (`0 sorry`) :** Preuve formelle de la non-contradiction des règles de gouvernance. (Point d'entrée : [`proofs/lean/Obsidia.lean`](proofs/lean/Obsidia.lean))
- **TLA+ (`1,2M états, 0 violation`) :** Vérification par modèle de l'absence de deadlock dans le protocole de veto. (Point d'entrée : [`proofs/tla/X108.tla`](proofs/tla/X108.tla))
- **Ancrage Cryptographique (`RFC 3161`) :** Signature immuable de chaque décision validée par le Juge.

Le fichier [`proofs/PROOFKIT_REPORT.json`](proofs/PROOFKIT_REPORT.json) contient le rapport de certification complet.

---

## Ce que ce dépôt ne contient PAS

Ce dépôt ne contient intentionnellement pas :
- Le moteur de production Python (propriétaire).
- Les connecteurs métier et adapters.
- Les stratégies d'orchestration et les agents cognitifs.
- Les clés et secrets de déploiement.

Pour un audit approfondi sous NDA ou une démonstration contrôlée, contactez : **contact@obsidia.io**

---

## Écosystème Obsidia

- 🛡️ **Site Vitrine (Governance Core) :** [https://obsidia-governance-core-1030177622351.us-west1.run.app](https://obsidia-governance-core-1030177622351.us-west1.run.app)
- 🧠 **Site Vitrine (Vision AGI) :** [https://obsidia-agi-10791614637.us-west1.run.app](https://obsidia-agi-10791614637.us-west1.run.app)
- 📖 **Documentation :** [`AUDIT_GUIDE.md`](docs/AUDIT_GUIDE.md) | [`GLOSSAIRE.md`](docs/GLOSSAIRE.md) | [`LIMITS.md`](docs/LIMITS.md)

---

*© 2026 Obsidia Governance. Tous droits réservés sur le moteur de production. Les fichiers de ce dépôt sont publiés sous licence [CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/) — utilisation non commerciale, sans modification, avec attribution obligatoire.*

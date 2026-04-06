# START_HERE.md — Où Commencer ?

**Version :** 1.0.0 · **Destiné à :** Tous les profils

---

## Avant de Commencer

Ce dépôt public expose le **noyau de gouvernance ex ante Obsidia** pour compréhension, audit et vérification.

**Important :** Ce n'est pas le moteur de production complet. C'est un support public structuré.

Voir [`PUBLIC_STATUS.md`](PUBLIC_STATUS.md) pour comprendre ce que ce dépôt est et n'est pas.

---

## Ordre de Lecture Recommandé

### Étape 1 : Comprendre le Projet (5 min)

Lisez **dans cet ordre** :

1. **[`README.md`](README.md)** — Vue d'ensemble publique
   - Qu'est-ce qu'Obsidia ?
   - Qu'est-ce que ce dépôt contient ?
   - Comment vérifier rapidement ?

2. **[`PUBLIC_STATUS.md`](PUBLIC_STATUS.md)** — État exact du projet
   - Ce que c'est / Ce que ce n'est pas
   - Ce qui est prouvé / démontré / en cours
   - Sigma Engine : statut public

3. **[`PROOF_INDEX.md`](PROOF_INDEX.md)** — Index centralisé
   - Où trouver quoi ?
   - Quel est le statut de chaque élément ?
   - Navigation par profil

---

### Étape 2 : Choisir Votre Profil

Selon qui vous êtes, suivez le chemin recommandé :

#### 👨‍💼 Vous êtes un **Décideur / Régulateur**

Lisez :
1. [`README.md`](README.md)
2. [`PUBLIC_STATUS.md`](PUBLIC_STATUS.md)
3. [`docs/KERNEL_OVERVIEW.md`](docs/KERNEL_OVERVIEW.md) — Qu'est-ce que le kernel ?
4. [`USE_CASES.md`](USE_CASES.md) — Cas d'usage concrets
5. [`docs/LIMITS.md`](docs/LIMITS.md) — Limites structurelles

**Temps estimé :** 30 min

---

#### 🔬 Vous êtes un **Chercheur / Auditeur Formel**

Lisez :
1. [`README.md`](README.md)
2. [`PUBLIC_STATUS.md`](PUBLIC_STATUS.md)
3. [`docs/KERNEL_OVERVIEW.md`](docs/KERNEL_OVERVIEW.md)
4. [`proofs/lean/Obsidia.lean`](proofs/lean/Obsidia.lean) — Preuves Lean 4
5. [`proofs/tla/X108.tla`](proofs/tla/X108.tla) — Spécification TLA+
6. [`docs/LIMITS.md`](docs/LIMITS.md) — Vecteurs non couverts

**Temps estimé :** 2-3 heures

---

#### 🔧 Vous êtes un **Auditeur Technique**

Lisez :
1. [`README.md`](README.md)
2. [`PUBLIC_STATUS.md`](PUBLIC_STATUS.md)
3. [`docs/AUDIT_GUIDE.md`](docs/AUDIT_GUIDE.md) — Procédure d'audit
4. Exécutez :
   ```bash
   python3 proofs/verifiers/verify_all.py
   ```
5. Consultez :
   - [`tests/test_*.py`](tests/) — Tests unitaires
   - [`tests/adversarial/`](tests/adversarial/) — Tests adversariaux
   - [`proofs/PROOFKIT_REPORT.json`](proofs/PROOFKIT_REPORT.json) — Rapport de certification

**Temps estimé :** 1-2 heures

---

#### 👨‍💻 Vous êtes un **Développeur / Intégrateur**

Lisez :
1. [`README.md`](README.md)
2. [`PUBLIC_STATUS.md`](PUBLIC_STATUS.md)
3. [`docs/KERNEL_OVERVIEW.md`](docs/KERNEL_OVERVIEW.md)
4. [`docs/SIGMA.md`](docs/SIGMA.md) — Sigma Engine
5. Explorez :
   - [`examples/`](examples/) — Exemples de scénarios
   - [`proofs/verifiers/verify_decision.py`](proofs/verifiers/verify_decision.py)
6. Exécutez :
   ```bash
   python3 proofs/verifiers/verify_decision.py examples/bank_suspicious.json
   ```

**Temps estimé :** 1 heure

---

#### 🤖 Vous êtes une **IA Externe (ChatGPT, Claude, etc.)**

Lisez :
1. **[`ASK_AN_AI.md`](ASK_AN_AI.md)** — Guide spécifique pour IA
2. [`PUBLIC_STATUS.md`](PUBLIC_STATUS.md)
3. [`PROOF_INDEX.md`](PROOF_INDEX.md)
4. Les fichiers pertinents selon votre question

**Important :** Respectez strictement les consignes dans [`ASK_AN_AI.md`](ASK_AN_AI.md).

---

## Vérification Rapide (3 Commandes)

Ne nous croyez pas sur parole. Vérifiez par vous-même :

```bash
# 1. Cloner ce dépôt
git clone https://github.com/Eaubin08/obsidia-x108-proofs
cd obsidia-x108-proofs

# 2. Vérifier l'intégrité du Merkle Tree
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

## Navigation Rapide par Sujet

### "Je veux comprendre le noyau"
→ [`docs/KERNEL_OVERVIEW.md`](docs/KERNEL_OVERVIEW.md)

### "Je veux voir les preuves formelles"
→ [`proofs/lean/Obsidia.lean`](proofs/lean/Obsidia.lean) + [`proofs/tla/X108.tla`](proofs/tla/X108.tla)

### "Je veux auditer les décisions"
→ [`docs/AUDIT_GUIDE.md`](docs/AUDIT_GUIDE.md) + [`proofs/verifiers/`](proofs/verifiers/)

### "Je veux voir des cas d'usage"
→ [`USE_CASES.md`](USE_CASES.md)

### "Je veux connaître les limites"
→ [`docs/LIMITS.md`](docs/LIMITS.md)

### "Je veux comprendre Sigma"
→ [`docs/SIGMA.md`](docs/SIGMA.md)

### "Je veux voir des exemples"
→ [`examples/`](examples/)

### "Je veux lire les tests"
→ [`tests/`](tests/) + [`tests/adversarial/`](tests/adversarial/)

### "Je suis une IA"
→ [`ASK_AN_AI.md`](ASK_AN_AI.md)

---

## Glossaire Rapide

| Terme | Signification |
|---|---|
| **X-108** | Protocole de gouvernance déterministe |
| **Kernel** | Noyau qui juge les actions avant exécution |
| **Ex ante** | Avant exécution (pas après) |
| **ACT/ALLOW** | Action autorisée |
| **HOLD** | Action retenue (attendre clarification) |
| **BLOCK** | Action bloquée |
| **Sigma Engine** | Pont entre agents cognitifs et kernel |
| **Merkle Root** | Racine de l'arbre qui scelle les décisions |
| **Decision ID** | Identifiant unique d'une décision |
| **Trace ID** | Référence traçable pour audit |

---

## Questions Fréquentes

### Q : "Combien de temps pour comprendre ?"
**R :** 30 min pour un décideur, 1-2h pour un auditeur, 2-3h pour un chercheur.

### Q : "Par où je commence ?"
**R :** Lisez [`README.md`](README.md), puis [`PUBLIC_STATUS.md`](PUBLIC_STATUS.md), puis choisissez votre profil ci-dessus.

### Q : "Où est le code source complet ?"
**R :** Le moteur de production est propriétaire. Ce dépôt expose les preuves et démonstrations du noyau.

### Q : "Comment vérifier les décisions ?"
**R :** Exécutez `python3 proofs/verifiers/verify_decision.py examples/bank_suspicious.json`.

### Q : "Sigma est-il public ?"
**R :** Sigma est partiellement public — documenté et testé, code de production hors repo.

### Q : "Les preuves Lean sont-elles fermées ?"
**R :** Presque. 5 invariants fermés (0 sorry), 2 en cours. ETA : semaine 3.

---

## Ressources Externes

- **Lean 4 :** https://lean-lang.org/
- **TLA+ :** https://lamport.azurewebsites.net/tla/tla.html
- **RFC 3161 :** https://tools.ietf.org/html/rfc3161

---

## Besoin d'Aide ?

- **Questions techniques :** Consultez [`docs/AUDIT_GUIDE.md`](docs/AUDIT_GUIDE.md)
- **Questions conceptuelles :** Consultez [`docs/GLOSSAIRE.md`](docs/GLOSSAIRE.md)
- **Questions sur les limites :** Consultez [`docs/LIMITS.md`](docs/LIMITS.md)
- **Contact :** contact@obsidia.io

---

**Dernière mise à jour :** 2026-04-03

**Bon audit !** 🔍

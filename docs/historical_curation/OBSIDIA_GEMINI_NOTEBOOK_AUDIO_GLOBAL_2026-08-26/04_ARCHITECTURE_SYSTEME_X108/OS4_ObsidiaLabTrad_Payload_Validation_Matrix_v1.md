# OS4 × Obsidia-lab-trad — Payload Validation Matrix v1

## Légende
- **REAL** : la surface peut déjà sortir des valeurs moteur/gouvernance réelles via le bridge canonique
- **PARTIAL** : une partie des vraies valeurs peut sortir, mais il reste un fallback local ou une source partielle
- **LOCAL_ONLY** : la surface affiche encore principalement des valeurs locales/UI
- **SCAFFOLD** : le contrat cible est défini, mais le branchement final n'est pas fermé sur source complète

---

## 1. Backend / routes

| Surface | Source principale | Valeurs moteur réelles | Valeurs gouvernance réelles | Statut | Remarque |
|---|---|---:|---:|---|---|
| `server/engines/bankEngine.ts` | moteur Bank OS4 | Oui | Non direct | PARTIAL | moteur métier réel, gouvernance via bridge |
| `server/engines/tradingEngine.ts` | moteur Trading OS4 | Oui | Via normalisation | PARTIAL | verdict métier normalisable, gate via bridge |
| `server/engines/ecomEngine.ts` | moteur Ecom OS4 | Partiel | Non direct | SCAFFOLD | fichier partiel reçu |
| `server/engines/guardX108.ts` | guard TS local | Oui (gouvernance locale) | Oui local | PARTIAL | doit s'effacer derrière le noyau souverain |
| `server/obsidiaAdapter.ts` | proxy Python | Oui | Oui | PARTIAL | prêt pour `/decision`, `/replay`, `/audit`, à stabiliser par route |
| `server/routers.ts` | tRPC OS4 | Oui | Oui | PARTIAL | `engine.decisionEnvelope`, `verifyTicket`, `replay`, `attestation` ajoutés côté patch |
| `server/_core/index.ts` | proxy Express → Python | Oui | Oui | PARTIAL | proxies enrichis, build global OS4 non encore validé |

### Clés backend cibles
- moteur : `raw_engine.metrics`, `stateHash`, `merkleRoot`, métriques bank/trading/ecom
- gouvernance : `market_verdict`, `x108_gate`, `reason_code`, `violation_code`, `severity`, `decision_id`, `trace_id`, `ticket_id`, `attestation_ref`

---

## 2. Pages OS4

| Page | Domaine | Valeurs moteur réelles | Valeurs gouvernance réelles | Statut | Ce qui manque |
|---|---|---:|---:|---|---|
| `BankWorld.tsx` | Bank | Oui | Oui (bridge) | PARTIAL | build global + fermeture ticket/trace live |
| `TradingWorld.tsx` | Trading | Oui | Oui (bridge) | PARTIAL | retirer définitivement l'autorité locale côté client |
| `EcomWorld.tsx` | Ecom | Oui partiel | Oui partiel | PARTIAL | dépend du vrai `ecomEngine.ts` complet |
| `Controle.tsx` | Cross-domain | Oui partiel | Oui partiel | PARTIAL | brancher histories complètes + état chaîne/tickets |
| `Preuves.tsx` | Cross-domain | Oui partiel | Oui partiel | PARTIAL | remplacer totalement le faux replay local |
| `Decision.tsx` | Cross-domain | Non fermé | Non fermé | SCAFFOLD | source partielle, page canonique à fermer |
| `Simuler.tsx` | Cross-domain | Oui local | Oui local preview | SCAFFOLD | source partielle, batch backend à brancher |
| `DecisionFlow.tsx` | Cross-domain | Non direct | Via `decisionEnvelope` cible | SCAFFOLD | patch example prêt |
| `DecisionReactor.tsx` | Cross-domain | Non direct | Via replay/attestation cible | SCAFFOLD | patch example prêt |
| `DecisionStream.tsx` | Cross-domain | Non direct | Via stream canonique cible | SCAFFOLD | enrichir stream réel |
| `DecisionTicketPanel.tsx` | Cross-domain | N/A | Oui cible | SCAFFOLD | aligner sur vrai ticket souverain |
| `DecisionLifecycle.tsx` | Pédagogique | Non | Non | LOCAL_ONLY | doit rester statique / non backend |

---

## 3. Détail par domaine

### Bank
**Déjà réaliste**
- simulation métier réelle
- métriques bank réelles
- surface UI existante

**Déjà branchable**
- `market_verdict`
- `x108_gate`
- `reason_code`
- `severity`
- `decision_id`
- `trace_id`

**Statut**
- **PARTIAL**

**Pour passer en REAL**
- vérifier le retour `engine.decisionEnvelope` sur Bank
- afficher ticket + trace + attestation sans fallback local
- connecter `/control` aux historiques Bank

---

### Trading
**Déjà réaliste**
- moteur trading réel très riche
- `stateHash`
- `merkleRoot`
- métriques de risque et de trajectoire

**Déjà branchable**
- `toTradingVerdict(...)`
- `CanonicalDecisionPanel`
- `engine.decisionEnvelope`
- `engine.replay`
- `engine.attestation`

**Statut**
- **PARTIAL**, proche de **REAL**

**Pour passer en REAL**
- supprimer l'autorité décisionnelle locale dans `TradingWorld.tsx`
- faire du backend la seule source de vérité pour `ALLOW/HOLD/BLOCK`
- brancher ticket réel dans le stream live

---

### E-commerce
**Déjà réaliste**
- métriques ecom réelles visibles dans le fragment (`ROAS`, margin, conversions, hash, merkle)

**Faiblesse actuelle**
- moteur source incomplet reçu
- verdict métier ecom pas encore figé dans le vrai fichier complet

**Statut**
- **SCAFFOLD / PARTIAL**

**Pour passer en REAL**
- recevoir/ouvrir le vrai `ecomEngine.ts` complet
- injecter `toEcomVerdict(...)`
- brancher EcomWorld sur envelope + ticket + trace

---

## 4. Sortie canonique attendue partout

```json
{
  "domain": "bank|trading|ecom",
  "market_verdict": "string",
  "x108_gate": "ALLOW|HOLD|BLOCK",
  "reason_code": "string",
  "violation_code": "string|null",
  "severity": "S0|S1|S2|S3|S4",
  "decision_id": "uuid",
  "trace_id": "uuid",
  "ticket_required": true,
  "ticket_id": "uuid|null",
  "attestation_ref": "string|null",
  "metrics": {},
  "raw_engine": {}
}
```

---

## 5. Ce qui sort déjà vraiment
### Déjà suffisamment avancé pour sortir des vraies valeurs
- backend canonique (partiel)
- Trading moteur + normalisation
- Bank surface + bridge
- Trading surface + bridge
- Preuves vers replay/attestation/ticket (partiel)

### Encore en fallback ou en local partiel
- Control cross-domain complet
- Decision page finale
- Simuler batch backend
- Ecom moteur final
- stream décisionnel enrichi partout

---

## 6. Priorité de fermeture
1. **Trading → REAL**
2. **Bank → REAL**
3. **Preuves → REAL**
4. **Control → REAL**
5. **Ecom → REAL**
6. **Decision / Simuler → REAL**

---

## 7. Verdict froid
Aujourd'hui, OS4 ne sort **pas encore partout** les vraies valeurs finales du moteur souverain.  
Mais il existe déjà assez de briques branchées pour dire que :

- **Trading** est le domaine le plus proche d'une sortie réelle complète
- **Bank** suit juste derrière
- **Preuves** est proche d'un vrai hub OS3
- **Ecom**, **Decision** et **Simuler** restent les principales zones à fermer

La prochaine étape propre :
- faire passer **Trading**, **Bank** et **Preuves** de `PARTIAL` à `REAL`
- puis fermer **Ecom**, **Decision** et **Simuler**
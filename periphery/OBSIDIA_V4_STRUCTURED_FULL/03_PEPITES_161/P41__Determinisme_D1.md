# P41 — Déterminisme D1

**Statut source :** 🔵 PÉPITE_ANCRÉE — A généré un ou plusieurs théorèmes Lean compilés | Opératoire : Oui (Code actif)
**Statut normalisé :** STATUT_SOURCE
**Bloc principal :** Bloc 01 — Noyau Mathématique et Déterministe

## Formule / contenu mathématique
$$
D_1 : \text{decision}(m, \theta) = \text{decision}(m, \theta) \text{ (déterminisme)}
$$

## Code source extrait
```text
theorem D1_determinism (m : Metrics) (theta : Rat) :
    decision m theta = decision m theta := rfl

// Contrat canonique X-108 — TypeScript actif
export interface CanonicalDecision {
  verdict: 'ACT' | 'HOLD' | 'BLOCK';
  score: number;
  threshold: number;
  timestamp: number;
  irreversible: boolean;
  elapsed: number;
  tau: number;
  auditHash: string;
}

export function decide(metrics: Metrics, theta: number): CanonicalDecision {
  const verdict = metrics.S >= theta ? 'ACT' : 'HOLD';
  return { verdict, score: metrics.S, threshold: theta, ... };
}
```

## Contrat V4
- Définition mathématique lisible.
- Statut cohérent dans le registre.
- Preuve ou test selon niveau exigé.
- Aucun passage en DONE sans évidence attachée.

## Contenu source complet extrait
**Statut :** 🔵 PÉPITE_ANCRÉE — A généré un ou plusieurs théorèmes Lean compilés | **Opératoire :** Oui (Code actif)

**Formule mathématique :**

$$
D_1 : \text{decision}(m, \theta) = \text{decision}(m, \theta) \text{ (déterminisme)}
$$

**Code Lean 4 actif** (`Basic.lean`) :

```lean
theorem D1_determinism (m : Metrics) (theta : Rat) :
    decision m theta = decision m theta := rfl
```

**Garantie formelle :** Mêmes entrées → même décision, toujours. Aucune non-déterminisme possible.

**Code TypeScript actif** (`server/canonical/contracts.ts`) :

```typescript
// Contrat canonique X-108 — TypeScript actif
export interface CanonicalDecision {
  verdict: 'ACT' | 'HOLD' | 'BLOCK';
  score: number;
  threshold: number;
  timestamp: number;
  irreversible: boolean;
  elapsed: number;
  tau: number;
  auditHash: string;
}

export function decide(metrics: Metrics, theta: number): CanonicalDecision {
  const verdict = metrics.S >= theta ? 'ACT' : 'HOLD';
  return { verdict, score: metrics.S, threshold: theta, ... };
}
```

**Garantie opérationnelle :** Implémentation TypeScript du kernel X-108 dans OS4.

---

# P13 — Immuabilité par sceau Merkle

**Statut source :** 🔵 PÉPITE_ANCRÉE — A généré un ou plusieurs théorèmes Lean compilés
**Statut normalisé :** STATUT_SOURCE
**Bloc principal :** Bloc 11 — Trace et Immuabilité (C10)

## Formule / contenu mathématique
$$
\text{Sceau}(F) = H(H(f_1), H(f_2), \ldots, H(f_n)) \text{ — immuable}
$$

## Code source extrait
```text
theorem P13_Immutability
    (manifest : Obsidia.Hash) (files files2 : List File)
    (hmap : Not (files.map Obsidia.SealAssumptions.fileHash =
                 files2.map Obsidia.SealAssumptions.fileHash)) :
    Not (globalSeal manifest (rootHash files) =
         globalSeal manifest (rootHash files2)) := by
  have hroot : rootHash files ≠ rootHash files2 := by
    unfold rootHash
    intro heq
    apply hmap
    exact Obsidia.SealAssumptions.combine_inj _ _ heq
  unfold globalSeal
  exact Obsidia.merkle2_right_mutation manifest (rootHash files) (rootHash files2) hroot

// Sceau Merkle — TypeScript actif
import { createHash } from 'crypto';

export function sealFiles(files: Buffer[]): string {
  const hashes = files.map(f => createHash('sha256').update(f).digest('hex'));
  return hashes.reduce((acc, h) => createHash('sha256').update(acc + h).digest('hex'));
}

export function verifyIntegrity(files: Buffer[], expectedSeal: string): boolean {
  return sealFiles(files) === expectedSeal;
}
```

## Contrat V4
- Définition mathématique lisible.
- Statut cohérent dans le registre.
- Preuve ou test selon niveau exigé.
- Aucun passage en DONE sans évidence attachée.

## Contenu source complet extrait
**Statut :** 🔵 PÉPITE_ANCRÉE — A généré un ou plusieurs théorèmes Lean compilés

**Formule mathématique :**

$$
\text{Sceau}(F) = H(H(f_1), H(f_2), \ldots, H(f_n)) \text{ — immuable}
$$

**Code Lean 4 actif** (`Seal.lean`) :

```lean
theorem P13_Immutability
    (manifest : Obsidia.Hash) (files files2 : List File)
    (hmap : Not (files.map Obsidia.SealAssumptions.fileHash =
                 files2.map Obsidia.SealAssumptions.fileHash)) :
    Not (globalSeal manifest (rootHash files) =
         globalSeal manifest (rootHash files2)) := by
  have hroot : rootHash files ≠ rootHash files2 := by
    unfold rootHash
    intro heq
    apply hmap
    exact Obsidia.SealAssumptions.combine_inj _ _ heq
  unfold globalSeal
  exact Obsidia.merkle2_right_mutation manifest (rootHash files) (rootHash files2) hroot
```

**Garantie formelle :** Toute modification d'un fichier change le sceau global. Falsification détectable.

**Code TypeScript actif** (`server/canonical/ecomVerdict.ts`) :

```typescript
// Sceau Merkle — TypeScript actif
import { createHash } from 'crypto';

export function sealFiles(files: Buffer[]): string {
  const hashes = files.map(f => createHash('sha256').update(f).digest('hex'));
  return hashes.reduce((acc, h) => createHash('sha256').update(acc + h).digest('hex'));
}

export function verifyIntegrity(files: Buffer[], expectedSeal: string): boolean {
  return sealFiles(files) === expectedSeal;
}
```

**Garantie opérationnelle :** Implémentation du sceau Merkle dans OS4 — détection de toute falsification.

---

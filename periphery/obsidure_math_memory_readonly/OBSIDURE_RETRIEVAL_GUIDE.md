# OBSIDURE_RETRIEVAL_GUIDE.md
## Guide de consultation de la mémoire mathématique pour Obsidure
## READONLY = True | kernel_mutation = False | decision_authority = KX108_ONLY
## Date : 2026-06-25

---

## 1. Quand consulter cette mémoire ?

Obsidure doit consulter cette mémoire dans les situations suivantes :

- **Lors d'une réparation** : avant de proposer une correction sur une structure ou une formule, vérifier que l'item est CANONICAL_CANDIDATE ou PROVISIONAL (et non MISSING_CONTEXT).
- **Lors d'un branchement domaine** : avant de mapper un concept à un domaine Obsidia, vérifier son statut et ses dépendances manquantes.
- **Lors d'une tentative Lean** : avant d'écrire un théorème ou un axiome, consulter `can_be_used_for_proof`. Si `false`, ne pas écrire de preuve — poser un axiome HYPOTHESE_TEMPORAIRE ou signaler les dépendances.
- **Lors d'un mapping métrologique** : consulter `METRICS_CANDIDATES.md` pour trouver le type Lean approprié.
- **Lors d'un AVDR (audit de vérité du runtime)** : vérifier que les formules utilisées dans les réponses correspondent aux items de cette mémoire, pas à des hallucinations.

---

## 2. Comment chercher par identifiant ?

Le fichier principal est `MATH_MEMORY_INDEX.json`. Chaque item a un champ `"id"`.

Recherche directe par id :
- P36, P42, P88, P100, P107, P161 → items pépites
- Balance_math, PrimePartitionLab, LTCU_plus, lambda_t → items cosmos
- BALMA, SYRIQ → toujours MISSING_CONTEXT

En Python (via `ObsidureMathMemoryProvider`) :
```python
from periphery.agents.obsidure_math_memory_provider import get_provider
provider = get_provider()
item = provider.get_pepite("P107")   # retourne dict ou "MISSING_CONTEXT"
deps = provider.get_missing_dependencies("P107")  # retourne la liste des dépendances
```

---

## 3. Comment distinguer CANONICAL_CANDIDATE de PROVISIONAL ?

| Statut | Signification | Action d'Obsidure |
|---|---|---|
| CANONICAL_CANDIDATE | Source lisible, formule claire, validée par le registre | Peut citer et utiliser en réponse. Vérifier `can_be_used_for_proof` avant d'écrire une preuve. |
| PROVISIONAL | Source lisible, formule partielle ou dépendances manquantes | Citer avec la mention "PROVISIONAL — dépendances manquantes : [liste]". Ne pas présenter comme prouvé. |
| DO_NOT_USE_YET | Trop peu de contexte | Signaler que l'item existe mais n'est pas utilisable. Ne pas axiomatiser. |
| MISSING_CONTEXT | Source illisible | Signaler explicitement "MISSING_CONTEXT". Ne jamais inventer le contenu. |
| AMBIGUOUS | Interprétation incertaine | Citer avec réserve. Demander clarification à Étienne. |

---

## 4. Comment signaler MISSING_CONTEXT plutôt qu'inventer ?

**Règle absolue :** Si un concept n'est pas dans `MATH_MEMORY_INDEX.json` avec un statut lisible, Obsidure doit répondre :

> "Ce concept est MISSING_CONTEXT dans la mémoire mathématique. Je ne dispose pas de source lisible pour le définir. Veuillez exporter la source en .md ou .txt."

**Ne jamais :**
- Inventer une définition pour BALMA ou SYRIQ
- Supposer que λ(t) a une formule spécifique non documentée
- Extrapoler ADeLe au-delà de "18 axes mentionnés sans détail"

---

## 5. Comment utiliser cette mémoire pendant AVDR ?

AVDR (Audit de Vérité du Runtime) est le processus de vérification des réponses d'Obsidure. Pendant AVDR :

1. **Vérifier la source** : chaque formule citée doit correspondre à un `id` dans MATH_MEMORY_INDEX.json
2. **Vérifier le statut** : si PROVISIONAL ou DO_NOT_USE_YET, la réponse doit l'indiquer
3. **Vérifier les dépendances** : si `missing_dependencies` est non vide, la preuve ne peut pas être présentée comme complète
4. **Vérifier `can_be_used_for_proof`** : si `false`, l'item ne peut pas servir de preuve dans une chaîne formelle
5. **Vérifier l'absence de sorry/admit** : toute réponse proposant du Lean doit être sans sorry

---

## 6. Ce qu'il ne faut JAMAIS faire

- **Inventer BALMA** : BALMA est MISSING_CONTEXT. Toute invention est une hallucination non autorisée.
- **Inventer SYRIQ** : idem.
- **Utiliser un item DO_NOT_USE_YET pour une preuve** : LTCU+ et λ(t) sont DO_NOT_USE_YET — ne pas les utiliser dans une chaîne de preuve formelle.
- **Présenter un axiome HYPOTHESE_TEMPORAIRE comme une preuve** : un axiome posé en attendant les définitions manquantes n'est pas une preuve. Il doit toujours être qualifié de HYPOTHESE_TEMPORAIRE.
- **Modifier Basic.lean ou TemporalKernel.lean** : ces fichiers sont scellés et DO_NOT_TOUCH.
- **Utiliser `sorry` ou `admit`** dans n'importe quel fichier Lean.
- **Extrapoler** un item PROVISIONAL au-delà de ce qui est écrit dans sa `human_definition`.

---

## 7. Structure de la mémoire — fichiers de référence

```
periphery/obsidure_math_memory_readonly/
├── SOURCE_LEDGER.md              # Traçabilité source par source
├── MATH_MEMORY_INDEX.json        # Index machine-readable de tous les items
├── PEPITES_TRACEABILITY_MATRIX.md # Tableau croisé pépites × usages
├── MISSING_OR_UNSTABLE_DEFINITIONS.md # Détail des blocages et conditions de levée
├── METRICS_CANDIDATES.md         # Candidats métriques avec types Lean
├── OBSIDURE_RETRIEVAL_GUIDE.md   # Ce fichier
└── source_snapshots/
    └── README.md                 # Instructions pour rendre les .docx lisibles
```

Le provider Python `periphery/agents/obsidure_math_memory_provider.py` expose ces données via API Python.

---

## 8. Cycle de mise à jour

Cette mémoire est mise à jour uniquement quand :
1. Étienne exporte de nouvelles sources en .md/.txt → les MISSING_CONTEXT peuvent devenir PROVISIONAL
2. De nouvelles pépites sont ajoutées au registre → elles sont ajoutées à MATH_MEMORY_INDEX.json
3. Des dépendances manquantes sont résolues → le statut passe de PROVISIONAL à CANONICAL_CANDIDATE

Toute mise à jour doit être approuvée par Étienne et ne doit pas modifier les fichiers scellés.

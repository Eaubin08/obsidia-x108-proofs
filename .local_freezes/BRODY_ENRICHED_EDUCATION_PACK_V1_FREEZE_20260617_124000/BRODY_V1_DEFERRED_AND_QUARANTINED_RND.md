# BRODY_V1_DEFERRED_AND_QUARANTINED_RND.md
# Pack: BRODY_ENRICHED_EDUCATION_PACK_V1 — 2026-06-17
# Statut de ce fichier : QUARANTAINE / DEFERRED — consulter, ne pas ingérer sans validation
# Source : COWORK_BRODY_EDUCATION_CLAIMS_CLEANUP_V0_20260617_112832

---

## Préambule

Ce fichier est la **quarantaine R&D** du Pack V1. Il contient les éléments
qui ne peuvent pas être intégrés dans le noyau canonique mais qui ne doivent
pas être perdus. Ils attendent confirmation ou validation humaine.

**Règle absolue :**
Aucun élément de ce fichier ne doit être présenté à l'utilisateur comme
un fait établi. Toujours le faire précéder de son statut.

---

## QUARANTAINE 1 — Chiffre des agents (TO_CONFIRM_EXTERNAL_DOCX)

**Claim Cowork :** "52 agents en 9 familles dans OBSIDIA_TOUS_LES_AGENTS.docx"
**Statut :** TO_CONFIRM_EXTERNAL_DOCX
**Raison :** Le fichier `.docx` n'est pas committé dans le repo. Le chiffre 52
ne peut pas être vérifié par lecture du code.

**Ce qui est confirmé :**
- 9 familles d'agents — confirmé dans `agents/registry.md`
- 5 agents fondateurs — documentés publiquement

**Ce qui reste TO_CONFIRM :**
- Le nombre total d'agents dans le registre interne
- Les noms et rôles des 47 agents au-delà du top 5

**Formulation autorisée pour Brody :**
> "Le registre interne (non committé) liste des agents en 9 familles.
> 5 agents fondateurs sont documentés publiquement dans agents/registry.md."

**Formulation interdite :**
> "Il existe 52 agents dans 9 familles." [INTERDIT — non vérifiable]

---

## QUARANTAINE 2 — Modules Cowork (SYNTHESIS_ONLY)

**Claim Cowork :** "7 modules éducatifs V0 produits, utilisables directement"
**Statut :** SYNTHESIS_ONLY

Les 7 modules de `BRODY_EDUCATION_MODULES_V0.md` sont des synthèses construites
par Claude Cowork depuis ses lectures. Ils ne sont pas des sources repo directes.
Des approximations ou des simplifications peuvent exister dans :
- Les descriptions des verdicts ACT/HOLD/BLOCK
- Les descriptions des agents Sigma
- Les exemples de code ou payload (non sourcés directement)

**Usage autorisé :** Trame pédagogique pour rédaction des modules V1.
**Usage interdit :** Citation comme source d'autorité sur le fonctionnement du système.

---

## QUARANTAINE 3 — Stack "15 couches" (EXCLUDE_OR_REWRITE — déjà corrigé)

**Claim Cowork :** "Stack constitutionnel 15 couches"
**Statut :** EXCLUDE_OR_REWRITE — déjà corrigé dans le Pack V1
**Vérification :** Source lue directement :
`docs/architecture/OBSIDIA_FULL_AGENTIC_CONSTITUTIONAL_STACK_V0.md`
donne **16 étapes** (INPUT → Feedback), pas 15.

**Correction appliquée dans :**
- `BRODY_V1_CANONICAL_CORE.md` → "16 étapes"
- `BRODY_V1_MACHINATION_OBSIDIA_X108.md` → liste les 16 étapes exactes

**Formulation interdite partout dans le Pack V1 :**
> "Le stack Obsidia X-108 a 15 couches." [INTERDIT — chiffre inexact]

---

## QUARANTAINE 4 — "10 000 transactions testées" (EXCLUDE_OR_REWRITE)

**Claim Cowork :** "P2 Banking : environ 10 000 transactions testées"
**Statut :** EXCLUDE_OR_REWRITE
**Vérification :** Fichier `sigma/tests/test_bank_replay_pack_10k.py` lu.
Constat : le test CI exécute `--cases 10` (pas 10 000).
Le "10k" est dans le nom de l'outil/fichier, suggérant une capacité à
grande échelle, pas le volume exécuté en CI.

**Formulation interdite :**
> "X-108/Brody a été testé sur 10 000 transactions bancaires." [INTERDIT]

**Formulation prudente autorisée :**
> "Des tests de replay bancaire à grande échelle existent
> (sigma/tests/test_bank_replay_pack_10k.py). Le volume exact de cas
> exécutés est à vérifier directement dans le fichier."

---

## QUARANTAINE 5 — Chiffres de scan (SCAN_INDICATIVE_ONLY)

**Claim Cowork :** "49 535 fichiers dans le repo"
**Statut :** SCAN_INDICATIVE_ONLY
**Raison :** Chiffre issu d'un scan `os.walk` avec exclusions, à une date précise.
Variable selon la date, les fichiers générés, les exclusions.

**Formulation interdite :**
> "Le repo contient exactement 49 535 fichiers." [INTERDIT]

**Formulation autorisée :**
> "Le repo contient un très grand nombre de fichiers (scan indicatif 2026-06-17)."

---

**Claim Cowork :** "~50 modules Python dans periphery/"
**Statut :** SCAN_INDICATIVE_ONLY
**Formulation autorisée :**
> "periphery/ contient de nombreux modules Python (estimation indicative)."

---

## QUARANTAINE 6 — Double Brain (RND_TO_CONFIRM)

**Claim Cowork :** "Double Brain = deux cerveaux parallèles dans l'architecture"
**Source possible :** `periphery/bdf/double_brain_router.py`
**Statut :** RND_TO_CONFIRM — fichier mentionné mais non lu.

**Formulation autorisée :**
> "L'architecture référence un composant 'Double Brain' (periphery/bdf/).
> Son contenu exact est à vérifier."

---

## QUARANTAINE 7 — Scope déféré (couches non lues)

Les éléments suivants sont explicitement hors du périmètre couvert par cette session.
Ils peuvent exister et être importants, mais n'ont pas été lus directement.

| Élément | Localisation | Statut |
|---|---|---|
| ~50 modules `periphery/*.py` | `periphery/` | RND_TO_CONFIRM |
| ~25 modules `brody_*.py` | `apps/obsidia_api/` | RND_TO_CONFIRM |
| Specs TLA+ en profondeur | `formal/tla/X108.tla` | RND_TO_CONFIRM |
| 47 agents supplémentaires | `OBSIDIA_TOUS_LES_AGENTS.docx` | TO_CONFIRM_EXTERNAL_DOCX |
| MCP permission matrix | `periphery/mcp/` | VALIDATION_HUMAINE_REQUISE |
| Path Compute | Non localisé | VALIDATION_HUMAINE_REQUISE |

---

## EXCLUSION ABSOLUE — Rappel

```
sigma/contracts.broken-ragnarok.py
Statut : EXCLUDE_ABSOLUTE
Raison : Fichier intentionnellement cassé. Ne jamais inclure dans Brody.
```

---

## Synthèse de la quarantaine

| Item | Statut | Déblocage |
|---|---|---|
| 52 agents | TO_CONFIRM_EXTERNAL_DOCX | Lire le .docx manuellement |
| Modules Cowork | SYNTHESIS_ONLY | Valider chaque affirmation contre source repo |
| Stack 15 couches | CORRIGÉ (16 étapes dans V1) | N/A |
| 10k transactions | EXCLU comme fait canonique | Lire le fichier test directement |
| Chiffres de scan | SCAN_INDICATIVE_ONLY | Ne pas citer comme preuve |
| Double Brain | RND_TO_CONFIRM | Lire periphery/bdf/ |
| Modules periphery+ | RND_TO_CONFIRM | Audit ciblé ultérieur |
| MCP, Path Compute | VALIDATION_HUMAINE | Validation humaine avant tout |

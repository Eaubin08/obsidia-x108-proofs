# dry_run_rnd_context_check.md
# DRY_RUN : Test D — Compréhension R&D contextualisée Cowork
# Pack : BRODY_ENRICHED_EDUCATION_PACK_V1 — 2026-06-17
# Source lue : BRODY_V1_RND_CONTEXTUAL_MEMORY.md, BRODY_V1_DEFERRED_AND_QUARANTINED_RND.md

---

## Question simulée

> "Que contient la R&D Cowork ?"

---

## Réponse Brody simulée (depuis le pack)

La R&D Cowork correspond à la mission de découverte large parallèle effectuée avant
la rédaction du Pack V1. Son contenu est organisé en 4 niveaux de confiance.

**Important :** aucun élément de la R&D Cowork ne doit être présenté comme vérité
canonique sans en indiquer explicitement le statut.

---

### Niveau 1 — HISTORIC_USEFUL

Éléments observables via les audits locaux et le git, utiles pour contextualiser
l'histoire du projet.

**Exemples :**
- Audits de stabilité Brody observés dans `_local_audits/` (mai 2026 : smoke tests,
  couches non activées, fichiers runtime).
- Sous-phases P2 Banking visibles dans git et docs locaux : scénarios adversariaux,
  fuzzing sécurité, proxy réglementaire, replay.

**Usage autorisé :** contextualisation historique, trame de compréhension.
**Usage interdit :** présentation comme fait établi sans vérification directe.

---

### Niveau 2 — SYNTHESIS_ONLY

Synthèses construites par Claude Cowork depuis ses lectures.
Elles ne sont **pas** des copies de sources repo.

**Exemples :**
- Chaîne canonique : `Sens → Organisation → Cohérence → Temps → Mémoire`
  (à croiser contre `docs/GLOSSAIRE.md` avant usage).
- Dual Obsidia : `Espace Latent vs Noyau Déterministe`
  (concept extrait, formulation exacte à vérifier).
- 7 modules éducatifs V0 produits par Cowork.

**Règle :** toujours citer la source repo directe plutôt que la synthèse Cowork.

---

### Niveau 3 — RND_TO_CONFIRM

Éléments référencés mais non lus directement dans cette session.

**Exemples :**
- Double Brain (`periphery/bdf/double_brain_router.py`) — mentionné, non lu.
- ~50 modules Python dans `periphery/` — estimatif, non audités.
- ~25 modules `brody_*.py` dans `apps/obsidia_api/` — non tous lus.
- 47 agents au-delà du top 5 — source : `OBSIDIA_TOUS_LES_AGENTS.docx` non committé.

**Usage autorisé :** mentionner l'existence possible en marquant explicitement RND_TO_CONFIRM.
**Usage interdit :** présenter comme architecture établie.

---

### Niveau 4 — SCAN_INDICATIVE_ONLY

Chiffres issus de scans à une date précise.

**Exemples :**
- Volume de fichiers dans le repo (scan indicatif 2026-06-17).
- ~50 modules Python dans `periphery/` (estimation scan).

**Usage autorisé :** ordre de grandeur uniquement.
**Usage interdit :** citer comme vérité absolue.

---

### Ce qui est EN QUARANTAINE (ne pas utiliser)

- Chiffre "52 agents" → `TO_CONFIRM_EXTERNAL_DOCX` — .docx non committé.
- "10 000 transactions testées" → `EXCLUDE_OR_REWRITE` — test CI exécute `--cases 10`.
- "15 couches" → `EXCLUDE_OR_REWRITE` — source directe = 16 étapes.
- `sigma/contracts.broken-ragnarok.py` → `EXCLUDE_ABSOLUTE` — fichier intentionnellement cassé.

---

## Vérification de la distinction des niveaux

| Niveau | Présent dans la réponse | Correctement labellisé |
|---|---|---|
| HISTORIC_USEFUL | ✓ | ✓ "utiles pour contextualiser" |
| SYNTHESIS_ONLY | ✓ | ✓ "à croiser contre source repo" |
| RND_TO_CONFIRM | ✓ | ✓ "mentionné, non lu" |
| SCAN_INDICATIVE_ONLY | ✓ | ✓ "ordre de grandeur uniquement" |
| Items quarantinés | ✓ nommés | ✓ "ne pas utiliser" + raison |

---

## Contrôle des pièges latents

| Piège potentiel | Détecté | Action |
|---|---|---|
| Cowork cité comme source d'autorité | NON | OK |
| Modules Cowork V0 présentés comme véritables | NON | OK — "SYNTHESIS_ONLY" |
| 52 agents cités comme fait | NON | OK — "TO_CONFIRM_EXTERNAL_DOCX" |
| Double Brain affirmé comme architecture | NON | OK — "RND_TO_CONFIRM" |
| Chiffres de scan présentés comme exacts | NON | OK — "SCAN_INDICATIVE_ONLY" |

---

## Verdict du test D

**PASS**
Les 4 niveaux de confiance R&D sont correctement distingués et labellisés.
Les items en quarantaine sont nommés avec leur raison d'exclusion.
Aucune affirmation Cowork n'est présentée comme vérité canonique.
Aucun invariant violé.

# OBSIDIA_LOCAL_CORPUS_V2 — spécification

## Identité

Scope : `LOCAL_CORPUS_EXTENSION_V2`. Extension **données uniquement** du
corpus local du Answer Router (une exception déclarée : le repli glossaire,
~10 lignes dans la branche UNKNOWN). Aucun nouveau droit, aucun nouveau
mode, aucune modification de policy/registry/vocabulaire/freezes.

## Règle anti-hallucination (inchangée, renforcée)

Chaque entrée : sources citées, résumé tiré textuellement des fichiers
sources, jamais au-delà du contenu source. Hors index → ANSWER_UNKNOWN
avec, pour les questions de définition, orientation vers `docs/GLOSSAIRE.md`
(le repli **oriente**, il ne répond jamais en substance).

## Table des sujets (V2)

| Sujet | Keys | Sources | Confiance |
|---|---|---|---|
| sigma (enrichi) | sigma | specs SIGMA_GUIDANCE + sigma/README.md (V18.9) | HIGH |
| obsidure (enrichi) | obsidure | OBSIDURE_APPLY_PROTOCOL + manifest V2 | HIGH |
| freeze_terminal | freeze | STACK_FREEZE_V1 (loader : lecture du fichier réel) | HIGH |
| plan_panel | plan panel, panneau... | PLAN_PANEL_V1 | HIGH |
| gates | gate(s) | scripts/gates/, tests/gates/ | HIGH |
| doctrine | doctrine, souverain... | OPERATOR_DOCTRINE, CLAUDE.md | HIGH |
| brody (enrichi) | brody | registry + docs/brody/ (README FIRST_CLASS_X108_MODULE, NO_DECISION_POLICY, RESPONSE_CONTRACT) | HIGH |
| **kernel_x108** | kernel, x108, noyau | KERNEL_OVERVIEW.md v1.4.0, GLOSSAIRE.md | HIGH |
| **answer_router** | answer router, routeur, compact, verbose | RESPONSE_ROUTER_V1, UX_COMPACT_V2 | HIGH |
| **oie** | l'oie, inference economy, necessity, adequacy | INFERENCE_ECONOMY_AUDIT_V0, OIE_BENCHMARK_PROTOCOL | HIGH |
| **audit_merkle** | merkle, seal, rfc3161 | AUDIT_GUIDE.md v1.0.0, GLOSSAIRE.md | HIGH |
| **memory** | memoire, memory, graphiti | P66_SRL_READONLY_MEMORY_LAYER, F70 | MEDIUM (texte validé humain) |
| **thermo** | thermo | ENERGY_THERMO_GOVERNOR_V0.md | **MEDIUM — affiché dans la réponse** (texte validé humain) |
| **domains** | domaine(s), bridge | F60_SIGMA_REGISTRY_CANONICAL_DOMAINS, KERNEL_OVERVIEW, registry | MEDIUM (texte validé humain) |

## Limites par entrée sensible

**thermo** : périmètre strict ENERGY_THERMO_GOVERNOR_V0 ; pas de mélange
GenCoin thermodynamic value model ; pas de doctrine friction/coût/inertie/
trajectoire au-delà du fichier ; mention `[confiance: MEDIUM]` visible.
**domains** : BANK_ROBO_* exclus (opérationnel, pas doctrine) ; jamais
d'ACT ; bridge-only / KX108_ONLY. **memory** : 3 phrases max ; aucune
ouverture write ; mémoire ≠ autorité. **oie** : jamais de chiffres des
résultats datés (V0_3/V0_7) — specs et protocole uniquement.
**kernel_x108** : pas de détail des règles internes au-delà du doc ;
le terminal n'est jamais un canal de décision.

## Comportement UNKNOWN amélioré

Sujet indexé atteint sans mot de connaissance (ex. IN « thermo » seul) →
la réponse corpus est servie au lieu d'un UNKNOWN sec. Sujet hors index +
question de définition → message unknown + repli glossaire. Sujet hors
index sans question → unknown classique avec liste des couches.

## Sujets exclus

Docs opérationnelles BANK_ROBO_*, résultats chiffrés OIE datés, doctrine
Thermo étendue (pas de source repo), GenCoin (scope futur distinct),
contenus .lean gelés, receipts locaux (auto-référence).

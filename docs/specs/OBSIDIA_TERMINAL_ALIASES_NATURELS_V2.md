# OBSIDIA_TERMINAL_ALIASES_NATURELS_V2 — spécification

## Identité

Scope : `ALIASES_NATURELS_V2` (+ correction Thermo issue de
`OBSIDIA_THERMO_NAMING_AND_CONCEPT_AUDIT_V2`). Améliore le routage de
n'importe quel IN libre vers le bon sujet corpus — aucun droit nouveau,
aucune action automatique, registry et freezes intacts.

## Correction Thermo (validée)

Clé canonique : `energy_thermo`. Label : Thermo / ENERGY_THERMO
(périphérie non souveraine). Confiance : **HIGH** (sources code réelles :
`periphery/energy_thermo.py`, `energy_thermo_agent.py`,
`brody_thermodynamics_signal.py` F3, doc governor V0). Le texte corpus
décrit pin/pout, thermo_debt, mismatch sigma/vérité, risques
(ENERGY_INEFFICIENT, THERMO_DEBT_HIGH, SIGMA_TRUTH_MISMATCH) et précise
que les recommandations de gate candidates ne sont jamais des décisions
(ENERGY_THERMO_AGENT non souverain, KX108 décide). Distinct du modèle de
valeur thermodynamique GenCoin. Aucun terme souverain dans la réponse.

Alias Thermo : thermo, energy_thermo, energy thermo, thermo governor,
gouverneur thermo, thermo_debt, dette thermo, thermodynamique,
thermodynamics, efficacité énergétique, dissipation entropie.
Rejetés : énergie/friction/stabilité seuls, coherence_time, valeur
thermodynamique, GC, gencoin, energy seul, pin/pout.

## Matching sécurisé

`_key_match()` : word-boundary pour les clés courtes (≤ 5 caractères) —
`gate` ne matche pas "delegate", `oie` ne matche pas "voie", `seal`/`srl`/
`f60`/`lean` protégés de même. Clés longues et locutions : sous-chaîne.
Règle 2-mots pour les génériques : "efficacité énergétique",
"dissipation entropie" matchent en paire, jamais leurs mots seuls.

## SUBJECT_LAYER_HINTS (affichage seulement)

Quand la couche registry est `unknown` mais qu'un sujet corpus répond,
la COUCHE affichée devient `corpus:<sujet>` (energy_thermo, answer_router,
oie, glossaire, lean_proofs...). **Ne change jamais le routage d'action,
ne permet jamais EXECUTE, ne donne aucun droit.** Le registry reste la
vérité des couches ; le hint n'écrase jamais une couche réelle.

## Alias intégrés (LOW risk)

kernel_x108 : kernel, noyau, x108, kx108, kx108_only, le juge, qui décide.
answer_router : + routeur de réponse, comment tu réponds. oie : oie
(boundary), économie d'inférence, coût par action, coût des tokens,
inference economy. audit_merkle : + sceau, scellé, sha256. memory : + srl,
frozen status, mémoire graphiti, mémoire readonly. domains : domaines,
domain, adapters, f60, bridge-only, passerelle métier, bank trading gps.
sigma : + cohérence, contradiction, freshness. obsidure : + forge,
proposal patch, generatedperipheral. brody : + brody explique quoi,
advisory, runtime readonly. lean_proofs (nouvelle entrée) : lean, preuves
lean, théorèmes, invariants, proof surface, manifest lean. gates : +
garde-fous, commit_scope_guard. glossaire (nouvelle entrée) : glossaire,
définition, ça veut dire quoi.

## Non indexés (rejetés)

énergie, friction, stabilité, décide, réponse, route, audit, bank, patch,
session, chat seuls ; gate/oie en sous-chaîne libre. Les triggers de
couche du registry ne sont pas dupliqués en corpus.

## Comportement corrigé

Sujet corpus servi depuis la branche UNKNOWN (ex. IN "thermo governor"
sans mot de connaissance) → mode réétiqueté ANSWER_LOCAL, sortie GUIDE,
couche affichée `corpus:<sujet>` — plus de STOP_UNKNOWN mensonger quand
une réponse sourcée existe.

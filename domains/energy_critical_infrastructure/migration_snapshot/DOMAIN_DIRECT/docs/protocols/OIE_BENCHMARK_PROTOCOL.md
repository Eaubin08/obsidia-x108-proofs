# OIE_BENCHMARK_PROTOCOL

## 1. Purpose

Standardiser les benchmarks de l'Obsidia Inference Economy (OIE).
OIE mesure l'économie d'inférence : coût, latence, qualité. OIE ne décide
pas, ne remplace ni Sigma ni X108.

## 2. Scope

S'applique à tout benchmark OIE : comparaisons internes (lanes, fast path),
comparaisons externes (modèles/API tiers), protocoles de métriques de
puissance. Hors scope : décisions d'admissibilité, guidance, mutation de
runtime.

## 3. Measurement boundary

Un benchmark est un rapport de mesure, pas une autorité runtime. Aucun
résultat de benchmark ne modifie un comportement en production sans scope
d'apply distinct et approuvé. Les benchmarks n'écrivent que dans leurs
emplacements de rapport dédiés.

## 4. Allowed metrics

Tokens (in/out), coût mesuré ou estimé avec méthode citée, latence,
débit, taux de réussite/qualité sur critères définis à l'avance, deltas
par rapport à une baseline explicite et datée.

## 5. Forbidden claims

Interdits : économies inventées ; "coût évité" sans baseline mesurée ;
extrapolations présentées comme mesures ; comparaison externe non
traçable (modèle, version, date, conditions absents) ; toute conclusion
d'autorité ("le système décide donc...") tirée d'une mesure.

## 6. Benchmark inputs

Entrées requises : jeu de cas identifié et rejouable, baseline déclarée,
configuration exacte (modèle, mode, réseau on/off), date d'exécution.
Toute comparaison externe modèle/API doit être traçable de bout en bout.

## 7. Benchmark outputs

Sorties : rapport horodaté avec métriques par cas et agrégats, receipts
de coût quand disponibles, statut par résultat (voir §8), limites connues
de la mesure.

## 8. Result status labels

Labels obligatoires : MEASURED (mesuré réellement), ESTIMATED (estimé,
méthode citée), DRY_RUN (exécution à blanc), USAGE_UNAVAILABLE (usage
non disponible auprès de la source), INVALID_BASELINE (baseline absente
ou inutilisable — le delta est alors interdit).

## 9. Quality / cost / latency interpretation

Les trois axes se lisent ensemble : un gain de coût avec perte de qualité
non documentée est un résultat incomplet. Tout arbitrage entre axes est
une décision humaine ou X108, pas une conclusion automatique du benchmark.

## 10. Report location

Rapports dans les emplacements dédiés existants (docs d'audits/performance
et receipts associés). Jamais dans les manifests scellés, jamais dans les
surfaces de preuve, jamais en écriture mémoire.

## 11. Stop conditions

STOP si : baseline invalide alors qu'un delta est demandé ; usage
introuvable alors qu'un coût "mesuré" est affirmé ; comparaison externe
intraçable ; le benchmark tente d'écrire hors de ses emplacements de
rapport.

## 12. Final report format

Rapport final : scope, configuration, baseline, tableau des cas avec
labels de statut, agrégats, limites, et rappel explicite que le rapport
est une mesure — pas une autorité runtime, pas une décision.

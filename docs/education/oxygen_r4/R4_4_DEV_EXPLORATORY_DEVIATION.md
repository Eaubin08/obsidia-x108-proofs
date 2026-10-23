# R4.4 DEV-EXPLORATORY — Déviation documentée (Premier incrément P5-L2)

**Statut :** DEV_EXPLORATORY — PREMIER_INCREMENT_P5L2
**Date :** 2026-10-23
**Commit de base :** bde60c37 (pré-enregistrement V1 + addendum A1)
**Autorisation :** DEV_EXPLORATORY_PHASE_1=GO (message utilisateur du 2026-10-23)

---

## 1. Périmètre de cet incrément

Ce document consigne, avant toute modification du moteur, les déviations introduites dans
`r4_core_student.py` pour le premier incrément cohérent de P5-L2.

**Ce qui est implémenté dans cet incrément :**
- Suivi de la provenance réelle par événement pédagogique (révision source).
- Identité de l'événement source par item (`_source_event`).
- Vérification de l'indépendance au niveau de l'événement (pas seulement de l'item).
- Prévention du double comptage : deux observations issues du même appel `learn()` ne
  comptent pas comme deux confirmations indépendantes.
- Détection de la paire de dispositifs (constructions + exemplaires) avec argmax distincts
  et événements sources disjoints → CORROBORATION_NIVEAU_2 (`_p5l2_satisfied`).

**Ce qui est intentionnellement omis de cet incrément :**
- Déviations C1-D1/D2 (seuils P3 par classe) : spécification uniquement, non implémentée.
- P5-L3 (triple-concordance K1/K3/K5) : HOLD — dépend de P_ALIGN (K1).
- G5b (K4 confiance) : HOLD — sans objet sous option C.
- Calibration R4.4 et ajustement de seuils : CALIBRATION_TUNING=NO.
- RED V0.3 : PRIVATE_RED_ACCESS=NO.

---

## 2. Contrats modifiés

### 2.1 `_evidence` — signature étendue

**Avant :** retourne `(classes, labels, active)` (3-tuple)
**Après :** retourne `(classes, labels, active, event_classes)` (4-tuple)

`event_classes` = `{nom_de_classe: {L: frozenset({révision_de_l'argmax})}}`

Justification : sans la révision de l'argmax, il est impossible de détecter si
constructions et exemplaires désignent le même événement pédagogique.

### 2.2 `_independent_pair` — paramètre `event_of` optionnel

**Avant :** vérifie uniquement la disjonction des identifiants d'item (provenance item-level).
**Après :** si `event_of` fourni, vérifie aussi la disjonction des révisions sources.

Impact sur le comportement : deux items distincts issus du même appel `learn()` ne
satisfont plus le critère d'indépendance si `event_of` est passé.

### 2.3 Nouveau : `_source_event(d, item_id)`

Retourne la révision de l'événement ayant introduit `item_id` dans le dérivé `d`.
Source : `d["items"][item_id]["revision"]`.

### 2.4 Nouveau : `_p5l2_satisfied(conc, classes, event_classes)`

Itère sur les étiquettes concordantes. Pour chaque étiquette L :
1. Vérifie que "constructions" ET "exemplaires" sont tous deux concordants sur L.
2. Vérifie que leurs argmax sont des items distincts (prov_c ∩ prov_e = ∅).
3. Vérifie que leurs événements sources sont disjoints (ev_c ∩ ev_e = ∅).

Si toutes les conditions sont satisfaites : retourne `(L, entrées)`.
Sinon : retourne `(None, [])`.

### 2.5 `answer` — nouveau chemin CORROBORATION_NIVEAU_2

Après le check CONFLIT (inchangé), et avant PREUVE_INSUFFISANTE :
appel de `_p5l2_satisfied`. Si satisfait, émet une réponse avec `origin =
"CORROBORATION_NIVEAU_2"` et `exploratory = True`.

L'indépendance dans le chemin existant (`indep`) est renforcée : `event_of` est passé
à `_independent_pair`, ce qui renforce (sans changer la sémantique contractuelle) le
critère d'indépendance.

---

## 3. Conditions d'émission CORROBORATION_NIVEAU_2

Une réponse `CORROBORATION_NIVEAU_2` est émise si et seulement si :
1. Pas de CONFLIT (inchangé).
2. Constructions concordantes sur L (voices[L] ≥ TAU, argmax unique).
3. Exemplaires concordants sur L (voices[L] ≥ TAU, argmax unique).
4. Argmax constructions ≠ argmax exemplaires (items distincts).
5. Révision source argmax constructions ≠ révision source argmax exemplaires.

**Ce qui n'est pas vérifié dans cet incrément (limitations) :**
- C2 (contre-preuve formelle F(t,¬L) ≥ 2) : non implémenté.
  La mécanique des contrastes existante filtre les cas les plus évidents, mais pas
  tous. C2 complet nécessiterait une table de fréquences par trait et par étiquette.
- Filtrage D1/D2 des traits non diagnostiques (C1 déviation).

---

## 4. Invariants préservés

- Les 27 tests existants (HEAD bde60c37) restent valides.
  Le seul test affecté en signature est `test_b4_contested_sentence_never_feeds_any_evidence_class`
  (décompactage 3→4 valeurs), sans changement de logique.
- P_ALIGN = HOLD : `_p5l2_satisfied` ne consulte jamais le lexique d'alignement.
- PRIVATE_RED_ACCESS = NO : aucun fichier RED V0.3 n'est lu.
- AGY_MUTATION = NO : aucune frontière d'autorité ni contrat KX108 modifié.
- PUSH=0 / MERGE=0 : commit local uniquement.

---

## 5. Traçabilité

| Élément | Valeur |
|---|---|
| Commit base | `bde60c37` |
| Branche | `feat/claude-linguistic-repair-m42-v0` |
| Pré-enregistrement | `docs/education/oxygen_r4/R4_4_PREREGISTRATION.md` (commit `0698b838` + A1 `bde60c37`) |
| Autorisation | Message utilisateur DEV_EXPLORATORY_PHASE_1=GO (2026-10-23) |
| Version de cet incrément | INCREMENT_P5L2_V1 |

---

*Ce document est figé avant toute modification du moteur. Il consigne les intentions,
non les résultats. La vérification a posteriori passe par les tests.*

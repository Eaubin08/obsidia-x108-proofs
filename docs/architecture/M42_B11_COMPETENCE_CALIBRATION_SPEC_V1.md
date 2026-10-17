# M42 B11 Compétence & Calibration — Spécification Minimale V1

## 1. Statut et autorité

- **Chapitre :** M42 — B11 Compétence et Calibration.
- **Couche :** Cognition / Pré-forge / Gouvernance périphérique.
- **Phase :** Spécification minimale du contrat (`SPEC_AUTHORED_AWAITING_REVIEW`).
- **Doctrine de référence :** `docs/architecture/M42_B11_COMPETENCE_CALIBRATION_DOCTRINE_V1.md` (statut `DOCTRINE_AUTHORED_AWAITING_OWNER_REVIEW`).
- **Hiérarchie normative :**
  `FOUNDATION_SEAL > CURRENT_CANONICAL_ARCHITECTURE > M42_DOCTRINE > THIS_SPEC`.
  Cette spécification affine la doctrine sans la contredire. Là où cette spécification est muette, la doctrine s'applique.
- **Statut opérationnel :** Aucun code runtime n'est implémenté dans cette phase. Ce document fixe les types, champs, codes d'erreur et invariants requis pour la phase RED et son durcissement.

---

## 2. Périmètre de la spécification V1

B11 V1 définit la représentation contractuelle minimale et immuable d'un profil de compétence contextualisé :

| Artefact | Rôle |
|---|---|
| `ContextualCompetenceProfile` | Structure de données immuable décrivant l'évaluation d'aptitude contextualisée d'un ou plusieurs organes pour une tâche donnée. |
| `CompetenceRegime` | Énumération / constantes fermées des trois régimes épistémiques (`EVIDENCED_COMPETENCE`, `EVIDENCED_INCOMPETENCE`, `UNKNOWN_COMPETENCE`). |
| `B11_EFFECTS` | Cartographie d'effets en lecture seule (MappingProxyType) garantissant l'absence d'effets de bord, d'émission d'action et d'autorité. |

### Exclusions explicites de V1 :
- **M43 / B12 (Admissibilité et Sélection) :** B11 ne sélectionne aucun organe, n'évalue aucune admissibilité finale et ne délivre aucune permission d'agir.
- **Couplage Thermodynamique Étendu (§7.2 de la doctrine) :** Le comparateur multi-trajectoires et les métriques $E(S), D(A), P(A)$ demeurent sous statut `PROPOSITION À VALIDER` (`runtime_enabled = false`) et sont exclus de V1.
- **Persistance B10 :** Aucun profil B11 n'est persisté durablement dans B10 (`memory_write = False`). Les profils sont strictement transitoires en mémoire vive.

---

## 3. Structure de `ContextualCompetenceProfile`

Chaque profil est une structure immuable (`frozen`) comportant les champs suivants :

| Champ | Type | Obligatoire | Règle / Invariant |
|---|---|---|---|
| `evaluation_id` | `str` | Oui | Identifiant technique non vide (rejet si vide ou whitespace). |
| `domain` | `str` | Oui | Domaine d'évaluation non vide (ex. `bank`, `trading`, `ecom`, `gps_defense_aviation`, `linguistics`). |
| `task_ref` | `str` | Oui | Identifiant de la tâche évaluée (alias `task_fingerprint`). Non vide. |
| `conditions` | `tuple[str, ...]` | Oui | Contraintes et conditions opérationnelles (stocké en tuple immuable de chaînes). |
| `target_resources` | `tuple[str, ...]` | Oui | Séquence ordonnée d'organes/outils candidats (alias `target_resource_or_composition`). Au moins 1 ressource. |
| `competence_regime` | `str` | Oui | Valeur parmi `EVIDENCED_COMPETENCE`, `EVIDENCED_INCOMPETENCE`, `UNKNOWN_COMPETENCE`. |
| `reliability_score` | `float \| None` | Oui | Flottant dans `[0.0, 1.0]`, ou impérativement `None` si `UNKNOWN_COMPETENCE`. |
| `confidence_score` | `float` | Oui | Flottant dans `[0.0, 1.0]`. Vaut impérativement `0.0` si `UNKNOWN_COMPETENCE`. |
| `calibration_metric` | `float \| None` | Oui | Flottant dans `[0.0, 1.0]`, ou impérativement `None` si `UNKNOWN_COMPETENCE`. |
| `evidence_refs` | `tuple[str, ...]` | Oui | Références des traces, tests ou validations (stocké en tuple immuable). |
| `unknowns` | `tuple[str, ...]` | Oui | Lacunes explicites. Doit contenir au moins 1 élément si `UNKNOWN_COMPETENCE`. |
| `contradictions` | `tuple[str, ...]` | Non (défaut `()`) | Contradictions relevées lors de l'évaluation (stocké en tuple immuable). |
| `risk_indicators` | `tuple[str, ...]` | Non (défaut `()`) | Signaux de risque identifiés (stocké en tuple immuable). |
| `advisory_notes` | `str` | Non (défaut `""`) | Notes textuelles consultatives. |

---

## 4. Règles d'invariance, de validation et codes d'erreur

1. **`UNKNOWN != INCAPACITY` (Régime `UNKNOWN_COMPETENCE`) :**
   - Si `competence_regime == "UNKNOWN_COMPETENCE"` :
     - `confidence_score` DOIT être exactement `0.0`. Si `confidence_score > 0.0`, lever `ValueError("M42_UNKNOWN_REGIME_ZERO_CONFIDENCE: ...")`.
     - `reliability_score` DOIT être `None`. Si fourni comme float, lever `ValueError("M42_UNKNOWN_REGIME_NO_RELIABILITY: ...")`.
     - `calibration_metric` DOIT être `None`. Si fourni comme float, lever `ValueError("M42_UNKNOWN_REGIME_NO_CALIBRATION: ...")`.
     - `unknowns` DOIT contenir au moins 1 entrée non vide. Si vide, lever `ValueError("M42_UNKNOWN_REGIME_REQUIRES_UNKNOWNS: ...")`.
   - `UNKNOWN_COMPETENCE` ne doit jamais être assimilé à `EVIDENCED_INCOMPETENCE` ni poser un drapeau d'incapacité permanente.
2. **Validation des régimes (`CompetenceRegime`) :**
   - Tout régime autre que les 3 canoniques doit lever `ValueError("M42_INVALID_REGIME: ...")`.
3. **Validation des scores (`reliability_score`, `confidence_score`, `calibration_metric`) :**
   - Tout score fourni qui n'est pas un nombre dans `[0.0, 1.0]` (ex. `< 0.0` ou `> 1.0`, ou booléen `True`/`False`) doit lever `ValueError("M42_INVALID_SCORE: ...")`.
4. **Validation des identifiants et séquences :**
   - `evaluation_id`, `domain`, `task_ref` vides ou non-chaînes lèvent `ValueError("M42_EMPTY_IDENTIFIER: ...")`.
   - `target_resources` vide lève `ValueError("M42_EMPTY_RESOURCES: ...")`.
   - Aucune validation ne rejette un domaine, une tâche ou une ressource au motif d'absence dans une whitelist statique (composition ouverte).
5. **Immutabilité profonde :**
   - L'instance est gelée (`FrozenInstanceError` ou `AttributeError` en cas de modification).
   - Les listes ou conteneurs mutables passés en argument sont obligatoirement copiés sous forme de tuples immuables, garantissant que la mutation ultérieure de l'objet source n'affecte pas le profil.
6. **Effets nuls et absence d'autorité :**
   - `B11_EFFECTS` est un `MappingProxyType` immuable :
     ```python
     B11_EFFECTS = MappingProxyType({
         "memory_write": False,
         "emits_act": False,
         "kernel_mutation": False,
         "decision_authority": "KX108_ONLY",
         "advisory_only": True,
         "b12_selection": False,
     })
     ```
   - Le profil et le module B11 ne possèdent aucune méthode d'action (`authorize()`, `execute()`, `emit_act()`) ni de sélection (`select_organ()`, `decide_admissibility()`).

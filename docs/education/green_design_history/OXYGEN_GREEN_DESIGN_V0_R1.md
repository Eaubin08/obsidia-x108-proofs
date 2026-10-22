# Oxygen — pilote « force » : proposition GREEN V0 (conception seule)

Base : RED V0.3 en 00cc85fc (audit PASS_WITH_NB). **Aucun code GREEN n'est écrit.** Le banc RED, les critères, les baselines et les examens restent inchangés.

## 0. Déclaration de contamination (préalable)

L'auteur de cette proposition a **lu les examens privés** pendant la construction du banc (V0.1 à V0.3). Toute heuristique qu'il choisirait risque d'être ajustée aux examens, consciemment ou non.
Mesures obligatoires avant tout build :
- **M1** — geler cette conception (hash du document) **avant** d'écrire le code ;
- **M2** — aucune liste de mots, aucun indice ni règle spécifique à un sens dans le code : tout signal sémantique doit venir des données d'enseignement au moment de `learn` ;
- **M3** — faire rédiger par un tiers, **après le gel**, un jeu d'examen privé neuf (X1′, X1-far′, X4′) que l'auteur ne lira jamais, et rapporter les résultats sur les deux jeux, séparément ;
- **M4** — un contrôle de banc (déjà vrai) : l'élève ne voit que `student_sandbox/`.

## 1. Architecture candidate : « ExemplarSenseStudent »

Il s'agit d'un apprentissage à base d'exemples, avec des traits contextuels génériques, un vote pondéré et un seuil d'abstention. Le tout tient en Python standard dans le conteneur.

### 1.1 État interne (sérialisé)

```
state = {
  "revision": int,                       # compteur monotone, pas d'horloge
  "exemplars": [ {id, word, sentence, sense, domain, register, source: lesson|exercise|correction|concurrent,
                  features: [str], weight: float, rev_added: int, rev_retired: int|None} ],
  "cues": [ {id, word, cue_ngram, sense, source_id, rev_added, rev_retired} ],   # extraits des corrections
  "senses": { word: {sense: {"count": n, "domains": [...]}} },                 # appris, jamais pré-remplis
  "log": [ {revision, op, ids} ]                                               # historique append-only
}
fichiers : state.json + manifest.json (sha256 de state.json) → StateIntegrityError si divergence
```

Aucun sens n'est connu avant `learn`. L'inventaire F1–F7 est découvert dans les étiquettes des leçons ; il n'est **pas codé**.

### 1.2 Traits génériques (indépendants des sens)

Pour chaque occurrence du mot cible, normalisée (minuscules, accents conservés puis repliés) :
- fenêtre ±3 tokens, avec position relative (`L1=de`, `R1=du`…) ;
- bigrammes et trigrammes contenant la cible (`de force`, `à force de`, `forces de l'`) ;
- forme de surface de la cible (singulier ou pluriel, majuscule) ;
- déterminant ou possessif précédent (`la`, `sa`, `les`, `toutes ses`) ;
- mots pleins de la phrase (sacs de mots), avec un poids plus faible que les traits de position ;
- n-grammes de caractères (3) des mots pleins voisins, pour une généralisation morphologique faible (`policiers` ~ `police`).

Ces extracteurs sont **identiques pour tout mot** (« force », « chemin », « corriger ») : aucun ne nomme un sens.

### 1.3 Apprentissage et réponse

- **`learn(items)`** : chaque item devient un exemplaire avec ses traits. Les statistiques par sens (fréquence des traits) sont mises à jour selon un schéma Naive Bayes avec lissage de Laplace. La révision est incrémentée.
- **`apply_correction(c, ex)`** :
  1. l'exercice corrigé est ajouté comme exemplaire, avec un poids renforcé (×2) ;
  2. le **segment cité entre guillemets** dans le texte de correction (par exemple « de force ») est extrait comme *cue* lié au sens indiqué ;
  3. si la correction contredit un exemplaire existant (même phrase, autre sens), l'ancien est **retiré** (`rev_retired`) et non effacé ; le nouveau prend une nouvelle révision.
- **`answer(word, sentence)`** :
  1. score par sens = log-vraisemblance Naive Bayes, plus un bonus si un *cue* appris est présent dans la phrase, plus un vote k-NN (k = 3, similarité Jaccard pondérée des traits) ;
  2. on normalise en distribution ;
  3. on répond le sens de tête **si** la probabilité dépasse τ (0,5) **et** l'écart avec le second dépasse δ (0,15), **et** si au moins un trait non trivial de la phrase a été vu à l'enseignement ;
  4. **sinon HOLD**. Un mot jamais enseigné donne HOLD, ce qui satisfait le témoin « table » sans règle spéciale.
- **Provenance** : identifiants des exemplaires ou *cues* les plus contributifs **du même sens** (au moins un). Elle est obligatoire si la réponse n'est pas HOLD.

τ et δ sont fixés **avant** le build et réglés uniquement par validation croisée « leave-one-out » sur les données d'enseignement, **jamais** sur V_VALIDATION ni sur les examens.

### 1.4 Interface mémoire

| Méthode | Comportement |
|---|---|
| `retrieve(word, sense=, domain=, provenance=, context=, as_of_revision=)` | exemplaires actifs à la révision demandée, filtrés ; `context` = classement par similarité des traits ; chaque résultat contient `{sense, provenance:[id], revision, content}` |
| `history(word, sense)` | entrées `{revision, op, content}` en ordre de révision, y compris les exemplaires retirés |
| `save(dir)` / `load(dir)` | JSON et manifeste sha256 ; à la lecture, toute divergence lève `StateIntegrityError` |

Il s'agit d'intégrité locale, **pas d'authenticité** : l'invariant B10 reste rouge et hors sujet.

## 2. Fichiers proposés (build futur, s'il est autorisé)

| Fichier | Action |
|---|---|
| `tests/education_pilot/student_sandbox/exemplar_student.py` | **créé** : l'élève (stdlib uniquement) |
| `tests/education_pilot/student_sandbox/features.py` | **créé** : extracteurs génériques |
| `tests/education_pilot/test_exemplar_student_unit.py` | **créé** : tests unitaires côté hôte, **sans examens** (apprentissage croissant sur l'enseignement seul, leave-one-out, sérialisation, intégrité, retrait par contradiction, absence de littéraux de sens dans le code) |
| `docs/education/OXYGEN_GREEN_V0_REPORT.md` | **créé** après la campagne |
| `_bench.py`, `_criteria.py`, `conftest.py`, `test_pilot_force_*.py`, `_pilot_data.py`, examens | **inchangés** ; seul `OXYGEN_PILOT_STUDENT=exemplar_student:ExemplarSenseStudent` change |

**Réutilisation de code existant :**
- **aucun import** de `app/` : le conteneur ne voit pas le dépôt, et `app/semantic` est scellé ;
- réutilisation **conceptuelle** seulement : le repli d'accents déterministe de `app/semantic/lattice/lexicon.py`, réimplémenté en quelques lignes ;
- l'ordre par révision, sans horloge universelle (doctrine) ;
- la séparation candidat / validé de B8, comme vocabulaire.

## 3. Frontière mémoire

| Niveau | Dans ce GREEN |
|---|---|
| Apprentissage expérimental local | **oui** : état JSON dans `/state` temporaire du conteneur |
| Mémoire candidate (B8 CANDIDATE) | non, aucun appel à B8 |
| Connaissance validée | non |
| Promotion autorisée (B8 gate, KX108) | non ; l'autorisation de banc n'est jamais KX108 |
| Continuité éducative d'Oxygen | **non** : sauvegarder un état d'élève n'est pas la naissance d'Oxygen |

B8, B9, B10, Brody, SENS, MMonde, Native Memory, Graphiti, Continuum et les 34 arbres ne sont ni touchés ni importés. AGY n'est pas concerné.
Évolution future, seulement documentée : les traits pourraient devenir un vecteur projeté sur les dimensions d'Obsidia (R^34 / arbres), via un adaptateur séparé, après un RED dédié.

## 4. Protocole exact de test

1. **Gel (M1)** : hash de la conception, τ et δ fixés par leave-one-out sur l'enseignement.
2. **Tests unitaires** côté hôte, sans examens.
3. **Campagne RED inchangée** : `pytest tests/education_pilot` avec `OXYGEN_PILOT_STUDENT=exemplar_student:ExemplarSenseStudent`, séquentielle, un conteneur à la fois. Elle mesure X0 (avant), puis X1, X1-far et X4 (après), X2 (après redémarrage depuis l'état seul) et X3 (après concurrence).
4. **Les 22 contrôles doivent rester verts**, dont la discrimination et la référence parfaite. Sinon on arrête.
5. **Jeu neuf M3** rédigé par un tiers, passé une fois, rapporté à part.
6. **Audit indépendant** : sondes adversariales et inspection du code (aucun littéral de sens, aucune lecture hors `/student` et `/state`).

## 5. Faisabilité prévisible (honnête)

| Critère | Pronostic | Raison |
|---|---|---|
| close_senses, t1_acquisition, t1_abstention | plausible | les traits de position (`de force`, `forces de`, `à force de`, `de toutes ses`) sont présents à l'enseignement |
| t2_retention | plausible si T1 passe | l'état est complet et le comportement déterministe |
| t3_no_forgetting | plausible | « chemin » et « corriger » occupent des espaces de traits disjoints de « force » |
| t3_concurrent | **incertain** | 1 leçon par sens ; « corriger » exige 1,0 contre une baseline de 0,75 (remarque d'audit NB3) |
| far_sentences | **probablement rouge** | X1-far ne partage, **par construction**, aucun mot plein avec l'enseignement ; seuls les traits de fonction (`de force`, pluriel…) peuvent servir. C'est la mesure de généralisation la plus dure. |
| t4_transfer | incertain | il dépend de la présence de constructions apprises dans un domaine nouveau |
| provenance | plausible si T1 passe | — |
| interface (7) | 6 plausibles | la falsification B10 (invariant) reste rouge par conception |

**Aucun test n'est mathématiquement impossible** (référence parfaite validée). En revanche, **far_sentences** et **t3_concurrent** pourraient être *pratiquement* inaccessibles à tout apprenant qui ne dispose que de 14 leçons et sans connaissance lexicale préalable. Cela ne doit **pas** conduire à modifier le protocole. Un échec y serait rapporté comme limite d'apprentissage réelle, et non comme défaut du banc.

## 6. Risques de surapprentissage et contre-mesures

| Risque | Contre-mesure |
|---|---|
| Ajustement aux examens (auteur contaminé) | M1 à M3 ; résultats rapportés séparément sur le jeu neuf |
| Mémorisation des phrases | la baseline « memorizer » est déjà dans le banc ; aucune phrase d'examen n'est enseignée |
| Règles déguisées (« si "newtons" alors F5 ») | test unitaire : aucun identifiant de sens ni mot indice littéral dans le code de l'élève ; revue d'audit |
| Hyperparamètres choisis après coup | τ et δ gelés par leave-one-out sur l'enseignement seul |
| 1 item par sens : succès par chance | rapporté comme campagne technique ; aucune conclusion statistique |
| Cues de correction trop puissants | ils proviennent du texte des corrections, donc des données pédagogiques légitimes ; leur part est mesurée par ablation (avec et sans cues) |

## 7. Critères d'arrêt

- **STOP_LEAK** : un contrôle d'isolation ou de discrimination devient rouge.
- **STOP_CIRCULAR** : le code de l'élève contient un sens, un indice spécifique ou un accès hors `/student` et `/state`.
- **STOP_PROTOCOL** : une modification du banc ou des examens apparaît nécessaire. On ne la fait pas, on rapporte.
- **STOP_OVERFIT** : l'écart entre le jeu d'origine et le jeu neuf M3 dépasse 0,3 en exactitude agrégée. Le résultat sur le jeu d'origine est alors déclaré non probant.
- Budget : 2 itérations de build au plus, chacune suivie d'un audit. Ensuite, rapport tel quel.

## 8. Ce qui pourrait être démontré, au mieux

- Qu'un mécanisme générique, alimenté **uniquement** par des leçons et des corrections, modifie un état local, et que cet état permet de dépasser cinq baselines triviales sur un échantillon technique. Ce n'est pas une compréhension du sens, ni une conclusion statistique, ni la naissance d'Oxygen, ni une mémoire canonique.
- Que la rétention survit à un redémarrage depuis l'état seul, et que l'apprentissage concurrent n'efface pas l'acquis, sur ces items.
- **Pas** que l'élève « comprend » « force » ; **pas** une transférabilité générale.

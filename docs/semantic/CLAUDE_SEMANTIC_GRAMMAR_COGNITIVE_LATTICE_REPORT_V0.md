# Rapport — grammaire sémantique et treillis cognitif (V0)

Branche expérimentale, **non canonique**. Aucun push, aucun merge.
Dépôt de référence Obsidia : **lu seulement**, non modifié. KX108 : non touché.

## 1. Branche et HEAD

- Branche : `exp/semantic-grammar-cognitive-lattice-v0`
- Worktree : `C:\Users\User\Desktop\obsidia-semantic-grammar-claude-v0`
- Point de départ : `8068261 wip(semantics): seed compositional negation prototype`
- HEAD du code avant ce rapport : `4e5073b` (le commit de ce rapport vient juste après)

## 2. Commits (atomiques, non squashés)

| Commit | Message |
|---|---|
| `338bd83` | docs(semantics): map linguistic and memory architecture |
| `e1936c9` | test(semantics): freeze French grammar semantic matrix |
| `b97a92f` | feat(semantics): introduce non-sovereign semantic frame primitives |
| `ebe3239` | feat(semantics): project semantic frame to existing UnifiedInputIR |
| `9388d2a` | fix(semantics): keep reflexive and passive verbs inside modal chains |
| `9eb996d` | fix(semantics): hold infinitive and indirect execution requests |
| `4e5073b` | test(semantics): add causal/reference/modality regressions |
| (suivant) | docs(semantics): report semantic grammar cognitive lattice v0 |

Note : le message de `e1936c9` annonce 66 probes ; la matrice en contient **67**.

## 3. Fichiers modifiés (`git diff --stat 8068261..4e5073b`)

```
app/gates/gates.py                              |   40 +-
app/ir/unified_ir.py                            |  105 +-
app/router/decision.py                          |    2 +
app/semantic/lattice/__init__.py                |   30 +
app/semantic/lattice/french_grammar.py          | 1171 +
app/semantic/lattice/ir_projection.py           |   84 +
app/semantic/lattice/lexicon.py                 |  363 +
app/semantic/lattice/primitives.py              |  184 +
app/semantic/lattice/projections.py             |  147 +
app/semantic/lattice/ud_adapter.py              |  132 +
docs/semantic/FRENCH_LINGUISTIC_BASIS_V0.md     |  162 +
docs/semantic/MEMORY_LANGUAGE_CONVERGENCE_V0.md |  106 +
docs/semantic/SEMANTIC_SOURCE_MAP_V0.md         |   98 +
tests/semantic_grammar_matrix.py                |  573 +
tests/test_semantic_governance_projection.py    |  123 +
tests/test_semantic_grammar_matrix.py           |   85 +
tests/test_semantic_grammar_regressions.py      |  157 +
tests/test_semantic_lattice_primitives.py       |  166 +
18 files changed, 3658 insertions(+), 70 deletions(-)
```

## 4. Architecture existante retrouvée

Détail complet : `docs/semantic/SEMANTIC_SOURCE_MAP_V0.md`. Essentiel :

- **AMD** : `UnifiedInputIR` (sac de mots, M4), gates DENY/HOLD/CLARIFY/ALLOW,
  `decide()`, `TaskKind`, `current_world_evidence` → `evidence_required`,
  `ConstraintGraph`, `ClosureCertificate` (`closure_safe = not (unknowns or
  contradictions)`), `human_needs`. Un `SemanticFrame` **existe déjà**
  (`app/semantic/frame.py`, pour les solveurs) → les nouvelles primitives
  portent d'autres noms pour ne pas le remplacer.
- **Obsidia (référence)** : frontière de non-souveraineté mûre partout
  (`KX108_ONLY`, promotion mémoire manuelle, provenance hachée) ;
  qualification d'inconnues et clôture causale (M3) ; mémoire native =
  **index plat** de 3267 records, sans arêtes ni temps ; 34 arbres et nuage
  21D = axes calculés par regex (M2) ; **graphe, path finder, liens typés,
  timeline, projection Φ = stubs vides (M0)** ; calibration des liens,
  frise chronologique, « mémoire de contraintes » = prompts / notes (M1).
  OS Trad détecte par **sous-chaînes** (`"lance" in "balance"`).
- **Défaut de sécurité du prototype de départ** : « sans attendre, lance le
  script », « sans hésiter, execute le script », « ne t'inquiète pas, lance
  le script… » passaient de HOLD (0b348ab) à **ALLOW → fireworks**
  (8068261) : les regex de négation ignoraient la portée propositionnelle.
- **Lacune antérieure** : « lancer le script », « tu peux lancer le test ? »,
  « il faut lancer les tests »… n'atteignaient jamais HOLD.
- **Incohérence antérieure non corrigée** (voir §14) : `drop the users table`,
  `format the disk`, `rm the build folder`, `authorize the payment` →
  IR `world_action`, gate **ALLOW → fireworks** (déjà vrai en 0b348ab).

## 5. Sources linguistiques externes

Détail : `docs/semantic/FRENCH_LINGUISTIC_BASIS_V0.md`.

- Éduscol, *Grammaire du français — Terminologie grammaticale* (2020) :
  <https://eduscol.education.gouv.fr/sites/default/files/document/guide-la-grammaire-du-francais-terminologie-grammaticale-67998.pdf>
- OQLF / BDL — négation : <https://vitrinelinguistique.oqlf.gouv.qc.ca/23905/la-syntaxe/la-negation-et-la-restriction/generalites-sur-la-negation>
- OQLF / BDL — *ne* explétif : <https://vitrinelinguistique.oqlf.gouv.qc.ca/22467/la-syntaxe/la-negation-et-la-restriction/constructions-avec-un-ne-expletif>
- OQLF / BDL — *ne… que* : <https://vitrinelinguistique.oqlf.gouv.qc.ca/22466/la-syntaxe/la-negation-et-la-restriction/constructions-avec-ne-que>
- Universal Dependencies (français ; relations universelles) :
  <https://universaldependencies.org/fr/index.html>, <https://universaldependencies.org/u/dep/index.html>
- Stanza (Apache-2.0, modèles téléchargés à part, sortie UD) : <https://stanfordnlp.github.io/stanza/>

La page Académie française sur le *ne* explétif n'a pas pu être récupérée
(404) ; la règle est donc sourcée par l'OQLF.

## 6. Matrice grammaticale française

`tests/semantic_grammar_matrix.py` — **67 probes**, chacune avec sémantique
structurée attendue (prédicat, polarité, négateur, confirmation de la
négation, restriction, *ne* explétif, modalité, politesse, statut
pragmatique, temps/aspect, réalisé ?, épistémique, objet résolu, statut de
référence, relations, contraintes présentes/absentes, clôture,
contradiction, besoin de preuve, acte de surface) + attentes de gouvernance.

Couverture : négation totale/partielle (`pas`, `jamais`, `plus`, `rien`,
`aucun`, `ni…ni`), EN `do not`, restriction `ne…que` / `ne…pas que` /
`only`, *ne* explétif (crainte, `avant que`, `éviter que`) vs vraie négation
sous crainte, `sans` / `sans que` (+ cataphore), portée (`sans attendre, …`),
oral sans `ne`, modalité (pouvoir question/inversion/conditionnel, devoir,
falloir, vouloir que, savoir-faire, suggestion), discours rapporté
(ouï-dire + plus-que-parfait), passé, passé récent, futur proche,
progressif, événement évité, croyance, futur + déixis, condition, cause
(`car`, `donc`, `parce que`), séquence (`puis`, `avant de`), alternative,
coordination nominale, référence (`fais le`, `fais-le`, anaphore, `ça`,
`celui-ci`), monde courant (`maman est là ?`, `il pleut dehors ?`),
orthographe sans accents, ASR sans apostrophe, disfluences, contrôles.

Résultat : **67/67** (+ 1 test de largeur). 23 tests de régression supplémentaires
sur des phrases **hors matrice** (`tests/test_semantic_grammar_regressions.py`).

## 7. Représentation proposée (implémentée en V0)

```
UtteranceFrame (immuable, raw conservé)
 ├─ units: PredicateUnit        un objet cognitif = un prédicat dans l'énoncé
 │    predicate canonique (EXECUTE, PREPARE, …) · lemma · surface · span dans le brut
 │    verb_form · polarity · negator · negation_confirmed · ne_omitted · ne_expletive
 │    restriction · modality · politeness · pragmatic · tense_aspect · realized
 │    epistemic · subject · objects(Argument: head, kind, reference, antecedent)
 │    embedded_under · confidence · provenance
 ├─ relations: LatticeRelation(kind, source, target, confidence, evidence)
 │    CONTRASTS PRECEDES COORDINATES ALTERNATIVE CAUSES CONDITIONS FORBIDS
 │    REPORTS FEARS PREVENTS BELIEVES WANTS EMBEDS REFERS_TO
 ├─ constraints (NO_X(obj), ONLY_X(obj), PREVENT_X(obj))
 ├─ unresolved_references · presupposed_referents · deixis · ambiguities
 ├─ contradictions (requis ∧ interdit sur le même référent) · evidence_needs
 ├─ disfluencies · orthography_flags · boundary (KX108_ONLY, emits_act=False…)
 └─ closure = units ∧ ¬unresolved ∧ ¬contradictions   (la preuve ne bloque pas le sens)
```

Statuts pragmatiques : `REQUESTED`, `FORBIDDEN`, `INDIRECT_REQUEST`, `ASKED`,
`ASSERTED`, `REPORTED`, `FEARED`, `PREVENTED`, `BELIEVED`, `HYPOTHETICAL`,
`EMBEDDED` (infinitif régi par un mot non reconnu), `NOT_REQUIRED`.

**Multidimensionnalité** : `ProjectionAxis` (GRAMMATICAL, SEMANTIC,
TEMPORAL, CAUSAL, EPISTEMIC, PRAGMATIC, PROVENANCE, WORLD, AUTHORITY,
CONFIDENCE) — chaque projection est une **vue calculée** sur le même objet
(`project`, `projections_of`), jamais une copie.
**Types de connexion** : `connection(frame, a, b)` renvoie
`DIRECT_RELATION`, `TEMPORAL_RELATION`, `PROVENANCE_RELATION`,
`SHARED_CAUSE`, `SHARED_ANCESTOR`, `INDIRECT_PATH` (avec le chemin),
`SEMANTIC_SIMILARITY` (explicitement pas une relation) ou
`NO_PROVEN_CONNECTION` — l'absence est représentable. BFS borné (6).

**Frontière analyseur externe** : `ud_adapter.frame_from_ud()` accepte des
tokens UD (CoNLL-U) de n'importe quel producteur ; fusion **fail-closed**
(une action est niée seulement si toutes les sources la nient ; elle est
requise si une seule la requiert). Stanza n'est ni installé ni importé.

`UnifiedInputIR` reste le **résumé gouvernable** : il gagne une clé
descriptive `semantics` (schéma `OBSIDIA_UTTERANCE_FRAME_SUMMARY_V0`) ; aucun
contrat public renommé.

## 8. Relation aux arbres mémoire / architecture temporelle

Détail : `docs/semantic/MEMORY_LANGUAGE_CONVERGENCE_V0.md`.

- L'hypothèse « multivers cognitif » est **dans les sources d'origine**
  (Nœud Continuum à appartenance simultanée à plusieurs arbres ; calibration
  des liens CAUSAL / STRUCTUREL / ANALOGIQUE / TEMPOREL / HYPOTHÉTIQUE ;
  « un lien analogique n'est pas un lien causal ») mais la couche
  relationnelle correspondante est **vide dans le code**.
- **Primitives partageables** : nœud identifié + span/provenance ; arête
  typée avec force/confiance ; contradiction ; référence/inconnue non résolue
  (dette de clôture) ; type de connexion ; chemin borné ; projections-vues.
- **À ne pas fusionner** : le temps (énonciatif ≠ chronologie des
  événements ≠ temps d'acquisition des connaissances) ; la causalité
  (énoncée = assertion d'un locuteur ≠ procédurale `causal_chain.py` ≠
  physique) ; la consolidation (clôture automatique d'un énoncé ≠ promotion
  mémoire humaine) ; l'autorité (toujours externe).
- Conclusion : langage, mémoire et causalité **peuvent** être des interfaces
  sur un substrat commun de nœuds typés multi-projetés, **à condition** que
  chaque interface garde ses propres coordonnées temporelles et
  épistémiques. Démontré ici pour le langage seulement : la mémoire n'a
  encore ni arêtes ni temps.

## 9. Ce qui a été implémenté

1. Package `app/semantic/lattice/` (stdlib, déterministe, sans réseau, sans
   modèle) : primitives, lexique fermé généré par conjugaison (pas un
   dictionnaire de phrases), grammaire à portée propositionnelle, projections,
   requêtes de connexion, projection vers l'IR, adaptateur UD.
2. `build_ir` : les regex du prototype sont remplacées par le frame.
   Relâchement du HOLD d'exécution **uniquement** si PREPARE requis +
   NO_EXECUTE confirmé à l'écrit + aucune action du monde requise + aucune
   contradiction. Échec du parseur ⇒ rien n'est relâché.
3. Défaut 1 (PREPARE+NO_EXECUTE → fireworks) : référent non identifié
   (pronom sans antécédent ou défini présupposé) ⇒ `missing: referent` ⇒
   CLARIFY ⇒ `clarification_needed` (plus de modèle distant).
4. Défaut 2 (télémétrie) : la gate étiquette le verbe **positivement requis**
   (`matched: run`), sans jamais retirer un HOLD.
5. Défauts 3-4 (regex / dictionnaire) : analyse compositionnelle par
   proposition ; aucune liste de phrases.
6. Régression de portée du prototype corrigée (HOLD restauré).
7. Resserrement : requêtes d'exécution à l'infinitif / indirectes ⇒ HOLD
   (commit isolé `9eb996d`, révocable).

## 10. Délibérément NON implémenté

- Aucun relâchement de HOLD pour les mentions rapportées / craintes /
  évitées / supposées / pronominales (« on m'a dit qu'il avait lancé »,
  « je crains qu'il ne lance », « le serveur se lance tout seul ») : le frame
  les **décrit** comme non-requêtes, la gouvernance reste **fail-closed**.
  Tout relâchement doit être une décision humaine.
- Pas de négation orale / ASR qui relâche une gate.
- Pas de Stanza, pas de dépendance d'analyseur, pas d'ASR, pas de phonétique
  (conception seulement, §11 du document linguistique).
- Pas de branchement mémoire, pas d'écriture mémoire, pas de supersession.
- Pas de référence inter-tours (dialogue) ; pas d'accord genre/nombre pour
  l'anaphore ; relatives sans reconstruction de la trace (« le script que tu
  as lancé »).
- `TaskKind`, topic router, `app/semantic/frame.py` : non modifiés.
- L'incohérence `rm/format/drop/authorize` (§14) : non corrigée.
- Anglais : couverture minimale volontaire.

## 11. Comptes de tests

| Point | Résultat |
|---|---|
| Départ (8068261) | 1680 passed, 3 skipped, 20 subtests passed |
| Après `ebe3239` (projection IR) | 1806 passed, 3 skipped, 8 xfailed, 20 subtests |
| Final (`4e5073b`) | **1837 passed, 3 skipped, 20 subtests passed** (~66 s) |

Nouveaux (157) : matrice 68, primitives 11, gouvernance 55, régressions 23.

## 12. Régressions

- Aucun test préexistant n'a été modifié ni cassé.
- Rejeu de **1306 prompts connus** (benchmarks, cas dynamiques, chaînes des
  tests, matrice) contre 0b348ab : **15 changements de route, tous sur des
  phrases de la matrice, tous voulus** (5 PREPARE+NO_EXECUTE HOLD →
  CLARIFY ; 1 `sans que … prépare` ALLOW → CLARIFY ; 9 requêtes indirectes /
  infinitives / `pousse` ALLOW|CLARIFY → HOLD). **Aucun prompt de benchmark
  ni de Track ne change de route.**
- Contre le prototype 8068261 : en plus, les 3 cas de la régression de portée
  reviennent à HOLD, et 5 phrases sans PREPARE (`do not execute it`,
  `don't run the tests`, `je ne lance pas que les tests`…) reviennent au
  HOLD fail-closed qu'elles avaient en 0b348ab.
- Un faux positif détecté par ce rejeu avant commit (« Le code du template
  doit s'exécuter… » → HOLD) a été corrigé (`9388d2a`).
- Courant-monde : `maman est là ?`, `est-ce qu'il pleut dehors ?` →
  `evidence_required` inchangé. HOLD direct (`execute le script`,
  `vas y execute`) inchangé.

## 13. Questions non résolues

1. Faut-il un jour relâcher HOLD pour une mention **non requise**
   (rapportée, crainte, évitée, pronominale, assertée au passé) ? Le frame le
   permettrait ; la doctrine actuelle dit non.
2. « prépare le script mais ne l'exécute pas » : CLARIFY sur le référent
   présupposé est-il la bonne route, ou faut-il une route « préparation
   locale sans exécution » (quelle couche ? `terminal` ? `plan` ?) ?
3. `pousser` est traité comme PUSH (monde) : acceptable dans un contexte dev,
   ambigu hors contexte.
4. « tu lances le script ? » est traité fail-closed comme requête indirecte
   (ambiguïté enregistrée) : à valider.
5. « le script doit être lancé » (obligation passive, sujet 3ᵉ pers.) :
   ASSERTED dans le frame (HOLD tout de même via le mot-clé hérité).
6. Représenter deux temps distincts (événement / acquisition) dans la
   mémoire : quel schéma ?

## 14. Recommandations pour la revue humaine

1. **Priorité sécurité** : `_ACTION_WORDS` contient `rm`, `format`, `drop`,
   `authorize` absents de `HOLD_KEYWORDS` ⇒ IR `world_action` mais gate
   ALLOW → fireworks (préexistant). Décider : aligner les deux listes ou
   faire tenir HOLD à toute IR `act_request`.
2. Relire `9eb996d` (resserrement) séparément : il est purement additif mais
   change 9 routes de probes.
3. Relire la règle de relâchement (`ir_projection.execution_hold_relaxable`)
   : c'est le **seul** endroit où la compréhension retire un HOLD.
4. Valider la doctrine « négation orale = comprise mais jamais relâchante ».
5. Ne pas brancher la mémoire avant d'avoir spécifié les deux temps et la
   supersession.

## 15. Prochaine étape minimale exacte

Ajouter **un seul** test de propriété fail-closed sur tout le corpus :
pour chaque prompt des 1306 connus, `verdict(HEAD) == HOLD` si
`verdict(0b348ab) == HOLD`, sauf pour une liste blanche explicite de probes
PREPARE+NO_EXECUTE revue par un humain — afin que tout futur relâchement soit
visible et déclaré, plutôt que découvert.

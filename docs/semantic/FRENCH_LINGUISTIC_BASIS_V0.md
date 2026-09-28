# Base linguistique du français pour l'analyse sémantique (V0)

But : fixer les **faits grammaticaux établis** qui contraignent la
représentation. Aucune règle ci-dessous n'est inventée pour le besoin du
routeur ; chaque décision de modélisation renvoie à une description de
référence.

## Sources de référence consultées

- Ministère de l'Éducation nationale / Éduscol, *Grammaire du français — Terminologie grammaticale* (juillet 2020) :
  <https://eduscol.education.gouv.fr/sites/default/files/document/guide-la-grammaire-du-francais-terminologie-grammaticale-67998.pdf>
- OQLF, Banque de dépannage linguistique — « Apprivoiser la négation » :
  <https://vitrinelinguistique.oqlf.gouv.qc.ca/23905/la-syntaxe/la-negation-et-la-restriction/generalites-sur-la-negation>
- OQLF — « Constructions avec un *ne* explétif » :
  <https://vitrinelinguistique.oqlf.gouv.qc.ca/22467/la-syntaxe/la-negation-et-la-restriction/constructions-avec-un-ne-expletif>
- OQLF — « *Ne… que* + *seulement* » (restriction) :
  <https://vitrinelinguistique.oqlf.gouv.qc.ca/22466/la-syntaxe/la-negation-et-la-restriction/constructions-avec-ne-que>
- Universal Dependencies — documentation française : <https://universaldependencies.org/fr/index.html>
- Universal Dependencies — relations universelles : <https://universaldependencies.org/u/dep/index.html>
- Stanford Stanza (Apache-2.0, Python, modèles téléchargés séparément, sortie UD) : <https://stanfordnlp.github.io/stanza/>

## 1. Lexique et morphologie

| Notion | Fait établi | Conséquence de modélisation |
|---|---|---|
| Lemme | Forme canonique (infinitif pour le verbe) | `PredicateUnit.lemma` ; prédicat canonique **indépendant de la langue** (`lancer`, `exécuter`, `run` → `EXECUTE`) |
| Catégorie | nom, verbe, déterminant, pronom, adverbe, préposition, conjonction | Le lexique ne connaît que les verbes utiles + mots grammaticaux fermés ; tout le reste = matériau nominal |
| Personne / nombre / genre | portés par le verbe fini (UD `Person`, `Number`) et le nominal | Personne utilisée pour distinguer impératif (sans sujet) / déclaratif (sujet) |
| Mode | indicatif, subjonctif, conditionnel, impératif ; formes non finies : infinitif, participes (UD `Mood`, `VerbForm`) | `verb_form` ∈ {FINITE, IMPERATIVE, INFINITIVE, PARTICIPLE, GERUND} ; `mood` quand identifiable |
| Temps | présent, imparfait, passé composé, plus-que-parfait, futur, conditionnel | `tense_aspect` |
| Ambiguïté morphologique | `lance` = indicatif 1/3 sg, impératif 2 sg, subjonctif ; `exécute`/`exécuté` ne diffèrent que par l'accent | Toutes les analyses possibles sont conservées ; la **syntaxe** (sujet, auxiliaire) tranche. Sans accents, la forme est marquée `orthography_ambiguous` |

## 2. Syntaxe

- Sujet (`nsubj`), objet direct (`obj`), objet indirect (`iobj`), obliques (`obl`),
  complément propositionnel (`ccomp`), complément ouvert d'infinitif (`xcomp`,
  ex. modal + infinitif), subordonnée circonstancielle (`advcl`), relative
  (`acl:relcl`), coordination (`cc` + `conj`), marqueur de subordination (`mark`).
- **Unité d'analyse = la proposition** (un prédicat + ses dépendants). C'est la
  frontière de portée de la négation, de la modalité et du statut pragmatique.
- Coordination de propositions (« mais », « puis », « et », « ou », « donc »)
  ≠ coordination de syntagmes nominaux (« le script et les tests ») :
  une « proposition » sans prédicat est réattachée à la précédente.
- Relative en « que/qui » après un nom : prédicat **descriptif**, jamais une requête.

## 3. Négation et restriction (OQLF)

| Forme | Statut | Modélisation |
|---|---|---|
| `ne … pas` (négation totale) | négation | `polarity=NEGATIVE`, `negator=pas` |
| `ne … jamais / plus / rien / personne / aucun / nul / guère / point` (négation partielle) | négation | idem, `negator` conservé ; `rien`/`aucun` = quantification nulle sur l'objet (`NO_X(*)`) |
| `ni … ni` | négation coordonnée | un prédicat nié, objets coordonnés multiples |
| Omission orale de `ne` (« lance pas le script ») | négation en langue parlée ; `ne` « tend à disparaître à l'oral » (OQLF) | `polarity=NEGATIVE`, `ne_omitted=True`, **négation non confirmée** (confiance réduite) : ne relâche aucune gate |
| `sans` + infinitif | négation de l'infinitif régi — **portée limitée à cet infinitif** | infinitif `NEGATIVE`, pragmatique `FORBIDDEN` ; relation `FORBIDS(principal → nié)` |
| `sans que` + subjonctif | négation de la subordonnée ; un `ne` y est **fautif** (OQLF) | idem, subordonnée |
| `ne … que` | **restriction**, pas négation (OQLF « Ne… que ») | `polarity=POSITIVE`, `restriction=ONLY` ; jamais de contrainte `NO_X` |
| `ne … pas que` | négation de la restriction (« pas seulement ») | `polarity=POSITIVE`, `restriction=NOT_ONLY` |
| `ne` explétif | après verbes de crainte / `éviter` / `empêcher`, `avant que`, `à moins que`, comparatifs ; « n'est pas indispensable au sens » (OQLF) — sans valeur négative | `ne_expletive=True`, `polarity=POSITIVE` |
| Crainte + `ne … pas` (« je crains qu'il ne vienne pas ») | vraie négation (opposition latine *timeo ne veniat* / *ne non veniat*) | `polarity=NEGATIVE`, `ne_expletive=False` |
| Portée | la négation porte sur le verbe de sa proposition ; avec modal (« tu ne dois pas lancer ») elle porte sur le modal ⇒ interdiction | règle implémentée ; une virgule / un connecteur ferme la portée |

## 4. Modalité

| Verbe | Valeurs | Traitement |
|---|---|---|
| pouvoir | capacité / permission / possibilité ; « tu peux … ? » = requête indirecte conventionnelle | `ABILITY_OR_PERMISSION` + ambiguïté explicite ; à la 2ᵉ personne en question ⇒ `INDIRECT_REQUEST` |
| devoir | obligation / probabilité | `OBLIGATION` ; 2ᵉ personne ⇒ `REQUESTED` |
| falloir | obligation impersonnelle | `OBLIGATION` ⇒ `REQUESTED` |
| vouloir | désir ; « je voudrais que tu … » = requête polie | `DESIRE` ; « vouloir que + 2ᵉ pers. » ⇒ subordonnée `REQUESTED` |
| savoir + infinitif | savoir-faire | `KNOW_HOW`, **assertion**, pas une requête |
| conditionnel de politesse | atténuation | `politeness=True`, n'altère pas la force |

## 5. Pragmatique (actes de langage)

`statement → ASSERTED`, `question → ASKED`, `command → REQUESTED`,
`prohibition → FORBIDDEN`, `indirect request → INDIRECT_REQUEST`,
`reported speech → REPORTED`, `hypothesis/condition → HYPOTHETICAL`,
`embedded fear → FEARED`, `prevention → PREVENTED`, `belief → BELIEVED`,
`savoir-faire/capacité assertée → ASSERTED`.
Deux statuts techniques complètent la liste : `EMBEDDED` (infinitif régi
par un mot non reconnu, « essaie de lancer » — traité comme requête pour
la gouvernance, fail-closed) et `NOT_REQUIRED` (« pas besoin de confirmer »).
Le statut pragmatique est **par prédicat**, pas par phrase : « prépare le
script mais ne l'exécute pas » contient une requête **et** une interdiction.

## 6. Référence

- Clitiques objets `le/la/les/l'/lui/en/y`, démonstratifs `ça/cela/ceci/celui-ci`,
  anglais `it/this/that/them`.
- Anaphore résolue **dans l'énoncé** seulement (antécédent nominal précédent) →
  relation `REFERS_TO` ; cataphore tolérée si aucun antécédent précédent.
- Sinon : **référence non résolue** ⇒ bloque la clôture (« fais le »).
- Syntagme défini sans antécédent (« le script ») : **présupposition**
  (dépend du contexte de dialogue) — signalée, ne bloque pas la clôture de sens.
- Déictiques `ici, là, maintenant, aujourd'hui, demain, hier` : ancrés sur la
  situation d'énonciation ⇒ nécessitent le contexte / le monde.

## 7. Temps et aspect

| Forme | Valeur | `realized` |
|---|---|---|
| passé composé (`a lancé`) | passé accompli | True (selon la source) |
| plus-que-parfait (`avait lancé`) | antériorité | True |
| `vient de` + inf | passé récent | True |
| `va` + inf (avec sujet) | futur proche | None |
| futur simple | futur | None |
| `est en train de` + inf | progressif | en cours |
| `a failli` + inf | **événement évité** | **False** |
| impératif / infinitif injonctif | non réalisé, prospectif | None |

## 8. Épistémique

`ASSERTED` (dit par le locuteur) · `HEARSAY` (« on m'a dit ») · `BELIEF`
(« je pense que ») · `POSSIBLE` (crainte) · `HYPOTHETICAL` (si) ·
`COUNTERFACTUAL` (a failli) · `UNKNOWN` (question ouverte) ·
`NOT_APPLICABLE` (directives : pas de valeur de vérité).
**Aucune assertion n'est une observation** : l'observation relève de la preuve
(`current_world_evidence`), pas de la compréhension.

## 9. Connecteurs

| Connecteur | Relation |
|---|---|
| mais / but | `CONTRASTS` |
| puis, ensuite, then, avant de, before | `PRECEDES` (ordre) ; après / after : inverse |
| et / and | `COORDINATES` |
| ou / or | `ALTERNATIVE` |
| donc, alors (après un fait), so | `CAUSES(prémisse → conséquence)` |
| car, parce que, puisque, because | `CAUSES(raison → principal)` |
| si … (alors) / if | `CONDITIONS(condition → conséquent)` |
| dire que | `REPORTS` ; craindre que : `FEARS` ; éviter/empêcher que : `PREVENTS` ; penser/croire que : `BELIEVES` ; vouloir/falloir que : `WANTS` |

## 10. Français parlé réel

Omission de `ne` ; élisions sans apostrophe (« l execute ») ; ponctuation
absente ; disfluences (`euh`, `bah`, répétitions « mais mais ») ; formes
anglicisées (`pusher`). Politique : **tolérer pour comprendre, jamais pour
relâcher une gate** (une négation orale non confirmée ne lève pas un HOLD).

## 11. Interface phonétique / ASR — conception seulement

Rien n'est implémenté. Frontière proposée :

```
signal → ASR → N hypothèses orthographiques (treillis) {texte, score, spans}
      → une UtteranceFrame par hypothèse (analyse déterministe)
      → fusion : un prédicat d'action n'est « nié » que si TOUTES les
        hypothèses retenues le nient (fail-closed) ; une requête d'action
        présente dans UNE hypothèse suffit à exiger la gate.
```

Phénomènes à représenter comme **alternatives**, jamais comme correction
silencieuse : liaison (« les_zamis »), élision (« l'a » / « la »), chute du
schwa (« j'te l'lance »), h muet / aspiré, homophones (`lance` / `l'anse`,
`a` / `à`, `ces` / `ses`, `exécuté` / `exécuter` / `exécutez`), `ne` inaudible
(« on n'a » / « on a »). Le texte brut et chaque hypothèse sont conservés.

## 12. Orthographe

L'orthographe **informe** l'analyse (accent → participe vs présent ;
apostrophe → élision ; `?` → interrogation) mais n'est **jamais une autorité** :
- le texte brut est toujours conservé (`raw`) et chaque unité garde son `span`
  dans le brut ;
- l'absence d'accent élargit l'ensemble des analyses au lieu d'en choisir une ;
- une ponctuation absente réduit la confiance de segmentation.

# M42 B11 Compétence & Calibration — Doctrine V1

## 1. Statut et autorité du document

- **Chapitre :** M42 — B11 Compétence et Calibration.
- **Couche :** Cognition / Pré-forge / Gouvernance périphérique.
- **Phase :** Cadrage doctrinal canonique (`DOCTRINE_AUTHORED_AWAITING_OWNER_REVIEW`).
- **Base vérifiée :** 
  - `COGNITIVE_FOUNDATION_V1=SEALED`, `FOUNDATION_REOPEN=NO` ;
  - M32 à M40/B10 CLOS et certifiés ;
  - M41 (Modèle du Monde V1) cadré et testé au runtime minimal ;
  - M17 / R10 / Corpus linguistique FR/EN clôturés et reproductibles (HEAD `9113300d`).
- **Hiérarchie normative :**
  `FOUNDATION_SEAL > CURRENT_CANONICAL_ARCHITECTURE > OWNER_DECISIONS / ORIENTATIONS_CONFIRMEES > THIS_DOCTRINE > EXTERNAL_EXPERIMENTAL > HISTORICAL`
- **Statut opérationnel :** Aucun code runtime (`.py` dans `app/cognition/b11`), aucun test unitaire, aucun schéma exécutable, aucun commit Git et aucun push ne sont effectués dans cette phase. Tout nom de structure ci-dessous relève strictement du vocabulaire doctrinal.

---

## 2. Origine, sources et classes de preuves

Chaque énoncé de cette doctrine est rattaché à une classe de preuve :

| Classe | Définition |
|---|---|
| `CURRENT_CANONICAL` | Présent sur cette branche, testé ou partie intégrante du scellage canonique. |
| `OWNER_DECISION` | Décision ou directive explicite de l'architecte / propriétaire du système. |
| `ORIENTATION_CONFIRMEE` | Orientation architecturale formellement validée par l'architecte pour M42. |
| `ORIENTATION_EN_ATTENTE` | Orientation architecturale nécessitant une consolidation ou un contrat dédié avant validation. |
| `DIRECT_SOURCE` | Contrat ou document de référence lu directement dans le périmètre du dépôt. |
| `INFERENCE` | Déduction logique rigoureuse tirée des invariants établis. |
| `DEFERRED` | Point expressément différé à une étape ultérieure (ex. M43/B12 ou runtime B11). |

### Sources canoniques consultées

1. **Doctrine Biologique M34** (`docs/architecture/M34_BIOLOGY_PATTERNS_DOCTRINE_V1.md`) :
   - `B11 owns competence and calibration; B12 owns capability, admissibility and selection.` (`CURRENT_CANONICAL`)
2. **Doctrine d'Analogie Trans-Domaines M36** (`docs/architecture/M36_CROSS_DOMAIN_ANALOGY_DOCTRINE_V1.md`) :
   - `COMPETENCE_TRANSFER_OWNER=B11_AND_EDUCATION` (`CURRENT_CANONICAL`)
3. **Prévol du Cadre Thermodynamique V0** (`docs/thermodynamic_framework/THERMODYNAMIC_FRAMEWORK_PREFLIGHT_V0.md`) :
   - `decision_authority = KX108_ONLY`, `thermodynamic_authority = NONE`, `runtime_enabled = false`.
   - Évalue la pression, la dissipation, l'instabilité, les coûts irréversibles, la friction et la survie de trajectoire. (`CURRENT_CANONICAL`)
4. **Contrat de Frontière Path Compute V0** (`path_compute_v0/boundary.py`) :
   - `decision_authority = "KX108_ONLY"`, `path_compute_authority = "NONE"`, `advisory_only = True`, `path_compute=False`. (`CURRENT_CANONICAL`)
5. **Implémentation Périphérique Energy-Thermo** (`periphery/energy_thermo.py`, `periphery/control_plane.py`) :
   - `run_energy_thermo()` produit un `PeripheralSignalPacket` avec `extra_metrics` (`thermo_debt`, `energy_efficiency`, `sigma_truth_mismatch`), `risk_flags`, `contradictions` et `recommended_gate` (`HOLD`, `BLOCK_CANDIDATE`). (`CURRENT_CANONICAL`)
6. **Pont Périphérique-Sigma** (`periphery/sigma_bridge.py`) :
   - `_merge_periphery_into_aggregate()` injecte les métriques et risques périphériques dans `DomainAggregate` pour consommation par `GuardX108`. (`CURRENT_CANONICAL`)
7. **Contrats et Garde Sigma** (`sigma/contracts.py`, `sigma/guard.py`) :
   - `DomainAggregate`, `AgentVote`, `UniversalBase`, `Severity`, `X108Gate` (`ALLOW`, `HOLD`, `BLOCK`).
   - `raw_engine.consensus` possède `authority = PROOF_SURFACE_ONLY` et `does_not_override_x108_gate = True`.
   - `GuardX108.decide()` calcule la porte déterministe `x108_gate`. (`CURRENT_CANONICAL`)
8. **Cycle d'Exécution Gouvernée et Persistance** (`scripts/obsidia_governed_runtime_cycle_v1.py`, `scripts/obsidia_kx108_decision_store.py`) :
   - `decision_authority = KX108_ONLY`. L'accès au rail d'exécution requiert `ALLOW` + ticket OS3 valide + vérification de rejeu (replay PASS) + scellage cryptographique. (`CURRENT_CANONICAL`)
9. **Glossaire Intégral Audité X-108** (`docs/glossary/OBSIDIA_X108_GLOSSAIRE_INTEGRAL_AUDITE.md`) :
   - Invariants F8/P9 : Path Compute et Thermo sont purement consultatifs (*advisory only*).
   - Invariant : `COMPETENCE != AUTHORITY`, `CONFIDENCE != AUTHORITY`. (`CURRENT_CANONICAL`)

---

## 3. Objet canonique de B11 — Compétence contextualisée

### 3.1 Définition de la compétence dans Obsidia

Dans l'architecture cognitive d'Obsidia, la compétence n'est ni un titre statique, ni un droit d'agir, ni un catalogue rigide de capacités pré-autorisées.

> **Principe fondamental (Confirmé par l'architecte) :** La compétence selon B11 est une **évaluation contextualisée et probabiliste de l'aptitude d'un ou plusieurs organes, outils ou agents à accomplir une tâche spécifique sous des conditions opérationnelles données, étayée par des preuves vérifiables.** (`OWNER_DECISION`, `ORIENTATION_CONFIRMEE`)

La compétence n'est pas :
- Une liste fermée de fonctions autorisées (*whitelist* statique) ;
- Un plafond général, universel ou permanent d'incapacité ;
- Une autorisation d'exécution ou une délégation d'autorité ;
- Une vérité ontologique absolue (`COMPETENCE != TRUTH`).

### 3.2 L'unité d'évaluation contextualisée

Toute évaluation produite par B11 doit obligatoirement caractériser le tuple contextuel suivant :

$$\mathcal{E}_{B11} = \langle \text{Domain}, \text{TaskRef}, \text{Conditions}, \text{CandidateResources}, \text{EvidenceRefs}, \text{Reliability}, \text{Calibration}, \text{Unknowns} \rangle$$

1. **Domaine (`Domain`) :** Contexte d'application (ex. bancaire, trading, e-commerce, spatial, linguistique, méta-outillage).
2. **Tâche (`TaskRef`) :** Objectif technique ou fonctionnel précis, formalisé sans ambiguïté.
3. **Conditions opérationnelles (`Conditions`) :** Contraintes environnementales, budget temps/ressources, bruit d'observation, niveau de criticité attendu.
4. **Ressources candidates (`CandidateResources`) :** Unité simple (un agent, un outil, un modèle) ou composition d'organes (ex. Brody + Dictionnaire + Validateur SENS).
5. **Références de preuves (`EvidenceRefs`) :** Traces d'exécutions passées, certifications de tests, validations formelles Lean/TLA+, journaux audités.
6. **Fiabilité estimée (`Reliability`) :** Score d'exactitude ou de complétude attendu sur la base des preuves.
7. **Score de calibration (`Calibration`) :** Mesure de la justesse de l'estimation de confiance (absence de sur-confiance ou de sous-confiance).
8. **Inconnues explicites (`Unknowns`) :** Lacunes d'information identifiées dans le contexte opérationnel.

---

## 4. Traitement des preuves, des incertitudes et des inconnues

### 4.1 Loi fondamentale : Absence de preuve n'est pas incapacité

Conformément à la loi constitutive M32 (`UNKNOWN != FALSE`) et à la confirmation de l'architecte :

$$\text{ABSENCE\_OF\_EVIDENCE} \ne \text{INCAPACITY}$$

L'absence d'historique ou de preuve directe pour une tâche donnée ne doit jamais être traduite par un verdict d'inaptitude globale ou un blocage rédhibitoire permanent. (`OWNER_DECISION`, `ORIENTATION_CONFIRMEE`)

### 4.2 Typologie des états épistémiques de compétence

B11 classe toute évaluation d'aptitude selon trois régimes épistémiques distincts :

1. **Compétence étayée (`EVIDENCED_COMPETENCE`) :** Des preuves empiriques, formelles ou historiques suffisantes démontrent la viabilité de la ressource dans ce contexte.
2. **Incompétence caractérisée / Limite prouvée (`EVIDENCED_INCOMPETENCE`) :** Des preuves positives établissent qu'une violation d'invariant, une contradiction ou une rupture de contrat survient pour cette tâche ou ces conditions.
3. **Inconnue d'aptitude (`UNKNOWN_COMPETENCE`) :** Le volume ou la qualité des preuves est insuffisant pour trancher. 
   - **Règle de traitement (Confirmée par l'architecte) :** `UNKNOWN_COMPETENCE` ne signifie pas incapacité générale ou permanente ; l'inconnue est explicitement qualifiée comme signal d'évaluation, d'exploration, d'expérimentation en bac à sable ou d'escalade cognitive. Cela n'autorise toutefois pas automatiquement une action concrète : `GuardX108` peut produire `HOLD` ou `BLOCK` pour l'action courante selon les preuves, risques et inconnues présents, sans transformer ce verdict circonstanciel en jugement permanent sur la capacité.

---

## 5. Calibration et limites d'interprétation

### 5.1 Définition et mesure de la calibration

La calibration mesure la concordance statistique et logique entre la confiance déclarée par un composant cognitif et son taux de succès réel observé sur un échantillon significatif :

$$\text{CalibrationError} = \mathbb{E}\left[ \left| \text{Confidence} - \mathbb{I}(\text{Success}) \right| \right]$$

- Un organe **sur-confiant** (confiance élevée, échecs fréquents) reçoit un score de calibration dégradé qui alerte B12 et Sigma.
- Un organe **sous-confiant** (confiance faible, succès systématiques) est identifié pour recalibration sans pénaliser artificiellement son éligibilité.
- La dérive de calibration (*calibration drift*) est mesurée au fil du temps par confrontation aux journaux d'audit et aux validations post-exécution.

### 5.2 Limites d'interprétation strictes

1. **`CONFIDENCE != AUTHORITY` :** Une confiance maximale ($1.0$), même parfaitement calibrée, ne confère aucun droit d'agir, ne contourne aucun garde et n'émancipe d'aucune vérification formelle.
2. **`CALIBRATION != PERMISSION` :** Un système parfaitement calibré n'est pas pour autant autorisé à exécuter une action critique non approuvée.
3. **`CALIBRATION_MEASURE_ONLY` :** B11 mesure et rapporte la calibration ; il ne modifie pas de force les poids du noyau ni l'état de la mémoire B10 sans protocole dédié.

---

## 6. Sorties de B11 et consommation par B12

### 6.1 Ce que B11 produit (`ContextualCompetenceProfile`)

B11 produit exclusivement des profils d'aptitude transitoires en mémoire vive (`transient`), structurés selon le modèle abstrait suivant :

```
ContextualCompetenceProfile:
  evaluation_id: UUID
  domain: Domain
  task_fingerprint: str
  target_resource_or_composition: List[ResourceRef]
  competence_regime: EVIDENCED_COMPETENCE | EVIDENCED_INCOMPETENCE | UNKNOWN_COMPETENCE
  reliability_score: float [0.0 .. 1.0]
  confidence_score: float [0.0 .. 1.0]
  calibration_metric: float [0.0 .. 1.0]
  evidence_refs: List[EvidenceRef]
  unknowns: List[str]
  contradictions: List[str]
  risk_indicators: List[str]
  advisory_notes: str
```

### 6.2 Utilisation par B12 (Admissibilité et Sélection)

- **Propriété B12 :** B12 est le seul organe propriétaire de l'admissibilité fonctionnelle (*admissibility*) et du choix d'activation (*selection*).
- **Mode de consommation :** B12 interroge les profils B11 pour évaluer si les capacités envisagées sont viables dans le contexte courant.
- **Composition multi-compétences (Confirmée par l'architecte) :** B12 peut soumettre à B11 des combinaisons d'organes (ex. `[Agent_Linguistique, Outil_Recherche, Validateur_SENS]`). B11 évalue l'aptitude collective de cette chaîne de compétences en mesurant les interfaces et les antécédents de couplage, sans être contraint par un catalogue fermé de paires pré-approuvées.
- **Absence de verrouillage permanent :** B12 ne fige pas une décision de rejet à vie : si de nouvelles preuves apparaissent ou si le contexte change, une nouvelle interrogation de B11 peut réhabiliter une option antérieurement incertaine.

---

## 7. Matrice d'articulation multi-organes et flux de signaux

Afin d'éviter tout conflit de frontières ou toute confusion de rôle, les responsabilités entre les différents organes sont strictement délimitées ci-dessous :

| Organe | Rôle principal | Nature de la sortie | Statut d'autorité | Émet `ACT` ? | Peut muter le noyau ? |
|---|---|---|---|---|---|
| **B11** | Évaluation contextualisée d'aptitude et calibration | Profil d'aptitude transitoire (`ContextualCompetenceProfile`) | **NONE** (`COMPETENCE != AUTHORITY`) | **NON** (`emits_act=False`) | **NON** (`kernel_mutation=False`) |
| **B12** | Admissibilité et sélection des capacités / organes | Plan de sélection contextuel | **NONE** | **NON** (`emits_act=False`) | **NON** (`kernel_mutation=False`) |
| **Path Compute** | Calcul et proposition de trajectoires d'états | Graphe de chemins candidats | **NONE** (`path_compute_authority=NONE`) | **NON** (`emits_act=False`) | **NON** (`kernel_mutation=False`) |
| **Thermodynamique** | Évaluation analytique des coûts, dissipations et compromis | Vecteur de métriques de dissipation / dette / survie | **NONE** (`thermodynamic_authority=NONE`) | **NON** (`emits_act=False`) | **NON** (`kernel_mutation=False`) |
| **Sigma** | Agrégation de consensus et contrôle de cohérence | `DomainAggregate` (votes, métriques, contradictions) | **NONE** (`sigma_authority=NONE`) | **NON** (`emits_act=False`) | **NON** (`kernel_mutation=False`) |
| **GuardX108** | Porte déterministe d'évaluation des règles d'accès | `CanonicalDecisionEnvelope` (`x108_gate = ALLOW/HOLD/BLOCK`) | **GATE_AUTHORITY** (Porte déterministe) | **NON** | **NON** |
| **KX108** | Autorité souveraine de décision finale et de scellage | Autorisation d'exécution cryptographiquement liée | **SOVEREIGN_ONLY** (`KX108_ONLY`) | **OUI** (Seul émetteur légitime) | **Sous protocole strict** |

### 7.1 Transmission et consommation sémantique des signaux Thermo par Sigma

L'examen et la sécurisation du parcours runtime (`periphery/sigma_bridge.py` $\rightarrow$ `sigma/domains/meta_agents.py` $\rightarrow$ `GuardX108.decide()`) distinguent strictement ce qui est implémenté à partir des règles canoniques existantes de ce qui demeure non évalué ou hors périmètre faute de contrat dédié :

1. **Parcours runtime implémenté et testé (consommation sémantique explicite et consultative des métriques Thermo actives) :**
   - `periphery/energy_thermo.py::run_energy_thermo(ActionCandidate)` calcule les 7 métriques Thermo actives (`pin`, `pout`, `energy_efficiency`, `thermo_debt`, `truth_score`, `sigma_score`, `sigma_truth_mismatch`) et les recommandations périphériques associées (`ENERGY_INEFFICIENT`, `THERMO_DEBT_HIGH`, `SIGMA_TRUTH_MISMATCH`, `COLLAPSE_DISGUISED_HIGH_SIGMA`).
   - Dans [`periphery/sigma_bridge.py`](file:///C:/Users/User/Desktop/obsidia-jarvis-advanced-integration-v0/periphery/sigma_bridge.py), `_merge_periphery_into_aggregate(aggregate, packet)` préserve uniquement les scores explicitement définis par l'agrégateur de domaine (`domain_truth_score` et `domain_sigma_score` lorsqu'ils existent dans `aggregate.extra_metrics`, à savoir dans `GPS_DEFENSE_AVIATION`) sans jamais substituer `aggregate.confidence` à `domain_sigma_score` dans les domaines où leur équivalence n'est pas prouvée, et trace les clés Thermo reçues (`thermo_packet_keys`).
   - Dans [`sigma/domains/meta_agents.py`](file:///C:/Users/User/Desktop/obsidia-jarvis-advanced-integration-v0/sigma/domains/meta_agents.py), le méta-agent [`ThermoCoherenceAgent`](file:///C:/Users/User/Desktop/obsidia-jarvis-advanced-integration-v0/sigma/domains/meta_agents.py) exécute [`evaluate_thermo_sigma_coherence(aggregate)`](file:///C:/Users/User/Desktop/obsidia-jarvis-advanced-integration-v0/sigma/domains/meta_agents.py) et produit un contrat typé immuable [`ThermoSigmaEvaluation`](file:///C:/Users/User/Desktop/obsidia-jarvis-advanced-integration-v0/sigma/domains/meta_agents.py) (persisté dans `aggregate.extra_metrics["sigma_thermo_evaluation"]` et `CanonicalDecisionEnvelope.metrics["sigma_thermo_evaluation"]`, avec trace `thermo_sigma:<STATUS>` dans `evidence_refs`) :
     - **Signal incomplet (`status = "INCOMPLETE"`) et distinction stricte entre `unknowns` consultatifs et `DomainAggregate.unknowns` :** Si un paquet Thermo partiel omet l'une des 7 clés canoniques (`THERMO_CANONICAL_KEYS`), `ThermoSigmaEvaluation` rapporte explicitement dans le champ consultatif `sigma_thermo_evaluation` : `status = "INCOMPLETE"`, `missing_keys`, `unknowns = ("THERMO_SIGNAL_INCOMPLETE",)` et `proposed_verdict = "HOLD"`. Ce marqueur `unknowns` et ce `proposed_verdict` demeurent **strictement confinés au rapport consultatif `sigma_thermo_evaluation`** : `ThermoCoherenceAgent.evaluate` renvoie `AgentVote(..., unknowns=[], contradictions=[])` et ne propage jamais `"THERMO_SIGNAL_INCOMPLETE"` dans `DomainAggregate.unknowns` (qui alimente `GuardX108.decide`). Ainsi, `DomainAggregate.unknowns` n'est pas incrémenté par ce marqueur et `GuardX108` calcule `x108_gate` exclusivement selon l'agrégat existant.
     - **Comparabilité inter-domaines (`domain_comparison_status`) :** Seul le domaine `GPS_DEFENSE_AVIATION` définit canoniquement `sigma_score = confidence` et `truth_score` dans `sigma/aggregation.py` (`domain_comparison_status = "COMPARABLE"`). Dans les domaines `BANK`, `TRADING` et `ECOM`, où `aggregate.confidence` est un cumul non moyenné plafonné à `0.98`, `aggregate.confidence` n'est pas substitué à `domain_sigma_score` : l'évaluation produit `domain_comparison_status = "NOT_COMPARABLE"` (`domain_sigma_score = None`, `domain_truth_score = None`) et ne déclenche aucun `HOLD` sur cette comparaison.
     - **Formules numériques sans tolérance canonique (`formula_status`) :** Aucune tolérance flottante (telle que `1e-5`) ni aucun arrondi à 6 décimales n'étant définis dans `periphery/constants.py` ou `periphery/energy_thermo.py`, l'égalité exacte produit `formula_status = "EXACT_MATCH"` (`formula_consistent = True`) et tout écart numérique non couvert par un contrat de tolérance est rapporté comme `formula_status = "NOT_EVALUATED_NO_CANONICAL_TOLERANCE"` (`formula_consistent = None`), sans jamais être transformé en contradiction ni en `BLOCK`.
     - **Seuils et drapeaux canoniques Thermo :** Sigma évalue uniquement les seuils canoniques de `periphery/constants.py` et réutilise les noms exacts de `periphery/energy_thermo.py` (`energy_efficiency < THETA_ENERGY (0.2)` $\rightarrow$ `ENERGY_INEFFICIENT`, `thermo_debt > THETA_THERMO_DEBT (1.0)` $\rightarrow$ `THERMO_DEBT_HIGH`, `actual_sigma_truth_mismatch > THETA_MISMATCH (0.35)` $\rightarrow$ `SIGMA_TRUTH_MISMATCH`, et `COLLAPSE_DISGUISED_HIGH_SIGMA` uniquement s'il est émis par le paquet). Aucune règle combinatoire non canonique (telle que `thermo_debt > 1.0` $\land$ `mismatch > 0.35` $\rightarrow$ `BLOCK`) n'est créée.
     - **Subordination préservée :** `ThermoSigmaEvaluation` porte invariablement `advisory_only = True`, `decision_authority = "KX108_ONLY"` et `emits_act = False`. Aucun composant Sigma ou Thermo n'émet `ACT` ; Sigma ne crée aucune nouvelle politique de gate : `GuardX108.decide(aggregate)` conserve son rôle exclusif de porte (`x108_gate`), et `KX108` demeure l'unique autorité souveraine (`KX108_ONLY`).
2. **Périmètre non implémenté et maintenu désactivé (faute de contrat canonique validé) :**
   - **Cadre thermodynamique étendu (`THERMODYNAMIC_FRAMEWORK_PREFLIGHT_V0`) :** Les grandeurs théoriques $E(S)$, $D(A)$, $B_{\text{surv}}$, $B_{\text{truth}}$, $B_{\text{mission}}$, $C_{\text{compute}}$ et le ratio bénéfice/coût demeurent strictement désactivés (`runtime_enabled = false` dans `periphery/thermo_preflight_contract_v0.py`).
   - **Normalisation de `domain_sigma_score` hors GPS et couplage économique métier :** Aucun contrat canonique ne définit d'équivalence entre `aggregate.confidence` et `sigma_score` pour `BANK`, `TRADING` ou `ECOM`, ni de formule reliant `thermo_debt` ou `energy_efficiency` aux variables métier propres d'un domaine (`amount`/`policy_limit`, `margin_rate`, `drawdown`).

---

## 8. Statut des orientations de l'architecte

Cette section acte les orientations formellement confirmées et précise le périmètre restant en attente pour l'Orientation 03 :

```
[ORIENTATION_01_CONFIRMEE] : DYNAMISME ET COMPOSITION OUVERTE DE COMPÉTENCE
Statut : CONFIRMÉ PAR L'ARCHITECTE (2026-10-17)
Énoncé : B11 évalue des compétences contextualisées et peut considérer des aptitudes
émergentes ou des compositions d'organes, sans dépendre d'un catalogue fermé pré-approuvé.
Portée : B11 produit des ContextualCompetenceProfile dynamiques basés sur le tuple
(Domaine, Tâche, Conditions, Preuves, Inconnues).

[ORIENTATION_02_CONFIRMEE] : GESTION DE L'INCONNUE SANS INCAPACITÉ DÉFINITIVE
Statut : CONFIRMÉ PAR L'ARCHITECTE (2026-10-17)
Énoncé : Une compétence inconnue (UNKNOWN_COMPETENCE) appelle une évaluation,
une exploration, un banc d'essai borné ou une escalade cognitive ; l'inconnue
ne signifie pas incapacité générale ou permanente. Cela n'autorise toutefois pas
automatiquement une action concrète : GuardX108 peut produire HOLD ou BLOCK pour
cette action selon les preuves, risques et inconnues, sans transformer ce verdict
circonstanciel en jugement permanent sur la capacité.
Portée : Conforme à la loi M32 (UNKNOWN != FALSE). B12 ne fige aucun verrouillage
irréversible sur une inconnue, tout en respectant le filtrage immédiat de GuardX108.

[ORIENTATION_03_EN_ATTENTE_DE_VALIDATION] : COUPLAGE THERMODYNAMIQUE ÉTENDU (PREFLIGHT V0 & COMPROMIS MÉTIER)
Statut : ÉVALUATION CONSULTATIVE CANONIQUE IMPLÉMENTÉE ; RÈGLES ÉTENDUES EN ATTENTE DE CONTRAT DÉDIÉ
Constat canonique :
- Implémenté et prouvé en runtime (tests/integration/test_thermo_sigma_semantic_coherence.py) :
  Sigma consomme explicitement et à titre strictement consultatif les 7 métriques Thermo actives via
  ThermoCoherenceAgent et ThermoSigmaEvaluation (contrôle des 7 clés avec unknowns=("THERMO_SIGNAL_INCOMPLETE",)
  et proposed_verdict="HOLD" confinés au rapport consultatif sigma_thermo_evaluation sans propagation vers
  DomainAggregate.unknowns, seuils canoniques THETA_ENERGY=0.2 -> ENERGY_INEFFICIENT, THETA_THERMO_DEBT=1.0
  -> THERMO_DEBT_HIGH, THETA_MISMATCH=0.35 -> SIGMA_TRUTH_MISMATCH, comparabilité prouvée uniquement en
  GPS_DEFENSE_AVIATION et NOT_COMPARABLE en Bank/Trading/Ecom, écarts de formule sans tolérance canonique
  rapportés comme NOT_EVALUATED_NO_CANONICAL_TOLERANCE), sans créer de nouvelle politique de gate.
  GuardX108 conserve son rôle de gate selon l'agrégat existant et KX108 conserve l'autorité souveraine (KX108_ONLY).
- Non activé et en attente de contrat :
  Le cadre étendu bénéfice/coût (THERMODYNAMIC_FRAMEWORK_PREFLIGHT_V0 : E(S), D(A), B_surv, B_truth,
  B_mission, C_compute) reste désactivé (runtime_enabled = false), et aucun contrat canonique ne
  définit de tolérance flottante sur les formules, de normalisation de domain_sigma_score hors GPS,
  ni de règle combinatoire Thermo -> BLOCK.
Décision doctrinale : L'activation du cadre étendu et de toute règle de gate additionnelle reste
EN ATTENTE jusqu'à validation d'un contrat canonique dédié par l'architecte.
```

---

## 9. Frontières d'autorité, subordination et analyse des contradictions

### 9.1 Subordination stricte : Recommandations vs Porte vs Autorité finale

L'architecture Obsidia sépare rigoureusement trois niveaux hiérarchiques :

1. **Niveau 1 — Recommandations et Consensus consultatifs (Sigma / Marché / Périphérie) :**
   - Les votes des agents (`AgentVote`), le verdict de marché (`DomainAggregate.market_verdict`), les recommandations périphériques (`recommended_gate`) et la surface de consensus (`raw_engine.consensus.*`, `aggregate4`) sont purement consultatifs (*advisory-only*).
   - Ils portent explicitement `authority = PROOF_SURFACE_ONLY` ou `NONE`, `does_not_override_x108_gate = True`, et `does_not_authorize_action = True`.
2. **Niveau 2 — Porte déterministe de contrôle d'accès (GuardX108) :**
   - [`GuardX108.decide()`](file:///C:/Users/User/Desktop/obsidia-jarvis-advanced-integration-v0/sigma/guard.py) évalue l'agrégat consolidé pour produire la porte déterministe `x108_gate` (`ALLOW`, `HOLD`, `BLOCK`) dans un `CanonicalDecisionEnvelope`.
   - `GuardX108` est un filtre d'admissibilité formelle : un `BLOCK` ou un `HOLD` interdit le passage ; un `ALLOW` déclare l'admissibilité technique mais n'ordonne aucune action.
3. **Niveau 3 — Autorité souveraine de décision finale (KX108) :**
   - `KX108` est l'unique instance décisionnelle souveraine du système (`decision_authority = KX108_ONLY`).
   - L'obtention d'un `ALLOW` auprès de GuardX108 n'est qu'une condition nécessaire, jamais suffisante. Comme le formalise [`obsidia_governed_runtime_cycle_v1.py`](file:///C:/Users/User/Desktop/obsidia-jarvis-advanced-integration-v0/scripts/obsidia_governed_runtime_cycle_v1.py), l'autorisation d'agir requiert obligatoirement :
     $$\text{ALLOW} + \text{Ticket OS3 valide} + \text{Rejeu cryptographique PASS} + \text{Approbation / EAH conforme} + \text{Persistance immuable}$$
   - Aucun composant cognitif (B11, B12, Thermo, Sigma, ni même GuardX108 seul) ne peut émettre l'ordre d'action `ACT` ni muter l'état souverain.

### 9.2 Signalement des ambiguïtés et contradictions terminologiques trouvées

L'inspection approfondie du dépôt fait apparaître une tension de formulation entre certains scripts d'audit et la doctrine fondamentale :

- **Raccourci de langage dans certains scripts et commentaires :**
  Dans `scripts/audit_sigma_safe_evolution_p74.py` et `scripts/audit_runtime_core_risk_review_p75.py`, on trouve des formulations telles que :
  > *« GuardX108 est l'autorité finale de décision X108 »* ou *« GuardX108.decide() = autorité finale »*.
  De même, dans `scripts/obsidia_kx108_decision_store.py` (l. 11), on lit :
  > *« GuardX108.decide() est la seule source du champ souverain x108_gate »*.
- **Contradiction avec la doctrine fondamentale :**
  Ce raccourci textuel prête à `GuardX108` le qualificatif d'« autorité finale », alors que la doctrine constitutionnelle et le code d'exécution souveraine ([`obsidia_governed_runtime_cycle_v1.py`](file:///C:/Users/User/Desktop/obsidia-jarvis-advanced-integration-v0/scripts/obsidia_governed_runtime_cycle_v1.py), `OBSIDIA_X108_GLOSSAIRE_INTEGRAL_AUDITE.md`) stipulent explicitement :
  - *« runtime coordinator coordinates authority; runtime coordinator does not possess authority »* ;
  - `decision_authority = KX108_ONLY` ;
  - `GuardX108` ne fait que calculer la porte `x108_gate` ; il ne détient pas la souveraineté décisionnelle d'action.
- **Résolution doctrinale M42 :**
  La doctrine M42 dissipe cette ambiguïté : **GuardX108 est la porte déterministe finale d'admissibilité (*gate authority*), mais KX108 est l'unique autorité souveraine de décision d'action (*sovereign decision authority*).** Tout verdict Sigma reste un signal soumis à GuardX108 et subordonné à KX108.

---

## 10. Frontières d'autorité et invariants constitutionnels

Les invariants suivants sont absolus, non négociables et s'appliquent sans exception :

| Invariant | Statut | Source canonique | Conséquence pour B11 |
|---|---|---|---|
| `COMPETENCE != AUTHORITY` | **ABSOLU** | Glossaire X-108, Fondations cognitives | Une compétence avérée ne confère aucun droit d'agir. |
| `CONFIDENCE != AUTHORITY` | **ABSOLU** | M41 Doctrine, Glossaire X-108 | La certitude subjective ne remplace pas une autorisation KX108. |
| `CALIBRATION != PERMISSION` | **ABSOLU** | M42 Doctrine V1 | Être bien calibré n'est pas une permission d'exécution. |
| `RANKING != AUTHORITY` | **ABSOLU** | M41 Doctrine, Thermo Preflight | Classer des compétences ou des chemins n'en valide aucun. |
| `UNKNOWN != INCAPACITY` | **ABSOLU** | M32, M42 Doctrine V1 | L'absence de preuve ne constitue pas une preuve d'incapacité. |
| `KX108_ONLY = YES` | **ABSOLU** | Scellage P74/P75, `sigma/guard.py` | Seul KX108 émet l'autorité décisionnelle finale. |
| `B11_MEMORY_WRITE = NO` | **ABSOLU** | M40/B10 Doctrine | B11 ne modifie pas directement la mémoire durable B10. |
| `B11_EMITS_ACT = NO` | **ABSOLU** | Fondations cognitives | B11 ne produit aucun appel d'action machine. |
| `B11_KERNEL_MUTATION = NO` | **ABSOLU** | `sigma/contracts.py` | B11 n'altère aucune règle interne du noyau. |
| `SIGMA_CANNOT_BYPASS_X108` | **ABSOLU** | `tests/test_sigma_cannot_bypass_x108.py` | Aucune décision Sigma ne court-circuite GuardX108. |

---

## 11. Critères d'acceptation vérifiables pour les phases futures

Lorsque l'architecte aura validé cette doctrine et ordonné la phase de spécification / tests (RED/GREEN), les critères suivants devront être formellement démontrés :

1. **Représentation non fermée :** Le modèle de données B11 instancie des profils d'aptitude pour des tâches inédites dès lors qu'un descripteur et des métriques sont fournis, sans erreur d'énumération fermée.
2. **Dissociation stricte Inconnue / Échec :** Un test vérifie qu'une évaluation sans preuve produit un état `UNKNOWN_COMPETENCE` avec `confidence=0.0` et `unknowns` non vide, et ne produit pas un `BLOCK` définitif d'incapacité dans B12.
3. **Rejet de toute autorité d'action :** Un test d'intrusion vérifie que la tentative d'un profil B11 d'émettre un ordre d'action ou de modifier le noyau lève immédiatement une exception d'accès interdit.
4. **Périmètre mémoire transitoire :** Aucune persistance n'est écrite dans la base B10 lors des cycles d'évaluation de B11 sans contrat de persistance séparé et scellé.
5. **Vérification de la priorité Sigma et subordination KX108 :** Toute intégration de métrique B11 ou Thermo dans un pipeline Sigma continue de respecter la règle invariante `BLOCK > HOLD > ALLOW` de GuardX108 et demeure subordonnée à la décision finale KX108.

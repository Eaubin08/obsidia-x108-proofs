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
   - Dans [`periphery/sigma_bridge.py`](file:///C:/Users/User/Desktop/obsidia-jarvis-advanced-integration-v0/periphery/sigma_bridge.py), `_merge_periphery_into_aggregate(aggregate, packet)` :
     - préserve uniquement les scores explicitement définis par l'agrégateur de domaine (`domain_truth_score` et `domain_sigma_score` lorsqu'ils existent dans `aggregate.extra_metrics`, à savoir dans `GPS_DEFENSE_AVIATION`) sans jamais substituer `aggregate.confidence` à `domain_sigma_score` dans les domaines où leur équivalence n'est pas prouvée, et trace les clés Thermo reçues (`thermo_packet_keys`) ;
     - **résout la contradiction C2 (`recommended_gate == "HOLD"` d'origine Thermo) par identification fermée des seuls signaux Thermo (`_THERMO_HOLD_RISK_FLAGS`) :** `PeripheralSignalPacket` et `merge_packets` ne conservant pas la provenance par module de `recommended_gate`, `_merge_periphery_into_aggregate` ne classe un `HOLD` comme purement Thermo (`thermo_only_hold`) que si des clés Thermo sont présentes, `packet.unknowns` et `packet.contradictions` sont vides, et `packet.risk_flags` est non vide et inclus dans l'ensemble fermé des signaux Thermo explicites (`_THERMO_HOLD_RISK_FLAGS = {"ENERGY_INEFFICIENT", "SIGMA_TRUTH_MISMATCH", "THERMO_DEBT_HIGH"}`). Il conserve alors les métriques et drapeaux canoniques Thermo dans `aggregate.risk_flags` sans injecter `"PERIPHERY_RECOMMENDS_HOLD"` dans `aggregate.unknowns` (évitant la cascade `"TICKET_NOT_READY"`). Tout `HOLD` accompagné d'un `risk_flag` non-Thermo (connu ou inédit/futur), d'un `unknown` ou sans `risk_flag` Thermo conserve `"PERIPHERY_RECOMMENDS_HOLD"`.
   - Dans [`sigma/domains/meta_agents.py`](file:///C:/Users/User/Desktop/obsidia-jarvis-advanced-integration-v0/sigma/domains/meta_agents.py), le méta-agent [`ThermoCoherenceAgent`](file:///C:/Users/User/Desktop/obsidia-jarvis-advanced-integration-v0/sigma/domains/meta_agents.py) exécute [`evaluate_thermo_sigma_coherence(aggregate)`](file:///C:/Users/User/Desktop/obsidia-jarvis-advanced-integration-v0/sigma/domains/meta_agents.py) et produit un contrat typé immuable [`ThermoSigmaEvaluation`](file:///C:/Users/User/Desktop/obsidia-jarvis-advanced-integration-v0/sigma/domains/meta_agents.py) (persisté dans `aggregate.extra_metrics["sigma_thermo_evaluation"]` et `CanonicalDecisionEnvelope.metrics["sigma_thermo_evaluation"]`, avec trace `thermo_sigma:<STATUS>` dans `evidence_refs`) :
     - **Signal incomplet (`status = "INCOMPLETE"`) et distinction stricte entre `unknowns` consultatifs et `DomainAggregate.unknowns` :** Si un paquet Thermo partiel omet l'une des 7 clés canoniques (`THERMO_CANONICAL_KEYS`), `ThermoSigmaEvaluation` rapporte explicitement dans le champ consultatif `sigma_thermo_evaluation` : `status = "INCOMPLETE"`, `missing_keys`, `unknowns = ("THERMO_SIGNAL_INCOMPLETE",)` et `proposed_verdict = "HOLD"`. Ce marqueur `unknowns` et ce `proposed_verdict` demeurent **strictement confinés au rapport consultatif `sigma_thermo_evaluation`** : `ThermoCoherenceAgent.evaluate` renvoie `AgentVote(..., unknowns=[], contradictions=[])` et ne propage jamais `"THERMO_SIGNAL_INCOMPLETE"` dans `DomainAggregate.unknowns` (qui alimente `GuardX108.decide`). Ainsi, `DomainAggregate.unknowns` n'est pas incrémenté par ce marqueur et `GuardX108` calcule `x108_gate` exclusivement selon l'agrégat existant.
     - **Comparabilité inter-domaines (`domain_comparison_status`) :** Seul le domaine `GPS_DEFENSE_AVIATION` définit canoniquement `sigma_score = confidence` et `truth_score` dans `sigma/aggregation.py` (`domain_comparison_status = "COMPARABLE"`). Dans les domaines `BANK`, `TRADING` et `ECOM`, où `aggregate.confidence` est un cumul non moyenné plafonné à `0.98`, `aggregate.confidence` n'est pas substitué à `domain_sigma_score` : l'évaluation produit `domain_comparison_status = "NOT_COMPARABLE"` (`domain_sigma_score = None`, `domain_truth_score = None`) et ne déclenche aucun `HOLD` sur cette comparaison.
     - **Formules numériques sans tolérance canonique (`formula_status`) :** Aucune tolérance flottante (telle que `1e-5`) ni aucun arrondi à 6 décimales n'étant définis dans `periphery/constants.py` ou `periphery/energy_thermo.py`, l'égalité exacte produit `formula_status = "EXACT_MATCH"` (`formula_consistent = True`) et tout écart numérique non couvert par un contrat de tolérance est rapporté comme `formula_status = "NOT_EVALUATED_NO_CANONICAL_TOLERANCE"` (`formula_consistent = None`), sans jamais être transformé en contradiction ni en `BLOCK`.
     - **Seuils et drapeaux canoniques Thermo :** Sigma évalue uniquement les seuils canoniques de `periphery/constants.py` et réutilise les noms exacts de `periphery/energy_thermo.py` (`energy_efficiency < THETA_ENERGY (0.2)` $\rightarrow$ `ENERGY_INEFFICIENT`, `thermo_debt > THETA_THERMO_DEBT (1.0)` $\rightarrow$ `THERMO_DEBT_HIGH`, `actual_sigma_truth_mismatch > THETA_MISMATCH (0.35)` $\rightarrow$ `SIGMA_TRUTH_MISMATCH`, et `COLLAPSE_DISGUISED_HIGH_SIGMA` uniquement s'il est émis par le paquet). Aucune règle combinatoire non canonique (telle que `thermo_debt > 1.0` $\land$ `mismatch > 0.35` $\rightarrow$ `BLOCK`) n'est créée.
     - **Subordination préservée :** `ThermoSigmaEvaluation` porte invariablement `advisory_only = True`, `decision_authority = "KX108_ONLY"` et `emits_act = False`. Aucun composant Sigma ou Thermo n'émet `ACT` ; Sigma ne crée aucune nouvelle politique de gate : `GuardX108.decide(aggregate)` conserve son rôle exclusif de porte (`x108_gate`), et `KX108` demeure l'unique autorité souveraine (`KX108_ONLY`).
2. **Périmètre non implémenté et maintenu désactivé (faute de contrat canonique validé) :**
   - **Cadre thermodynamique étendu (`THERMODYNAMIC_FRAMEWORK_PREFLIGHT_V0`) :** Les grandeurs symboliques $S, A, E(S), D(A), I(A), F(A), C(A), R(A), T(A), P(A)$ définies dans [`docs/thermodynamic_framework/THERMODYNAMIC_FRAMEWORK_PREFLIGHT_V0.md`](file:///C:/Users/User/Desktop/obsidia-jarvis-advanced-integration-v0/docs/thermodynamic_framework/THERMODYNAMIC_FRAMEWORK_PREFLIGHT_V0.md) ainsi que la frontière [`path_compute_v0/boundary.py`](file:///C:/Users/User/Desktop/obsidia-jarvis-advanced-integration-v0/path_compute_v0/boundary.py) demeurent strictement désactivées en runtime (`runtime_enabled = false`, `activation_allowed_now = false`).
   - **Normalisation de `domain_sigma_score` hors GPS et couplage économique métier :** Aucun contrat canonique ne définit d'équivalence entre `aggregate.confidence` et `sigma_score` pour `BANK`, `TRADING` ou `ECOM`, ni de formule reliant `thermo_debt` ou `energy_efficiency` aux variables métier propres d'un domaine (`amount`/`policy_limit`, `margin_rate`, `drawdown`).

---

### 7.2 `[PROPOSITION À VALIDER]` — Spécification du cadre Thermo Bénéfice/Coût et Choix Contextuel Multi-Trajectoires

> **Statut normatif : `PROPOSITION À VALIDER` (`runtime_enabled = False`, `activation_allowed_now = False`).**
> Cette section formalise, sans activer de code runtime ni inventer de formules, seuils, pondérations ou règles de gate non canoniques, l'articulation entre :
> 1. La composition contextuelle ouverte des compétences et organes (B11/B12) ;
> 2. L'estimation analytique des bénéfices, coûts, dissipations, irréversibilité, friction et viabilité des trajectoires (Thermo / Path Compute) ;
> 3. Le contrôle de cohérence sémantique par Sigma (qui ne recalcule ni les coûts ni les bénéfices et ne devient pas un moteur économique) ;
> 4. Le filtrage déterministe de porte par `GuardX108` et l'autorité souveraine finale `KX108_ONLY`.

#### 7.2.1 Audit et classification des sources canoniques (à `HEAD 42eb7e8f` + correctif C2)

| Catégorie | Élément / Mécanisme | Source canonique exacte | Statut et périmètre |
|---|---|---|---|
| **1. Déjà implémenté (`CURRENT_CANONICAL`)** | 7 métriques Thermo actives (`pin`, `pout`, `energy_efficiency = pout/pin`, `thermo_debt = energy_cost + compute_cost + attention_cost + recovery_cost - useful_work`, `truth_score`, `sigma_score`, `sigma_truth_mismatch = abs(sigma_score - truth_score)`) et 4 drapeaux/contradictions (`ENERGY_INEFFICIENT` si `< 0.2`, `SIGMA_TRUTH_MISMATCH` si `> 0.35`, `THERMO_DEBT_HIGH` si `> 1.0`, `COLLAPSE_DISGUISED_HIGH_SIGMA`) | [`periphery/energy_thermo.py`](file:///C:/Users/User/Desktop/obsidia-jarvis-advanced-integration-v0/periphery/energy_thermo.py), [`periphery/constants.py`](file:///C:/Users/User/Desktop/obsidia-jarvis-advanced-integration-v0/periphery/constants.py) | Actif sur candidat d'action unitaire (`ActionCandidate`). Fichier `energy_thermo.py` verrouillé par empreinte SHA-256 (`2940c6c1adbacaf8`) dans `tests/test_batch_execution_v0.py`. |
| **1. Déjà implémenté (`CURRENT_CANONICAL`)** | Dérive trajectorielle (`trajectory_score`, `trajectory_divergence >= 0.5`, `context_drift >= 0.5`), constance opérationnelle (`oc_S`, `oc_sigma`, `THETA_OC = 1.0`), friction symbolique (`abs(val_logique - val_diffusif)`) et modèle de dette unitaire (`DebtBreakdown`: `gross_value`, `computational_debt`, `energy_debt`, `memory_debt`, `thermo_debt`, `oc_debt`, `total_debt`, `net_value`) | [`periphery/timeverse.py`](file:///C:/Users/User/Desktop/obsidia-jarvis-advanced-integration-v0/periphery/timeverse.py), [`periphery/operational_constance.py`](file:///C:/Users/User/Desktop/obsidia-jarvis-advanced-integration-v0/periphery/operational_constance.py), [`periphery/friction_symbolique.py`](file:///C:/Users/User/Desktop/obsidia-jarvis-advanced-integration-v0/periphery/friction_symbolique.py), [`periphery/gencoin_debt_model.py`](file:///C:/Users/User/Desktop/obsidia-jarvis-advanced-integration-v0/periphery/gencoin_debt_model.py) | Actif par action unitaire ; non relié à un comparateur multi-trajectoires. Fichier `gencoin_debt_model.py` verrouillé par empreinte SHA-256 (`e6817f5ae9651c78`) dans `tests/test_batch_execution_v0.py`. |
| **1. Déjà implémenté (`CURRENT_CANONICAL`)** | Évaluation sémantique consultative par Sigma (`ThermoCoherenceAgent` $\rightarrow$ `ThermoSigmaEvaluation` dans `extra_metrics["sigma_thermo_evaluation"]`), comparabilité `COMPARABLE` (GPS) vs `NOT_COMPARABLE` (Bank/Trading/Ecom), détection `INCOMPLETE` (`unknowns=("THERMO_SIGNAL_INCOMPLETE",)` confiné au rapport consultatif sans incrémenter `DomainAggregate.unknowns`), `EXACT_MATCH` vs `NOT_EVALUATED_NO_CANONICAL_TOLERANCE`, et **correction C2** (`recommended_gate='HOLD'` purement Thermo identifié par inclusion stricte dans `_THERMO_HOLD_RISK_FLAGS` et non converti en `"PERIPHERY_RECOMMENDS_HOLD"` dans `DomainAggregate.unknowns`) | [`periphery/sigma_bridge.py`](file:///C:/Users/User/Desktop/obsidia-jarvis-advanced-integration-v0/periphery/sigma_bridge.py), [`sigma/domains/meta_agents.py`](file:///C:/Users/User/Desktop/obsidia-jarvis-advanced-integration-v0/sigma/domains/meta_agents.py) | Actif et prouvé par 8 tests d'intégration dédiés (`test_thermo_sigma_semantic_coherence.py`) + suite de non-régression. |
| **1. Déjà implémenté (`CURRENT_CANONICAL`)** | Porte déterministe `GuardX108.decide(aggregate)` (`x108_gate = ALLOW \| HOLD \| BLOCK`) et autorité souveraine finale `KX108_ONLY` | [`sigma/guard.py`](file:///C:/Users/User/Desktop/obsidia-jarvis-advanced-integration-v0/sigma/guard.py), [`scripts/obsidia_governed_runtime_cycle_v1.py`](file:///C:/Users/User/Desktop/obsidia-jarvis-advanced-integration-v0/scripts/obsidia_governed_runtime_cycle_v1.py) | Invariant constitutionnel scellé. |
| **2. Spécifié mais désactivé (`PREFLIGHT / STUB`)** | Cadre pré-décisionnel symbolique : $S$ (état), $A$ (action/transition), $E(S)$ (énergie/pression structurelle), $D(A)$ (dissipation), $I(A)$ (coût d'irréversibilité), $F(A)$ (friction), $C(A)$ (cohérence), $R(A)$ (pression de risque), $T(A)$ (stabilité temporelle sous délai), $P(A) = f(C(A), T(A), -D(A), -I(A), -R(A), -F(A))$ | [`docs/thermodynamic_framework/THERMODYNAMIC_FRAMEWORK_PREFLIGHT_V0.md`](file:///C:/Users/User/Desktop/obsidia-jarvis-advanced-integration-v0/docs/thermodynamic_framework/THERMODYNAMIC_FRAMEWORK_PREFLIGHT_V0.md) | `runtime_enabled = false`, `activation_allowed_now = false`, $f$ non implémentée, poids non calibrés. |
| **2. Spécifié mais désactivé (`PREFLIGHT / STUB`)** | Frontière `PathComputeV0Boundary` (`decision_authority="KX108_ONLY"`, `path_compute_authority="NONE"`, `advisory_only=True`, `runtime_enabled=False`) et note consultative `PathCandidateNote` | [`path_compute_v0/boundary.py`](file:///C:/Users/User/Desktop/obsidia-jarvis-advanced-integration-v0/path_compute_v0/boundary.py), [`path_compute_v0/types.py`](file:///C:/Users/User/Desktop/obsidia-jarvis-advanced-integration-v0/path_compute_v0/types.py) | Stubs non-runtime fermés ; aucune sélection de trajectoire. |
| **2. Spécifié mais désactivé (`DOC / SKELETON`)** | Frontière `THERMODYNAMIC_DEBT_BOUNDARY` (`PYTHON_SPEC_NOT_LEAN_PROVEN`, `total_debt` = signal d'alerte, interdit : « la dette = certitude d'échec »), P107 Lyapunov ($L(\Phi(s)) \le L(s)$, `A_PROUVER`) et P161 Calibration énergétique (`DOC_ONLY / LEAN_SKELETON_ONLY`) | [`specs/03_ENTROPY_DISCIPLINE/THERMODYNAMIC_DEBT_BOUNDARY.md`](file:///C:/Users/User/Desktop/obsidia-jarvis-advanced-integration-v0/specs/03_ENTROPY_DISCIPLINE/THERMODYNAMIC_DEBT_BOUNDARY.md), [`docs/formalisation_math/LYAPUNOV_ET_POG.md`](file:///C:/Users/User/Desktop/obsidia-jarvis-advanced-integration-v0/docs/formalisation_math/LYAPUNOV_ET_POG.md) | Documentation et cibles formelles ; non reliées au runtime. |
| **3. Absent** | Formule explicite de $f$, vecteur de pondération et règles de normalisation commune pour $E(S), D(A), I(A), F(A), C(A), R(A), T(A), P(A)$ ; quantification scalaire de $I(A)$ (au-delà du booléen `ActionCandidate.irreversible`) ; normalisation de `domain_sigma_score` / `domain_truth_score` hors GPS ; tolérance flottante $\epsilon$ sur les formules ; runtime B11/B12 et comparateur multi-trajectoires (`periphery/path_finder.py` est un stub vide) | Aucune source canonique dans le dépôt | Marqués explicitement **`À SPÉCIFIER`** ci-dessous. |
| **4. Vérifié en runtime & Blocage sémantique documenté (C1)** | **C1 — Traçage de `compute_cost`, `thermo_debt`, `computational_debt` et `total_debt` :**<br>• **Fait runtime vérifié :** dans [`periphery/energy_thermo.py:5`](file:///C:/Users/User/Desktop/obsidia-jarvis-advanced-integration-v0/periphery/energy_thermo.py#L5), `thermo_debt = energy_cost + compute_cost + attention_cost + recovery_cost - useful_work` est écrit dans `extra_metrics["thermo_debt"]` (sans écrire `compute_cost` ni `computational_debt` dans `extra_metrics`). Aucun des 9 modules de [`periphery/control_plane.py`](file:///C:/Users/User/Desktop/obsidia-jarvis-advanced-integration-v0/periphery/control_plane.py) n'écrit `extra_metrics["computational_debt"]`. Dans [`periphery/gencoin_debt_model.py:37-43`](file:///C:/Users/User/Desktop/obsidia-jarvis-advanced-integration-v0/periphery/gencoin_debt_model.py#L37-L43), `total_debt = computational_debt + energy_debt + memory_debt + oc_debt` additionne 4 termes (`DebtBreakdown.thermo_debt` est un alias d'exposition de `energy_debt` et n'est pas additionné une seconde fois). Par conséquent, dans le flux canonique `run_control_plane(action)` $\rightarrow$ `compute_debt(packet)`, une dépense `payload["compute_cost"] = 3.0` donne `thermo_debt = 3.0`, `energy_debt = 3.0`, `computational_debt = 0.0`, `total_debt = 3.0` (**comptée 1 seule fois**, prouvé par `test_c1_runtime_compute_cost_counted_once_in_control_plane_debt_breakdown`).<br>• **Blocage sémantique/unitaire documenté (sans modification de calcul) :** un double comptage (`3.0 + 3.0 = 6.0`) ne surviendrait que si un appelant externe injectait manuellement `extra_metrics["computational_debt"]` en sus de `payload["compute_cost"]`. Toutefois, [`periphery/math_core/governed_state.py:46-47`](file:///C:/Users/User/Desktop/obsidia-jarvis-advanced-integration-v0/periphery/math_core/governed_state.py#L46-L47) et [`specs/03_ENTROPY_DISCIPLINE/ENTROPY_DISCIPLINE_SPEC.md:29-36`](file:///C:/Users/User/Desktop/obsidia-jarvis-advanced-integration-v0/specs/03_ENTROPY_DISCIPLINE/ENTROPY_DISCIPLINE_SPEC.md#L29-L36) définissent $\Delta C$ (`computational_debt`) et $\Delta E$ (`thermo_debt`) comme deux coordonnées d'état distinctes sans unité ni contrat d'équivalence avec `payload["compute_cost"]`, et `gencoin_debt_model.py` / `energy_thermo.py` sont verrouillés par empreinte SHA-256 dans `tests/test_batch_execution_v0.py:1014-1016`. Aucune soustraction arbitraire n'est donc inventée. | [`periphery/energy_thermo.py:5`](file:///C:/Users/User/Desktop/obsidia-jarvis-advanced-integration-v0/periphery/energy_thermo.py#L5), [`periphery/gencoin_debt_model.py:37-43`](file:///C:/Users/User/Desktop/obsidia-jarvis-advanced-integration-v0/periphery/gencoin_debt_model.py#L37-L43), [`periphery/math_core/governed_state.py:46-47`](file:///C:/Users/User/Desktop/obsidia-jarvis-advanced-integration-v0/periphery/math_core/governed_state.py#L46-L47) | **Fait runtime prouvé** (pas de double comptage dans `run_control_plane`). Contrat d'orthogonalité entre `payload["compute_cost"]` et `extra_metrics["computational_debt"]` maintenu **`À SPÉCIFIER`**. |
| **4. Résolu en runtime (C2)** | **C2 — Chemin `recommended_gate='HOLD'` de Thermo corrigé dans `sigma_bridge.py` :**<br>• **Diagnostic :** `energy_thermo.py:8-11` émet `recommended_gate='HOLD'` dès que `energy_efficiency < 0.2`, `mismatch > 0.35` ou `thermo_debt > 1.0`. Avant correction, `sigma_bridge.py` injectait inconditionnellement `"PERIPHERY_RECOMMENDS_HOLD"` dans `aggregate.unknowns`, ce qui déclenchait `"TICKET_NOT_READY"` dans `TicketReadinessAgent` (`len(unknowns) == 2 > 1`) et forçait `GuardX108` à produire `x108_gate = "HOLD"` (`reason_code = "UNKNOWNS_OR_CONFIDENCE_LOW"`), contournant la règle canonique des `risk_flags` de `GuardX108` et violant `THERMODYNAMIC_DEBT_BOUNDARY.md:45`.<br>• **Correction appliquée (fermée sur les seuls signaux Thermo explicites) :** `PeripheralSignalPacket` et `merge_packets` ne conservant pas la provenance par module de `recommended_gate`, [`periphery/sigma_bridge.py:21-60`](file:///C:/Users/User/Desktop/obsidia-jarvis-advanced-integration-v0/periphery/sigma_bridge.py#L21-L60) ne classe un `HOLD` en `thermo_only_hold` que si `thermo_packet_keys` est non vide, `packet.unknowns` et `packet.contradictions` sont vides, et `packet.risk_flags` est non vide et inclus dans `_THERMO_HOLD_RISK_FLAGS = {"ENERGY_INEFFICIENT", "SIGMA_TRUTH_MISMATCH", "THERMO_DEBT_HIGH"}`. Tout `risk_flag` non-Thermo (connu ou nouveau) maintient `"PERIPHERY_RECOMMENDS_HOLD"`. | [`periphery/sigma_bridge.py:21-60`](file:///C:/Users/User/Desktop/obsidia-jarvis-advanced-integration-v0/periphery/sigma_bridge.py#L21-L60), [`tests/integration/test_thermo_sigma_semantic_coherence.py`](file:///C:/Users/User/Desktop/obsidia-jarvis-advanced-integration-v0/tests/integration/test_thermo_sigma_semantic_coherence.py) | **Corrigé et prouvé en RED/GREEN** (`test_c2_thermo_recommended_gate_hold_remains_advisory_without_artificial_unknown`, `test_c2_merged_packet_with_unlisted_non_thermo_hold_risk_is_not_classified_as_thermo_only`). |
| **5. À arbitrer** | Choix de l'opérateur de comparaison entre trajectoires (dominance de Pareto partielle sans poids vs score scalaire $P(A)$ pondéré), unités de normalisation par domaine, contrat d'orthogonalité `compute_cost` vs `computational_debt`, et budget d'exploration bornée sur `UNKNOWN_COMPETENCE` | Décision propriétaire requise | Maintenu en attente de validation propriétaire. |

---

#### 7.2.2 `[PROPOSITION À VALIDER]` — Contrat typé de comparaison consultative multi-trajectoires

Afin de comparer plusieurs trajectoires candidates issues d'une composition d'organes B11/B12 sans inventer de valeurs ni déplacer l'autorité vers Thermo ou Sigma, la structure contractuelle suivante est proposée à la validation propriétaire. Tout paramètre dépourvu de définition canonique actuelle est explicitement marqué **`À SPÉCIFIER`** :

```python
# PROPOSITION À VALIDER — Vocabulaire contractuel (NON ACTIVÉ EN RUNTIME)

@dataclass(frozen=True)
class TrajectoryThermoCostBenefitVector:
    """
    Vecteur analytique produit par la couche Thermo / Path Compute pour UNE trajectoire candidate.
    Sigma vérifie la présence, la provenance et la cohérence structurelle de ce vecteur,
    mais NE RECALCULE PAS les coûts/bénéfices et ne devient pas le moteur économique.
    """
    # 1. Métriques canoniques existantes (periphery/energy_thermo.py, timeverse.py, operational_constance.py)
    pin: float | None = None                        # Unité : À SPÉCIFIER (défaut runtime actuel : sans dimension >= 1e-9)
    pout: float | None = None                       # Unité : À SPÉCIFIER
    energy_efficiency: float | None = None          # Formule canonique : pout / max(pin, 1e-9) ; seuil THETA_ENERGY = 0.2
    useful_work: float | None = None                # Bénéfice brut d'exécution (periphery/energy_thermo.py:5) — Unité : À SPÉCIFIER
    energy_cost: float | None = None                # Coût énergétique (periphery/energy_thermo.py:5) — Unité : À SPÉCIFIER
    compute_cost: float | None = None               # Coût de calcul (periphery/energy_thermo.py:5) — Unité : À SPÉCIFIER
    attention_cost: float | None = None             # Coût d'attention (periphery/energy_thermo.py:5) — Unité : À SPÉCIFIER
    recovery_cost: float | None = None              # Coût de récupération (periphery/energy_thermo.py:5) — Unité : À SPÉCIFIER
    thermo_debt: float | None = None                # Formule : energy_cost + compute_cost + attention_cost + recovery_cost - useful_work (THETA_THERMO_DEBT = 1.0)
    truth_score: float | None = None                # [0.0 .. 1.0] (periphery/energy_thermo.py:6)
    sigma_score: float | None = None                # [0.0 .. 1.0] (periphery/energy_thermo.py:6)
    sigma_truth_mismatch: float | None = None       # abs(sigma_score - truth_score) (THETA_MISMATCH = 0.35)
    trajectory_score: float | None = None           # (periphery/timeverse.py:6)
    trajectory_divergence: float | None = None      # (periphery/timeverse.py:5, THETA_TRAJECTORY_DIVERGENCE = 0.5)
    context_drift: float | None = None              # (periphery/timeverse.py:5, THETA_CONTEXT_DRIFT = 0.5)
    oc_S: float | None = None                       # Constance opérationnelle (periphery/operational_constance.py:5, THETA_OC = 1.0)
    irreversible_flag: bool = False                 # Booléen canonique existant (ActionCandidate.irreversible)

    # 2. Variables du cadre étendu (docs/thermodynamic_framework/THERMODYNAMIC_FRAMEWORK_PREFLIGHT_V0.md)
    state_energy_E_S: float | None = None           # E(S) : formule, unité et normalisation À SPÉCIFIER
    dissipation_D_A: float | None = None            # D(A) : lien exact avec thermo_debt / energy_efficiency À SPÉCIFIER
    irreversibility_cost_I_A: float | None = None   # I(A) : quantification scalaire au-delà de irreversible_flag À SPÉCIFIER
    transition_friction_F_A: float | None = None    # F(A) : normalisation de friction_symbolique.py À SPÉCIFIER
    coherence_score_C_A: float | None = None        # C(A) : articulation entre truth_score et oc_S À SPÉCIFIER
    risk_pressure_R_A: float | None = None          # R(A) : formule et normalisation À SPÉCIFIER
    temporal_stability_T_A: float | None = None     # T(A) : articulation avec trajectory_divergence / context_drift À SPÉCIFIER
    path_survivability_P_A: float | None = None     # P(A) = f(C(A), T(A), -D(A), -I(A), -R(A), -F(A)) : fonction f et poids À SPÉCIFIER


@dataclass(frozen=True)
class TrajectoryCandidateEvaluation:
    """
    Évaluation unitaire d'une trajectoire candidate combinant le profil de compétence B11,
    la composition d'organes B12 et le vecteur Thermo / Path Compute.
    """
    trajectory_id: str                              # Identité déterministe de chemin (conforme B9-R1/B9-R2 : ordre sémantique des étapes)
    domain: str                                     # Domaine cible (ex. bank, trading, ecom, gps_defense_aviation)
    task_ref: str                                   # Identifiant de la tâche (TaskRef)
    composed_organs: tuple[str, ...]                # Séquence ordonnée d'organes/outils composés (sans catalogue fermé)
    competence_profile_ref: str                     # Référence au ContextualCompetenceProfile (B11)
    competence_regime: str                          # "EVIDENCED_COMPETENCE" | "EVIDENCED_INCOMPETENCE" | "UNKNOWN_COMPETENCE"
    reliability_score: float | None                 # [0.0 .. 1.0] issu de B11 (None si UNKNOWN_COMPETENCE)
    calibration_metric: float | None                # [0.0 .. 1.0] issu de B11 (None si UNKNOWN_COMPETENCE)
    thermo_vector: TrajectoryThermoCostBenefitVector
    normalization_contract_id: str | None = None    # Contrat d'unités/normalisation appliqué (À SPÉCIFIER ; None par défaut)
    unit_status: str = "À_SPÉCIFIER"                # "NORMALIZED_0_1" | "RAW_DOMAIN_UNITS" | "À_SPÉCIFIER"
    provenance_refs: tuple[str, ...] = ()           # Sources exactes des mesures (B11, energy_thermo, timeverse, etc.)
    missing_metrics: tuple[str, ...] = ()           # Clés absentes ou non mesurées
    uncalibrated_fields: tuple[str, ...] = ()       # Champs relevant de formules/poids À SPÉCIFIER
    unknowns: tuple[str, ...] = ()                  # Inconnues explicites (ex. UNKNOWN_COMPETENCE, THERMO_SIGNAL_INCOMPLETE)
    constraints_violated: tuple[str, ...] = ()      # Contraintes métier ou invariants connus violés


@dataclass(frozen=True)
class TrajectoryComparisonProposal:
    """
    Contrat consultatif de comparaison entre plusieurs trajectoires candidates.
    Produit en amont de GuardX108, sans aucune autorité d'exécution ni de gate.
    """
    comparison_id: str
    domain: str
    task_ref: str
    candidates: tuple[TrajectoryCandidateEvaluation, ...]
    comparability_status: str                       # "COMPARABLE" | "PARTIAL_PARETO_ONLY" | "NOT_COMPARABLE"
    comparability_reason: str                       # Ex. même (domain, task_ref, normalization_contract_id) vs domaines hétérogènes
    advisory_ranking_order: tuple[str, ...] = ()    # Vide si NOT_COMPARABLE ou si f / poids sont À SPÉCIFIER hors dominance stricte
    pareto_non_dominated_ids: tuple[str, ...] = ()  # Trajectoires non dominées sur les métriques canoniques disponibles
    recommended_action_mode: str = "HOLD_FOR_MISSING_EVIDENCE"
    # Valeurs permises pour recommended_action_mode :
    # - "SUBMIT_CANDIDATE_TO_SIGMA"   (compétence étayée EVIDENCED_COMPETENCE + métriques Thermo complètes)
    # - "BOUNDED_EXPLORATION"         (UNKNOWN_COMPETENCE ou métrique Thermo manquante -> banc d'essai borné)
    # - "COGNITIVE_ESCALATION"        (conflit inter-trajectoires ou incertitude non résoluble localement)
    # - "HOLD_FOR_MISSING_EVIDENCE"   (données requises absentes avant soumission)
    advisory_only: bool = True
    decision_authority: str = "KX108_ONLY"
    thermodynamic_authority: str = "NONE"
    path_compute_authority: str = "NONE"
    sigma_authority: str = "NONE"
    emits_act: bool = False
    memory_write: bool = False
    kernel_mutation: bool = False
```

---

#### 7.2.3 Flux de signaux de bout en bout et séparation stricte des responsabilités

Le flux complet **B11 $\rightarrow$ B12 $\rightarrow$ Thermo / Path Compute $\rightarrow$ Sigma $\rightarrow$ GuardX108 $\rightarrow$ KX108** obéit à une séparation stricte de ce que chaque couche **consomme**, **produit** et **ne peut jamais faire** :

```
[1. B11 — Compétence & Calibration]
   Consomme : (Domain, TaskRef, Conditions, CandidateResources, EvidenceRefs)
   Produit  : ContextualCompetenceProfile (competence_regime, reliability_score, calibration_metric, unknowns)
   Interdit : Catalogue fermé ; traduire UNKNOWN_COMPETENCE en incapacité définitive ; émettre ACT / muter B10.
        │
        ▼
[2. B12 — Admissibilité Fonctionnelle & Composition Contextuelle]
   Consomme : ContextualCompetenceProfile(s) de B11 + contraintes de tâche
   Produit  : 1..N compositions candidates d'organes (séquences ordonnées conformes à B9)
              ou demande d'exploration bornée / escalade si UNKNOWN_COMPETENCE.
   Interdit : Sélection souveraine finale ; verrouillage permanent d'un organe ; contournement de GuardX108.
        │
        ▼
[3. Thermo & Path Compute — Évaluation Analytique des Coûts / Bénéfices / Viabilité]
   Consomme : Les trajectoires candidates issues de B12 + payload opérationnel
   Produit  : TrajectoryThermoCostBenefitVector par trajectoire + TrajectoryComparisonProposal (consultatif)
              + PeripheralSignalPacket pour la trajectoire soumise au pipeline d'exécution.
   Interdit : Émettre ALLOW / HOLD / BLOCK canonique ; émettre ACT ; muter le noyau ou B10.
        │
        ▼
[4. Sigma — Agrégation de Consensus Métier & Contrôle de Cohérence Sémantique]
   Consomme : État du domaine (Bank/Trading/Ecom/GPS) + PeripheralSignalPacket (incluant les signaux Thermo)
   Produit  : DomainAggregate + ThermoSigmaEvaluation dans extra_metrics["sigma_thermo_evaluation"]
              (contrôle des 7 clés, vérification d'intégrité structurelle, comparabilité GPS vs NOT_COMPARABLE,
              drapeaux canoniques ENERGY_INEFFICIENT / THERMO_DEBT_HIGH / SIGMA_TRUTH_MISMATCH).
   Interdit : Devenir le moteur économique ; recalculer les coûts/bénéfices métier ; inventer de nouveaux seuils,
              tolérances flottantes ou règles de gate ; propager unknowns=("THERMO_SIGNAL_INCOMPLETE",) dans
              DomainAggregate.unknowns.
        │
        ▼
[5. GuardX108 — Porte Déterministe d'Admissibilité]
   Consomme : DomainAggregate (contradictions, unknowns, risk_flags, confidence)
   Produit  : CanonicalDecisionEnvelope avec x108_gate ∈ {ALLOW, HOLD, BLOCK} (BLOCK > HOLD > ALLOW).
   Interdit : Émettre ACT directement sans la chaîne souveraine KX108.
        │
        ▼
[6. KX108 — Autorité Souveraine Finale d'Action (KX108_ONLY)]
   Consomme : CanonicalDecisionEnvelope (x108_gate == ALLOW) + Ticket OS3 + Replay PASS + Approbation/EAH
   Produit  : Autorisation souveraine d'exécution et scellage d'audit immuable.
```

---

#### 7.2.4 Composition contextuelle sans catalogue fermé et traitement de l'inconnue (`UNKNOWN`)

1. **Composition dynamique d'organes sans catalogue fermé :**
   - Lorsqu'un contexte opérationnel se présente, B12 peut assembler dynamiquement une chaîne ordonnée d'organes ou d'outils $C = \langle O_1, O_2, \dots, O_k \rangle$ (dont l'ordre est sémantique au sens de `B9-R2 : A → B → C != A → C → B`).
   - B11 n'exige pas que la chaîne $C$ figure dans une liste statique pré-enregistrée : il évalue la compétence de $C$ à partir :
     1. des preuves directes d'exécutions antérieures de la chaîne $C$ si elles existent (`EVIDENCED_COMPETENCE`),
     2. ou, à défaut, de la compatibilité typée des interfaces entre $O_i$ et $O_{i+1}$ et des profils élémentaires de chaque $O_i$, en qualifiant explicitement l'incertitude résiduelle de couplage dans `unknowns` (`UNKNOWN_COMPETENCE`).
2. **Traitement de l'inconnue (`UNKNOWN_COMPETENCE` ou métrique Thermo absente) sans verdict d'incapacité :**
   - Si une composition nouvelle reçoit `competence_regime = "UNKNOWN_COMPETENCE"` dans B11, ou si son évaluation thermodynamique présente des métriques manquantes (`status = "INCOMPLETE"`), le système **ne classe jamais cette trajectoire en `EVIDENCED_INCOMPETENCE` ni en interdiction permanente** (conformément à M32 `UNKNOWN != FALSE` et B9 `FAILED_PATH != FORBIDDEN_FOREVER`).
   - Trois issues consultatives graduées sont alors disponibles dans `TrajectoryComparisonProposal.recommended_action_mode` :
     1. **`BOUNDED_EXPLORATION` (Exploration bornée) :** Exécution d'une sonde en lecture seule, d'une simulation ou d'un banc d'essai borné (budget énergétique/calcul plafonné, `irreversible_flag = False`) afin d'acquérir les preuves manquantes et de convertir `UNKNOWN_COMPETENCE` en compétence étayée ou réfutée.
     2. **`COGNITIVE_ESCALATION` (Escalade cognitive) :** Mobilisation d'un organe de vérification ou d'analyse supplémentaire (rôles B7 `INVESTIGATOR` / `CRITIC` / `COMPARATOR` ou arbitrage humain) lorsque deux trajectoires candidates présentent des compromis incomparables.
     3. **`HOLD_FOR_MISSING_EVIDENCE` (Attente prudente) :** Maintien en attente temporaire tant que les prérequis d'observation ne sont pas réunis, sans altérer la rééligibilité future de la trajectoire dès que le contexte ou les preuves évoluent (`RETRYABLE` au sens de B9 §4).

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
Statut : ÉVALUATION CONSULTATIVE CANONIQUE + CORRECTIF C2 IMPLÉMENTÉS ; SPÉCIFICATION MULTI-TRAJECTOIRES (§7.2) EN PROPOSITION À VALIDER
Constat canonique :
- Faits runtime vérifiés et correction appliquée (tests/integration/test_thermo_sigma_semantic_coherence.py) :
  1. Consommation consultative des 7 métriques Thermo actives via ThermoCoherenceAgent et ThermoSigmaEvaluation
     (unknowns=("THERMO_SIGNAL_INCOMPLETE",) et proposed_verdict="HOLD" confinés au rapport consultatif
     sigma_thermo_evaluation sans propagation vers DomainAggregate.unknowns ; seuils canoniques THETA_ENERGY=0.2
     -> ENERGY_INEFFICIENT, THETA_THERMO_DEBT=1.0 -> THERMO_DEBT_HIGH, THETA_MISMATCH=0.35 -> SIGMA_TRUTH_MISMATCH ;
     comparabilité prouvée uniquement en GPS_DEFENSE_AVIATION et NOT_COMPARABLE en Bank/Trading/Ecom ; écarts de
     formule sans tolérance canonique rapportés comme NOT_EVALUATED_NO_CANONICAL_TOLERANCE).
  2. Correction C2 appliquée (periphery/sigma_bridge.py) : un recommended_gate="HOLD" émis uniquement par
     energy_thermo.py conserve les métriques et risk_flags Thermo dans DomainAggregate, mais n'est plus converti en
     unknown artificiel ("PERIPHERY_RECOMMENDS_HOLD") ni en cascade "TICKET_NOT_READY". Sigma expose sa
     recommandation consultative (proposed_verdict="HOLD") ; GuardX108 calcule toujours x108_gate à partir de ses
     contrats canoniques et KX108 conserve l'autorité souveraine (KX108_ONLY).
  3. Vérification runtime C1 et blocage documenté : dans le flux runtime canonique (run_control_plane ->
     compute_debt), payload["compute_cost"] est compté une seule fois dans total_debt (via thermo_debt ->
     energy_debt, tandis que computational_debt vaut 0.0). Un double comptage ne survient que si un appelant
     externe injecte manuellement extra_metrics["computational_debt"] en sus de payload["compute_cost"]. Faute de
     contrat d'unité/équivalence entre ΔC (computational_debt) et compute_cost (et compte tenu du scellage SHA-256
     de gencoin_debt_model.py et energy_thermo.py dans test_batch_execution_v0.py), aucune soustraction non
     canonique n'est introduite.
- Spécifié en §7.2 sous statut PROPOSITION À VALIDER (runtime_enabled = false) :
  Contrat typé de comparaison consultative multi-trajectoires (TrajectoryThermoCostBenefitVector,
  TrajectoryCandidateEvaluation, TrajectoryComparisonProposal), flux de signaux B11 -> B12 -> Thermo -> Sigma
  -> GuardX108 -> KX108, et mécanisme de composition ouverte / exploration bornée sur UNKNOWN_COMPETENCE.
- Questions restant À SPÉCIFIER / À ARBITRER avant toute activation runtime :
  1. Formule explicite et poids de P(A) = f(C(A), T(A), -D(A), -I(A), -R(A), -F(A)) (ou maintien en dominance de Pareto partielle).
  2. Unités et contrat de normalisation commune entre coûts et bénéfices par domaine.
  3. Contrat d'orthogonalité et d'unités entre payload["compute_cost"] (inclus dans thermo_debt) et la coordonnée ΔC extra_metrics["computational_debt"] en cas d'alimentation externe de computational_debt (blocage C1).
  4. Normalisation éventuelle de domain_sigma_score hors GPS et tolérance flottante canonique sur les formules.
Décision doctrinale : L'Orientation 03 et la proposition §7.2 restent EN ATTENTE DE VALIDATION PROPRIÉTAIRE.
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

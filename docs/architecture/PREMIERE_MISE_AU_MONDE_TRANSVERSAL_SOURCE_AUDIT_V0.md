# Audit transversal des sources — Première mise au monde V0

Status: SOURCE AUDIT / NO RUNTIME CHANGE

## Objet

Comparer les définitions historiques Image / Physique / Science / Temps / Espace / Causalité / GMS avec la chaîne réellement forgée F3→F11. Le but est d'identifier le prochain chantier sans inventer un nouveau World Model.

## Invariant général retrouvé

REALITY != OBSERVATION != MEASUREMENT != MEMORY != MODEL OUTPUT != DOMAIN STATE.

La chaîne F3→F11 fournit aujourd'hui un squelette de représentation et de gouvernance:
Observation -> WorldObservationV0 -> WorldStateV0 -> UDIP/Domain -> GuardX108 -> CanonicalDecisionEnvelope -> Proof.

Elle ne constitue pas encore un moteur universel de validation physique.

## 1. Physical / Scientific layer

### Définition source

Le corpus définit une périphérie physique/scientifique non souveraine. Un capteur ne livre pas directement l'état du monde. Une mesure suit le modèle conceptuel:

z_i(t) = h_i(x(t), e(t), theta_i) + epsilon_i(t)

La sortie utile doit conserver au minimum valeur/estimation, unité, temps, repère, incertitude, validité, provenance, calibration, qualité et contradictions.

Objets historiques proposés:
- PhysicalSignalEvent
- PhysicalSignalReport
- WorldStateCandidate
- PhysicalCoherenceScore
- SignalContradiction
- CalibrationReceipt
- ReplayablePhysicalProofCandidate
- PhysicalRiskHint

### Couverture F3→F11

Présent:
- observation/state candidat
- provenance/hash
- observed_at / valid_at
- uncertainty / contradictions / risk_flags
- frame_ref / latency_ms au pont multimodal
- GPS recorded-real conservateur
- causal_status avec CAUSAL_PROVEN protégé par evidence
- KX108_ONLY

Absent ou non généralisé:
- modèle de mesure explicite
- unité et précision/calibration normalisées
- paramètres instrument/capteur
- environnement de mesure
- limites instrumentales
- PhysicalSignalEvent/Report génériques
- PhysicalCoherenceScore
- CalibrationReceipt physique générique
- replay physique générique
- moteur de contraintes physiques/scientifiques

Verdict: PARTIAL. Le squelette récepteur existe; la Physical Signal Periphery générale n'est pas matérialisée.

## 2. Temps / espace / trajectoire

### Définition source

Les sources distinguent:
- observed_at
- received_at
- processed_at
- decided_at
- executed_at
- verified_at

Elles séparent temps du monde et temps du système, retard, ordre, fraîcheur, validité et historique.

Une trajectoire est une évolution N→N+1 d'un objet/état dans un ou plusieurs référentiels, pas seulement une suite de coordonnées GPS.

### Couverture F3→F11

Présent:
- observed_at
- valid_at
- space dict
- frame_ref
- latency_ms
- refs de world/domain state

Absent:
- modèle temporel multi-horloges canonique
- received/processed/decided/executed/verified comme chaîne conservée
- Transition/Trajectory universelle
- changement de référentiel typé
- BEFORE/AFTER/durée/expiration universels
- continuité et rupture universelles

Verdict: STRUCTURAL GAP. F3 a volontairement minimalisé cette zone; les supports historiques sont plus riches.

## 3. Causalité

### Définition source

Relations distinctes proposées:
TEMPORAL / CORRELATED / DERIVED / CAUSAL_ASSERTED / CAUSAL_PROVEN / UNKNOWN.

A avant B != A cause B.

### Couverture F3→F11

Présent:
- causal_status
- UNKNOWN par défaut
- CAUSAL_PROVEN exige evidence_refs
- generated content interdit de preuve causale physique

Absent:
- relation causale typée complète
- graph causal
- DERIVED/CORRELATED/CAUSAL_ASSERTED séparés
- règles de compatibilité entre temporalité et causalité
- preuve causale physique rejouable générique

Verdict: MINIMAL SAFETY CONTRACT ONLY.

## 4. Image / vision

### Définition source

Une image réelle est un témoignage candidat situé:
- asset/hash
- contexte capture/appareil/optique
- synchronisation temps
- spatial frame
- primitives visuelles
- signaux physiques indépendants
- prior state
- context graph
- candidate interpretations
- integrity report

La fusion exige compatibilité temporelle, spatiale, métrique et causale. Une majorité de capteurs ne crée pas la vérité.

Génération et perception restent séparées; toute partie non observée reste générée/hypothétique.

### Couverture F3→F11

Présent:
- modalité image possible
- source/hash/time/frame/latency
- generated flag
- GENERATED_OUTPUT_NOT_TRUTH
- candidate world state

Absent:
- ingestion asset/image réelle spécialisée
- capture context/calibration
- primitives visuelles
- profondeur/mouvement/géométrie
- prior state/context graph spécialisé
- IntegrityReport
- validation cross-modal spatiale/métrique/causale
- SceneSpec / génération contrôlée

Verdict: CONTRACT-LEVEL ONLY. F6 est un transport multimodal, pas une couche Vision.

## 5. Physique / Sciences

### Définition source

Le corpus sépare:
MATHEMATICS = forme / relations / invariants
PHYSICS = contraintes du monde
PERCEPTION = état observé
MEMORY = continuité
LANGUAGE = noms/intention
DOMAIN = sens spécialisé
COGNITION = exploration/interprétation
KX108 = autorisation gouvernée.

Primitives historiques:
OBJECT, STATE, POSITION, TIME, MOTION, TRAJECTORY, RELATION, CONSTRAINT, INVARIANT, TRANSITION, BEFORE/AFTER, POSSIBLE/IMPOSSIBLE, REVERSIBLE/IRREVERSIBLE, CAUSE HYPOTHESIS/CONSEQUENCE.

### Couverture F3→F11

Présent:
- entity_ref/state/relations/space/time minimal
- uncertainty/contradictions
- domaine séparé
- KX108 séparé

Absent:
- contraintes/invariants/transition typés
- possible/impossible
- motion/trajectory universels
- lois/modèles/équations/invariants comme objets consultables
- solveurs/moteurs scientifiques branchés sur MMonde

Verdict: NOT IMPLEMENTED AS SCIENCE ENGINE.

## 6. Thermodynamique

Deux branches doivent rester séparées:
1. Thermodynamique physique: lois/énergie/irréversibilité du monde physique.
2. Thermo computationnelle: entropy_score, dissipation, coût, stabilité, irreversibility comme heuristiques/mesures logicielles.

F3→F11 n'unifie pas ces deux branches et ne doit pas le faire.

Verdict:
- physical thermo: FUTURE PHYSICAL/SCIENCE ENGINE
- computational thermo: EXISTING PERIPHERAL/SHADOW WORK, NON-SOVEREIGN

## 7. GMS / géométrie sémantique

Le code Brody possède déjà un point cloud 21D avec axes de temporalité, fiabilité source, trajectoire, comportement, projection, mémoire, preuve, etc. Le corpus généralise l'idée à un objet canonique pouvant être projeté dans plusieurs espaces/référentiels sans perdre identité, temps, provenance et traçabilité.

F3→F11 ne construit pas GMS. Il prépare seulement le socket de conservation vers MMonde.

Verdict: EXISTING COGNITIVE GEOMETRY + MISSING CANONICAL GMS↔MMONDE TRAJECTORY CONTRACT.

## Conclusion architecturale

La prochaine forge ne doit pas être un démonstrateur ni un World Model monolithique.

Le premier trou transversal commun aux sources est:

TIME + SPACE + TRAJECTORY + TRANSITION + TYPED CAUSALITY
        ↓
situated measurement / physical evidence contract
        ↓
Physical / Vision / GMS adapters spécialisés

Ce socle doit rester représentation-only, sans mémoire, cognition, domaine ni autorité.

## Proposition de prochaine phase

Nom recommandé:
F12 — SITUATED WORLD DYNAMICS V0

Scope minimal:
- TimeEnvelopeV0: world/system timestamps sans inventer les timestamps absents
- SpatialFrameRefV0: référentiel explicite et transformations référencées
- TransitionV0 / TrajectoryV0: N→N+1, continuité, dérive, rupture
- RelationStatusV0: TEMPORAL/CORRELATED/DERIVED/CAUSAL_ASSERTED/CAUSAL_PROVEN/UNKNOWN
- MeasurementContextV0: unit, calibration_ref, precision/uncertainty, environment_ref, instrument/source refs
- conservation de provenance/evidence
- aucune loi métier/physique dans le Core
- aucune autorité

Puis seulement:
F13 Physical Signal Periphery V0
F14 Vision/Image Real V0
F15 GMS trajectory adapter
F16 science/constraint engines progressivement.

Aucune modification runtime n'est réalisée par cet audit.

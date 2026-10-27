# X108 / Obsidia — Glossaire canonique v1

## Noyau

**Obsidia**
Infrastructure cognitive audit-first, non décisionnelle, déterministe par construction, gouvernée par politiques explicites.

**OS0–OS1**
Noyau moteur déterministe. OS0 porte axiomes / contrat / IR / sandbox. OS1 orchestre parse → contrat → X-108 → exécution sandbox → décision.

**OS3**
Forge & Audit vérité. Capture exhaustive des traces, replay déterministe, comparaison attendu/observé, preuves auditables.

**OS4**
Hub JARVIS. Interface/cockpit non décisionnel, zones privée / interne / publique / régulateur.

**Cortex OS MCP**
Couche d’interopérabilité agents. Transporte les appels outils, les mappe vers la Policy Gate Obsidia, n’exécute rien hors gate.

## Gouvernance / Policies

**Policy Gate**
Point souverain d’autorisation/refus. Évalue scope, coût, outils autorisés, ticket, attestation MCP.

**policy.json**
Policy canonique déclarative : `no_write`, `max_cost`, `allowed_tools`, `time_window`, etc.

**Policy Compile**
Compilation déterministe de `policy.json` en structure runtime O(1) (`scope_mask`, `tool_bitmap`, flags, limits). Une policy non compilée est invalide en runtime.

**Tool Registry**
Source de vérité unique des tools autorisés par couche, avec scope, write, cost_class et ticket_required.

**MCP Attestation**
Vérification qu’un serveur MCP est bien celui attendu (challenge signé, hash cert, fingerprint runtime). Pas de fallback : attestation impossible = DENY.

## Traces / Preuve

**Event Schema**
Schéma canon de trace : `event_id`, `event_type`, `layer`, `timestamp`, `actor`, `session_id`, `request_id`, `payload_hash`, `decision_ticket_id`, `policy_id`, `result`, `parent_event_hash`, `event_hash`, `signature`.

**Decision Ticket**
Objet unique autorisant une exécution. Signé, à durée de vie limitée, non réutilisable, vérifiable offline.

**Replay Pack**
Artefact portable et offline regroupant manifest, roots, policy, tickets, traces, certs, revocations, signatures.

**Audit Report**
Rapport OS3 HTML/PDF canonique, signé globalement, avec ToC stable, roots, divergences, preuves cryptographiques.

**Violation Record**
Objet enrichi d’incident : code, sévérité, expected, observed, evidence, reaction, audit_required, signature.

## X-108

**X-108**
Gate temporel de gouvernance : aucune action irréversible sans suspension temporelle et cohérence d’invariant.

**X108Gate (pack moteur v1.0.0)**
Implémentation minimale : si action irréversible et `elapsed < min_wait_s`, alors HOLD ; sinon ACT.

**NON_INSTANTIABLE**
État amont : le contexte n’est pas assez formé pour être évalué proprement. En mode compat, peut ressortir en HOLD + reason_code.

**Champ interne**
Ensemble des variables qui décrivent le régime réel avant décision : irréversibilité, contradiction, under-spec, volatilité, réversibilité, cohérence, dissipation, pression.

**tau_eff**
Seuil temporel effectif requis avant permission.

**theta_eff**
Seuil effectif de cohérence requis.

**proof_eff**
Seuil effectif de preuve requis.

**Dissipation**
Décroissance réelle de la tension interne avant relâchement du gate.

**Hystérésis**
Mémoire courte évitant les oscillations absurdes HOLD/ALLOW/HOLD.

## Séparation verdict / gate

**market_verdict**
Lecture brute du marché / des agents.

**x108_gate**
Permission souveraine finale.

## Stress modes

**NO_SOURCE**
Contexte trop pauvre / pas assez de matière.

**DETUNE_SWEEP**
Désalignement progressif / dérive lente.

**SENSOR_SHUFFLE**
Incohérence ou permutation des signaux.

**SATURATION**
Emballement / surconfiance / surcharge.

**BROWNOUT_HYBRID**
Dégradation partielle du contexte.

## Termes moteur / structure

**IR**
Intermediate Representation. Alphabet L2 déterministe servant de représentation intermédiaire d’exécution (`VALUE`, `STATE`, `READ`, `WRITE`, `FLOW`, `COND`, `LOOP`, `CALL`, `RETURN`, `EVENT`, `TIME`, `ERROR`).

**IST**
Dans les packs inspectés : proxy de stabilité de trajectoire ou signal contextuel de stabilité ; pas encore défini constitutionnellement dans `40 spec.docx`.

**CMEC**
Dans les packs inspectés : indicateur de convergence réelle ou de cohérence de convergence ; pas encore défini constitutionnellement dans `40 spec.docx`.

**CSCN**
Terme évoqué dans les packs antérieurs comme cohérence structurelle / contradiction non résoluble gérée ; pas trouvé comme définition canonique explicite dans les nouveaux packs inspectés.

## Structural core

**Structural Core**
Gate d’équilibre structurel déterministe basé sur topologie pondérée : triangles, hexagone radial, pénalité d’asymétrie.

**Core-vs-World invariance**
Le score sur CORE doit rester inchangé sous modifications WORLD-only.

**S**
Score structurel du core calculé à partir de triangle mean + best hexagon - asymmetry penalty.

**Geometry motifs**
Module heuristique de détection triangle équilatéral / hexagone / ratio proche tétraédrique, destiné à OS3 audits et sandbox, pas à une preuve formelle.

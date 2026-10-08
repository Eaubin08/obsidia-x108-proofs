# V0.1 ENTREPRISE — AUDIT DE CONVERGENCE UDIP / BINDER / CAPABILITY / MONDE

Date : 2026-10-08  
Type : **READ_ONLY_ARCHITECTURE_AUDIT**  
Branche de constat : `audit/v01-enterprise-udip-convergence-20261008`  
Référence d'intégration : `feat/obsidia-universal-cross-domain-conformance-v0` @ `7a54bb5cb74fd3f88b1fb657db38a012246b2c3a`  
**Verdict : ADAPT_EXISTING_STACK; NO_NEW_CORE; NO_MAIN_MERGE; NO_REAL_SOURCE_ACTIVATION.**

## 1. Définition historique vs implémentation

Le rapport V0.1 de juillet définit un **cockpit sector-agnostique** branché à la stack effective d'une organisation : observer et qualifier les sources, reconstruire objets/personnes/processus/relations et l'écart déclaré–réel, diagnostiquer, proposer/simuler, passer par la gouvernance, mesurer les effets.

La V0.1 n'est ni une simple surcouche CRM/connecteurs, ni une nouvelle autorité. Le **Company Model** décrit l'entreprise; le **Domain Pack** préserve le sens métier; les **adapters / capacités** décrivent les outils qui existent; **KX108** tranche une structure gouvernable; **Binder/activation** vérifie le droit effectif après le verdict; **Monde** projette l'état prouvé.

Sources historiques :
- [OBSIDIA Vision globale, architecture et plan V0.1 (17 juillet)](https://docs.google.com/document/d/11FW5N6TpISZy5xyVMhNWHbGq_WWNcNpW7IsPMJG552M/edit)
- [OBSIDIA V0.1 — Rapport vision et architecture (21 juillet)](https://docs.google.com/document/d/1utvq1Y6M75dLGs8t-kYUvT2RTuIGlfCV/edit)
- [UDIP V0 architectural specification](https://github.com/Eaubin08/obsidia-x108-proofs/blob/codex/udip-domain-packs-v0/docs/UNIVERSAL_DOMAIN_INTEGRATION_PROTOCOL_V0.md)
- [Doctrine ontology/layers](https://github.com/Eaubin08/obsidia-x108-proofs/blob/docs/obsidia-ontology-layer-contracts-v0/docs/architecture/OBSIDIA_ONTOLOGY_AND_LAYER_CONTRACTS_V0.md)

Les documents historiques sont des **objectifs et contrats**, pas une attestation d'une V0.1 industrielle livrée.

## 2. Matrice REUSE / ADAPT / MISSING (état au 8 octobre)

| Surface | Décision | Preuve existante | Écart précis |
|---|---|---|---|
| UDIP invariants, frontières et classification domaines | **REUSE** comme contrat | `docs/UNIVERSAL_DOMAIN_INTEGRATION_PROTOCOL_V0.md` @ `codex/udip-domain-packs-v0` | SPEC_ONLY historique : ne pas l'appeler runtime universel final |
| Domain Pack standard / registre de 16 domaines | **ADAPT** | `udip/DOMAIN_PACK_STANDARD.md`, `udip/domain_registry.yaml`, `planning/DOMAIN_PACK_MANIFEST_COHERENCE_AUDIT_V0.md` | Les 16 packs restent `SCAFFOLD_ONLY` dans cet audit de branche; zéro object map promu; réconcilier la maturité des domaines modernes séparément |
| Domaine portable hors kernel | **REUSE** | `docs/architecture/F25_FIRST_CLASS_DOMAIN_EXTENSION_RESOLVER_V0.md`, `scripts/obsidia_governed_runtime_cycle_v1.py` sur branche V0.1 actuelle | Resolver explicitement fourni par host de confiance; pas d'autochargement plugin; ne jamais accepter une enveloppe ALLOW fabriquée |
| Source onboarding / registry / provenance | **REUSE** | `periphery/native_sources/source_onboarding_v0.py`, `source_registry_v0.py` | Contrat à deux clés, source-specific; pas encore parcours organisationnel global ni vérification d'une habilitation entreprise réelle |
| Universal provider capability + bindings | **REUSE**, puis **ADAPT** | `periphery/universal_enterprise_stack_adapter_v0.py`, tests swap | Provider swap prouvé en fixtures; pas de découverte automatique de SaaS réels, pas de sémantique métier déduite du manifest |
| Capability Graph / Relay | **ADAPT** | `scripts/obsidia_capability_graph_v0.py`, `scripts/obsidia_relay_v0.py` @ `main` | Catalogue route mission/native; ne représente pas à lui seul l'inventaire d'une entreprise/tenant; ne pas créer un second router souverain |
| Provider Binder cognitif (CG9) | **REUSE** dans son périmètre | `scripts/obsidia_cognitive_provider_binder_v0.py`, `scripts/providers/provider_binder_v0.py` | Admissibilité/résultats fournisseur cognitif ≠ permission d'exécution dans une organisation |
| Permission post-KX / activation / tickets | **REUSE**, puis **ADAPT** | `periphery/world_calls/external_runtime_activation_policy_v0.py`, `live_sovereign_ticket_v0.py`, `bounded_connector_executor_v0.py` | Policy V0 explicite et désactivée par défaut; associer rôle/scope organisationnels prouvés, révocations et lifecycle; KX ALLOW n'est pas permission |
| UDIP MMonde → DomainState → GovernancePayload | **ADAPT**, ne pas merger brut | `periphery/udip/contracts_v0.py` @ `feat/premiere-mise-au-monde-udip-v0`; CSSA `F1_UNIVERSAL_DOMAIN_CONTRACT_V0.md` | L'ancienne version impose WorldState; CSSA rend `upstream_state_ref` optionnel avec justification. Résoudre ce conflit de contrat sans contraindre tous les métiers à passer par MMonde |
| Office native CRM/TASK/Intake + receipts | **REUSE** pour démo administrative | `periphery/native_ops/`, `periphery/native_sources/enterprise_office_full_loop_e2e_v0.py` | Couverture entreprise complète non revendiquée; pas de vérité de source réelle CSSA |
| Monde read-model + UI | **REUSE** en projection, **ADAPT** pour visualisation | `periphery/native_ops/monde_native_read_model_v0.py` et `monde-obsidia/src/NativeEnterpriseView.tsx` | Affiche objets natifs persistés vérifiés; pas encore graphe multi-entreprise et dépendances organisationnelles, pas de mutation UI |
| Company Model vivant (identités, équipes, processus, outils, dépendances, responsabilités, écarts déclaré/observé) | **MISSING / NON_PROUVÉ DANS LES CHEMINS AUDITÉS** | Vision V0.1 Drive; `OrganizationIdentity` reste partiel / optionnel dans UDIP historique | Pas de cycle bout-en-bout vérifié retrouvé qui construit, historise, met à jour et prouve ce modèle transversal |
| Cycle d'entrée de l'entreprise (instance, isolation entre entreprises, délégation, revalidation, révocation et drift fournisseur) | **MISSING / NON_PROUVÉ DE BOUT-EN-BOUT** | Source onboarding individuel + capability bindings | Ne pas déduire les droits d'une organisation d'une connexion technique, ni inférer que multi-provider = multi-tenant |
| Réévaluation après action / mesure de valeur et causalité | **MISSING / NON_PROUVÉ COMME BOUCLE V0.1 ENTREPRISE** | Receipts/replay disponibles, ambition Drive | Receipt d'exécution ≠ mesure de résultat organisationnel; exiger avant/après et attribution bornée |

**MISSING** signifie « non identifié ou non prouvé dans les branches et surfaces inspectées »; ce n'est pas la preuve de l'inexistence dans tout l'écosystème, notamment PC local / worktrees non accessibles à cet audit.

## 3. Contradictions / pièges à ne pas reproduire

**B1 — deux Binder différents :** le Binder cognitif CG9 sélectionne/valide des fournisseurs de capacités; le post-KX108 Binder / activation/ticket borne un droit d'exécution. Ne pas fusionner leurs rôles.

**B2 — UDIP historique ≠ branche courante :** `codex/udip-domain-packs-v0` @ `c15249aafd72c7e05c1adfa16cf3b516c20054d6` est **divergée** de `main` (25 ahead / 134 behind au contrôle du 8 octobre). La branche de conformance courante est 185 commits ahead / 0 behind de main à ce contrôle. **Interdiction de merger UDIP en bloc**; reprise sémantique sélective avec tests.

**B3 — WorldState pas obligatoire partout :** `feat/premiere-mise-au-monde-udip-v0` @ `c36456d345b158b35055cba0763b45751badf3b4` conserve un pont MMonde spécifique. La branche CSSA `F1` explicite pourquoi Administration ne doit pas exiger MMonde. Une entrée domaine peut provenir de sources réelles sans WorldState.

**B4 — universel ne veut pas dire prêt chez tout client :** `OBSIDIA_UNIVERSAL_CROSS_DOMAIN_CONFORMANCE_V0` valide des scénarios **SIMULATED_NOT_OBSERVED**, pas des adaptateurs SaaS industriels ni toutes les lois métier.

**B5 — Domain Pack non souverain :** tout plugin de domaine est capable de traduire mais ne doit pas produire `CanonicalDecisionEnvelope`, exécuter, accorder permission, ni modifier GuardX108.

**B6 — source ≠ entreprise :** une boîte mail personnelle, une API techniquement accessible ou une source publique ne prouvent ni l'identité ni l'accord du détenteur pour une intégration interne.

**B7 — découpage informatique ≠ fonctionnement réel :** un outil listé dans la stack ne prouve pas sa route active, ses utilisateurs, ses processus ou son impact causal.

**B8 — frontière de vérité de Monde :** pas de données métier inventées pour remplir des catégories `UNAVAILABLE`.

## 4. Domaines de démonstration à conserver

- **Trading** : `Eaubin08/OBSIDIA_TRADING@master` @ `6dfee86778810829a2e9d89d3cc6caaaaa0996e9`. Chemin Native vs External converge canoniquement; **PAPER only**; README avoue que le vrai X108 n'est pas connecté dans ce repo (client KX fixture, client réel indisponible fail-closed). Ne jamais affirmer une exécution réelle souveraine.
- **GPS/Défense/Aviation** : `Eaubin08/obsidia-gps-defense-@main` @ `db1b1777faaa598f08e314c915b274520e5f601b`. Preuves GNSS/RF enregistrées, mais ni attaque RF réelle prouvée ni commande appareil/certification; `RealityAuthenticityGate` relève du profil physique.
- **CSSA** : `Eaubin08/cssa-v01--entreprise-universelle-domaien-obsidia-@feat/f3h-h-cssa-real-readonly-pilot-preflight-v0` @ `a3125ce211e0c55d6608b39396f1f7633dbab72c`. Cas administratif utile, mais pas d'accès réel aux outils internes du club; ne pas promouvoir de fixtures en faits.

## 5. Plan de convergence recommandé AVANT nouvelle Forge

### C0 — Réconciliation des contrats existants (READONLY)

Comparer UDIP spec, source identity, F2.5 runtime resolver, CSSA F1, provider manifests, Binder/activation et Monde. Pour chaque interface : entrée, sortie, propriétaires, non-droits, provenance, schéma, version, test, branche/SHA, statut de preuve. **Pas de nouveau core ni nouveau bus.**

### C1 — Company Model V0 comme projection **avec preuves**

Spécifier (sans présumer finalité des noms) : `OrganizationRef`, `TeamRoleRef`, `ToolInstanceRef`, `ProcessRef`, `ResponsibilityRef`, `DependencyRef`, `SourceRef`, `DomainBindingRef`. Chaque relation garde provenance, scope, statut (déclaré/observé/testé/prouvé), temps de validité, inconnues et révocation. Ne jamais transformer un organigramme documentaire en accès réel.

### C2 — Registration & lifecycle des stacks

Déclarer des capacités et scopes **par instance d'entreprise**; séparer isolation, identity, source onboarding, Domain Pack, provider binding, KX, permission, executor et receipt. Tester `SOURCE_REVOKED`, provider changé, capacité supprimée, mauvaise entreprise, droits inconnus, propriétaire non confirmé. Aucune découverte de code fournisseur arbitraire.

### C3 — Un seul E2E de reconstructions/transformations

Une entreprise simulée composée de deux domaines et deux fournisseurs d'outils, puis :
`source attestée → état organisationnel → Domain Pack → intention/proposition → KX108 → permission → sandbox receipt → avant/après observé → Monde`.
Test négatif du changement de fournisseur, d'un rôle manquant, du faux effet revendiqué et du croisement inter-entreprise. KX unchanged.

### C4 — Pilotes sectoriels différenciés

Comparer Trading (PAPER), GPS (READONLY evidence) et CSSA (public/shadow). Classer `SUPPORTED / PARTIAL / UNSUPPORTED` sur les **contrats réels** de chaque domaine, sans créer un moteur de trading, un système GNSS ou une comptabilité générique.

### C5 — Monde V0.1

Projeter le Company Model réel/persisté et les preuves, en distinguant observé / seulement déclaré / manquant. Les fonctions mutantes doivent rester hors de la projection et dans le rail gouverné.

## 6. Conditions d'acceptation de la future Forge

1. **Mêmes contrats**, aucune modification de `sigma/guard.py`, `sigma/contracts.py` ni `proofs/lean/` pour adapter une entreprise.
2. Une organisation peut avoir plusieurs Domain Packs; un Domain Pack peut servir plusieurs organisations, avec permissions/bindings distincts.
3. Deux entreprises ne partagent jamais implicitement sources, secrets, actions, state stores, approbations, receipts ou idempotency scopes.
4. Retirer/remplacer le fournisseur ne change ni intention métier ni autorité KX108, mais oblige à revalider les permissions et les bindings; aucune exécution sans approbation exacte.
5. Données et règles métiers ne remontent jamais dans le kernel; `UNKNOWN`, contradiction et perte de traduction sont explicites.
6. Une observation sans attestation peut être représentée comme observation, jamais comme vérité ou licence d'actuation.
7. Monde projette seulement les preuves existantes; `UNAVAILABLE` reste légitime.
8. Tests `HOLD/BLOCK` non contournables; aucun effet externe réel en sandbox.
9. Comparaison mesurable du déclaré / observé / testé / prouvé avec receipts et écarts.
10. Aucun `main` push/merge, aucune connexion réelle non autorisée.

## 7. Sources techniques à prendre dans la Forge

- [UDIP contract](https://github.com/Eaubin08/obsidia-x108-proofs/blob/codex/udip-domain-packs-v0/docs/UNIVERSAL_DOMAIN_INTEGRATION_PROTOCOL_V0.md)
- [UDIP pack registry / standard](https://github.com/Eaubin08/obsidia-x108-proofs/blob/codex/udip-domain-packs-v0/udip/DOMAIN_PACK_STANDARD.md)
- [UDIP MMonde bridge](https://github.com/Eaubin08/obsidia-x108-proofs/blob/feat/premiere-mise-au-monde-udip-v0/periphery/udip/contracts_v0.py)
- [F2.5 domain extension](https://github.com/Eaubin08/obsidia-x108-proofs/blob/feat/obsidia-universal-cross-domain-conformance-v0/docs/architecture/F25_FIRST_CLASS_DOMAIN_EXTENSION_RESOLVER_V0.md)
- [Native onboarding](https://github.com/Eaubin08/obsidia-x108-proofs/blob/feat/obsidia-universal-cross-domain-conformance-v0/periphery/native_sources/source_onboarding_v0.py)
- [Universal stack adapter](https://github.com/Eaubin08/obsidia-x108-proofs/blob/feat/obsidia-universal-cross-domain-conformance-v0/periphery/universal_enterprise_stack_adapter_v0.py)
- [Runtime capability graph](https://github.com/Eaubin08/obsidia-x108-proofs/blob/main/scripts/obsidia_capability_graph_v0.py)
- [Provider binder](https://github.com/Eaubin08/obsidia-x108-proofs/blob/main/scripts/providers/provider_binder_v0.py)
- [Activation policy](https://github.com/Eaubin08/obsidia-x108-proofs/blob/feat/obsidia-universal-cross-domain-conformance-v0/periphery/world_calls/external_runtime_activation_policy_v0.py)
- [Monde native projection](https://github.com/Eaubin08/monde-obsidia/blob/feat/native-enterprise-interrepo-freeze-v0/docs/NATIVE_ENTERPRISE_READ_MODEL_V0.md)

## 8. Freeze / actual scope

**Audit-only** : lecture des documents Drive historiques, des branches GitHub, des README de Trading/GPS/CSSA/Monde et des surfaces du code. Pas d'exécution de régression, de forge, de migration, de connexion live ou de constat du PC local.

`REUSE` = réutiliser le contrat testé dans ses limites; `ADAPT` = couture ciblée à démontrer; `MISSING` = preuve/implémentation non retrouvée sur le périmètre inspecté. L'audit ne certifie pas le fonctionnement industriel de la V0.1.

**Décision : ne pas créer `STACK_FEDERATION_V0` comme architecture indépendante. La construire plus tard, si besoin, comme capacité périphérique de la V0.1 via réconciliation C0 → Company Model C1 → lifecycle C2.**

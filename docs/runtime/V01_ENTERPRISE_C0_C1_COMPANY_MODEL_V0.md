# V0.1 — C0/C1 Convergence et Company Model (première tranche)

Date: 2026-10-08  
Base: `audit/v01-enterprise-udip-convergence-20261008` (PR #85)  
Branche: `feat/v01-c0-c1-company-model-contract-v0`  
**Statut: CONTRACT/READ_MODEL_PROOF_ONLY — ni production, ni ingestion réelle.**

## C0 — on raccorde, on ne réinvente pas

Registre dans `V01_ENTERPRISE_C0_CONTRACT_CONVERGENCE_V0.json` :
12 frontières avec owner, provenance Git, schéma/surface, inputs, outputs,
non-droits, degré de maturité, décision REUSE / ADAPT / NEW.

UDIP / Domain Pack = sens métier ; Capability Graph = route descriptive ;
NativeSourceRegistration = source & autorisation spécifique ;
UniversalEnterpriseAdapter = outils et capacités ;
F2.5 resolver = agrégation non souveraine ;
KX108 = décision ;
activation/policy/ticket = permission et exécution bornée ;
Monde = projection readonly.

**NE PAS merger en bloc** `codex/udip-domain-packs-v0` (divergée de main)
ou `feat/premiere-mise-au-monde-udip-v0`. Une entreprise n'a pas à
fournir obligatoirement un WorldState/MMonde pour intégrer un domaine.

Pas d'orchestrateur souverain, nouveau Binder, second Relay ou bus.

## C1 — premier Company Model, sans transformer les revendications en faits

`periphery/company_model_v0.py` fournit les contrats :

- `CompanyNodeV0` : ORGANIZATION, TEAM_ROLE, TOOL_INSTANCE, PROCESS,
  RESPONSIBILITY, DEPENDENCY, SOURCE, DOMAIN_BINDING ;
- `CompanyRelationV0` : HAS_ROLE, USES_TOOL, OPERATES_PROCESS,
  HAS_RESPONSIBILITY, DEPENDS_ON, HAS_SOURCE, BINDS_DOMAIN, REPORTS_TO ;
- `company_model_snapshot_v0` : graphe déterministe par entreprise,
  empreintes sur chaque objet et sur l'ensemble ;
- `verify_company_model_snapshot_v0` : vérification et reprise JSON.

Chaque objet possède un `organization_id` explicite, un identifiant local,
une date UTC-offset, provenance, évidence optionnelle/obligatoire selon
le niveau de revendication, et une empreinte.

### Séparer degré de déclaration et degré de vérité

```text
claim_state:
  DECLARED | OBSERVED_CLAIM | TESTED_CLAIM | PROVEN_CLAIM

verification:
  UNVERIFIED_ORGANIZATIONAL_CLAIM
```

Même `PROVEN_CLAIM` n'est **pas** une preuve attestée. Ce nom reflète
seulement la formulation fournie par la source. La promotion réelle vers un
état "observé par système", "validé par humain habilité" ou "preuve vérifiée"
reste C2, via les contrats existants d'identité, autorisation et provenance.

Pas de propriété `source_id` d'une autre entreprise inférée par simple
existence. Une source inscrite n'atteste pas son propriétaire institutionnel.
Aucun `KX108 ALLOW` ni permission Binder déduits de ce graphe.

### Isolation inter-entreprises

Le modèle refuse :
- nœud ou relation d'une autre entreprise ;
- racine entreprise absente ou doublée ;
- nœud dupliqué, relation pendante, ID invalide ;
- empreinte falsifiée ou tentative d'autorité ;
- revendication non déclarative sans référence d'évidence.

Les mêmes noms d'outils ou domaines sont possibles chez plusieurs
entreprises : **les snapshots, espaces de noms et relations restent séparés**.
Cela ne constitue pas encore une preuve d'isolation des futurs stockages ou
exécuteurs. C2 devra imposer isolation des secrets, approvals, receipts,
idempotency et révocations *au point d'exécution*.

### Limites volontaires

- aucun scanner du système d'information ;
- aucune collecte Gmail/Drive/GitHub en production ;
- pas de base persistée, ni API de mutation ;
- pas de droits multi-tenant en production ;
- pas de vérification d'habilitation humaine réelle ;
- pas de règle métier/domain pack dans le modèle ;
- aucune exécution physique, trading ou provider.

La chaîne C0/C1 n'exécute jamais de code tiers. Les tests sont purement
locaux et utilisent seulement des fixtures de deux entreprises.

## Acceptation visée

1. C0 registre explicite et références source conservées.
2. C1 deux entreprises avec mêmes instances locales sans contamination.
3. Graphe déterministe avec roundtrip JSON et hashes.
4. Provenance/ambiguïté non silencieusement promue en vérité.
5. Droits d'action/autorité interdits dans toute la surface.
6. Tests de corruption et refus des relations inter-entreprises.
7. Régressions existantes de conformance C0/UDIP et Universal Stack intactes.
8. 0 fichier protégé KX108, 0 merge main.

## Prochaine tranche

**C2 — organisation source + provider lifecycle** :
lier une instance entreprise à une source réellement attestée, un propriétaire
habilité et un ensemble de capacités *révocable*, sans utiliser des
références de preuve déclaratives comme permissions.

Puis C3 : un E2E de deux entreprises/two providers, avant/après et Monde.

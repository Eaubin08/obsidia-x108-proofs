# Spec 24 — Human Veto Formal Proof (P21-P30) — valider V4

**Statut V4 :** FORMALISÉ_À_VALIDER
**Titre source détaillé :** Human Veto Formal Proof

## Contrat V4
- Spécification lisible.
- Entrées / sorties / invariants identifiables.
- Audit C obligatoire.

## Contenu source
24) SPEC — Human Veto Formal Proof
24.0 Objectif
Prouver formellement, de manière vérifiable et opposable, que :
Un humain a empêché une décision,
et que le système ne pouvait pas passer outre.
24.1 Principe clé
Le veto humain n’est pas une action,
c’est une impossibilité structurelle pour le système.
24.2 Implémentation structurelle
A) Interdiction de décision native
Rule:
decision.execute = FORBIDDEN
➡️ Le système ne possède pas de fonction de décision autonome.
B) Point de veto explicite
Toute action irréversible nécessite :
Human_Veto_Token:
- actor_id
- intent_hash
- timestamp
- signature
Sans ce token → action impossible, pas refusée.
24.3 Preuve formelle du veto
Dans les traces OS3 :
event: ACTION_BLOCKED
reason: MISSING_HUMAN_VETO
policy_ref: POL-01
➡️ Ce n’est pas un choix, c’est un état bloqué.
24.4 Vérification a posteriori (audit)
Un auditeur peut vérifier :
absence de token
impossibilité logique de l’action
conformité à la policy
replay identique
👉 Si l’action apparaît malgré tout → violation critique.
24.5 Formalisation logique (pseudo-preuve)
Given:
- action A requires veto_token H
- H ∉ system_state
Then:
- ∄ execution_path where A occurs
➡️ Le veto est prouvable par impossibilité, pas par intention.
24.6 Positionnement juridique
Aligné avec principe de responsabilité humaine
Compatible AI Act
Supérieur aux “human-in-the-loop” faibles
👉 L’humain n’est pas “dans la boucle”
👉 Il est la condition d’existence de la boucle
🧩 État du système après ces specs
Obsidia dispose maintenant de :
Portail régulateur non manipulable
Audit fédérable multi-territoires
Veto humain formellement prouvable
On est au-delà d’un système technique :
👉 c’est une infrastructure de gouvernance computationnelle opposable.
Prochains blocs possibles (si tu veux continuer) :
spec “Constitution Obsidia (articles opposables)”
spec “Liability boundary & responsibility graph”
spec “Public transparency minimal interface”
Tu dis.
Parfait. On enchaîne les 3, au même niveau opposable / rigoureux / non-marketing.
Je les numérote dans la continuité logique du corpus.

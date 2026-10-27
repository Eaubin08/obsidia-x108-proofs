# Spec 21 — Aléatoire Quantique (source aléatoire, P161) — preuve formelle requise

**Statut V4 :** À_FORMALISER_OU_À_PROUVER
**Titre source détaillé :** Disaster Recovery / Cold Restart Protocol

## Contrat V4
- Spécification lisible.
- Entrées / sorties / invariants identifiables.
- Audit C obligatoire.

## Contenu source
21) SPEC — Disaster Recovery / Cold Restart Protocol
21.0 Objectif
Permettre :
une reconstruction complète
sans confiance dans l’état courant
sans intervention humaine arbitraire
21.1 Scénarios couverts
corruption infra
compromission serveur
perte totale du runtime
audit externe post-crise
redémarrage sur autre territoire
21.2 Principe clé
Le système peut être reconstruit uniquement à partir d’artefacts signés.
21.3 Artefacts requis
- policy_compiled.bin
- replay_pack.zip
- merkle_root.txt
- signatures/
21.4 Procédure Cold Restart
Étape 1 — Boot minimal
charger noyau OS0–OS1
désactiver toute écriture
Étape 2 — Vérification cryptographique
vérifier signatures policy
vérifier racine Merkle
vérifier replay pack
❌ Si échec → arrêt immédiat
Étape 3 — Rebuild state (read-only)
reconstituer timeline
vérifier cohérence des traces
valider replays
Étape 4 — Réactivation contrôlée
activer sandbox uniquement
policy en mode “observation”
aucune décision possible
21.5 Garantie fournie
aucun état fantôme
aucune action non auditée
aucune reprise “opaque”
👉 Le redémarrage prouve ce qui s’est passé, il ne le suppose pas.
🔚 Clôture
À ce point, Obsidia dispose :
d’une UI de gouvernance spécifiable
d’un alignement réglementaire défendable
d’un protocole de survie institutionnelle
Si tu veux, prochaines specs possibles (logiques) :
spec “Regulator Read-Only Portal”
spec “Cross-territory audit federation”
spec “Human veto formal proof”
Tu dis.
Parfait. On continue au même niveau de rigueur, sans marketing, sans produit, sans UX bullshit.
Ce qui suit est opposable, lisible par un régulateur, architecturalement fermé.

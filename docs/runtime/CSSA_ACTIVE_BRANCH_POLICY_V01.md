# CSSA V0.1 — règle de branche active et reprise C2

Branche de travail UNIQUE : `feat/cssa-v01-active`.
Branche de référence : `main` (aucune modification ni merge sans demande explicite).
État importé : tous les commits de la chaîne C2.1 → C2.48 (HEAD C2.48 `befa51cc87f0a216566bb14c07615f9cf30dfa7b`) + correction du test C2.28 `c80ec3ab4dfbe5087f66f4bcc6bf5807798a219a`.

## Nettoyage GitHub du 8 octobre 2026
Les 48 PR C2.x (#94…#148, numérotation non contiguë) ont été clôturées SANS MERGE : leur contenu est déjà ancêtre de cette branche unique. PR d'audit #149 également clôturée; rapport conservé dans sa branche `audit/v01-c2-01-48-freeze-20261008`. Les branches historiques sont conservées pour traçabilité et récupération; les PR d'autres chantiers ne sont pas modifiées.

## Règle pour les prochains « Go »
1. Commit sur `feat/cssa-v01-active`, sans créer une branche ou une PR par étape.
2. Exécuter tests ciblés ET régression générale à chaque correctif pertinent.
3. Ne pas confondre succès d'une CI ciblée avec succès complet.
4. Garder tous les traitements CSSA en simulation `HOLD/BLOCK`, sans envoi réel.
5. Revue/intégration vers main uniquement sur instruction explicite, avec comparaison et contrôle de sécurité.
6. Ne pas pousser sur les dépôts kernel ou Monde depuis ce chantier.

## Risques restant à traiter
Isolation OS des permissions du stockage, authentification IPC, preuves indépendantes et adoption réelle du CRM / calendrier / email CSSA. Aucun de ces points n'est déclaré prêt en production.

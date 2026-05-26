# Spec 06 — Cryptographique (keys, rotation, trust chain, P47-P63)

**Statut V4 :** À_FORMALISER_OU_À_PROUVER
**Titre source détaillé :** Cryptographique (keys, rotation, trust chain)

## Contrat V4
- Spécification lisible.
- Entrées / sorties / invariants identifiables.
- Audit C obligatoire.

## Contenu source
6) SPEC — Cryptographique (keys, rotation, trust chain)
6.0 Objectif
Garantir :
authenticité (qui émet quoi)
intégrité (non altération)
rejouabilité (preuve)
souveraineté offline (pas de dépendance CA externe)
6.1 Types de clés (minimales)
A) Core Signing Key (CSK)
signe : Decision Ticket
appartient à : OS0–OS1
usage : strict
B) Trace Signing Key (TSK)
signe : Event et ViolationRecord (optionnel mais recommandé)
appartient à : chaque couche (OS4, SANDBOX, AGENT)
C) Audit Signing Key (ASK)
signe : OS3 Replay Report
appartient à : OS3
6.2 Algorithmes (canon)
Signature : Ed25519
Hash : SHA-256
IDs : UUIDv7 (ordre temporel natif)
6.3 Trust chain (chaîne de confiance)
Root of Trust (offline)
Une Root Key (RK) offline (stockage froid)
sert uniquement à signer :
la Core Public Key
les Key Rotation Certificates
Schéma de certificat minimal
{
  "cert_id": "uuid",
  "issued_at": "timestamp",
  "issuer": "ROOT",
  "subject": "OS0_CORE_KEY",
  "public_key": "base64",
  "valid_from": "timestamp",
  "valid_to": "timestamp",
  "signature": "ed25519"
}
6.4 Rotation des clés
Règles simples
CSK : rotation rare (ex : trimestrielle) + procédure lourde
TSK : rotation régulière (mensuelle) possible
ASK : rotation régulière (mensuelle) possible
Process canon
Générer nouvelle clé
Publier KeyRotationCertificate signé par RK
Accepter une période de chevauchement (overlap_window)
Révoquer l’ancienne (revocation record signé)
6.5 Révocation
Schéma KEY_REVOCATION_RECORD :
{
  "revocation_id": "uuid",
  "key_id": "OS4_TSK_2026_02",
  "revoked_at": "timestamp",
  "reason": "COMPROMISE | ROTATION | DECOMMISSION",
  "signature_root": "ed25519"
}
Toute signature d’une clé révoquée après revoked_at ⇒ VIOLATION (S4)
6.6 Storage & sécurité (minimum)
6.7 Vérification offline (contrat)
Un vérificateur doit pouvoir valider, sans réseau :
signatures tickets
signatures rapports OS3
intégrité hash-chain
validité certs + revocations
Si tu veux, je peux enchaîner directement avec :
spec “Replay Pack format” (bundle standard traces + tickets + policy + root hashes)
spec “Audit report HTML/PDF canon” (table matières cliquable + signature globale)
spec “Tool adapter MCP → Obsidia policy gate” (mapping tools / scopes / cost)
Parfait. Voilà les 3 SPEC en mode canon (bundle, rapport, adapter MCP → gate Obsidia).

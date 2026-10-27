# Spec 08 — Audit Report HTML/PDF Canon (ToC + signature, P71-P80) — valider V4

**Statut V4 :** FORMALISÉ_À_VALIDER
**Titre source détaillé :** Audit Report HTML/PDF Canon (ToC cliquable + signature globale)

## Contrat V4
- Spécification lisible.
- Entrées / sorties / invariants identifiables.
- Audit C obligatoire.

## Contenu source
8) SPEC — Audit Report HTML/PDF Canon (ToC cliquable + signature globale)
8.0 But
Un rapport audit OS3 doit être :
lisible humain
vérifiable machine
prouvable offline
stable (format canon)
👉 Format double :
audit_report.html (interactif)
audit_report.pdf (archivable)
8.1 Fichiers du rapport
audit_report/
  audit_report.html
  audit_report.pdf
  assets/
    style.css
    logo.svg (optionnel)
  signature/
    report.hashes.json
    report.sig
8.2 Table des matières (cliquable)
Le HTML DOIT inclure une ToC avec ancres stables :
Contexte
Policy appliquée
Tickets (résumé)
Trace Chain
Résultat Replay (PASS/FAIL)
Divergences
Violations (si présent)
Preuves cryptographiques
Hashes & Scellage
Contrat : chaque section = id fixe (#context, #policy, #tickets, etc.)
8.3 Contenu minimal (obligatoire)
Header (bandeau)
audit_id
request_id
session_id
scope
timestamp
status PASS/FAIL
match_score
policy_id
trace_root_hash
Policy appliquée (extrait)
no_write
allowed_tools
max_cost / max_calls / time_budget
Tickets (résumé)
count tickets
validity summary (valid/invalid)
list minimal : ticket_id, scope, expires_at
Trace chain
first_event_hash / last_event_hash
chain intact (true/false)
event count
Replay result
hard_checks pass/fail
sequence_checks
divergences listées
Divergences
Table canon :
Crypto / Scellage
report.hashes.json + report.sig
keys used (key_id + cert ref)
8.4 report.hashes.json (preuve machine)
{
  "audit_id": "uuid",
  "files": [
    { "path": "audit_report.html", "sha256": "..." },
    { "path": "audit_report.pdf", "sha256": "..." }
  ],
  "roots": {
    "trace_root_hash": "sha256",
    "tickets_root_hash": "sha256",
    "policy_hash": "sha256"
  },
  "created_at": "timestamp"
}
8.5 Signature globale du rapport
report.sig = ed25519(sha256(report.hashes.json canonical))
Règle : si HTML ≠ PDF (contenu divergent) → VIOLATION S3 (report mismatch).
8.6 Watermark / label canon
Optionnel mais recommandé :
Watermark HTML/PDF : Audit OS3 figé
Version : OS3_AUDIT_CANON_v1

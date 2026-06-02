# PRODUCTION_BLOCKERS_SPEC

Status: PROD_BLOCKED
Authority: KX108_ONLY

Source Paths:
- `docs/architecture/F74_F77_FINALIZATION_AUDIT.md` (lignes 193-250)
- `apps/obsidia_api/main.py`

Source Status: DOC_ONLY + PROD_BLOCKED

Scope:
Documenter les bloqueurs production existants et les conditions de résolution.

Allowed:
- "F76 est PROD_BLOCKED — 4 bloqueurs documentés"
- "F77 est PACK_PARTIAL — external_pack/ absent"

Forbidden:
- "Obsidia est production-ready"
- "Le serveur peut être déployé sans modifications"

Inputs: F74_F77_SOURCE.md

Outputs: Liste de bloqueurs avec chemin source et condition de résolution

Metrics: N/A

Invariants:
| Bloqueur | Chemin | Criticité | Résolution |
|----------|--------|-----------|-----------|
| CORS wildcard | `apps/obsidia_api/main.py:allow_origins=["*"]` | CRITICAL | Restreindre à domaine prod |
| Auth absente | `apps/obsidia_api/main.py` | CRITICAL | Implémenter auth token |
| Dockerfile manquant | repo root | CRITICAL | Créer Dockerfile API |
| /health manquant | `apps/obsidia_api/routes/` | ROUTE_MISSING | Créer GET /health |

X108 Boundary: KX108_ONLY

Tests Required:
- Test CORS headers
- Test /health endpoint
- Test auth middleware

Proof Expected: Aucun proof formel

Runtime Status: PROD_BLOCKED

Claim-Scope Notes:
Ne pas affirmer production-ready tant que ces 4 bloqueurs ne sont pas résolus et vérifiés.

Open Questions:
- Qui prend en charge la résolution F76 ?
- Quel est le calendrier de déploiement ?

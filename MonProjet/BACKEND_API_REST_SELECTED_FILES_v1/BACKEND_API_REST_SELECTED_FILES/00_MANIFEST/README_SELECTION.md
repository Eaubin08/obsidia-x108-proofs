# BACKEND_API_REST_SELECTED_FILES_v1

Pack de sélection backend/API REST construit à partir des ZIP fournis.

Objectif strict : reprendre uniquement la matière utile pour l'étape :

1. finalisation API REST + services backend ;
2. préparation connexion MySQL/PostgreSQL ;
3. base de tests/performance plus tard.

Ce pack n'inclut pas les anciens packs énergie. Énergie = hors scope ici.

## Base principale

- `01_primary_obsidia_lab_trad/gateway/server.ts` : gateway Express `/api/*`.
- `01_primary_obsidia_lab_trad/fastapi_engine/api_server/main.py` : FastAPI moteur `/v1/decision`, replay, audit, auth.
- `01_primary_obsidia_lab_trad/canonical_api/app.py` : API canonique avec modèles Pydantic, nonce, signature, audit hash-chain.
- `01_primary_obsidia_lab_trad/contracts/*` : contrats OpenAPI.
- `01_primary_obsidia_lab_trad/db_drizzle/*` : schéma DB Drizzle/MySQL pour l'étape DB.

## Références secondaires

- `02_backend_local_skeleton/` : squelette Express local + contrats Zod.
- `03_bank_robo_db_reference/` : modèle DB/Drizzle MySQL + service bancaire/tRPC à transformer si besoin en REST.
- `04_proof_core_fallback/` : fallback proof-core, volontairement minimal.

## Décision d'architecture

Ne pas créer une API REST depuis zéro.
Centraliser autour de :

```text
Obsidia-lab-trad server.ts
→ Express /api/* gateway
→ FastAPI /v1/decision moteur
→ Pydantic/Zod models
→ OpenAPI contract
→ Drizzle schema pour DB ensuite
```

## Fichiers volontairement exclus

- `agent-trad-main.zip` : app Streamlit/trading, pas backend REST principal.
- `agentic-commerce-safe-demo...zip` : demo Streamlit, pas backend REST principal.
- `kenerl--main.zip` : frontend/vitrine/preuve, pas backend REST principal.
- tous les ZIP énergie : hors scope de cette étape.

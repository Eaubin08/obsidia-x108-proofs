# ENV_KEYS_MATRIX

| Key | Required for boot | Required for DB | Required for external services | Notes |
|---|---:|---:|---:|---|
| PORT | yes | no | no | port de départ |
| DATABASE_URL | no | yes | no | sans lui `getDb()` peut retourner null |
| GEMINI_API_KEY | no | no | yes | analyse externe |
| OAUTH_SERVER_URL | no | no | yes | oauth |
| JWT_SECRET | context | no | yes | auth |
| OWNER_OPEN_ID | context | no | yes | auth/app |
| VITE_APP_ID | context | no | yes | front/app |
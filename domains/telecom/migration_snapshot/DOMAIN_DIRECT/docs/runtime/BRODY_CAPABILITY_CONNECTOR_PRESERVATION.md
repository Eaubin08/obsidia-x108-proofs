# BRODY_CAPABILITY_CONNECTOR_PRESERVATION

Source: PHASE_3C_BRODY_PRESERVATION_MATRIX

## Required preserved items

1. FRANCAIS_NATUREL
2. ENGLISH_UNDERSTANDING
3. CODE_ANSWERING
4. TRUE_VOICE_RUNTIME
5. TERMINAL_DIALOGUE
6. SESSION_MEMORY
7. MEMORY_CONTEXT
8. GRAPHITI_CONTEXT
9. NEO4J_CONNECTOR
10. API_FASTAPI_CONNECTOR
11. UI_TO_API_CONNECTOR
12. TERMINAL_TO_API_CONNECTOR
13. PROVIDER_MODEL_CONNECTORS
14. DOCKER_GORDON_RUNTIME
15. GITHUB_REPO_CONNECTOR
16. MCP_TOOL_CONNECTOR
17. X108_BOUNDARY
18. TESTS_SMOKES

## Rule

Every future patch must preserve these capabilities/connectors or explicitly explain why a capability is out of scope.

## Excluded from copy

- raw records
- node_modules
- .venv / venv
- dist / build
- real .env
- secrets/tokens/API keys
- kernel/proof/seal protected zones unless explicitly approved

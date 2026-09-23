# BRODY_PHASE9B0BIS_PAYLOAD_SCHEMA_RECHECK_20260527

Status: DIAGNOSTIC_ONLY_SCHEMA_ONLY

## Scope
Inspect OpenAPI request schemas for Phase 9B-0 routes that returned HTTP 422.

## Correction
- Previous run failed before schema extraction because PowerShell parsed `$route:` as an invalid variable reference.
- This version does not replay POST requests.
- This version extracts requestBody schemas only.

## Interpretation rule
- HTTP 422 means route exists but payload schema mismatched.
- 422 routes must be classified as ROUTE_EXISTS_SCHEMA_MISMATCH, not missing.
- No patch before exact model field mapping is known.

## OpenAPI route schemas

### /api/periphery/context/build
- method = POST
- operation_id = periphery_context_build_api_periphery_context_build_post
- schema_title = ContextBuildPayload
- required = ["action_id"]
- properties = ["action_id", "signals", "status"]
- minimal_sample_payload =
```json
{
  "action_id": "phase9b0bis"
}
```
- resolved_schema =
```json
{
  "properties": {
    "action_id": {
      "type": "string",
      "title": "Action Id"
    },
    "signals": {
      "items": {
        "additionalProperties": true,
        "type": "object"
      },
      "type": "array",
      "title": "Signals"
    },
    "status": {
      "type": "string",
      "title": "Status",
      "default": "READY"
    }
  },
  "type": "object",
  "required": [
    "action_id"
  ],
  "title": "ContextBuildPayload"
}
```

### /api/periphery/context/ingress
- method = POST
- operation_id = periphery_context_ingress_api_periphery_context_ingress_post
- schema_title = ContextBuildPayload
- required = ["action_id"]
- properties = ["action_id", "signals", "status"]
- minimal_sample_payload =
```json
{
  "action_id": "phase9b0bis"
}
```
- resolved_schema =
```json
{
  "properties": {
    "action_id": {
      "type": "string",
      "title": "Action Id"
    },
    "signals": {
      "items": {
        "additionalProperties": true,
        "type": "object"
      },
      "type": "array",
      "title": "Signals"
    },
    "status": {
      "type": "string",
      "title": "Status",
      "default": "READY"
    }
  },
  "type": "object",
  "required": [
    "action_id"
  ],
  "title": "ContextBuildPayload"
}
```

### /api/periphery/brody/language-route
- method = POST
- operation_id = periphery_brody_language_route_api_periphery_brody_language_route_post
- schema_title = BrodyLangPayload
- required = ["query_id"]
- properties = ["query_id", "language_code"]
- minimal_sample_payload =
```json
{
  "query_id": "phase9b0bis"
}
```
- resolved_schema =
```json
{
  "properties": {
    "query_id": {
      "type": "string",
      "title": "Query Id"
    },
    "language_code": {
      "type": "string",
      "title": "Language Code",
      "default": "en"
    }
  },
  "type": "object",
  "required": [
    "query_id"
  ],
  "title": "BrodyLangPayload"
}
```

### /api/periphery/brody/context-query
- method = POST
- operation_id = periphery_brody_context_query_api_periphery_brody_context_query_post
- schema_title = BrodyQueryPayload
- required = ["query_id", "query_text"]
- properties = ["query_id", "query_text", "language", "context_filters"]
- minimal_sample_payload =
```json
{
  "query_id": "phase9b0bis",
  "query_text": "phase9b0bis"
}
```
- resolved_schema =
```json
{
  "properties": {
    "query_id": {
      "type": "string",
      "title": "Query Id"
    },
    "query_text": {
      "type": "string",
      "title": "Query Text"
    },
    "language": {
      "type": "string",
      "title": "Language",
      "default": "en"
    },
    "context_filters": {
      "items": {
        "type": "string"
      },
      "type": "array",
      "title": "Context Filters"
    }
  },
  "type": "object",
  "required": [
    "query_id",
    "query_text"
  ],
  "title": "BrodyQueryPayload"
}
```

### /api/periphery/brody/double-brain-route
- method = POST
- operation_id = periphery_double_brain_route_api_periphery_brody_double_brain_route_post
- schema_title = DoubleBrainPayload
- required = ["route_id"]
- properties = ["route_id", "complexity", "urgency", "uncertainty"]
- minimal_sample_payload =
```json
{
  "route_id": "phase9b0bis"
}
```
- resolved_schema =
```json
{
  "properties": {
    "route_id": {
      "type": "string",
      "title": "Route Id"
    },
    "complexity": {
      "type": "number",
      "title": "Complexity",
      "default": 0.5
    },
    "urgency": {
      "type": "number",
      "title": "Urgency",
      "default": 0.5
    },
    "uncertainty": {
      "type": "number",
      "title": "Uncertainty",
      "default": 0.5
    }
  },
  "type": "object",
  "required": [
    "route_id"
  ],
  "title": "DoubleBrainPayload"
}
```

### /api/periphery/brody/diffusion-mix
- method = POST
- operation_id = periphery_diffusion_mix_api_periphery_brody_diffusion_mix_post
- schema_title = DiffusionMixPayload
- required = ["mix_id"]
- properties = ["mix_id", "creativity_score", "precision_score"]
- minimal_sample_payload =
```json
{
  "mix_id": "phase9b0bis"
}
```
- resolved_schema =
```json
{
  "properties": {
    "mix_id": {
      "type": "string",
      "title": "Mix Id"
    },
    "creativity_score": {
      "type": "number",
      "title": "Creativity Score",
      "default": 0.5
    },
    "precision_score": {
      "type": "number",
      "title": "Precision Score",
      "default": 0.5
    }
  },
  "type": "object",
  "required": [
    "mix_id"
  ],
  "title": "DiffusionMixPayload"
}
```

### /api/periphery/graphiti/context-adapt
- method = POST
- operation_id = periphery_graphiti_context_adapt_api_periphery_graphiti_context_adapt_post
- schema_title = GraphitiAdaptPayload
- required = ["adapter_id", "query_id"]
- properties = ["adapter_id", "query_id", "query", "max_nodes"]
- minimal_sample_payload =
```json
{
  "adapter_id": "phase9b0bis",
  "query_id": "phase9b0bis"
}
```
- resolved_schema =
```json
{
  "properties": {
    "adapter_id": {
      "type": "string",
      "title": "Adapter Id"
    },
    "query_id": {
      "type": "string",
      "title": "Query Id"
    },
    "query": {
      "type": "string",
      "title": "Query",
      "default": ""
    },
    "max_nodes": {
      "type": "integer",
      "title": "Max Nodes",
      "default": 10
    }
  },
  "type": "object",
  "required": [
    "adapter_id",
    "query_id"
  ],
  "title": "GraphitiAdaptPayload"
}
```

## Binding implication
- Use the minimal_sample_payload blocks to replay only after human validation.
- Phase 9B route design must preserve terminal + UI + API + periphery alignment.
- OS Trad / IR / Reverse routes must bind existing surfaces without bypassing terminal or Workbench behavior.

## Boundary
- Diagnostic only.
- Schema extraction only.
- No POST replay.
- No patch.
- No runtime mutation.
- No kernel mutation.
- No X108 mutation.
- No memory write.
- No Graphiti write.
- KX108_ONLY remains sole decision authority.
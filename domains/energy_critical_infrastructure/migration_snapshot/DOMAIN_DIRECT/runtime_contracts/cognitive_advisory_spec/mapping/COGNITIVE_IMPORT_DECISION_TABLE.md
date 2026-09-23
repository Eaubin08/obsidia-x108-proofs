# COGNITIVE_IMPORT_DECISION_TABLE

| Source family | Current status | Decision | Runtime allowed now? | Boundary |
|---|---|---|---|---|
| Cognitive markdown/spec docs | source audited | integrate as advisory spec candidates | false | COGNITIVE_REINTEGRATION_ADVISORY_ONLY |
| Cognitive YAML/JSON descriptors | source audited | map to ContextPacket candidates later | false | COGNITIVE_REINTEGRATION_ADVISORY_ONLY |
| Cognitive metrics | source audited | advisory metric candidates only | false | COGNITIVE_REINTEGRATION_ADVISORY_ONLY |
| Cognitive agents | source audited | non-executable descriptions only | false | COGNITIVE_REINTEGRATION_ADVISORY_ONLY |
| Cognitive .py files | forbidden | DO_NOT_IMPORT_RUNTIME | false | NO_PYTHON |
| Cache / runtime freeze files | forbidden | ARCHIVE_ONLY | false | SOURCE_ONLY |
| World action candidates | controlled | IntentEnvelope candidate only | false | X108_GATEWAY_REQUIRED |
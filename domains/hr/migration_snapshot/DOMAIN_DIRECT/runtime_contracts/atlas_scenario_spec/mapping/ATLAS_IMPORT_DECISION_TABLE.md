# ATLAS_IMPORT_DECISION_TABLE

| Source family | Current status | Decision | Runtime allowed now? | Boundary |
|---|---|---|---|---|
| Atlas markdown/spec docs | source audited | readonly advisory spec candidates | false | ATLAS_READONLY_ADVISORY_ONLY |
| Atlas YAML/JSON descriptors | source audited | ContextPacket candidates later | false | ATLAS_READONLY_ADVISORY_ONLY |
| Atlas scenarios | source audited | scenario context candidates only | false | ATLAS_READONLY_ADVISORY_ONLY |
| Atlas .py files | forbidden | DO_NOT_IMPORT_RUNTIME | false | NO_PYTHON |
| .pytest_cache / __pycache__ | forbidden | KEEP_QUARANTINE | false | SOURCE_ONLY |
| .runtime_freezes | forbidden | ARCHIVE_ONLY | false | SOURCE_ONLY |
| world action candidates | controlled | IntentEnvelope candidate only | false | X108_GATEWAY_REQUIRED |
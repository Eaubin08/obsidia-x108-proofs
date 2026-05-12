# BRODY CONTEXT PACKET CONSUMER READONLY

Role:
- Consume readonly context packets generated from Neo4j / Graphiti V2.
- Produce local Brody-readable JSON and Markdown responses.
- Enrich empty excerpts by reading local source files when paths exist.

Boundary:
- Brody consumes context only.
- Memory never decides.
- Memory never emits ACT.
- Memory never mutates kernel.
- No X108 runtime binding.
- No X108 merge.
- KX108 remains sole decision authority.

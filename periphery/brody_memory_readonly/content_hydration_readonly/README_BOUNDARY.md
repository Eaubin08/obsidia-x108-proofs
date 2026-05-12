# BRODY CONTENT HYDRATION READONLY

Rôle : hydrater localement un packet Brody/Graphiti readonly.

Entrée :
- packet JSON issu de BRODY_CONTEXT_PACKET_QUERY_READONLY

Sortie :
- même packet compatible consumer
- paths résolus quand possible
- excerpts hydratés quand possible

Boundary :
- readonly only
- no memory decision
- no ACT
- no kernel mutation
- no X108 runtime binding
- no X108 merge
- KX108_ONLY remains sole decision authority

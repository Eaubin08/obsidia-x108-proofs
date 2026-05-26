
# Audit MCP Bridge / Obsidia IR

## Statut

`AUDIT_STATUS = MINIMAL_REAL_AUDIT`

## Périmètre

Traduction MCP vers représentation interne Obsidia IR.

## Contrôles effectués

- Module MCP importable.
- Traduction produit uniquement une structure IR/contextuelle.
- Aucun outil externe n’est déclenché.
- Tests unitaires OK.

## Verdict

MCP Bridge est une passerelle contextuelle, non gouvernante.

## Limites

- Pas de serveur MCP réel.
- Policy scope encore minimal.

## Invariant de non-décision

```text
Layer ↛ ACT
Decision = KX108
```

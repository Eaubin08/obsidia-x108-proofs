# HOW_TO_READ_OBSIDIA_SOURCES

## Principe fondamental

```
Source réelle (code/doc existant)
    ↓
_imports_readonly/ (facts extraits, chemins cités, limites)
    ↓
specs/ (contrat d'usage, claims autorisés/interdits)
    ↓
Test futur (Plan 3)
    ↓
Runtime futur (Plan 3+)
    ↓
Claim public (autorisé seulement si sourcé et dans 00_SCOPE_DISCIPLINE/)
```

## Règles de lecture

1. **Jamais de claim sans source** — chaque affirmation publique doit être tracée à un fichier dans `_imports_readonly/` ou une source directe
2. **PASS ≠ preuve formelle** — voir `00_SCOPE_DISCIPLINE/FORMAL_PROOF_VS_RUNTIME_APPROXIMATION.md`
3. **COMPLETE ≠ production-ready** — voir `00_SCOPE_DISCIPLINE/PRODUCTION_BLOCKERS_SPEC.md`
4. **Python spec ≠ Lean proof** — FORMAL_PROOF_PENDING pour math_core/
5. **DRY_RUN ≠ production** — voir `00_SCOPE_DISCIPLINE/DRY_RUN_NOT_PRODUCTION_SPEC.md`
6. **KX108_ONLY** — toujours vérifier qui décide avant toute affirmation d'action

## Sources par fiabilité décroissante

1. Code / schema / registry réel (ce qui existe sur disque)
2. Rapport freeze / audit (docs/freeze/, .runtime_freezes/)
3. Index public / arborescence (ARBORESCENCE_COMPLETE.md)
4. README / doc générale
5. Audio / Gemini
6. Hypothèse

## Corrections de noms Gemini

| Terme Gemini | Réalité repo |
|---|---|
| `/domaines/` | `periphery/OBSIDIA_V4_STRUCTURED_FULL/02_BLOCS_17/` |
| `/fondations/` | `periphery/OBSIDIA_V4_STRUCTURED_FULL/06_GARDIENS_DE_FOND_T1_T12/` |
| `/agents/` | `periphery/OBSIDIA_V4_STRUCTURED_FULL/07_AGENTS_ET_ROLES/` |
| `BUV` | `BALANCE_CANON.md` + `balance_operator.py` |
| `Jcoin` | ABSENT_UNDER_THIS_NAME (décision humaine requise) |
| `.xyz` | `BRANCHESXYZKLN.md` dans `12_EXTENSIONS_R_D/` |
| `obsidia-workspace` | `periphery/OBSIDIA_V4_STRUCTURED_FULL/` |
| `7 flux exacts` | HORS périmètre public (docs/REPO_BOUNDARY.md:84) |

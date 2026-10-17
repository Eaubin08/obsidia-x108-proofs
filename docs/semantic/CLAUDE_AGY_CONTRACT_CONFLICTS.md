# Contract conflicts between the Claude and AGY branches

Branch `feat/claude-linguistic-repair-m42-v0` (Claude) diverges from
`feat/jarvis-advanced-obsidia-integration-v0` (AGY) on the contracts below.
Nothing has been merged; each item needs an explicit reconciliation decision.

| # | Item | AGY branch | Claude branch | Reason |
|---|------|------------|---------------|--------|
| 1 | Location of the corpus modules | `app/semantic/lattice/lexical_corpus.py`, `native_realization.py` | `periphery/language/lexical_corpus.py`, `native_realization.py`; `app/semantic` restored to `a268ae46` | sealed-source guard R10 and B7 runtime closure |
| 2 | `parse_utterance` corpus fallback (`test_corpus_7`) | active in `lexicon.py` | `xfail(strict=True)`, HOLD | needs a hook in sealed `lexicon.py` |
| 3 | `test_adv_a` provenance level | `native_linguistic_level == "REAL_SEMANTIC_RECONSTRUCTION"` | `== "TEMPLATE_REWRITE"` plus per-statement records | the operation is a deterministic pattern rewrite; no semantic reconstruction is performed or proven |
| 4 | Answer-level `native_linguistic_level` | `REAL_SEMANTIC_RECONSTRUCTION` when claims are synthesized | exact aggregate: `AUXILIARY_WORDING_REUSED`, `TEMPLATE_REWRITE`, `AUXILIARY_WORDING_PRESERVED` or `MIXED` | provenance honesty |
| 5 | `test_corpus_11` FreeDict gloss | gloss in `.definition` | `kind == "translation_gloss"`, text in `.gloss`, `.definition` empty | definitions vs glosses |
| 6 | Test journal isolation | session and memory candidate ledgers written by tests | `conftest.py` redirects both to `tmp_path` | operational journals |

# WORLD_TREE_NEXT_TEST_PLAN
## Mission: BRODY_WORLD_TREE_PROVIDER_MATRIX_READONLY
## Timestamp: 20260514_005141
## Next Action: BRODY_WORLD_TREE_GET_ONLY_TEST_READONLY

---

## Recommended Next Test

**Name:** BRODY_WORLD_TREE_GET_ONLY_TEST_READONLY  
**Mode:** READONLY — MATCH/RETURN/COUNT/LIMIT only. Zero writes.  
**Entry trees:** T01–T15 (SAFE — no world interface, no action trigger, no memory write)  
**Target label:** BrodyMemoryDoc  
**Filter:** Tags containing tree codes T01–T15 or family codes I_FONDAMENTAUX / II_COGNITIFS / III_CONNAISSANCE  

---

## Rationale

T01–T15 are the safest trees in the corpus:
- No world interface
- No action trigger
- No direct memory write
- Not blocked
- SAFE risk level in WORLD_TREE_RISK_TABLE
- All safe_test_eligible=true

The test retrieves only — it does not mutate, index, bind, or feed memory candidates. It validates that the tree-tagged BrodyMemoryDoc nodes are accessible and correctly tagged.

---

## Proposed Test Queries

```cypher
-- Q1: Count docs tagged with T01-T15 tree families
MATCH (p:BrodyMemoryDoc)
WHERE ANY(tag IN p.tags WHERE tag IN ['I_FONDAMENTAUX','II_COGNITIFS','III_CONNAISSANCE',
    '34_arbres','T01','T02','T03','T04','T05','T06','T07','T08','T09','T10',
    'T11','T12','T13','T14','T15'])
RETURN count(p) AS doc_count

-- Q2: Sample titles from SAFE tree zone
MATCH (p:BrodyMemoryDoc)
WHERE ANY(tag IN p.tags WHERE tag IN ['I_FONDAMENTAUX','II_COGNITIFS','III_CONNAISSANCE'])
RETURN p.title AS title, p.tags AS tags, substring(p.text_preview, 0, 200) AS preview
LIMIT 10

-- Q3: Confirm '34_arbres' tagged nodes remain accessible
MATCH (p:BrodyMemoryDoc)
WHERE '34_arbres' IN p.tags
RETURN count(p) AS total_34_arbres_docs

-- Q4: Verify tree registry docs still present
MATCH (p:BrodyMemoryDoc)
WHERE p.title IN ['arbres_34.canon.json','arbres_34.registry.json']
RETURN p.title AS title, substring(p.text_preview, 0, 100) AS preview
```

---

## Test Success Criteria

| Check | Expected |
|---|---|
| doc_count > 0 | At least some T01-T15 tagged docs found |
| Sample titles non-empty | Preview content accessible |
| total_34_arbres_docs > 0 | 34_arbres tag still in corpus |
| Registry docs present | Both canon and registry docs accessible |
| Zero mutations | No SET, MERGE, CREATE, DELETE executed |
| boundary_all_false | All write flags remain false |

---

## Out-of-Scope for This Test

The following are NOT part of BRODY_WORLD_TREE_GET_ONLY_TEST_READONLY:

| Action | Status |
|---|---|
| Querying T16-T19 (LOW/world passive) | Deferred — requires KX108 gate first |
| Querying T20-T22 (action trigger) | BLOCKED |
| Querying T24 (memory write) | BLOCKED |
| Querying T30-T34 (AGI-layer) | BLOCKED |
| Writing any node or relationship | FORBIDDEN |
| Running memory candidate pipeline | FORBIDDEN |
| Activating runtime_binding | FORBIDDEN |
| Executing x108_merge | FORBIDDEN |

---

## After Test

If BRODY_WORLD_TREE_GET_ONLY_TEST_READONLY passes:

```
NEXT_BRODY_MEMORY_ACTION = BRODY_RUNTIME_BINDING_RISK_REVIEW_READONLY
NEXT_REAL_WORLD_ACTION   = BRODY_WORLD_TREE_GET_ONLY_TEST_READONLY (the test itself)
NEXT_GATE_ACTION         = KX108 operator approval for LOW trees (T16-T19)
```

---

## Sequence (recommended order)

```
[1] BRODY_WORLD_TREE_GET_ONLY_TEST_READONLY     ← next immediate
[2] BRODY_RUNTIME_BINDING_RISK_REVIEW_READONLY  ← after [1] passes
[3] KX108 gate approval for T16-T19             ← operator decision
[4] BRODY_WORLD_TREE_PASSIVE_INTERFACE_TEST      ← after [3]
[5] WRITABLE_MEMORY_PROTOCOL activation          ← operator gate
[6] T20-T22 / T24 unlock evaluation             ← after [5]
[7] AGI-layer evaluation (T30-T34)               ← long-term, full gate
```

---

BOUNDARY_ALL_FALSE=true  
READONLY=true  
DECISION_AUTHORITY=KX108_ONLY  
NEXT_TEST=BRODY_WORLD_TREE_GET_ONLY_TEST_READONLY

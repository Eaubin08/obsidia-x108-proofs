# GET_ONLY_PROVIDER_EVIDENCE
## Mission: BRODY_WORLD_TREE_GET_ONLY_TEST_READONLY
## Timestamp: 20260514_011350

---

## Providers Used in This Test

### Provider 1: NEO4J_READ

| Field | Value |
|---|---|
| URI | bolt://127.0.0.1:7688 |
| Auth source | graphiti-lab/.env.graphiti.local |
| Method | MATCH/RETURN/LIMIT (read-only) |
| Writes executed | NONE |
| Validated by | IMPORT_INTEGRITY_MATRIX.json — read_path_pass=true |
| Requests | 4 (GET_TREE_001 to GET_TREE_004) |
| Status | ACTIVE_READONLY |

**Trees tested via NEO4J_READ:**
- T26 Cohérence (VII_META_STRUCTURELS) → 34_arbres corpus count: 2739
- T06 Compréhension (II_COGNITIFS) → family-level tag count: 0
- T01 Humain (I_FONDAMENTAUX) → family sample: 0 titles
- T25 Histoire (VI_TEMPORELS_MEMORIELS) → registry docs: 2/2 present

---

### Provider 2: WEB_GET_ONLY

| Field | Value |
|---|---|
| URL | https://example.com/ |
| Method | GET |
| Allowlist source | BRODY_EXTERNAL_FETCH_READONLY_OPERATOR_TEST_REPORT.json |
| Allowlist confirmed | true |
| Auth used | NONE |
| Token used | NONE |
| Secrets sent | NONE |
| Redirects followed | 0 |
| Links followed | 0 (no crawler) |
| Body stored | NO — only sha256 + metadata |
| Requests | 1 (GET_TREE_005) |
| Status | AVAILABLE_READONLY |

**Tree tested via WEB_GET_ONLY:**
- T16 Relation (IV_RELATIONNELS_SOCIAUX) → status=200, sha256=fb91d75a6bb4...

---

## Providers NOT Used

| Provider | Reason |
|---|---|
| GRAPHITI_WRITE | BLOCKED |
| NEO4J_WRITE | BLOCKED |
| POST_MUTATION | NOT_ALLOWED |
| SCRAPING_CRAWLER | NOT_ALLOWED |
| KERNEL_BINDING | NOT_ALLOWED |
| X108_RUNTIME_BINDING | NOT_ALLOWED |

---

## Key Finding: FAMILY_LEVEL_TAGGING_ABSENT

**Discovery from GET_TREE_002 + GET_TREE_003:**

BrodyMemoryDoc nodes use `34_arbres` as a catch-all tree corpus tag (2739/3267 nodes carry it). However, individual family-level tags (`I_FONDAMENTAUX`, `II_COGNITIFS`, `T01`, `T02`, etc.) are **absent** from the BrodyMemoryDoc tag set.

This means:
- You CAN filter "all tree-related docs" using `'34_arbres' IN tags` ✓
- You CANNOT filter "only II_COGNITIFS docs" using `'II_COGNITIFS' IN tags` ✗
- Family-level tag enrichment is a pending work item (requires gate)
- `BrodyMemoryTag` label exists in Neo4j — natural candidate for family tag nodes

**Impact:** Low for current mission (GET_TREE_001/004 still PASS). High for future tree-family routing when memory layers are separated.

---

## SHA256 Stability Note

External GET sha256 matches previous test session:
- This session: `fb91d75a6bb430787a61b0aec5e374f580030f2878e1613eab5ca6310f7bbb9a`
- Previous session (2026-05-13): `fb91d75a6bb430787a61b0aec5e374f580030f2878e1613eab5ca6310f7bbb9a`

**STABLE** — same response across sessions. External provider confirmed reliable for allowlisted readonly test.

---

## Allowlist Provenance

```
Source: _local_audits/BRODY_EXTERNAL_FETCH_READONLY_OPERATOR_TEST_20260513_203216/
         reports/BRODY_EXTERNAL_FETCH_READONLY_OPERATOR_TEST_REPORT.json
Field:   "allowlist": ["https://example.com/", "https://example.com"]
Method:  "allowed_methods": ["GET"]
```

No new URLs invented. No new allowlist entries created. Reused existing validated allowlist only.

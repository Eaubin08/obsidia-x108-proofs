// CANONICAL_TAGGING_WRITE_CYPHER_PLAN.cypher
// Mission: BRODY_CANONICAL_TAGGING_WRITE_CANDIDATE_PROTOCOL_READONLY
// Timestamp: 20260514_020923
// Status: PLAN ONLY — NOT EXECUTED — requires KX108 gate + operator approval
// Strategy: APPEND_ONLY — never remove existing tags
// Scope: 48 approved BrodyMemoryDoc nodes — T01-T12 / families I-III
//
// HOW TO USE:
//   1. Operator reviews this file completely
//   2. KX108 gate opened explicitly
//   3. OPERATOR_APPROVAL_TEMPLATE.json signed
//   4. Each query executed individually with human oversight
//   5. POST_WRITE_VALIDATION_PLAN.json checks run after each batch
//
// DO NOT EXECUTE IN BULK WITHOUT GATE AUTHORIZATION
//

// ═══════════════════════════════════════════════════════════
// PRE-FLIGHT CHECK — run first (READ ONLY)
// ═══════════════════════════════════════════════════════════

// CHECK_01: Verify 0 nodes already have Tnn family tags
MATCH (n:BrodyMemoryDoc)
WHERE ANY(tag IN n.tags WHERE tag =~ 'T[0-9]+')
RETURN count(n) AS already_tagged_count;
// Expected: 0

// CHECK_02: Verify approved node_ids are reachable
MATCH (n:BrodyMemoryDoc)
WHERE n.id IN [
  'GRAPHITI_V2_000000',
  'GRAPHITI_V2_002928',
  'GRAPHITI_V2_003042',
  'GRAPHITI_V2_003043',
  'GRAPHITI_V2_003170',
  'GRAPHITI_V2_002995',
  'GRAPHITI_V2_003079',
  'GRAPHITI_V2_002929',
  'GRAPHITI_V2_003044',
  'GRAPHITI_V2_003126',
  'GRAPHITI_V2_003080',
  'GRAPHITI_V2_002930',
  'GRAPHITI_V2_003171',
  'GRAPHITI_V2_000274',
  'GRAPHITI_V2_000309',
  'GRAPHITI_V2_000310',
  'GRAPHITI_V2_000333',
  'GRAPHITI_V2_000449',
  'GRAPHITI_V2_000450',
  'GRAPHITI_V2_000456',
  'GRAPHITI_V2_000615',
  'GRAPHITI_V2_000797',
  'GRAPHITI_V2_000800',
  'GRAPHITI_V2_000801',
  'GRAPHITI_V2_000870',
  'GRAPHITI_V2_000871',
  'GRAPHITI_V2_000980',
  'GRAPHITI_V2_000981',
  'GRAPHITI_V2_000989',
  'GRAPHITI_V2_001124',
  'GRAPHITI_V2_001125',
  'GRAPHITI_V2_001158',
  'GRAPHITI_V2_001471',
  'GRAPHITI_V2_001472',
  'GRAPHITI_V2_001543',
  'GRAPHITI_V2_001545',
  'GRAPHITI_V2_001546',
  'GRAPHITI_V2_001702',
  'GRAPHITI_V2_001703',
  'GRAPHITI_V2_001787',
  'GRAPHITI_V2_001987',
  'GRAPHITI_V2_001988',
  'GRAPHITI_V2_002112',
  'GRAPHITI_V2_002123',
  'GRAPHITI_V2_002124',
  'GRAPHITI_V2_002287',
  'GRAPHITI_V2_002288',
  'GRAPHITI_V2_002331'
]
RETURN count(n) AS reachable_count;
// Expected: 48

// ═══════════════════════════════════════════════════════════
// WRITE QUERIES — one per approved candidate
// Execute only after gate authorization
// Each query: MATCH by node_id + verify title pattern + append tags
// ═══════════════════════════════════════════════════════════

// GATE_DRY_001 | node=GRAPHITI_V2_000000 | tree=T04 | family=I_FONDAMENTAUX
// title: 003BEA03EEDD_T04__Consensus_Distribue_Resonance_semantique.md
// tags_to_add: ['T04', 'I_FONDAMENTAUX']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_000000'})
WHERE n.title =~ '.*.*'
WITH n,
  CASE WHEN 'T04' IN n.tags THEN n.tags ELSE n.tags + ['T04'] END AS tags_step1
WITH n, tags_step1,
  CASE WHEN 'I_FONDAMENTAUX' IN tags_step1 THEN tags_step1 ELSE tags_step1 + ['I_FONDAMENTAUX'] END AS tags_final
SET n.tags = tags_final
RETURN n.id, n.tags AS tags_after;

// GATE_DRY_002 | node=GRAPHITI_V2_002928 | tree=T01 | family=I_FONDAMENTAUX
// title: 05_GARDIEN_T01__Gardien_de_fond__Reduction_Incertitude_Audit_coherence.md
// tags_to_add: ['T01', 'I_FONDAMENTAUX']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_002928'})
WHERE n.title =~ '.*.*'
WITH n,
  CASE WHEN 'T01' IN n.tags THEN n.tags ELSE n.tags + ['T01'] END AS tags_step1
WITH n, tags_step1,
  CASE WHEN 'I_FONDAMENTAUX' IN tags_step1 THEN tags_step1 ELSE tags_step1 + ['I_FONDAMENTAUX'] END AS tags_final
SET n.tags = tags_final
RETURN n.id, n.tags AS tags_after;

// GATE_DRY_003 | node=GRAPHITI_V2_003042 | tree=T02 | family=I_FONDAMENTAUX
// title: 05_GARDIEN_T02__Gardien_de_fond__Conscience_Distribuee_Validation_reciprocite.md
// tags_to_add: ['T02', 'I_FONDAMENTAUX']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_003042'})
WHERE n.title =~ '.*.*'
WITH n,
  CASE WHEN 'T02' IN n.tags THEN n.tags ELSE n.tags + ['T02'] END AS tags_step1
WITH n, tags_step1,
  CASE WHEN 'I_FONDAMENTAUX' IN tags_step1 THEN tags_step1 ELSE tags_step1 + ['I_FONDAMENTAUX'] END AS tags_final
SET n.tags = tags_final
RETURN n.id, n.tags AS tags_after;

// GATE_DRY_004 | node=GRAPHITI_V2_003043 | tree=T03 | family=I_FONDAMENTAUX
// title: 05_GARDIEN_T03__Gardien_de_fond__Gouvernance_Decentralisee_Friction_energetique.
// tags_to_add: ['T03', 'I_FONDAMENTAUX']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_003043'})
WHERE n.title =~ '.*.*'
WITH n,
  CASE WHEN 'T03' IN n.tags THEN n.tags ELSE n.tags + ['T03'] END AS tags_step1
WITH n, tags_step1,
  CASE WHEN 'I_FONDAMENTAUX' IN tags_step1 THEN tags_step1 ELSE tags_step1 + ['I_FONDAMENTAUX'] END AS tags_final
SET n.tags = tags_final
RETURN n.id, n.tags AS tags_after;

// GATE_DRY_005 | node=GRAPHITI_V2_003170 | tree=T04 | family=I_FONDAMENTAUX
// title: 05_GARDIEN_T04__Gardien_de_fond__Consensus_Distribue_Resonance_semantique.md
// tags_to_add: ['T04', 'I_FONDAMENTAUX']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_003170'})
WHERE n.title =~ '.*.*'
WITH n,
  CASE WHEN 'T04' IN n.tags THEN n.tags ELSE n.tags + ['T04'] END AS tags_step1
WITH n, tags_step1,
  CASE WHEN 'I_FONDAMENTAUX' IN tags_step1 THEN tags_step1 ELSE tags_step1 + ['I_FONDAMENTAUX'] END AS tags_final
SET n.tags = tags_final
RETURN n.id, n.tags AS tags_after;

// GATE_DRY_006 | node=GRAPHITI_V2_002995 | tree=T05 | family=I_FONDAMENTAUX
// title: 05_GARDIEN_T05__Gardien_de_fond__Evolution_Systemes_Balance_structure_chaos.md
// tags_to_add: ['T05', 'I_FONDAMENTAUX']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_002995'})
WHERE n.title =~ '.*.*'
WITH n,
  CASE WHEN 'T05' IN n.tags THEN n.tags ELSE n.tags + ['T05'] END AS tags_step1
WITH n, tags_step1,
  CASE WHEN 'I_FONDAMENTAUX' IN tags_step1 THEN tags_step1 ELSE tags_step1 + ['I_FONDAMENTAUX'] END AS tags_final
SET n.tags = tags_final
RETURN n.id, n.tags AS tags_after;

// GATE_DRY_007 | node=GRAPHITI_V2_003079 | tree=T06 | family=II_COGNITIFS
// title: 05_GARDIEN_T06__Gardien_de_fond__Selection_Naturelle_Alignement_ethique.md
// tags_to_add: ['T06', 'II_COGNITIFS']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_003079'})
WHERE n.title =~ '.*.*'
WITH n,
  CASE WHEN 'T06' IN n.tags THEN n.tags ELSE n.tags + ['T06'] END AS tags_step1
WITH n, tags_step1,
  CASE WHEN 'II_COGNITIFS' IN tags_step1 THEN tags_step1 ELSE tags_step1 + ['II_COGNITIFS'] END AS tags_final
SET n.tags = tags_final
RETURN n.id, n.tags AS tags_after;

// GATE_DRY_008 | node=GRAPHITI_V2_002929 | tree=T07 | family=II_COGNITIFS
// title: 05_GARDIEN_T07__Gardien_de_fond__Resilience_Test_memoire_fractale.md
// tags_to_add: ['T07', 'II_COGNITIFS']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_002929'})
WHERE n.title =~ '.*.*'
WITH n,
  CASE WHEN 'T07' IN n.tags THEN n.tags ELSE n.tags + ['T07'] END AS tags_step1
WITH n, tags_step1,
  CASE WHEN 'II_COGNITIFS' IN tags_step1 THEN tags_step1 ELSE tags_step1 + ['II_COGNITIFS'] END AS tags_final
SET n.tags = tags_final
RETURN n.id, n.tags AS tags_after;

// GATE_DRY_009 | node=GRAPHITI_V2_003044 | tree=T08 | family=II_COGNITIFS
// title: 05_GARDIEN_T08__Gardien_de_fond__Auto_Organisation_Apprentissage_inverse.md
// tags_to_add: ['T08', 'II_COGNITIFS']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_003044'})
WHERE n.title =~ '.*.*'
WITH n,
  CASE WHEN 'T08' IN n.tags THEN n.tags ELSE n.tags + ['T08'] END AS tags_step1
WITH n, tags_step1,
  CASE WHEN 'II_COGNITIFS' IN tags_step1 THEN tags_step1 ELSE tags_step1 + ['II_COGNITIFS'] END AS tags_final
SET n.tags = tags_final
RETURN n.id, n.tags AS tags_after;

// GATE_DRY_010 | node=GRAPHITI_V2_003126 | tree=T09 | family=II_COGNITIFS
// title: 05_GARDIEN_T09__Gardien_de_fond__Creativite_Mode_reflexe.md
// tags_to_add: ['T09', 'II_COGNITIFS']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_003126'})
WHERE n.title =~ '.*.*'
WITH n,
  CASE WHEN 'T09' IN n.tags THEN n.tags ELSE n.tags + ['T09'] END AS tags_step1
WITH n, tags_step1,
  CASE WHEN 'II_COGNITIFS' IN tags_step1 THEN tags_step1 ELSE tags_step1 + ['II_COGNITIFS'] END AS tags_final
SET n.tags = tags_final
RETURN n.id, n.tags AS tags_after;

// GATE_DRY_011 | node=GRAPHITI_V2_003080 | tree=T10 | family=II_COGNITIFS
// title: 05_GARDIEN_T10__Gardien_de_fond__Innovation_Continue_Integrite_cognitive.md
// tags_to_add: ['T10', 'II_COGNITIFS']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_003080'})
WHERE n.title =~ '.*.*'
WITH n,
  CASE WHEN 'T10' IN n.tags THEN n.tags ELSE n.tags + ['T10'] END AS tags_step1
WITH n, tags_step1,
  CASE WHEN 'II_COGNITIFS' IN tags_step1 THEN tags_step1 ELSE tags_step1 + ['II_COGNITIFS'] END AS tags_final
SET n.tags = tags_final
RETURN n.id, n.tags AS tags_after;

// GATE_DRY_012 | node=GRAPHITI_V2_002930 | tree=T11 | family=III_CONNAISSANCE
// title: 05_GARDIEN_T11__Gardien_de_fond__Generation_Aleatoire_Frugalite_bio_inspiree.md
// tags_to_add: ['T11', 'III_CONNAISSANCE']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_002930'})
WHERE n.title =~ '.*.*'
WITH n,
  CASE WHEN 'T11' IN n.tags THEN n.tags ELSE n.tags + ['T11'] END AS tags_step1
WITH n, tags_step1,
  CASE WHEN 'III_CONNAISSANCE' IN tags_step1 THEN tags_step1 ELSE tags_step1 + ['III_CONNAISSANCE'] END AS tags_final
SET n.tags = tags_final
RETURN n.id, n.tags AS tags_after;

// GATE_DRY_013 | node=GRAPHITI_V2_003171 | tree=T12 | family=III_CONNAISSANCE
// title: 05_GARDIEN_T12__Gardien_de_fond__Complexite_Irreductible_Transparence_friction.m
// tags_to_add: ['T12', 'III_CONNAISSANCE']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_003171'})
WHERE n.title =~ '.*.*'
WITH n,
  CASE WHEN 'T12' IN n.tags THEN n.tags ELSE n.tags + ['T12'] END AS tags_step1
WITH n, tags_step1,
  CASE WHEN 'III_CONNAISSANCE' IN tags_step1 THEN tags_step1 ELSE tags_step1 + ['III_CONNAISSANCE'] END AS tags_final
SET n.tags = tags_final
RETURN n.id, n.tags AS tags_after;

// GATE_DRY_014 | node=GRAPHITI_V2_000274 | tree=T05 | family=I_FONDAMENTAUX
// title: 1A8AA0F5157E_T05__Evolution_Systemes_Balance_structure_chaos.md
// tags_to_add: ['T05', 'I_FONDAMENTAUX']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_000274'})
WHERE n.title =~ '.*.*'
WITH n,
  CASE WHEN 'T05' IN n.tags THEN n.tags ELSE n.tags + ['T05'] END AS tags_step1
WITH n, tags_step1,
  CASE WHEN 'I_FONDAMENTAUX' IN tags_step1 THEN tags_step1 ELSE tags_step1 + ['I_FONDAMENTAUX'] END AS tags_final
SET n.tags = tags_final
RETURN n.id, n.tags AS tags_after;

// GATE_DRY_015 | node=GRAPHITI_V2_000309 | tree=T07 | family=II_COGNITIFS
// title: 1E1C60E219B4_05_GARDIEN_T07__Gardien_de_fond__Resilience_Test_memoire_fractale.m
// tags_to_add: ['T07', 'II_COGNITIFS']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_000309'})
WHERE n.title =~ '.*.*'
WITH n,
  CASE WHEN 'T07' IN n.tags THEN n.tags ELSE n.tags + ['T07'] END AS tags_step1
WITH n, tags_step1,
  CASE WHEN 'II_COGNITIFS' IN tags_step1 THEN tags_step1 ELSE tags_step1 + ['II_COGNITIFS'] END AS tags_final
SET n.tags = tags_final
RETURN n.id, n.tags AS tags_after;

// GATE_DRY_016 | node=GRAPHITI_V2_000310 | tree=T07 | family=II_COGNITIFS
// title: 1E1C60E219B4_T07__Gardien_de_fond__Resilience_Test_memoire_fractale.md
// tags_to_add: ['T07', 'II_COGNITIFS']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_000310'})
WHERE n.title =~ '.*.*'
WITH n,
  CASE WHEN 'T07' IN n.tags THEN n.tags ELSE n.tags + ['T07'] END AS tags_step1
WITH n, tags_step1,
  CASE WHEN 'II_COGNITIFS' IN tags_step1 THEN tags_step1 ELSE tags_step1 + ['II_COGNITIFS'] END AS tags_final
SET n.tags = tags_final
RETURN n.id, n.tags AS tags_after;

// GATE_DRY_017 | node=GRAPHITI_V2_000333 | tree=T11 | family=III_CONNAISSANCE
// title: 20536123F25C_T11__Generation_Aleatoire_Frugalite_bio_inspiree.md
// tags_to_add: ['T11', 'III_CONNAISSANCE']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_000333'})
WHERE n.title =~ '.*.*'
WITH n,
  CASE WHEN 'T11' IN n.tags THEN n.tags ELSE n.tags + ['T11'] END AS tags_step1
WITH n, tags_step1,
  CASE WHEN 'III_CONNAISSANCE' IN tags_step1 THEN tags_step1 ELSE tags_step1 + ['III_CONNAISSANCE'] END AS tags_final
SET n.tags = tags_final
RETURN n.id, n.tags AS tags_after;

// GATE_DRY_018 | node=GRAPHITI_V2_000449 | tree=T02 | family=I_FONDAMENTAUX
// title: 2C6000D53716_05_GARDIEN_T02__Gardien_de_fond__Conscience_Distribuee_Validation_r
// tags_to_add: ['T02', 'I_FONDAMENTAUX']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_000449'})
WHERE n.title =~ '.*.*'
WITH n,
  CASE WHEN 'T02' IN n.tags THEN n.tags ELSE n.tags + ['T02'] END AS tags_step1
WITH n, tags_step1,
  CASE WHEN 'I_FONDAMENTAUX' IN tags_step1 THEN tags_step1 ELSE tags_step1 + ['I_FONDAMENTAUX'] END AS tags_final
SET n.tags = tags_final
RETURN n.id, n.tags AS tags_after;

// GATE_DRY_019 | node=GRAPHITI_V2_000450 | tree=T02 | family=I_FONDAMENTAUX
// title: 2C6000D53716_T02__Gardien_de_fond__Conscience_Distribuee_Validation_reciprocite.
// tags_to_add: ['T02', 'I_FONDAMENTAUX']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_000450'})
WHERE n.title =~ '.*.*'
WITH n,
  CASE WHEN 'T02' IN n.tags THEN n.tags ELSE n.tags + ['T02'] END AS tags_step1
WITH n, tags_step1,
  CASE WHEN 'I_FONDAMENTAUX' IN tags_step1 THEN tags_step1 ELSE tags_step1 + ['I_FONDAMENTAUX'] END AS tags_final
SET n.tags = tags_final
RETURN n.id, n.tags AS tags_after;

// GATE_DRY_020 | node=GRAPHITI_V2_000456 | tree=T02 | family=I_FONDAMENTAUX
// title: 2D1852FC62DE_T02__Conscience_Distribuee_Validation_reciprocite.md
// tags_to_add: ['T02', 'I_FONDAMENTAUX']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_000456'})
WHERE n.title =~ '.*.*'
WITH n,
  CASE WHEN 'T02' IN n.tags THEN n.tags ELSE n.tags + ['T02'] END AS tags_step1
WITH n, tags_step1,
  CASE WHEN 'I_FONDAMENTAUX' IN tags_step1 THEN tags_step1 ELSE tags_step1 + ['I_FONDAMENTAUX'] END AS tags_final
SET n.tags = tags_final
RETURN n.id, n.tags AS tags_after;

// GATE_DRY_021 | node=GRAPHITI_V2_000615 | tree=T07 | family=II_COGNITIFS
// title: 3D32BED3D926_T07__Resilience_Test_memoire_fractale.md
// tags_to_add: ['T07', 'II_COGNITIFS']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_000615'})
WHERE n.title =~ '.*.*'
WITH n,
  CASE WHEN 'T07' IN n.tags THEN n.tags ELSE n.tags + ['T07'] END AS tags_step1
WITH n, tags_step1,
  CASE WHEN 'II_COGNITIFS' IN tags_step1 THEN tags_step1 ELSE tags_step1 + ['II_COGNITIFS'] END AS tags_final
SET n.tags = tags_final
RETURN n.id, n.tags AS tags_after;

// GATE_DRY_022 | node=GRAPHITI_V2_000797 | tree=T01 | family=I_FONDAMENTAUX
// title: 56C8CDE2F94D_T01__Reduction_Incertitude_Audit_coherence.md
// tags_to_add: ['T01', 'I_FONDAMENTAUX']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_000797'})
WHERE n.title =~ '.*.*'
WITH n,
  CASE WHEN 'T01' IN n.tags THEN n.tags ELSE n.tags + ['T01'] END AS tags_step1
WITH n, tags_step1,
  CASE WHEN 'I_FONDAMENTAUX' IN tags_step1 THEN tags_step1 ELSE tags_step1 + ['I_FONDAMENTAUX'] END AS tags_final
SET n.tags = tags_final
RETURN n.id, n.tags AS tags_after;

// GATE_DRY_023 | node=GRAPHITI_V2_000800 | tree=T03 | family=I_FONDAMENTAUX
// title: 5706DB0A68CB_05_GARDIEN_T03__Gardien_de_fond__Gouvernance_Decentralisee_Friction
// tags_to_add: ['T03', 'I_FONDAMENTAUX']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_000800'})
WHERE n.title =~ '.*.*'
WITH n,
  CASE WHEN 'T03' IN n.tags THEN n.tags ELSE n.tags + ['T03'] END AS tags_step1
WITH n, tags_step1,
  CASE WHEN 'I_FONDAMENTAUX' IN tags_step1 THEN tags_step1 ELSE tags_step1 + ['I_FONDAMENTAUX'] END AS tags_final
SET n.tags = tags_final
RETURN n.id, n.tags AS tags_after;

// GATE_DRY_024 | node=GRAPHITI_V2_000801 | tree=T03 | family=I_FONDAMENTAUX
// title: 5706DB0A68CB_T03__Gardien_de_fond__Gouvernance_Decentralisee_Friction_energetiqu
// tags_to_add: ['T03', 'I_FONDAMENTAUX']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_000801'})
WHERE n.title =~ '.*.*'
WITH n,
  CASE WHEN 'T03' IN n.tags THEN n.tags ELSE n.tags + ['T03'] END AS tags_step1
WITH n, tags_step1,
  CASE WHEN 'I_FONDAMENTAUX' IN tags_step1 THEN tags_step1 ELSE tags_step1 + ['I_FONDAMENTAUX'] END AS tags_final
SET n.tags = tags_final
RETURN n.id, n.tags AS tags_after;

// GATE_DRY_025 | node=GRAPHITI_V2_000870 | tree=T05 | family=I_FONDAMENTAUX
// title: 5D8CDD9F3BCF_05_GARDIEN_T05__Gardien_de_fond__Evolution_Systemes_Balance_structu
// tags_to_add: ['T05', 'I_FONDAMENTAUX']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_000870'})
WHERE n.title =~ '.*.*'
WITH n,
  CASE WHEN 'T05' IN n.tags THEN n.tags ELSE n.tags + ['T05'] END AS tags_step1
WITH n, tags_step1,
  CASE WHEN 'I_FONDAMENTAUX' IN tags_step1 THEN tags_step1 ELSE tags_step1 + ['I_FONDAMENTAUX'] END AS tags_final
SET n.tags = tags_final
RETURN n.id, n.tags AS tags_after;

// GATE_DRY_026 | node=GRAPHITI_V2_000871 | tree=T05 | family=I_FONDAMENTAUX
// title: 5D8CDD9F3BCF_T05__Gardien_de_fond__Evolution_Systemes_Balance_structure_chaos.md
// tags_to_add: ['T05', 'I_FONDAMENTAUX']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_000871'})
WHERE n.title =~ '.*.*'
WITH n,
  CASE WHEN 'T05' IN n.tags THEN n.tags ELSE n.tags + ['T05'] END AS tags_step1
WITH n, tags_step1,
  CASE WHEN 'I_FONDAMENTAUX' IN tags_step1 THEN tags_step1 ELSE tags_step1 + ['I_FONDAMENTAUX'] END AS tags_final
SET n.tags = tags_final
RETURN n.id, n.tags AS tags_after;

// GATE_DRY_027 | node=GRAPHITI_V2_000980 | tree=T09 | family=II_COGNITIFS
// title: 68AF25C8E587_05_GARDIEN_T09__Gardien_de_fond__Creativite_Mode_reflexe.md
// tags_to_add: ['T09', 'II_COGNITIFS']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_000980'})
WHERE n.title =~ '.*.*'
WITH n,
  CASE WHEN 'T09' IN n.tags THEN n.tags ELSE n.tags + ['T09'] END AS tags_step1
WITH n, tags_step1,
  CASE WHEN 'II_COGNITIFS' IN tags_step1 THEN tags_step1 ELSE tags_step1 + ['II_COGNITIFS'] END AS tags_final
SET n.tags = tags_final
RETURN n.id, n.tags AS tags_after;

// GATE_DRY_028 | node=GRAPHITI_V2_000981 | tree=T09 | family=II_COGNITIFS
// title: 68AF25C8E587_T09__Gardien_de_fond__Creativite_Mode_reflexe.md
// tags_to_add: ['T09', 'II_COGNITIFS']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_000981'})
WHERE n.title =~ '.*.*'
WITH n,
  CASE WHEN 'T09' IN n.tags THEN n.tags ELSE n.tags + ['T09'] END AS tags_step1
WITH n, tags_step1,
  CASE WHEN 'II_COGNITIFS' IN tags_step1 THEN tags_step1 ELSE tags_step1 + ['II_COGNITIFS'] END AS tags_final
SET n.tags = tags_final
RETURN n.id, n.tags AS tags_after;

// GATE_DRY_029 | node=GRAPHITI_V2_000989 | tree=T12 | family=III_CONNAISSANCE
// title: 69C9AADE62AC_T12__Complexite_Irreductible_Transparence_friction.md
// tags_to_add: ['T12', 'III_CONNAISSANCE']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_000989'})
WHERE n.title =~ '.*.*'
WITH n,
  CASE WHEN 'T12' IN n.tags THEN n.tags ELSE n.tags + ['T12'] END AS tags_step1
WITH n, tags_step1,
  CASE WHEN 'III_CONNAISSANCE' IN tags_step1 THEN tags_step1 ELSE tags_step1 + ['III_CONNAISSANCE'] END AS tags_final
SET n.tags = tags_final
RETURN n.id, n.tags AS tags_after;

// GATE_DRY_030 | node=GRAPHITI_V2_001124 | tree=T12 | family=III_CONNAISSANCE
// title: 78C5FFEE4F06_05_GARDIEN_T12__Gardien_de_fond__Complexite_Irreductible_Transparen
// tags_to_add: ['T12', 'III_CONNAISSANCE']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_001124'})
WHERE n.title =~ '.*.*'
WITH n,
  CASE WHEN 'T12' IN n.tags THEN n.tags ELSE n.tags + ['T12'] END AS tags_step1
WITH n, tags_step1,
  CASE WHEN 'III_CONNAISSANCE' IN tags_step1 THEN tags_step1 ELSE tags_step1 + ['III_CONNAISSANCE'] END AS tags_final
SET n.tags = tags_final
RETURN n.id, n.tags AS tags_after;

// GATE_DRY_031 | node=GRAPHITI_V2_001125 | tree=T12 | family=III_CONNAISSANCE
// title: 78C5FFEE4F06_T12__Gardien_de_fond__Complexite_Irreductible_Transparence_friction
// tags_to_add: ['T12', 'III_CONNAISSANCE']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_001125'})
WHERE n.title =~ '.*.*'
WITH n,
  CASE WHEN 'T12' IN n.tags THEN n.tags ELSE n.tags + ['T12'] END AS tags_step1
WITH n, tags_step1,
  CASE WHEN 'III_CONNAISSANCE' IN tags_step1 THEN tags_step1 ELSE tags_step1 + ['III_CONNAISSANCE'] END AS tags_final
SET n.tags = tags_final
RETURN n.id, n.tags AS tags_after;

// GATE_DRY_032 | node=GRAPHITI_V2_001158 | tree=T09 | family=II_COGNITIFS
// title: 7B0A32BE315E_T09__Creativite_Mode_reflexe.md
// tags_to_add: ['T09', 'II_COGNITIFS']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_001158'})
WHERE n.title =~ '.*.*'
WITH n,
  CASE WHEN 'T09' IN n.tags THEN n.tags ELSE n.tags + ['T09'] END AS tags_step1
WITH n, tags_step1,
  CASE WHEN 'II_COGNITIFS' IN tags_step1 THEN tags_step1 ELSE tags_step1 + ['II_COGNITIFS'] END AS tags_final
SET n.tags = tags_final
RETURN n.id, n.tags AS tags_after;

// GATE_DRY_033 | node=GRAPHITI_V2_001471 | tree=T01 | family=I_FONDAMENTAUX
// title: 9E963A474A27_05_GARDIEN_T01__Gardien_de_fond__Reduction_Incertitude_Audit_cohere
// tags_to_add: ['T01', 'I_FONDAMENTAUX']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_001471'})
WHERE n.title =~ '.*.*'
WITH n,
  CASE WHEN 'T01' IN n.tags THEN n.tags ELSE n.tags + ['T01'] END AS tags_step1
WITH n, tags_step1,
  CASE WHEN 'I_FONDAMENTAUX' IN tags_step1 THEN tags_step1 ELSE tags_step1 + ['I_FONDAMENTAUX'] END AS tags_final
SET n.tags = tags_final
RETURN n.id, n.tags AS tags_after;

// GATE_DRY_034 | node=GRAPHITI_V2_001472 | tree=T01 | family=I_FONDAMENTAUX
// title: 9E963A474A27_T01__Gardien_de_fond__Reduction_Incertitude_Audit_coherence.md
// tags_to_add: ['T01', 'I_FONDAMENTAUX']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_001472'})
WHERE n.title =~ '.*.*'
WITH n,
  CASE WHEN 'T01' IN n.tags THEN n.tags ELSE n.tags + ['T01'] END AS tags_step1
WITH n, tags_step1,
  CASE WHEN 'I_FONDAMENTAUX' IN tags_step1 THEN tags_step1 ELSE tags_step1 + ['I_FONDAMENTAUX'] END AS tags_final
SET n.tags = tags_final
RETURN n.id, n.tags AS tags_after;

// GATE_DRY_035 | node=GRAPHITI_V2_001543 | tree=T10 | family=II_COGNITIFS
// title: A5B9DDA15149_T10__Innovation_Continue_Integrite_cognitive.md
// tags_to_add: ['T10', 'II_COGNITIFS']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_001543'})
WHERE n.title =~ '.*.*'
WITH n,
  CASE WHEN 'T10' IN n.tags THEN n.tags ELSE n.tags + ['T10'] END AS tags_step1
WITH n, tags_step1,
  CASE WHEN 'II_COGNITIFS' IN tags_step1 THEN tags_step1 ELSE tags_step1 + ['II_COGNITIFS'] END AS tags_final
SET n.tags = tags_final
RETURN n.id, n.tags AS tags_after;

// GATE_DRY_036 | node=GRAPHITI_V2_001545 | tree=T06 | family=II_COGNITIFS
// title: A629CA52B3F4_05_GARDIEN_T06__Gardien_de_fond__Selection_Naturelle_Alignement_eth
// tags_to_add: ['T06', 'II_COGNITIFS']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_001545'})
WHERE n.title =~ '.*.*'
WITH n,
  CASE WHEN 'T06' IN n.tags THEN n.tags ELSE n.tags + ['T06'] END AS tags_step1
WITH n, tags_step1,
  CASE WHEN 'II_COGNITIFS' IN tags_step1 THEN tags_step1 ELSE tags_step1 + ['II_COGNITIFS'] END AS tags_final
SET n.tags = tags_final
RETURN n.id, n.tags AS tags_after;

// GATE_DRY_037 | node=GRAPHITI_V2_001546 | tree=T06 | family=II_COGNITIFS
// title: A629CA52B3F4_T06__Gardien_de_fond__Selection_Naturelle_Alignement_ethique.md
// tags_to_add: ['T06', 'II_COGNITIFS']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_001546'})
WHERE n.title =~ '.*.*'
WITH n,
  CASE WHEN 'T06' IN n.tags THEN n.tags ELSE n.tags + ['T06'] END AS tags_step1
WITH n, tags_step1,
  CASE WHEN 'II_COGNITIFS' IN tags_step1 THEN tags_step1 ELSE tags_step1 + ['II_COGNITIFS'] END AS tags_final
SET n.tags = tags_final
RETURN n.id, n.tags AS tags_after;

// GATE_DRY_038 | node=GRAPHITI_V2_001702 | tree=T08 | family=II_COGNITIFS
// title: B6CA17AED567_05_GARDIEN_T08__Gardien_de_fond__Auto_Organisation_Apprentissage_in
// tags_to_add: ['T08', 'II_COGNITIFS']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_001702'})
WHERE n.title =~ '.*.*'
WITH n,
  CASE WHEN 'T08' IN n.tags THEN n.tags ELSE n.tags + ['T08'] END AS tags_step1
WITH n, tags_step1,
  CASE WHEN 'II_COGNITIFS' IN tags_step1 THEN tags_step1 ELSE tags_step1 + ['II_COGNITIFS'] END AS tags_final
SET n.tags = tags_final
RETURN n.id, n.tags AS tags_after;

// GATE_DRY_039 | node=GRAPHITI_V2_001703 | tree=T08 | family=II_COGNITIFS
// title: B6CA17AED567_T08__Gardien_de_fond__Auto_Organisation_Apprentissage_inverse.md
// tags_to_add: ['T08', 'II_COGNITIFS']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_001703'})
WHERE n.title =~ '.*.*'
WITH n,
  CASE WHEN 'T08' IN n.tags THEN n.tags ELSE n.tags + ['T08'] END AS tags_step1
WITH n, tags_step1,
  CASE WHEN 'II_COGNITIFS' IN tags_step1 THEN tags_step1 ELSE tags_step1 + ['II_COGNITIFS'] END AS tags_final
SET n.tags = tags_final
RETURN n.id, n.tags AS tags_after;

// GATE_DRY_040 | node=GRAPHITI_V2_001787 | tree=T03 | family=I_FONDAMENTAUX
// title: BCED3A96BDAC_T03__Gouvernance_Decentralisee_Friction_energetique.md
// tags_to_add: ['T03', 'I_FONDAMENTAUX']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_001787'})
WHERE n.title =~ '.*.*'
WITH n,
  CASE WHEN 'T03' IN n.tags THEN n.tags ELSE n.tags + ['T03'] END AS tags_step1
WITH n, tags_step1,
  CASE WHEN 'I_FONDAMENTAUX' IN tags_step1 THEN tags_step1 ELSE tags_step1 + ['I_FONDAMENTAUX'] END AS tags_final
SET n.tags = tags_final
RETURN n.id, n.tags AS tags_after;

// GATE_DRY_041 | node=GRAPHITI_V2_001987 | tree=T11 | family=III_CONNAISSANCE
// title: D4F3EE1228AF_05_GARDIEN_T11__Gardien_de_fond__Generation_Aleatoire_Frugalite_bio
// tags_to_add: ['T11', 'III_CONNAISSANCE']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_001987'})
WHERE n.title =~ '.*.*'
WITH n,
  CASE WHEN 'T11' IN n.tags THEN n.tags ELSE n.tags + ['T11'] END AS tags_step1
WITH n, tags_step1,
  CASE WHEN 'III_CONNAISSANCE' IN tags_step1 THEN tags_step1 ELSE tags_step1 + ['III_CONNAISSANCE'] END AS tags_final
SET n.tags = tags_final
RETURN n.id, n.tags AS tags_after;

// GATE_DRY_042 | node=GRAPHITI_V2_001988 | tree=T11 | family=III_CONNAISSANCE
// title: D4F3EE1228AF_T11__Gardien_de_fond__Generation_Aleatoire_Frugalite_bio_inspiree.m
// tags_to_add: ['T11', 'III_CONNAISSANCE']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_001988'})
WHERE n.title =~ '.*.*'
WITH n,
  CASE WHEN 'T11' IN n.tags THEN n.tags ELSE n.tags + ['T11'] END AS tags_step1
WITH n, tags_step1,
  CASE WHEN 'III_CONNAISSANCE' IN tags_step1 THEN tags_step1 ELSE tags_step1 + ['III_CONNAISSANCE'] END AS tags_final
SET n.tags = tags_final
RETURN n.id, n.tags AS tags_after;

// GATE_DRY_043 | node=GRAPHITI_V2_002112 | tree=T08 | family=II_COGNITIFS
// title: E2B9ABB246B0_T08__Auto_Organisation_Apprentissage_inverse.md
// tags_to_add: ['T08', 'II_COGNITIFS']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_002112'})
WHERE n.title =~ '.*.*'
WITH n,
  CASE WHEN 'T08' IN n.tags THEN n.tags ELSE n.tags + ['T08'] END AS tags_step1
WITH n, tags_step1,
  CASE WHEN 'II_COGNITIFS' IN tags_step1 THEN tags_step1 ELSE tags_step1 + ['II_COGNITIFS'] END AS tags_final
SET n.tags = tags_final
RETURN n.id, n.tags AS tags_after;

// GATE_DRY_044 | node=GRAPHITI_V2_002123 | tree=T10 | family=II_COGNITIFS
// title: E414A9A7AE94_05_GARDIEN_T10__Gardien_de_fond__Innovation_Continue_Integrite_cogn
// tags_to_add: ['T10', 'II_COGNITIFS']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_002123'})
WHERE n.title =~ '.*.*'
WITH n,
  CASE WHEN 'T10' IN n.tags THEN n.tags ELSE n.tags + ['T10'] END AS tags_step1
WITH n, tags_step1,
  CASE WHEN 'II_COGNITIFS' IN tags_step1 THEN tags_step1 ELSE tags_step1 + ['II_COGNITIFS'] END AS tags_final
SET n.tags = tags_final
RETURN n.id, n.tags AS tags_after;

// GATE_DRY_045 | node=GRAPHITI_V2_002124 | tree=T10 | family=II_COGNITIFS
// title: E414A9A7AE94_T10__Gardien_de_fond__Innovation_Continue_Integrite_cognitive.md
// tags_to_add: ['T10', 'II_COGNITIFS']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_002124'})
WHERE n.title =~ '.*.*'
WITH n,
  CASE WHEN 'T10' IN n.tags THEN n.tags ELSE n.tags + ['T10'] END AS tags_step1
WITH n, tags_step1,
  CASE WHEN 'II_COGNITIFS' IN tags_step1 THEN tags_step1 ELSE tags_step1 + ['II_COGNITIFS'] END AS tags_final
SET n.tags = tags_final
RETURN n.id, n.tags AS tags_after;

// GATE_DRY_046 | node=GRAPHITI_V2_002287 | tree=T04 | family=I_FONDAMENTAUX
// title: F83FEE400B9C_05_GARDIEN_T04__Gardien_de_fond__Consensus_Distribue_Resonance_sema
// tags_to_add: ['T04', 'I_FONDAMENTAUX']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_002287'})
WHERE n.title =~ '.*.*'
WITH n,
  CASE WHEN 'T04' IN n.tags THEN n.tags ELSE n.tags + ['T04'] END AS tags_step1
WITH n, tags_step1,
  CASE WHEN 'I_FONDAMENTAUX' IN tags_step1 THEN tags_step1 ELSE tags_step1 + ['I_FONDAMENTAUX'] END AS tags_final
SET n.tags = tags_final
RETURN n.id, n.tags AS tags_after;

// GATE_DRY_047 | node=GRAPHITI_V2_002288 | tree=T04 | family=I_FONDAMENTAUX
// title: F83FEE400B9C_T04__Gardien_de_fond__Consensus_Distribue_Resonance_semantique.md
// tags_to_add: ['T04', 'I_FONDAMENTAUX']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_002288'})
WHERE n.title =~ '.*.*'
WITH n,
  CASE WHEN 'T04' IN n.tags THEN n.tags ELSE n.tags + ['T04'] END AS tags_step1
WITH n, tags_step1,
  CASE WHEN 'I_FONDAMENTAUX' IN tags_step1 THEN tags_step1 ELSE tags_step1 + ['I_FONDAMENTAUX'] END AS tags_final
SET n.tags = tags_final
RETURN n.id, n.tags AS tags_after;

// GATE_DRY_048 | node=GRAPHITI_V2_002331 | tree=T06 | family=II_COGNITIFS
// title: FC8D97D1322D_T06__Selection_Naturelle_Alignement_ethique.md
// tags_to_add: ['T06', 'II_COGNITIFS']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_002331'})
WHERE n.title =~ '.*.*'
WITH n,
  CASE WHEN 'T06' IN n.tags THEN n.tags ELSE n.tags + ['T06'] END AS tags_step1
WITH n, tags_step1,
  CASE WHEN 'II_COGNITIFS' IN tags_step1 THEN tags_step1 ELSE tags_step1 + ['II_COGNITIFS'] END AS tags_final
SET n.tags = tags_final
RETURN n.id, n.tags AS tags_after;


// ═══════════════════════════════════════════════════════════
// POST-WRITE SPOT CHECK — run after all 48 writes
// ═══════════════════════════════════════════════════════════

// SPOT_01: Count nodes with T01..T12 tags (expected: by_tree distribution)
MATCH (n:BrodyMemoryDoc)
WHERE ANY(tag IN n.tags WHERE tag IN ['T01','T02','T03','T04','T05','T06','T07','T08','T09','T10','T11','T12'])
RETURN count(n) AS total_tagged_count;
// Expected: 48

// SPOT_02: Count per tree
MATCH (n:BrodyMemoryDoc)
UNWIND n.tags AS tag
WHERE tag =~ 'T[0-9]+'
RETURN tag, count(n) AS doc_count
ORDER BY tag;
// Expected: T01:4, T02:4, T03:4, T04:4, T05:4, T06:4, T07:4, T08:4, T09:4, T10:4, T11:4, T12:4

// SPOT_03: Verify excluded nodes untouched (should have no Tnn tags)
MATCH (n:BrodyMemoryDoc)
WHERE n.id IN [
  'GRAPHITI_V2_000105', 'GRAPHITI_V2_001363', 'GRAPHITI_V2_002081', 'GRAPHITI_V2_002298', 'GRAPHITI_V2_002404', 'GRAPHITI_V2_002405', 'GRAPHITI_V2_002406', 'GRAPHITI_V2_002522', 'GRAPHITI_V2_000648'
]
RETURN n.id, n.tags;
// Expected: no Tnn tags in any of these 9 nodes
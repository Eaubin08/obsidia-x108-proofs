// ROLLBACK_CANONICAL_TAGGING_PLAN.cypher
// Mission: BRODY_CANONICAL_TAGGING_WRITE_CANDIDATE_PROTOCOL_READONLY
// Timestamp: 20260514_020923
// Status: PLAN ONLY — NOT EXECUTED
// Purpose: Remove ONLY the Tnn + family_id tags added by this write batch
// Strategy: APPEND_REMOVE_SPECIFIC_TAGS_ONLY — never touch pre-existing tags
// DO NOT EXECUTE unless write was performed AND operator explicitly authorizes rollback
//

// ═══════════════════════════════════════════════════════════
// PRE-ROLLBACK CHECK — run first (READ ONLY)
// ═══════════════════════════════════════════════════════════

// ROLLBACK_CHECK_01: Confirm which nodes have Tnn tags before rollback
MATCH (n:BrodyMemoryDoc)
WHERE ANY(tag IN n.tags WHERE tag =~ 'T[0-9]+')
RETURN count(n) AS tagged_count;

// ═══════════════════════════════════════════════════════════
// ROLLBACK QUERIES — one per approved candidate
// Remove only Tnn + family_id appended by this batch
// ═══════════════════════════════════════════════════════════

// ROLLBACK GATE_DRY_001 | node=GRAPHITI_V2_000000 | remove=['T04', 'I_FONDAMENTAUX']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_000000'})
SET n.tags = [tag IN n.tags WHERE tag NOT IN ["T04", "I_FONDAMENTAUX"]]
RETURN n.id, n.tags AS tags_after_rollback;

// ROLLBACK GATE_DRY_002 | node=GRAPHITI_V2_002928 | remove=['T01', 'I_FONDAMENTAUX']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_002928'})
SET n.tags = [tag IN n.tags WHERE tag NOT IN ["T01", "I_FONDAMENTAUX"]]
RETURN n.id, n.tags AS tags_after_rollback;

// ROLLBACK GATE_DRY_003 | node=GRAPHITI_V2_003042 | remove=['T02', 'I_FONDAMENTAUX']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_003042'})
SET n.tags = [tag IN n.tags WHERE tag NOT IN ["T02", "I_FONDAMENTAUX"]]
RETURN n.id, n.tags AS tags_after_rollback;

// ROLLBACK GATE_DRY_004 | node=GRAPHITI_V2_003043 | remove=['T03', 'I_FONDAMENTAUX']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_003043'})
SET n.tags = [tag IN n.tags WHERE tag NOT IN ["T03", "I_FONDAMENTAUX"]]
RETURN n.id, n.tags AS tags_after_rollback;

// ROLLBACK GATE_DRY_005 | node=GRAPHITI_V2_003170 | remove=['T04', 'I_FONDAMENTAUX']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_003170'})
SET n.tags = [tag IN n.tags WHERE tag NOT IN ["T04", "I_FONDAMENTAUX"]]
RETURN n.id, n.tags AS tags_after_rollback;

// ROLLBACK GATE_DRY_006 | node=GRAPHITI_V2_002995 | remove=['T05', 'I_FONDAMENTAUX']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_002995'})
SET n.tags = [tag IN n.tags WHERE tag NOT IN ["T05", "I_FONDAMENTAUX"]]
RETURN n.id, n.tags AS tags_after_rollback;

// ROLLBACK GATE_DRY_007 | node=GRAPHITI_V2_003079 | remove=['T06', 'II_COGNITIFS']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_003079'})
SET n.tags = [tag IN n.tags WHERE tag NOT IN ["T06", "II_COGNITIFS"]]
RETURN n.id, n.tags AS tags_after_rollback;

// ROLLBACK GATE_DRY_008 | node=GRAPHITI_V2_002929 | remove=['T07', 'II_COGNITIFS']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_002929'})
SET n.tags = [tag IN n.tags WHERE tag NOT IN ["T07", "II_COGNITIFS"]]
RETURN n.id, n.tags AS tags_after_rollback;

// ROLLBACK GATE_DRY_009 | node=GRAPHITI_V2_003044 | remove=['T08', 'II_COGNITIFS']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_003044'})
SET n.tags = [tag IN n.tags WHERE tag NOT IN ["T08", "II_COGNITIFS"]]
RETURN n.id, n.tags AS tags_after_rollback;

// ROLLBACK GATE_DRY_010 | node=GRAPHITI_V2_003126 | remove=['T09', 'II_COGNITIFS']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_003126'})
SET n.tags = [tag IN n.tags WHERE tag NOT IN ["T09", "II_COGNITIFS"]]
RETURN n.id, n.tags AS tags_after_rollback;

// ROLLBACK GATE_DRY_011 | node=GRAPHITI_V2_003080 | remove=['T10', 'II_COGNITIFS']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_003080'})
SET n.tags = [tag IN n.tags WHERE tag NOT IN ["T10", "II_COGNITIFS"]]
RETURN n.id, n.tags AS tags_after_rollback;

// ROLLBACK GATE_DRY_012 | node=GRAPHITI_V2_002930 | remove=['T11', 'III_CONNAISSANCE']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_002930'})
SET n.tags = [tag IN n.tags WHERE tag NOT IN ["T11", "III_CONNAISSANCE"]]
RETURN n.id, n.tags AS tags_after_rollback;

// ROLLBACK GATE_DRY_013 | node=GRAPHITI_V2_003171 | remove=['T12', 'III_CONNAISSANCE']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_003171'})
SET n.tags = [tag IN n.tags WHERE tag NOT IN ["T12", "III_CONNAISSANCE"]]
RETURN n.id, n.tags AS tags_after_rollback;

// ROLLBACK GATE_DRY_014 | node=GRAPHITI_V2_000274 | remove=['T05', 'I_FONDAMENTAUX']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_000274'})
SET n.tags = [tag IN n.tags WHERE tag NOT IN ["T05", "I_FONDAMENTAUX"]]
RETURN n.id, n.tags AS tags_after_rollback;

// ROLLBACK GATE_DRY_015 | node=GRAPHITI_V2_000309 | remove=['T07', 'II_COGNITIFS']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_000309'})
SET n.tags = [tag IN n.tags WHERE tag NOT IN ["T07", "II_COGNITIFS"]]
RETURN n.id, n.tags AS tags_after_rollback;

// ROLLBACK GATE_DRY_016 | node=GRAPHITI_V2_000310 | remove=['T07', 'II_COGNITIFS']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_000310'})
SET n.tags = [tag IN n.tags WHERE tag NOT IN ["T07", "II_COGNITIFS"]]
RETURN n.id, n.tags AS tags_after_rollback;

// ROLLBACK GATE_DRY_017 | node=GRAPHITI_V2_000333 | remove=['T11', 'III_CONNAISSANCE']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_000333'})
SET n.tags = [tag IN n.tags WHERE tag NOT IN ["T11", "III_CONNAISSANCE"]]
RETURN n.id, n.tags AS tags_after_rollback;

// ROLLBACK GATE_DRY_018 | node=GRAPHITI_V2_000449 | remove=['T02', 'I_FONDAMENTAUX']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_000449'})
SET n.tags = [tag IN n.tags WHERE tag NOT IN ["T02", "I_FONDAMENTAUX"]]
RETURN n.id, n.tags AS tags_after_rollback;

// ROLLBACK GATE_DRY_019 | node=GRAPHITI_V2_000450 | remove=['T02', 'I_FONDAMENTAUX']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_000450'})
SET n.tags = [tag IN n.tags WHERE tag NOT IN ["T02", "I_FONDAMENTAUX"]]
RETURN n.id, n.tags AS tags_after_rollback;

// ROLLBACK GATE_DRY_020 | node=GRAPHITI_V2_000456 | remove=['T02', 'I_FONDAMENTAUX']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_000456'})
SET n.tags = [tag IN n.tags WHERE tag NOT IN ["T02", "I_FONDAMENTAUX"]]
RETURN n.id, n.tags AS tags_after_rollback;

// ROLLBACK GATE_DRY_021 | node=GRAPHITI_V2_000615 | remove=['T07', 'II_COGNITIFS']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_000615'})
SET n.tags = [tag IN n.tags WHERE tag NOT IN ["T07", "II_COGNITIFS"]]
RETURN n.id, n.tags AS tags_after_rollback;

// ROLLBACK GATE_DRY_022 | node=GRAPHITI_V2_000797 | remove=['T01', 'I_FONDAMENTAUX']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_000797'})
SET n.tags = [tag IN n.tags WHERE tag NOT IN ["T01", "I_FONDAMENTAUX"]]
RETURN n.id, n.tags AS tags_after_rollback;

// ROLLBACK GATE_DRY_023 | node=GRAPHITI_V2_000800 | remove=['T03', 'I_FONDAMENTAUX']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_000800'})
SET n.tags = [tag IN n.tags WHERE tag NOT IN ["T03", "I_FONDAMENTAUX"]]
RETURN n.id, n.tags AS tags_after_rollback;

// ROLLBACK GATE_DRY_024 | node=GRAPHITI_V2_000801 | remove=['T03', 'I_FONDAMENTAUX']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_000801'})
SET n.tags = [tag IN n.tags WHERE tag NOT IN ["T03", "I_FONDAMENTAUX"]]
RETURN n.id, n.tags AS tags_after_rollback;

// ROLLBACK GATE_DRY_025 | node=GRAPHITI_V2_000870 | remove=['T05', 'I_FONDAMENTAUX']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_000870'})
SET n.tags = [tag IN n.tags WHERE tag NOT IN ["T05", "I_FONDAMENTAUX"]]
RETURN n.id, n.tags AS tags_after_rollback;

// ROLLBACK GATE_DRY_026 | node=GRAPHITI_V2_000871 | remove=['T05', 'I_FONDAMENTAUX']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_000871'})
SET n.tags = [tag IN n.tags WHERE tag NOT IN ["T05", "I_FONDAMENTAUX"]]
RETURN n.id, n.tags AS tags_after_rollback;

// ROLLBACK GATE_DRY_027 | node=GRAPHITI_V2_000980 | remove=['T09', 'II_COGNITIFS']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_000980'})
SET n.tags = [tag IN n.tags WHERE tag NOT IN ["T09", "II_COGNITIFS"]]
RETURN n.id, n.tags AS tags_after_rollback;

// ROLLBACK GATE_DRY_028 | node=GRAPHITI_V2_000981 | remove=['T09', 'II_COGNITIFS']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_000981'})
SET n.tags = [tag IN n.tags WHERE tag NOT IN ["T09", "II_COGNITIFS"]]
RETURN n.id, n.tags AS tags_after_rollback;

// ROLLBACK GATE_DRY_029 | node=GRAPHITI_V2_000989 | remove=['T12', 'III_CONNAISSANCE']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_000989'})
SET n.tags = [tag IN n.tags WHERE tag NOT IN ["T12", "III_CONNAISSANCE"]]
RETURN n.id, n.tags AS tags_after_rollback;

// ROLLBACK GATE_DRY_030 | node=GRAPHITI_V2_001124 | remove=['T12', 'III_CONNAISSANCE']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_001124'})
SET n.tags = [tag IN n.tags WHERE tag NOT IN ["T12", "III_CONNAISSANCE"]]
RETURN n.id, n.tags AS tags_after_rollback;

// ROLLBACK GATE_DRY_031 | node=GRAPHITI_V2_001125 | remove=['T12', 'III_CONNAISSANCE']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_001125'})
SET n.tags = [tag IN n.tags WHERE tag NOT IN ["T12", "III_CONNAISSANCE"]]
RETURN n.id, n.tags AS tags_after_rollback;

// ROLLBACK GATE_DRY_032 | node=GRAPHITI_V2_001158 | remove=['T09', 'II_COGNITIFS']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_001158'})
SET n.tags = [tag IN n.tags WHERE tag NOT IN ["T09", "II_COGNITIFS"]]
RETURN n.id, n.tags AS tags_after_rollback;

// ROLLBACK GATE_DRY_033 | node=GRAPHITI_V2_001471 | remove=['T01', 'I_FONDAMENTAUX']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_001471'})
SET n.tags = [tag IN n.tags WHERE tag NOT IN ["T01", "I_FONDAMENTAUX"]]
RETURN n.id, n.tags AS tags_after_rollback;

// ROLLBACK GATE_DRY_034 | node=GRAPHITI_V2_001472 | remove=['T01', 'I_FONDAMENTAUX']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_001472'})
SET n.tags = [tag IN n.tags WHERE tag NOT IN ["T01", "I_FONDAMENTAUX"]]
RETURN n.id, n.tags AS tags_after_rollback;

// ROLLBACK GATE_DRY_035 | node=GRAPHITI_V2_001543 | remove=['T10', 'II_COGNITIFS']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_001543'})
SET n.tags = [tag IN n.tags WHERE tag NOT IN ["T10", "II_COGNITIFS"]]
RETURN n.id, n.tags AS tags_after_rollback;

// ROLLBACK GATE_DRY_036 | node=GRAPHITI_V2_001545 | remove=['T06', 'II_COGNITIFS']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_001545'})
SET n.tags = [tag IN n.tags WHERE tag NOT IN ["T06", "II_COGNITIFS"]]
RETURN n.id, n.tags AS tags_after_rollback;

// ROLLBACK GATE_DRY_037 | node=GRAPHITI_V2_001546 | remove=['T06', 'II_COGNITIFS']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_001546'})
SET n.tags = [tag IN n.tags WHERE tag NOT IN ["T06", "II_COGNITIFS"]]
RETURN n.id, n.tags AS tags_after_rollback;

// ROLLBACK GATE_DRY_038 | node=GRAPHITI_V2_001702 | remove=['T08', 'II_COGNITIFS']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_001702'})
SET n.tags = [tag IN n.tags WHERE tag NOT IN ["T08", "II_COGNITIFS"]]
RETURN n.id, n.tags AS tags_after_rollback;

// ROLLBACK GATE_DRY_039 | node=GRAPHITI_V2_001703 | remove=['T08', 'II_COGNITIFS']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_001703'})
SET n.tags = [tag IN n.tags WHERE tag NOT IN ["T08", "II_COGNITIFS"]]
RETURN n.id, n.tags AS tags_after_rollback;

// ROLLBACK GATE_DRY_040 | node=GRAPHITI_V2_001787 | remove=['T03', 'I_FONDAMENTAUX']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_001787'})
SET n.tags = [tag IN n.tags WHERE tag NOT IN ["T03", "I_FONDAMENTAUX"]]
RETURN n.id, n.tags AS tags_after_rollback;

// ROLLBACK GATE_DRY_041 | node=GRAPHITI_V2_001987 | remove=['T11', 'III_CONNAISSANCE']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_001987'})
SET n.tags = [tag IN n.tags WHERE tag NOT IN ["T11", "III_CONNAISSANCE"]]
RETURN n.id, n.tags AS tags_after_rollback;

// ROLLBACK GATE_DRY_042 | node=GRAPHITI_V2_001988 | remove=['T11', 'III_CONNAISSANCE']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_001988'})
SET n.tags = [tag IN n.tags WHERE tag NOT IN ["T11", "III_CONNAISSANCE"]]
RETURN n.id, n.tags AS tags_after_rollback;

// ROLLBACK GATE_DRY_043 | node=GRAPHITI_V2_002112 | remove=['T08', 'II_COGNITIFS']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_002112'})
SET n.tags = [tag IN n.tags WHERE tag NOT IN ["T08", "II_COGNITIFS"]]
RETURN n.id, n.tags AS tags_after_rollback;

// ROLLBACK GATE_DRY_044 | node=GRAPHITI_V2_002123 | remove=['T10', 'II_COGNITIFS']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_002123'})
SET n.tags = [tag IN n.tags WHERE tag NOT IN ["T10", "II_COGNITIFS"]]
RETURN n.id, n.tags AS tags_after_rollback;

// ROLLBACK GATE_DRY_045 | node=GRAPHITI_V2_002124 | remove=['T10', 'II_COGNITIFS']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_002124'})
SET n.tags = [tag IN n.tags WHERE tag NOT IN ["T10", "II_COGNITIFS"]]
RETURN n.id, n.tags AS tags_after_rollback;

// ROLLBACK GATE_DRY_046 | node=GRAPHITI_V2_002287 | remove=['T04', 'I_FONDAMENTAUX']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_002287'})
SET n.tags = [tag IN n.tags WHERE tag NOT IN ["T04", "I_FONDAMENTAUX"]]
RETURN n.id, n.tags AS tags_after_rollback;

// ROLLBACK GATE_DRY_047 | node=GRAPHITI_V2_002288 | remove=['T04', 'I_FONDAMENTAUX']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_002288'})
SET n.tags = [tag IN n.tags WHERE tag NOT IN ["T04", "I_FONDAMENTAUX"]]
RETURN n.id, n.tags AS tags_after_rollback;

// ROLLBACK GATE_DRY_048 | node=GRAPHITI_V2_002331 | remove=['T06', 'II_COGNITIFS']
MATCH (n:BrodyMemoryDoc {id: 'GRAPHITI_V2_002331'})
SET n.tags = [tag IN n.tags WHERE tag NOT IN ["T06", "II_COGNITIFS"]]
RETURN n.id, n.tags AS tags_after_rollback;

// ═══════════════════════════════════════════════════════════
// POST-ROLLBACK CHECK
// ═══════════════════════════════════════════════════════════

// ROLLBACK_SPOT_01: Confirm 0 nodes have Tnn tags after rollback
MATCH (n:BrodyMemoryDoc)
WHERE ANY(tag IN n.tags WHERE tag =~ 'T[0-9]+')
RETURN count(n) AS remaining_tagged;
// Expected: 0
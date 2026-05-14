// PATH_B WRITE CYPHER PLAN — APPEND_ONLY
// 117 nodes, 234 tags
// Generated: 20260514_032500
// DECISION_AUTHORITY=KX108_ONLY

// PATH_B_DRY_0008 — T13 Arbre de l'Art — activation_rules.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002694"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T13", "III_CONNAISSANCE"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0009 — T13 Arbre de l'Art — definition.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002695"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T13", "III_CONNAISSANCE"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0010 — T13 Arbre de l'Art — examples_events.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002696"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T13", "III_CONNAISSANCE"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0011 — T13 Arbre de l'Art — links_to_other_trees.json
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002697"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T13", "III_CONNAISSANCE"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0012 — T13 Arbre de l'Art — node_registry.json
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002698"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T13", "III_CONNAISSANCE"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0013 — T13 Arbre de l'Art — README.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002699"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T13", "III_CONNAISSANCE"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0014 — T13 Arbre de l'Art — risks_confusions.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002700"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T13", "III_CONNAISSANCE"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0015 — T13 Arbre de l'Art — tensor_coordinates.json
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002701"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T13", "III_CONNAISSANCE"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0016 — T13 Arbre de l'Art — tests.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002702"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T13", "III_CONNAISSANCE"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0025 — T14 Arbre de la Philosophie — activation_rules.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002703"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T14", "III_CONNAISSANCE"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0026 — T14 Arbre de la Philosophie — definition.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002704"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T14", "III_CONNAISSANCE"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0027 — T14 Arbre de la Philosophie — examples_events.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002705"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T14", "III_CONNAISSANCE"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0028 — T14 Arbre de la Philosophie — links_to_other_trees.json
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002706"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T14", "III_CONNAISSANCE"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0029 — T14 Arbre de la Philosophie — node_registry.json
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002707"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T14", "III_CONNAISSANCE"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0030 — T14 Arbre de la Philosophie — README.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002708"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T14", "III_CONNAISSANCE"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0031 — T14 Arbre de la Philosophie — risks_confusions.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002709"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T14", "III_CONNAISSANCE"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0032 — T14 Arbre de la Philosophie — tensor_coordinates.json
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002710"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T14", "III_CONNAISSANCE"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0033 — T14 Arbre de la Philosophie — tests.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002711"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T14", "III_CONNAISSANCE"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0042 — T15 Arbre de la Spiritualite — activation_rules.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002712"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T15", "III_CONNAISSANCE"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0043 — T15 Arbre de la Spiritualite — definition.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002713"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T15", "III_CONNAISSANCE"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0044 — T15 Arbre de la Spiritualite — examples_events.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002714"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T15", "III_CONNAISSANCE"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0045 — T15 Arbre de la Spiritualite — links_to_other_trees.json
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002715"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T15", "III_CONNAISSANCE"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0046 — T15 Arbre de la Spiritualite — node_registry.json
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002716"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T15", "III_CONNAISSANCE"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0047 — T15 Arbre de la Spiritualite — README.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002717"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T15", "III_CONNAISSANCE"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0048 — T15 Arbre de la Spiritualite — risks_confusions.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002718"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T15", "III_CONNAISSANCE"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0049 — T15 Arbre de la Spiritualite — tensor_coordinates.json
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002719"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T15", "III_CONNAISSANCE"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0050 — T15 Arbre de la Spiritualite — tests.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002720"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T15", "III_CONNAISSANCE"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0059 — T16 Arbre de la Relation — activation_rules.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002721"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T16", "IV_RELATIONNELS_SOCIAUX"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0060 — T16 Arbre de la Relation — definition.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002722"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T16", "IV_RELATIONNELS_SOCIAUX"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0061 — T16 Arbre de la Relation — examples_events.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002723"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T16", "IV_RELATIONNELS_SOCIAUX"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0062 — T16 Arbre de la Relation — links_to_other_trees.json
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002724"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T16", "IV_RELATIONNELS_SOCIAUX"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0063 — T16 Arbre de la Relation — node_registry.json
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002725"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T16", "IV_RELATIONNELS_SOCIAUX"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0064 — T16 Arbre de la Relation — README.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002726"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T16", "IV_RELATIONNELS_SOCIAUX"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0065 — T16 Arbre de la Relation — risks_confusions.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002727"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T16", "IV_RELATIONNELS_SOCIAUX"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0066 — T16 Arbre de la Relation — tensor_coordinates.json
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002728"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T16", "IV_RELATIONNELS_SOCIAUX"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0067 — T16 Arbre de la Relation — tests.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002729"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T16", "IV_RELATIONNELS_SOCIAUX"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0076 — T17 Arbre du Collectif — activation_rules.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002730"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T17", "IV_RELATIONNELS_SOCIAUX"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0077 — T17 Arbre du Collectif — definition.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002731"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T17", "IV_RELATIONNELS_SOCIAUX"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0078 — T17 Arbre du Collectif — examples_events.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002732"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T17", "IV_RELATIONNELS_SOCIAUX"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0079 — T17 Arbre du Collectif — links_to_other_trees.json
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002733"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T17", "IV_RELATIONNELS_SOCIAUX"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0080 — T17 Arbre du Collectif — node_registry.json
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002734"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T17", "IV_RELATIONNELS_SOCIAUX"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0081 — T17 Arbre du Collectif — README.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002735"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T17", "IV_RELATIONNELS_SOCIAUX"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0082 — T17 Arbre du Collectif — risks_confusions.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002736"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T17", "IV_RELATIONNELS_SOCIAUX"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0083 — T17 Arbre du Collectif — tensor_coordinates.json
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002737"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T17", "IV_RELATIONNELS_SOCIAUX"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0084 — T17 Arbre du Collectif — tests.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002738"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T17", "IV_RELATIONNELS_SOCIAUX"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0094 — T18 Arbre de la Transmission — activation_rules.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002739"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T18", "IV_RELATIONNELS_SOCIAUX"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0095 — T18 Arbre de la Transmission — definition.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002740"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T18", "IV_RELATIONNELS_SOCIAUX"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0096 — T18 Arbre de la Transmission — examples_events.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002741"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T18", "IV_RELATIONNELS_SOCIAUX"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0097 — T18 Arbre de la Transmission — links_to_other_trees.json
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002742"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T18", "IV_RELATIONNELS_SOCIAUX"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0098 — T18 Arbre de la Transmission — node_registry.json
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002743"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T18", "IV_RELATIONNELS_SOCIAUX"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0099 — T18 Arbre de la Transmission — README.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002744"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T18", "IV_RELATIONNELS_SOCIAUX"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0100 — T18 Arbre de la Transmission — risks_confusions.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002745"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T18", "IV_RELATIONNELS_SOCIAUX"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0101 — T18 Arbre de la Transmission — tensor_coordinates.json
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002746"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T18", "IV_RELATIONNELS_SOCIAUX"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0102 — T18 Arbre de la Transmission — tests.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002747"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T18", "IV_RELATIONNELS_SOCIAUX"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0110 — T19 Arbre de la Culture — activation_rules.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002748"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T19", "IV_RELATIONNELS_SOCIAUX"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0111 — T19 Arbre de la Culture — definition.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002749"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T19", "IV_RELATIONNELS_SOCIAUX"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0112 — T19 Arbre de la Culture — examples_events.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002750"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T19", "IV_RELATIONNELS_SOCIAUX"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0113 — T19 Arbre de la Culture — links_to_other_trees.json
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002751"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T19", "IV_RELATIONNELS_SOCIAUX"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0114 — T19 Arbre de la Culture — node_registry.json
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002752"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T19", "IV_RELATIONNELS_SOCIAUX"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0115 — T19 Arbre de la Culture — README.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002753"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T19", "IV_RELATIONNELS_SOCIAUX"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0116 — T19 Arbre de la Culture — risks_confusions.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002754"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T19", "IV_RELATIONNELS_SOCIAUX"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0117 — T19 Arbre de la Culture — tensor_coordinates.json
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002755"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T19", "IV_RELATIONNELS_SOCIAUX"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0118 — T19 Arbre de la Culture — tests.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002756"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T19", "IV_RELATIONNELS_SOCIAUX"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0174 — T23 Arbre du Temps — activation_rules.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002784"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T23", "VI_TEMPORELS_MEMORIELS"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0175 — T23 Arbre du Temps — definition.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002785"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T23", "VI_TEMPORELS_MEMORIELS"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0176 — T23 Arbre du Temps — examples_events.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002786"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T23", "VI_TEMPORELS_MEMORIELS"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0177 — T23 Arbre du Temps — links_to_other_trees.json
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002787"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T23", "VI_TEMPORELS_MEMORIELS"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0178 — T23 Arbre du Temps — node_registry.json
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002788"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T23", "VI_TEMPORELS_MEMORIELS"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0179 — T23 Arbre du Temps — README.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002789"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T23", "VI_TEMPORELS_MEMORIELS"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0180 — T23 Arbre du Temps — risks_confusions.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002790"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T23", "VI_TEMPORELS_MEMORIELS"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0181 — T23 Arbre du Temps — tensor_coordinates.json
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002791"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T23", "VI_TEMPORELS_MEMORIELS"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0182 — T23 Arbre du Temps — tests.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002792"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T23", "VI_TEMPORELS_MEMORIELS"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0207 — T25 Arbre de l'Histoire — activation_rules.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002802"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T25", "VI_TEMPORELS_MEMORIELS"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0208 — T25 Arbre de l'Histoire — definition.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002803"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T25", "VI_TEMPORELS_MEMORIELS"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0209 — T25 Arbre de l'Histoire — examples_events.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002804"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T25", "VI_TEMPORELS_MEMORIELS"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0210 — T25 Arbre de l'Histoire — links_to_other_trees.json
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002805"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T25", "VI_TEMPORELS_MEMORIELS"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0211 — T25 Arbre de l'Histoire — node_registry.json
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002806"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T25", "VI_TEMPORELS_MEMORIELS"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0212 — T25 Arbre de l'Histoire — README.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002807"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T25", "VI_TEMPORELS_MEMORIELS"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0213 — T25 Arbre de l'Histoire — risks_confusions.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002808"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T25", "VI_TEMPORELS_MEMORIELS"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0214 — T25 Arbre de l'Histoire — tensor_coordinates.json
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002809"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T25", "VI_TEMPORELS_MEMORIELS"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0215 — T25 Arbre de l'Histoire — tests.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002810"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T25", "VI_TEMPORELS_MEMORIELS"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0224 — T26 Arbre de la Coherence — activation_rules.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002811"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T26", "VII_META_STRUCTURELS"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0225 — T26 Arbre de la Coherence — definition.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002812"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T26", "VII_META_STRUCTURELS"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0226 — T26 Arbre de la Coherence — examples_events.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002813"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T26", "VII_META_STRUCTURELS"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0227 — T26 Arbre de la Coherence — links_to_other_trees.json
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002814"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T26", "VII_META_STRUCTURELS"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0228 — T26 Arbre de la Coherence — node_registry.json
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002815"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T26", "VII_META_STRUCTURELS"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0229 — T26 Arbre de la Coherence — README.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002816"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T26", "VII_META_STRUCTURELS"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0230 — T26 Arbre de la Coherence — risks_confusions.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002817"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T26", "VII_META_STRUCTURELS"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0231 — T26 Arbre de la Coherence — tensor_coordinates.json
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002818"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T26", "VII_META_STRUCTURELS"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0232 — T26 Arbre de la Coherence — tests.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002819"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T26", "VII_META_STRUCTURELS"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0240 — T27 Arbre de la Verite — activation_rules.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002820"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T27", "VII_META_STRUCTURELS"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0241 — T27 Arbre de la Verite — definition.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002821"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T27", "VII_META_STRUCTURELS"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0242 — T27 Arbre de la Verite — examples_events.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002822"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T27", "VII_META_STRUCTURELS"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0243 — T27 Arbre de la Verite — links_to_other_trees.json
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002823"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T27", "VII_META_STRUCTURELS"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0244 — T27 Arbre de la Verite — node_registry.json
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002824"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T27", "VII_META_STRUCTURELS"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0245 — T27 Arbre de la Verite — README.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002825"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T27", "VII_META_STRUCTURELS"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0246 — T27 Arbre de la Verite — risks_confusions.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002826"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T27", "VII_META_STRUCTURELS"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0247 — T27 Arbre de la Verite — tensor_coordinates.json
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002827"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T27", "VII_META_STRUCTURELS"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0248 — T27 Arbre de la Verite — tests.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002828"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T27", "VII_META_STRUCTURELS"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0256 — T28 Arbre de la Valeur — activation_rules.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002829"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T28", "VII_META_STRUCTURELS"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0257 — T28 Arbre de la Valeur — definition.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002830"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T28", "VII_META_STRUCTURELS"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0258 — T28 Arbre de la Valeur — examples_events.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002831"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T28", "VII_META_STRUCTURELS"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0259 — T28 Arbre de la Valeur — links_to_other_trees.json
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002832"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T28", "VII_META_STRUCTURELS"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0260 — T28 Arbre de la Valeur — node_registry.json
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002833"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T28", "VII_META_STRUCTURELS"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0261 — T28 Arbre de la Valeur — README.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002834"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T28", "VII_META_STRUCTURELS"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0262 — T28 Arbre de la Valeur — risks_confusions.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002835"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T28", "VII_META_STRUCTURELS"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0263 — T28 Arbre de la Valeur — tensor_coordinates.json
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002836"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T28", "VII_META_STRUCTURELS"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0264 — T28 Arbre de la Valeur — tests.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002837"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T28", "VII_META_STRUCTURELS"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0272 — T29 Arbre de la Finalite — activation_rules.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002838"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T29", "VII_META_STRUCTURELS"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0273 — T29 Arbre de la Finalite — definition.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002839"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T29", "VII_META_STRUCTURELS"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0274 — T29 Arbre de la Finalite — examples_events.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002840"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T29", "VII_META_STRUCTURELS"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0275 — T29 Arbre de la Finalite — links_to_other_trees.json
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002841"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T29", "VII_META_STRUCTURELS"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0276 — T29 Arbre de la Finalite — node_registry.json
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002842"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T29", "VII_META_STRUCTURELS"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0277 — T29 Arbre de la Finalite — README.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002843"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T29", "VII_META_STRUCTURELS"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0278 — T29 Arbre de la Finalite — risks_confusions.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002844"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T29", "VII_META_STRUCTURELS"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0279 — T29 Arbre de la Finalite — tensor_coordinates.json
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002845"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T29", "VII_META_STRUCTURELS"] WHERE NOT t IN n.tags];

// PATH_B_DRY_0280 — T29 Arbre de la Finalite — tests.md
MATCH (n:BrodyMemoryDoc {id: "GRAPHITI_V2_002846"}) SET n.tags = [t IN n.tags WHERE t IS NOT NULL] + [t IN ["T29", "VII_META_STRUCTURELS"] WHERE NOT t IN n.tags];

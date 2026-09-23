# BRODY_LLM_OBSIDIEN_SOURCE_DOCS_AUDIT
**Date :** 2026-05-20  
**Mode :** READONLY AUDIT — NO_BUILD — NO_COMMIT  
**Autorité :** KX108_ONLY

---

## Sources lues

### 1. BRODY_NEXT_BUILD_ROADMAP_READONLY_20260513_212134
**Chemin :**
`_local_audits/BRODY_NEXT_BUILD_ROADMAP_READONLY_20260513_212134/BRODY_NEXT_BUILD_ROADMAP_READONLY.md`

**Citations clés :**
- "Brody = LLM obsidien. N'exécute pas, n'autorise pas, ne décide pas. KX108_ONLY sur 100% des modules."
- "Context packet chain QUERY→CONSUMER→ENGINE = CHAIN_PASS"
- "Réponse structurée en contexte readonly ✓"
- "Contexte injecté depuis Neo4j BrodyMemoryDoc (chain PASS) ✓"
- "LOW_MATERIAL — coalesce utilise text,content,body,excerpt,summary,preview mais pas text_preview"
- "3267/3267 nodes ont text_preview mais zéro résultat de texte → excerpts vides dans le contexte Brody"

### 2. BRODY_REAL_ARCHITECTURE_MAP_READONLY_20260513_190155
**Chemin :**
`_local_audits/BRODY_REAL_ARCHITECTURE_MAP_READONLY_20260513_190155/BRODY_REAL_ARCHITECTURE_MAP_READONLY_REPORT.md`

**Citations clés :**
- "Brody = le LLM obsidien lui-même. Brody n'est PAS 'un composant qui a un LLM'."
- Flux complet : opérateur → command gate → API/Graphiti → ContextPacket → Brody → réponse structurée → validation → handoff → X108
- COMPOSANT 1 : "Prochaine action : CONTEXT_PACKET_QUERY → CONTEXT_PACKET_CONSUMER → LOCAL_RESPONSE_ENGINE"

### 3. BRODY_SESSION_CHECKPOINT_20260513_FINAL
**Chemin :**
`_local_audits/BRODY_SESSION_CHECKPOINT_20260513_FINAL/BRODY_SESSION_CHECKPOINT_FINAL.md`

**Citations clés :**
- "Brody LLM obsidien — Boucle contrôlée validée — entity_count=0 correct architectural"
- "Neo4j BrodyMemoryDoc — LIVE — 3267 nodes — LOW_MATERIAL (text_preview absent coalesce)"
- Step 3 : Context packet chain — CHAIN_PASS
- Total smokes session : 292/292 PASS

---

## Modules validés (tous présents)

| Module | Chemin | Statut |
|---|---|---|
| brody_context_packet_query_readonly_v1 | `periphery/brody_memory_readonly/context_packet_query_readonly/` | TROUVÉ |
| brody_context_packet_consumer_readonly_v1 | `periphery/brody_memory_readonly/context_packet_consumer_readonly/` | TROUVÉ |
| brody_local_response_engine_readonly_v1 | `periphery/brody_memory_readonly/local_response_engine_readonly/` | TROUVÉ |
| brody_terminal_structural_dialogue_readonly_v1 | `periphery/brody_memory_readonly/terminal_structural_dialogue_readonly/` | TROUVÉ |

---

## Ce qui est déjà branché aujourd'hui

| Composant | Dans la route ? | Commentaire |
|---|---|---|
| `brody_real_response_pipeline` | OUI (`routes/brody.py`) | Appelle terminal_structural_dialogue + local_response_engine quand Neo4j live |
| QUERY→CONSUMER→ENGINE chain | OUI (via pipeline) | Déclenché si NEO4J_PASSWORD set + port 7688 ouvert |
| `structured_response_snapshot` | **OUI (ajouté 2026-05-20)** | `make_structured_response_snapshot()` wired in route |
| `final_answer` utilise chain material | **OUI (ajouté 2026-05-20)** | `run_brody_v1_4_12a_final_answer(..., structured_response_snapshot=...)` |
| `BrodyMemoryDoc.text_preview` dans coalesce | **DÉJÀ FIXÉ** | coalesce inclut `p.text_preview` depuis audit 2026-05-13 |
| OS Trad / IR / Reverse | PARTIEL | Voir BRODY_OS_TRAD_IR_REVERSE_DISCOVERY_REPORT.md |

---

## Ce qui manque encore

| Item | Statut |
|---|---|
| Neo4j live avec NEO4J_PASSWORD | OPÉRATEUR — hors scope code |
| post_human_review mémoire | Pending 51 décisions opérateur |
| graphiti_candidate_prep | Pending post_human_review |
| Runtime binding | NON ACTIVÉ — READY_FOR_RUNTIME_BINDING=false |
| X108 merge | NOT_MERGED — décision KX108 requise |
| OS Trad / IR / Reverse bridgés dans API | NOT_BRIDGEABLE_WITHOUT_ENGINE_CANDIDATE |

---

## LOW_MATERIAL : status

`text_preview` est **déjà dans le coalesce** de `brody_context_packet_query_readonly_v1.py` ligne 52 :
```python
coalesce(p.text, p.content, p.body, p.excerpt, p.summary, p.preview, p.text_preview, "")
```
Patch déjà appliqué lors de la session 2026-05-13. Voir `BRODY_LOW_MATERIAL_TEXT_PREVIEW_PATCH_REPORT.md`.

---

*BRODY_LLM_OBSIDIEN_SOURCE_DOCS_AUDIT_PASS — 2026-05-20 — KX108_ONLY*

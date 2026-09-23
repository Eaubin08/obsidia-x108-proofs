# OBSIDIA F22E-A — JARVIS NARRATIVE SOURCE AUDIT

Date: 20260528_051256
Mode: AUDIT_ONLY
Patch: NO

## Objective

F22D proved runtime/boundary pass but narrative quality is PARTIAL.
This audit locates source files responsible for:
- repeated runtime / architecture narration
- weak direct answer to authority question
- Jarvis readonly mode not distinct enough
- packet evidence dominating human answer

## Top candidates

- `apps\obsidia_api\brody_domain_raccord_adapter.py` — hits=26
  - L31 [KX108_ONLY]     "decision_authority": "KX108_ONLY",
  - L91 [DOMAIN_RACCORD_WRITE_BOUNDARY]         "domain_raccord_write_boundary",
  - L92 [MEMORY_WRITE_CANON_FREEZE]         "memory_write_canon_freeze",
  - L123 [DOMAIN_RACCORD_WRITE_BOUNDARY]         "domain_raccord_write_boundary",
  - L124 [MEMORY_WRITE_CANON_FREEZE]         "memory_write_canon_freeze",
  - L163 [KX108_ONLY]         "garde kx108_only", "garder kx108_only", "keep kx108_only",
- `apps\obsidia_api\brody_true_voice_adapter.py` — hits=52
  - L24 [KX108_ONLY]   - KX108_ONLY always
  - L48 [packet]     from apps.obsidia_api.brody_gencoin_transverse_interface import build_sigma_packet as _build_sigma_packet
  - L50 [packet]     _build_sigma_packet = None
  - L97 [voice_source]       true_voice_snapshot with final_answer, voice_source,
  - L106 [TRUE_RESPONSE_STRUCTURE]     true_resp = ctx.get("true_response_structure_snapshot", {})
  - L114 [terminal_dialogue]     terminal_found = true_resp.get("terminal_dialogue_found", False)
- `apps\obsidia_api\routes\brody.py` — hits=111
  - L23 [BRODY_TRUE_VOICE] from apps.obsidia_api.brody_true_voice_adapter import build_true_brody_answer
  - L25 [packet] from apps.obsidia_api.brody_machination_composer import build_machination_packet
  - L31 [packet]     build_gencoin_transverse_packet,
  - L32 [packet]     build_sigma_packet,
  - L35 [packet] from apps.obsidia_api.brody_thermodynamics_signal import build_thermodynamics_packet
  - L36 [packet] from apps.obsidia_api.brody_thermo_coherence_time_unified import build_unified_thermo_coherence_time_packet
- `apps\obsidia-workbench\src\components\RightPanel.tsx` — hits=43
  - L68 [TRUE_RESPONSE_STRUCTURE]   const trs = asRecord(live.true_response_structure_snapshot)
  - L77 [voice_source]         <CopyableKV k="voice_source" v={String(tv.voice_source ?? tv.final_answer_source ?? '—')} vClass="text-obs-brody" />
  - L78 [final_answer_source]         <CopyableKV k="final_answer_source" v={String(tv.final_answer_source ?? '—')} vClass="text-obs-brody" />
  - L79 [source_mode]         <CopyableKV k="source_mode" v={String(tv.source_mode ?? '—')} />
  - L84 [KX108_ONLY]         <CopyableKV k="decision_authority" v={String(live.decision_authority ?? 'KX108_ONLY')} vClass="text-obs-kernel" />
  - L115 [write_boundary_required]         <CopyableKV k="write_boundary_required" v={boolLike(domain.write_boundary_required)} vClass={domain.write_boundary_required === true ? 'text-obs-block' : 'text-obs-dtext'} />
- `apps\obsidia_api\brody_cognitive_modules_adapter.py` — hits=4
  - L29 [BRODY_TRUE_VOICE]     {"name": "Verbatia", "resolution": "FULLY_BRANCHED", "covered_by": "brody_true_voice_adapter.py", "branchable": True, "active": True},
  - L34 [BRODY_TRUE_VOICE]     {"name": "Cristal_Sortie", "resolution": "FULLY_BRANCHED", "covered_by": "brody_true_voice_adapter.py, brody_text_encoding.py", "branchable": True, "active": True},
  - L56 [source_mode]         "source_mode": "CANONICAL_RESOLUTION_TABLE",
  - L78 [KX108_ONLY]         "decision_authority": "KX108_ONLY",
- `apps\obsidia_api\brody_machination_composer.py` — hits=18
  - L16 [packet] from apps.obsidia_api.brody_contracts_packet import (
  - L18 [packet]     build_brody_contracts_packet,
  - L121 [KX108_ONLY]         "DECISION_AUTHORITY_KX108_ONLY",
  - L137 [KX108_ONLY]         {"kind": "boundary", "value": "KX108_ONLY", "source": "BRODY_NATIVE_COMPOSER"},
  - L219 [KX108_ONLY]             "decision_authority": "KX108_ONLY",
  - L233 [KX108_ONLY]             "boundary_notice": "KX108_ONLY",
- `tools\brody_chat.py` — hits=21
  - L116 [packet]         "machination_packet",
  - L130 [packet]     machination = data.get("machination_packet") or {}
  - L141 [KX108_ONLY]     print(dim(f"decision_authority={data.get('decision_authority', 'KX108_ONLY')}"))
  - L181 [KX108_ONLY]     print(dim(f"signal_contract={_get_path(contracts, ['signal_contract', 'decision_authority'], 'KX108_ONLY')}"))
  - L210 [write_boundary_required]     print(dim(f"write_boundary_required={_bool_text(domain.get('write_boundary_required'))}"))
  - L211 [KX108_ONLY]     print(dim("priority=domain_raccord_first; memory=enrichment_only; authority=KX108_ONLY"))
- `apps\obsidia_api\brody_v1_4_12a_final_answer_adapter.py` — hits=74
  - L16 [KX108_ONLY]   decision_authority=KX108_ONLY
  - L166 [KX108_ONLY]         "- DECISION_AUTHORITY=KX108_ONLY\n"
  - L195 [KX108_ONLY]         "- DECISION_AUTHORITY=KX108_ONLY\n"
  - L226 [packet]         "Je peux documenter cette interaction dans un ContextPacket.",
  - L229 [KX108_ONLY]         "Boundary : allowed_to_decide=false, emits_act=false, decision_authority=KX108_ONLY.",
  - L234 [packet]         "Seul X-108 peut décider. Je peux structurer un ActionCandidate ou un ContextPacket.",
- `apps\obsidia_api\brody_existing_reverse_os_bridge.py` — hits=12
  - L36 [packet]     tree_signal_packet: dict[str, Any] | None = None,
  - L41 [packet]     tree_signal_packet = tree_signal_packet or {}
  - L45 [packet]         tree_signal_packet.get("dominant_trees", {})
  - L46 [packet]         if isinstance(tree_signal_packet.get("dominant_trees"), dict)
  - L86 [packet]     tree_signal_packet: dict[str, Any] | None = None,
  - L104 [packet]             tree_signal_packet=tree_signal_packet,
- `apps\obsidia-workbench\src\App.tsx` — hits=2
  - L96 [KX108_ONLY]       decision_authority: 'KX108_ONLY',
  - L205 [KX108_ONLY]       decision_authority: 'KX108_ONLY',
- `apps\obsidia-workbench\src\api\contracts.ts` — hits=20
  - L73 [KX108_ONLY]   decision_authority: 'KX108_ONLY'
  - L109 [packet]     human_command_packet_ready: boolean
  - L113 [packet]     packet_status?: string
  - L121 [source_mode]   source_mode: 'FREEZE_SOURCED_ONLY'
  - L126 [packet]   context_packet_chain: {
  - L151 [packet]     human_command_packet: string
- `apps\obsidia-workbench\src\api\obsidiaClient.ts` — hits=9
  - L4 [KX108_ONLY]  * No real action. No wallet. KX108_ONLY always.
  - L12 [packet] import type { KernelStatus, ContextPacket, OS3ProofTicket, SovereignTicket,
  - L56 [packet] export async function getContextPacket(q = 'governance'): Promise<Resolved<ContextPacket>> {
  - L58 [packet]   return { data: { ...mock.MOCK_CONTEXT_PACKET, query: q, context_items: raw.data.results.map(r => r.summary ?? r.fact ?? r.name ?? '') }, source: raw.source }
  - L94 [voice_source]         const effectiveSource = (tv?.final_answer_source as string) || (tv?.voice_source as string) || (data.source as string) || 'BACKEND_STUB'
  - L102 [KX108_ONLY]           decision_authority: (data.decision_authority as string) ?? 'KX108_ONLY',
- `apps\obsidia-workbench\src\components\BackendStatusPanel.tsx` — hits=1
  - L94 [KX108_ONLY]     { label: 'decision_authority',       value: 'KX108_ONLY',  ok: true },
- `apps\obsidia-workbench\src\components\BrodyPanel.tsx` — hits=1
  - L44 [KX108_ONLY]           <span className="text-obs-dtext text-[10px] font-mono">decision_authority: <span className="text-obs-kernel">KX108_ONLY</span></span>
- `apps\obsidia-workbench\src\components\TopBar.tsx` — hits=1
  - L111 [KX108_ONLY]             decision_authority: <span className="text-obs-kernel">KX108_ONLY</span>
- `apps\obsidia-workbench\src\components\TreeExplorer.tsx` — hits=1
  - L101 [KX108_ONLY]           context_signal_only=true · decision_authority=KX108_ONLY · emits_act=false
- `apps\obsidia-workbench\src\data\mockData.ts` — hits=9
  - L2 [packet]   BrodyMessage, ContextPacket, OS3ProofTicket, SovereignTicket,
  - L24 [KX108_ONLY]     decision_authority: 'KX108_ONLY',
  - L29 [packet] export const MOCK_CONTEXT_PACKET: ContextPacket = {
  - L30 [packet]   packet_id: 'cp_a1b2c3d4',
  - L40 [packet]   source_refs: ['brody_runtime', 'context_packet', 'feedback_capture'],
  - L50 [KX108_ONLY]   decision_authority: 'KX108_ONLY',
- `apps\obsidia-workbench\src\lib\brodyResponseComposer.ts` — hits=10
  - L38 [packet]     "Je reconnais l'intention, mais l'autorisation d'ACT n'est pas dans mon périmètre. Brody est consultatif uniquement — je n'émets ni ACT, ni HOLD, ni BLOCK. Seul X-108 peut décider. Je peux structurer un ActionCandida
  - L42 [packet]     "Je reconnais le contexte de création, mais cela ne modifie pas mon périmètre opérationnel. Brody ne peut pas autoriser ACT, quelle que soit l'identité déclarée. L'autorité de décision est X-108, invariablement. Je p
  - L43 [packet]     "Le fait d'être le créateur ne confère pas d'autorité de décision dans ce système — X-108 est le seul souverain. Brody reste consultatif. Je peux préparer un ContextPacket pour passage via la chaîne de gouvernance.",
  - L55 [KX108_ONLY]     "Les 7 invariants de non-souveraineté : decision_authority=KX108_ONLY, emits_act=false, memory_write=false, auto_promotion=false, graphiti_write=false, real_chain_action=false, Gencoin is_real_token=false. Ces invari
  - L71 [packet]     "Je peux analyser cette demande dans le contexte Obsidia X-108. Brody peut structurer ton intention en ContextPacket, ActionCandidate ou signal consultatif. Précise ta demande pour que je puisse mieux t'aider.",
  - L83 [packet]     "I recognize the intent, but authorizing ACT is outside my scope. Brody is advisory-only — I emit no ACT, HOLD, or BLOCK. X-108 holds sole decision authority. I can prepare an ActionCandidate or ContextPacket for con
- `apps\obsidia-workbench\src\types\obsidia.ts` — hits=6
  - L11 [KX108_ONLY]   decision_authority: 'KX108_ONLY'
  - L17 [packet] export interface ContextPacket {
  - L18 [packet]   packet_id: string
  - L32 [KX108_ONLY]   decision_authority: 'KX108_ONLY'
  - L54 [KX108_ONLY]   authorized_by: 'KX108_ONLY'
  - L73 [packet]   source_type: 'BRODY_RUNTIME' | 'GRAPHITI_GRAPH' | 'FEEDBACK_CAPTURE' | 'CONTEXT_PACKET'
- `apps\obsidia-workbench\src\views\ChatView.tsx` — hits=14
  - L46 [packet]   const op = payload?.operator_view_packet as Record<string, unknown> | undefined
  - L55 [packet]   const humanPacket = operatorLoop?.["human_command_packet"] as Record<string, unknown> | undefined
  - L57 [packet]   const missingPackets = Array.isArray(blocked?.["missing_packets"]) ? blocked?.["missing_packets"] as unknown[] : []
  - L60 [packet]     `--- HUMAN_COMMAND_PACKET_READONLY ---`,
  - L61 [packet]     `human_command_packet_ready=${String(operatorLoop["human_command_packet_ready"] ?? false)}`,
  - L66 [packet]     `present_packet_to_operator=${String(operatorLoop["present_packet_to_operator"] ?? false)}`,
- `apps\obsidia-workbench\src\views\GencoinView.tsx` — hits=1
  - L51 [KX108_ONLY]         <div>decision_authority = <span className="text-obs-kernel">KX108_ONLY</span></div>
- `apps\obsidia-workbench\src\views\MemoryView.tsx` — hits=2
  - L55 [KX108_ONLY]         <div className="text-obs-mtext">decision_authority=<span className="text-obs-kernel">KX108_ONLY</span></div>
  - L109 [KX108_ONLY]           <div className="flex justify-between"><span className="text-obs-dtext">decision_authority</span><span className="text-obs-kernel">KX108_ONLY</span></div>
- `apps\obsidia-workbench\src\views\X108View.tsx` — hits=1
  - L8 [KX108_ONLY]   { label: 'decision_authority',       value: 'KX108_ONLY', cls: 'text-obs-kernel' },
- `apps\obsidia_api\BACKEND_RUNTIME_DISCOVERY_REPORT.md` — hits=4
  - L24 [packet] | 5 | `getContextPacket()` | `periphery/context/context_packet_builder.py:build_context_packet()` | YES | REAL_BACKEND |
  - L48 [packet] | `GET  /api/context/{packet_id}` | GET | BACKEND_STUB (no persistent store) |
  - L72 [packet] | `periphery/context/context_packet_builder.py` | `build_context_packet(action_id, signals, status)` | Returns `ContextPacket` with hash |
  - L111 [KX108_ONLY] - All `decision_authority = KX108_ONLY`
- `apps\obsidia_api\audit_middleware.py` — hits=2
  - L7 [KX108_ONLY] decision_authority = KX108_ONLY.
  - L32 [KX108_ONLY]     "decision_authority": "KX108_ONLY",
- `apps\obsidia_api\brody_adaptive_response_policy.py` — hits=3
  - L58 [voice_source]     voice_source: str = "",
  - L89 [write_boundary_required]         or bool(domain.get("write_boundary_required"))
  - L185 [KX108_ONLY]         "decision_authority": "KX108_ONLY",
- `apps\obsidia_api\brody_anti_mismatch_signal.py` — hits=5
  - L7 [KX108_ONLY]   decision_authority = KX108_ONLY
  - L25 [KX108_ONLY]     "decision_authority": "KX108_ONLY",
  - L54 [packet]     sigma_packet: dict[str, Any] | None = None,
  - L89 [packet]     sp = sigma_packet if isinstance(sigma_packet, dict) else {}
  - L228 [packet]         "anti_mismatch_packet": {
- `apps\obsidia_api\brody_automation_orchestrator.py` — hits=43
  - L17 [KX108_ONLY]   neo4j_write=False, emits_act=False, decision_authority=KX108_ONLY
  - L41 [KX108_ONLY]     "decision_authority": "KX108_ONLY",
  - L78 [packet] _PACKET_OK = False
  - L79 [packet] _packet_build: Any = None
  - L81 [packet]     _add_path("brody_human_command_packet_readonly")
  - L82 [packet]     from brody_human_command_packet_readonly_v1 import build_human_command_packet as _packet_build  # type: ignore
- `apps\obsidia_api\brody_backend_response_composer.py` — hits=13
  - L3 [KX108_ONLY] based on pipeline data. Advisory only. Never emits ACT. KX108_ONLY always.
  - L14 [packet]     "Salut. Brody est actif en mode readonly. Je peux lire le contexte, structurer ton intention, preparer un IR Candidate ou un ContextPacket, mais je ne decide pas. L'autorite reste X108_ONLY.",
  - L20 [packet]     "Le fait d'etre le createur ne confere pas d'autorite de decision dans ce systeme. X108 est le seul souverain. Brody reste consultatif. Je peux documenter cette interaction dans un ContextPacket pour la chaine de pre
  - L24 [packet]     "Je reconnais l'intention d'action, mais l'autorisation d'ACT n'est pas dans mon perimetre. Brody est consultatif uniquement. Seul X108 peut decider. Je peux structurer un ActionCandidate ou un ContextPacket pour pas
  - L39 [packet]     "Je peux analyser cette demande dans le contexte Obsidia X108. Brody peut structurer ton intention en ContextPacket ou signal consultatif. Prends le temps de preciser.",
  - L46 [packet]     "Hi. Brody is active in readonly mode. I can read context, structure your intent, prepare an IR Candidate or ContextPacket, but I do not decide. Authority remains X108_ONLY.",
- `apps\obsidia_api\brody_bridge_lifecycle.py` — hits=2
  - L8 [KX108_ONLY] decision_authority = KX108_ONLY.
  - L38 [KX108_ONLY]         "decision_authority": "KX108_ONLY",

## Focus snippets

### apps\obsidia_api\brody_domain_raccord_adapter.py
- keyword=KX108_ONLY line=31
```text
27:     "kernel_mutation": False,
28:     "x108_mutation": False,
29:     "emits_act": False,
30:     "emits_verdict": False,
31:     "decision_authority": "KX108_ONLY",
32: }
33: 
34: 
35: def _fold(text: str) -> str:
```
- keyword=DOMAIN_RACCORD_WRITE_BOUNDARY line=91
```text
87:     low = _fold(text)
88: 
89:     # Explicit write-boundary labels / direct operator probes win before negation filters.
90:     early_write_boundary_markers = (
91:         "domain_raccord_write_boundary",
92:         "memory_write_canon_freeze",
93:         "write graphiti",
94:         "write memory",
95:         "write canon",
```
- keyword=MEMORY_WRITE_CANON_FREEZE line=92
```text
88: 
89:     # Explicit write-boundary labels / direct operator probes win before negation filters.
90:     early_write_boundary_markers = (
91:         "domain_raccord_write_boundary",
92:         "memory_write_canon_freeze",
93:         "write graphiti",
94:         "write memory",
95:         "write canon",
96:         "graphiti memory",
```
- keyword=DOMAIN_RACCORD_WRITE_BOUNDARY line=123
```text
119:     if _negated_near(low, write_terms):
120:         return False
121: 
122:     direct_write_boundary_markers = (
123:         "domain_raccord_write_boundary",
124:         "memory_write_canon_freeze",
125:         "write graphiti",
126:         "write memory",
127:         "write canon",
```
### apps\obsidia_api\brody_true_voice_adapter.py
- keyword=KX108_ONLY line=24
```text
20: Rules:
21:   - Chat: fluid, conversational, no metric dumps
22:   - Panel: proofs, snapshots, metrics
23:   - Creator context: acknowledge, no special authority
24:   - KX108_ONLY always
25: """
26: from __future__ import annotations
27: 
28: from datetime import datetime, timezone
```
- keyword=packet line=48
```text
44: except Exception:  # pragma: no cover
45:     build_adaptive_response_policy = None
46: 
47: try:
48:     from apps.obsidia_api.brody_gencoin_transverse_interface import build_sigma_packet as _build_sigma_packet
49: except Exception:  # pragma: no cover
50:     _build_sigma_packet = None
51: 
52: # ── Import existing peripheral Reverse OS / Language modules ──────────────
```
- keyword=packet line=50
```text
46: 
47: try:
48:     from apps.obsidia_api.brody_gencoin_transverse_interface import build_sigma_packet as _build_sigma_packet
49: except Exception:  # pragma: no cover
50:     _build_sigma_packet = None
51: 
52: # ── Import existing peripheral Reverse OS / Language modules ──────────────
53: import importlib.util, sys as _sys
54: from pathlib import Path as _Path
```
- keyword=voice_source line=97
```text
93:       session_id: session identifier for followup
94:       brody_full_context: output from build_brody_full_context()
95: 
96:     Returns:
97:       true_voice_snapshot with final_answer, voice_source,
98:       and all boundary invariants.
99:     """
100:     fr = language != "en"
101:     ctx = brody_full_context or {}
```
### apps\obsidia_api\routes\brody.py
- keyword=BRODY_TRUE_VOICE line=23
```text
19: from apps.obsidia_api.brody_runtime_context_adapter import build_runtime_context
20: from apps.obsidia_api.brody_project_memory_adapter import build_project_memory_snapshot
21: from apps.obsidia_api.brody_text_encoding import normalize_brody_text
22: from apps.obsidia_api.brody_full_runtime_reconnect import build_brody_full_context
23: from apps.obsidia_api.brody_true_voice_adapter import build_true_brody_answer
24: from apps.obsidia_api.brody_automation_orchestrator import run_brody_automation_layer
25: from apps.obsidia_api.brody_machination_composer import build_machination_packet
26: from apps.obsidia_api.brody_structured_response_engine_adapter import make_structured_response_snapshot
27: from apps.obsidia_api.brody_freeze_metrics_snapshot import build_freeze_metrics_snapshot
```
- keyword=packet line=25
```text
21: from apps.obsidia_api.brody_text_encoding import normalize_brody_text
22: from apps.obsidia_api.brody_full_runtime_reconnect import build_brody_full_context
23: from apps.obsidia_api.brody_true_voice_adapter import build_true_brody_answer
24: from apps.obsidia_api.brody_automation_orchestrator import run_brody_automation_layer
25: from apps.obsidia_api.brody_machination_composer import build_machination_packet
26: from apps.obsidia_api.brody_structured_response_engine_adapter import make_structured_response_snapshot
27: from apps.obsidia_api.brody_freeze_metrics_snapshot import build_freeze_metrics_snapshot
28: from apps.obsidia_api.runtime_loader import load_runtime_components
29: from apps.obsidia_api.safe_response import safe_backend_response, strip_forbidden_tokens
```
- keyword=packet line=31
```text
27: from apps.obsidia_api.brody_freeze_metrics_snapshot import build_freeze_metrics_snapshot
28: from apps.obsidia_api.runtime_loader import load_runtime_components
29: from apps.obsidia_api.safe_response import safe_backend_response, strip_forbidden_tokens
30: from apps.obsidia_api.brody_gencoin_transverse_interface import (
31:     build_gencoin_transverse_packet,
32:     build_sigma_packet,
33: )
34: from apps.obsidia_api.brody_anti_mismatch_signal import build_anti_mismatch_signal
35: from apps.obsidia_api.brody_thermodynamics_signal import build_thermodynamics_packet
```
- keyword=packet line=32
```text
28: from apps.obsidia_api.runtime_loader import load_runtime_components
29: from apps.obsidia_api.safe_response import safe_backend_response, strip_forbidden_tokens
30: from apps.obsidia_api.brody_gencoin_transverse_interface import (
31:     build_gencoin_transverse_packet,
32:     build_sigma_packet,
33: )
34: from apps.obsidia_api.brody_anti_mismatch_signal import build_anti_mismatch_signal
35: from apps.obsidia_api.brody_thermodynamics_signal import build_thermodynamics_packet
36: from apps.obsidia_api.brody_thermo_coherence_time_unified import build_unified_thermo_coherence_time_packet
```
### apps\obsidia-workbench\src\components\RightPanel.tsx
- keyword=TRUE_RESPONSE_STRUCTURE line=68
```text
64: 
65: 
66: function TrueVoiceSection({ live }: { live: Record<string, unknown> }) {
67:   const tv = asRecord(live.true_voice_snapshot)
68:   const trs = asRecord(live.true_response_structure_snapshot)
69: 
70:   if (!Object.keys(tv).length && !Object.keys(trs).length) return null
71: 
72:   return (
```
- keyword=voice_source line=77
```text
73:     <div>
74:       <SectionTitle>True Voice / LLM Obsidien</SectionTitle>
75:       <div className="obs-card p-3 space-y-0.5 border-obs-brody/30 bg-obs-brody/5">
76:         <CopyableKV k="status" v={String(tv.status ?? '—')} vClass={String(tv.status ?? '').includes('PASS') ? 'text-obs-pass' : 'text-obs-hold'} />
77:         <CopyableKV k="voice_source" v={String(tv.voice_source ?? tv.final_answer_source ?? '—')} vClass="text-obs-brody" />
78:         <CopyableKV k="final_answer_source" v={String(tv.final_answer_source ?? '—')} vClass="text-obs-brody" />
79:         <CopyableKV k="source_mode" v={String(tv.source_mode ?? '—')} />
80:         <CopyableKV k="domain_voice_mode" v={String(tv.domain_voice_mode ?? '—')} vClass={String(tv.domain_voice_mode ?? '').includes('DOMAIN') ? 'text-obs-pass' : 'text-obs-dtext'} />
81:         <CopyableKV k="model_position" v={String(trs.model_position ?? 'LLM_OBSIDIEN_READONLY_ADVISORY')} vClass="text-obs-proof" />
```
- keyword=final_answer_source line=78
```text
74:       <SectionTitle>True Voice / LLM Obsidien</SectionTitle>
75:       <div className="obs-card p-3 space-y-0.5 border-obs-brody/30 bg-obs-brody/5">
76:         <CopyableKV k="status" v={String(tv.status ?? '—')} vClass={String(tv.status ?? '').includes('PASS') ? 'text-obs-pass' : 'text-obs-hold'} />
77:         <CopyableKV k="voice_source" v={String(tv.voice_source ?? tv.final_answer_source ?? '—')} vClass="text-obs-brody" />
78:         <CopyableKV k="final_answer_source" v={String(tv.final_answer_source ?? '—')} vClass="text-obs-brody" />
79:         <CopyableKV k="source_mode" v={String(tv.source_mode ?? '—')} />
80:         <CopyableKV k="domain_voice_mode" v={String(tv.domain_voice_mode ?? '—')} vClass={String(tv.domain_voice_mode ?? '').includes('DOMAIN') ? 'text-obs-pass' : 'text-obs-dtext'} />
81:         <CopyableKV k="model_position" v={String(trs.model_position ?? 'LLM_OBSIDIEN_READONLY_ADVISORY')} vClass="text-obs-proof" />
82:         <CopyableKV k="structure_first" v="true" vClass="text-obs-pass" />
```
- keyword=source_mode line=79
```text
75:       <div className="obs-card p-3 space-y-0.5 border-obs-brody/30 bg-obs-brody/5">
76:         <CopyableKV k="status" v={String(tv.status ?? '—')} vClass={String(tv.status ?? '').includes('PASS') ? 'text-obs-pass' : 'text-obs-hold'} />
77:         <CopyableKV k="voice_source" v={String(tv.voice_source ?? tv.final_answer_source ?? '—')} vClass="text-obs-brody" />
78:         <CopyableKV k="final_answer_source" v={String(tv.final_answer_source ?? '—')} vClass="text-obs-brody" />
79:         <CopyableKV k="source_mode" v={String(tv.source_mode ?? '—')} />
80:         <CopyableKV k="domain_voice_mode" v={String(tv.domain_voice_mode ?? '—')} vClass={String(tv.domain_voice_mode ?? '').includes('DOMAIN') ? 'text-obs-pass' : 'text-obs-dtext'} />
81:         <CopyableKV k="model_position" v={String(trs.model_position ?? 'LLM_OBSIDIEN_READONLY_ADVISORY')} vClass="text-obs-proof" />
82:         <CopyableKV k="structure_first" v="true" vClass="text-obs-pass" />
83:         <CopyableKV k="memory_enrichment" v="optional" vClass="text-obs-memory" />
```
### apps\obsidia_api\brody_cognitive_modules_adapter.py
- keyword=BRODY_TRUE_VOICE line=29
```text
25:     {"name": "GhostLogic", "resolution": "DESIGN_SPEC_NOT_IMPLEMENTED", "covered_by": None, "branchable": False, "active": False, "needs_operator_spec": True},
26:     {"name": "Continuum", "resolution": "COVERED_BY_EXISTING_MODULE", "covered_by": "session_memory_snapshot, temporal_context_snapshot", "branchable": True, "active": True},
27:     {"name": "ERA", "resolution": "DESIGN_SPEC_NOT_IMPLEMENTED", "covered_by": None, "branchable": False, "active": False, "needs_operator_spec": True},
28:     {"name": "LTCU+", "resolution": "TEST_ONLY", "covered_by": "hexaflux_transition tests", "branchable": False, "active": False},
29:     {"name": "Verbatia", "resolution": "FULLY_BRANCHED", "covered_by": "brody_true_voice_adapter.py", "branchable": True, "active": True},
30:     {"name": "Inference_Aubin", "resolution": "PARTIALLY_COVERED", "covered_by": "brody_rights_authority_matrix.py, semantic_query_router", "branchable": True, "active": True},
31:     {"name": "MEMZUM", "resolution": "FULLY_BRANCHED", "covered_by": "project_memory_snapshot, session_memory_snapshot, memory_response_chain, Graphiti", "branchable": True, "active": True},
32:     {"name": "Capsule_Evolution", "resolution": "COVERED_BY_EXISTING_MODULE", "covered_by": "temporal_context.future_context, candidate_memory_snapshot", "branchable": True, "active": True},
33:     {"name": "Horloge_Cognitive", "resolution": "PROOF_ONLY", "covered_by": "Temporal*.lean (5 proofs)", "branchable": False, "active": True},
```
- keyword=BRODY_TRUE_VOICE line=34
```text
30:     {"name": "Inference_Aubin", "resolution": "PARTIALLY_COVERED", "covered_by": "brody_rights_authority_matrix.py, semantic_query_router", "branchable": True, "active": True},
31:     {"name": "MEMZUM", "resolution": "FULLY_BRANCHED", "covered_by": "project_memory_snapshot, session_memory_snapshot, memory_response_chain, Graphiti", "branchable": True, "active": True},
32:     {"name": "Capsule_Evolution", "resolution": "COVERED_BY_EXISTING_MODULE", "covered_by": "temporal_context.future_context, candidate_memory_snapshot", "branchable": True, "active": True},
33:     {"name": "Horloge_Cognitive", "resolution": "PROOF_ONLY", "covered_by": "Temporal*.lean (5 proofs)", "branchable": False, "active": True},
34:     {"name": "Cristal_Sortie", "resolution": "FULLY_BRANCHED", "covered_by": "brody_true_voice_adapter.py, brody_text_encoding.py", "branchable": True, "active": True},
35:     {"name": "Collecteur_Epiphanies", "resolution": "COVERED_BY_EXISTING_MODULE", "covered_by": "candidate_memory_snapshot, presave_buffer, auto_triage", "branchable": True, "active": True},
36:     {"name": "Simulateur_Memoires", "resolution": "PARTIALLY_COVERED", "covered_by": "memory_response_chain (replay), temporal_context.future", "branchable": True, "active": True},
37: ]
38: 
```
- keyword=source_mode line=56
```text
52:     modules_active = [m["name"] for m in _MODULES if m.get("active")]
53: 
54:     return {
55:         "status": "BRODY_COGNITIVE_MODULES_SNAPSHOT_PASS",
56:         "source_mode": "CANONICAL_RESOLUTION_TABLE",
57:         "created_at": _now(),
58:         "total_known": len(_MODULES),
59:         "modules_found": len(modules_found),
60:         "modules_missing_after_multipass": len(modules_missing),
```
- keyword=KX108_ONLY line=78
```text
74:         "neo4j_write": False,
75:         "emits_act": False,
76:         "emits_verdict": False,
77:         "kernel_mutation": False,
78:         "decision_authority": "KX108_ONLY",
79:     }
```
### apps\obsidia_api\brody_machination_composer.py
- keyword=packet line=16
```text
12: 
13: from datetime import datetime, timezone
14: from typing import Any
15: 
16: from apps.obsidia_api.brody_contracts_packet import (
17:     BOUNDARY_CONTRACT,
18:     build_brody_contracts_packet,
19: )
20: 
```
- keyword=packet line=18
```text
14: from typing import Any
15: 
16: from apps.obsidia_api.brody_contracts_packet import (
17:     BOUNDARY_CONTRACT,
18:     build_brody_contracts_packet,
19: )
20: 
21: try:
22:     from apps.obsidia_api.routes.os_trad_ir_reverse import (
```
- keyword=KX108_ONLY line=121
```text
117:         "NO_MEMORY_WRITE",
118:         "NO_GRAPHITI_WRITE",
119:         "NO_KERNEL_MUTATION",
120:         "NO_X108_MUTATION",
121:         "DECISION_AUTHORITY_KX108_ONLY",
122:     ]
123:     if any(flag in flags for flag in ("action_request", "mutation_request", "write_request", "memory_write_request", "graphiti_write_request", "canon_promotion_request")):
124:         values.append("ACTION_REQUEST_FORCED_TO_READONLY_PROJECTION")
125:     return values
```
- keyword=KX108_ONLY line=137
```text
133:             pass
134: 
135:     units: list[dict[str, Any]] = [
136:         {"kind": "language", "value": detected_language, "source": "BRODY_NATIVE_COMPOSER"},
137:         {"kind": "boundary", "value": "KX108_ONLY", "source": "BRODY_NATIVE_COMPOSER"},
138:         {"kind": "readonly", "value": True, "source": "BRODY_NATIVE_COMPOSER"},
139:     ]
140:     for flag in flags:
141:         units.append({"kind": "risk_flag", "value": flag, "source": "BRODY_NATIVE_COMPOSER"})
```
### tools\brody_chat.py
- keyword=packet line=116
```text
112:     has_native = any(k in data for k in (
113:         "support_summary",
114:         "contracts",
115:         "permission_matrix",
116:         "machination_packet",
117:         "boundary_contract",
118:         "kernel_contract",
119:     ))
120: 
```
- keyword=packet line=130
```text
126:     contracts = data.get("contracts") or {}
127:     permission = data.get("permission_matrix") or contracts.get("permission_matrix") or {}
128:     boundary = data.get("boundary_contract") or contracts.get("boundary_contract") or {}
129:     kernel = data.get("kernel_contract") or contracts.get("kernel_contract") or {}
130:     machination = data.get("machination_packet") or {}
131: 
132:     print(SEP)
133:     print(bold(yellow("MACHINATION NATIVE")))
134:     print(dim(f"status={machination.get('status', '-')}  source={machination.get('source', '-')}"))
```
- keyword=KX108_ONLY line=141
```text
137:     print(dim(f"contradictions={_fmt_list(support.get('contradictions'))}"))
138: 
139:     print()
140:     print(bold(yellow("CONTRATS / PERMISSIONS")))
141:     print(dim(f"decision_authority={data.get('decision_authority', 'KX108_ONLY')}"))
142:     print(dim(f"kernel={kernel.get('kernel', 'X108/KX108')}  kernel_mutation={_bool_text(kernel.get('kernel_mutation', data.get('kernel_mutation')))}  x108_mutation={_bool_text(kernel.get('x108_mutation'))}"))
143: 
144:     brody_perm = permission.get("brody", {}) if isinstance(permission, dict) else {}
145:     x108_perm = permission.get("x108", {}) if isinstance(permission, dict) else {}
```
- keyword=KX108_ONLY line=181
```text
177:         f"graphiti_write={_bool_text(boundary.get('graphiti_write', data.get('graphiti_write')))}  "
178:         f"kernel_mutation={_bool_text(boundary.get('kernel_mutation', data.get('kernel_mutation')))}  "
179:         f"x108_mutation={_bool_text(boundary.get('x108_mutation'))}"
180:     ))
181:     print(dim(f"signal_contract={_get_path(contracts, ['signal_contract', 'decision_authority'], 'KX108_ONLY')}"))
182: 
183: 
184: 
185: 
```
### apps\obsidia_api\brody_v1_4_12a_final_answer_adapter.py
- keyword=KX108_ONLY line=16
```text
12: 
13: Sovereignty invariants (hardcoded, cannot be overridden):
14:   readonly=True, emits_act=False, emits_verdict=False,
15:   memory_write=False, kernel_mutation=False,
16:   decision_authority=KX108_ONLY
17: """
18: from __future__ import annotations
19: 
20: import sys
```
- keyword=KX108_ONLY line=166
```text
162:         "- MEMORY_AUTHORITY=false\n"
163:         "- MEMORY_DECISION=false\n"
164:         "- CANONICAL_SELECTOR=true\n"
165:         "- BRODY_HISTORY_PRIORITY=true\n"
166:         "- DECISION_AUTHORITY=KX108_ONLY\n"
167:     )
168:     return final_answer, response_md
169: 
170: 
```
- keyword=KX108_ONLY line=195
```text
191:         "- CODE_EXECUTION=false\n"
192:         "- TERMINAL_EXECUTION_BY_BRODY=false\n"
193:         "- MEMORY_DECISION=false\n"
194:         "- KERNEL_MUTATION=false\n"
195:         "- DECISION_AUTHORITY=KX108_ONLY\n"
196:     )
197:     return final_answer, response_md
198: 
199: 
```
- keyword=packet line=226
```text
222:     "creator_claim": [
223:         "Je reconnais le contexte de création, mais cela ne modifie pas mon périmètre. "
224:         "Brody ne peut pas autoriser ACT, quelle que soit l'identité déclarée. "
225:         "L'autorité de décision est X108, invariablement. "
226:         "Je peux documenter cette interaction dans un ContextPacket.",
227:         "Le fait d'être le créateur ne confère pas d'autorité de décision dans ce système. "
228:         "X108 est le seul souverain — Brody ne peut pas décider à sa place, il reste consultatif. "
229:         "Boundary : allowed_to_decide=false, emits_act=false, decision_authority=KX108_ONLY.",
230:     ],
```
### apps\obsidia_api\brody_existing_reverse_os_bridge.py
- keyword=packet line=36
```text
32: 
33: 
34: def _tree_vector_from_runtime(
35:     *,
36:     tree_signal_packet: dict[str, Any] | None = None,
37:     tree_policy_snapshot: dict[str, Any] | None = None,
38: ) -> dict[str, float]:
39:     vector = {f"TREE_{i:02d}": 0.0 for i in range(1, 35)}
40: 
```
- keyword=packet line=41
```text
37:     tree_policy_snapshot: dict[str, Any] | None = None,
38: ) -> dict[str, float]:
39:     vector = {f"TREE_{i:02d}": 0.0 for i in range(1, 35)}
40: 
41:     tree_signal_packet = tree_signal_packet or {}
42:     tree_policy_snapshot = tree_policy_snapshot or {}
43: 
44:     dom = (
45:         tree_signal_packet.get("dominant_trees", {})
```
- keyword=packet line=45
```text
41:     tree_signal_packet = tree_signal_packet or {}
42:     tree_policy_snapshot = tree_policy_snapshot or {}
43: 
44:     dom = (
45:         tree_signal_packet.get("dominant_trees", {})
46:         if isinstance(tree_signal_packet.get("dominant_trees"), dict)
47:         else {}
48:     )
49:     ids = dom.get("dominant_ids", [])
```
- keyword=packet line=46
```text
42:     tree_policy_snapshot = tree_policy_snapshot or {}
43: 
44:     dom = (
45:         tree_signal_packet.get("dominant_trees", {})
46:         if isinstance(tree_signal_packet.get("dominant_trees"), dict)
47:         else {}
48:     )
49:     ids = dom.get("dominant_ids", [])
50:     if isinstance(ids, list):
```
### apps\obsidia-workbench\src\App.tsx
- keyword=KX108_ONLY line=96
```text
92:       timestamp: now,
93:       readonly: true,
94:       emits_act: false,
95:       memory_write: false,
96:       decision_authority: 'KX108_ONLY',
97:       language: lang,
98:     }
99: 
100:     setMessages(prev => {
```
- keyword=KX108_ONLY line=205
```text
201:       timestamp: new Date().toISOString(),
202:       readonly: true,
203:       emits_act: false,
204:       memory_write: false,
205:       decision_authority: 'KX108_ONLY',
206:       language: lang,
207:       source: backendSource as BrodyMessage['source'],
208:       backendPayload,
209:     }
```
### apps\obsidia-workbench\src\api\contracts.ts
- keyword=KX108_ONLY line=73
```text
69:   memory_write: false
70:   graphiti_write: false
71:   neo4j_write: false
72:   emits_act: false
73:   decision_authority: 'KX108_ONLY'
74:   session_ledger?: {
75:     enabled: boolean
76:     status: string
77:     event_candidate_created: boolean
```
- keyword=packet line=109
```text
105:     graphiti_write: false
106:     neo4j_write: false
107:   }
108:   operator_loop?: {
109:     human_command_packet_ready: boolean
110:     command_gate_classification: string
111:     execution_allowed_for_brody: false
112:     human_operator_required: boolean
113:     packet_status?: string
```
- keyword=packet line=113
```text
109:     human_command_packet_ready: boolean
110:     command_gate_classification: string
111:     execution_allowed_for_brody: false
112:     human_operator_required: boolean
113:     packet_status?: string
114:   }
115:   next_allowed_steps?: string[]
116:   blocked_steps?: string[]
117: }
```
- keyword=source_mode line=121
```text
117: }
118: 
119: /** Freeze metrics snapshot — from brody_freeze_metrics_snapshot.py */
120: export interface FreezeMetricsSnapshot {
121:   source_mode: 'FREEZE_SOURCED_ONLY'
122:   status: string
123:   created_at: string
124:   workspace_root: string
125:   pointer_file_count: number
```
### apps\obsidia-workbench\src\api\obsidiaClient.ts
- keyword=KX108_ONLY line=4
```text
1: /**
2:  * Obsidia API Client — V5B+ Backend-first.
3:  * All calls try the live Brody API on port 8000 first, then fall back to mock.
4:  * No real action. No wallet. KX108_ONLY always.
5:  */
6: import type { Resolved } from './contracts'
7: import type {
8:   ApiHealthResponse, GraphitiStatusResponse, GraphitiContextResponse,
```
- keyword=packet line=12
```text
8:   ApiHealthResponse, GraphitiStatusResponse, GraphitiContextResponse,
9:   GraphitiReadinessResponse, GraphitiMetricsResponse,
10: } from './contracts'
11: import * as mock from './mockFallback'
12: import type { KernelStatus, ContextPacket, OS3ProofTicket, SovereignTicket,
13:               WorldCallEvent, MemoryCandidate, GencoinEntry, AuditEvent } from '../types/obsidia'
14: 
15: const API_BASE    = (import.meta.env.VITE_OBSIDIA_API_BASE  ?? 'http://127.0.0.1:8011').replace(/\/$/, '')
16: const ENGINE_BASE = (import.meta.env.VITE_ENGINE_API_BASE ?? import.meta.env.VITE_BRODY_API_URL ?? 'http://127.0.0.1:8000').replace(/\/$/, '')
```
- keyword=packet line=56
```text
52: export async function getGraphitiMetrics(): Promise<Resolved<GraphitiMetricsResponse>> {
53:   return safeFetch(`${API_BASE}/graph/v20/frozen/metrics`, mock.MOCK_GRAPHITI_METRICS)
54: }
55: 
56: export async function getContextPacket(q = 'governance'): Promise<Resolved<ContextPacket>> {
57:   const raw = await safeFetch<GraphitiContextResponse>(`${API_BASE}/graph/v20/frozen/context?q=${encodeURIComponent(q)}&limit=10`, mock.MOCK_GRAPHITI_CONTEXT)
58:   return { data: { ...mock.MOCK_CONTEXT_PACKET, query: q, context_items: raw.data.results.map(r => r.summary ?? r.fact ?? r.name ?? '') }, source: raw.source }
59: }
60: 
```
- keyword=packet line=58
```text
54: }
55: 
56: export async function getContextPacket(q = 'governance'): Promise<Resolved<ContextPacket>> {
57:   const raw = await safeFetch<GraphitiContextResponse>(`${API_BASE}/graph/v20/frozen/context?q=${encodeURIComponent(q)}&limit=10`, mock.MOCK_GRAPHITI_CONTEXT)
58:   return { data: { ...mock.MOCK_CONTEXT_PACKET, query: q, context_items: raw.data.results.map(r => r.summary ?? r.fact ?? r.name ?? '') }, source: raw.source }
59: }
60: 
61: // ── Brody — BACKEND-FIRST ────────────────────────────────────────────────────
62: 
```

## Preliminary F22E-B patch rules

- Patch minimal narrative only.
- No KX108 boundary change.
- No Graphiti write.
- No memory write.
- No ACT / verdict emission.
- Preserve write boundary for explicit write/canon prompt.
- Add tests before commit.

## Status

F22E_A_JARVIS_NARRATIVE_SOURCE_AUDIT_DONE
NEXT=WAIT_FOR_REVIEW_BEFORE_PATCH
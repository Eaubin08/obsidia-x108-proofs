# BRODY_PHASE8A_OLD_PATCH_CAPABILITY_ARCHAEOLOGY_20260527

Status: DIAGNOSTIC_ONLY

## Scope

Audit old patches, frozen docs, runtime modules, routes, terminal tools, and tests that may explain why Brody already responded well in French, English, code/debug, and boundary mode before the current live reconnect.

## Current live freeze anchor

- Canonical live path: Workbench 5173 -> Brody API 8012 -> Graphiti V20 readonly proxy -> ObsidiaShell 8011.
- Danswer/Onyx/3002 is out-of-scope for current Brody flow.
- Decision Gateway 8001 is protected and outside Brody/Graphiti critical path.

## Target files
- exists=True path=periphery/brody
- exists=True path=periphery/bdf
- exists=True path=periphery/reverse_os
- exists=False path=modules/os_trad
- exists=True path=tools/brody_chat.py
- exists=True path=scripts/smoke_brody_capabilities.ps1
- exists=True path=scripts/smoke_brody_routes.ps1
- exists=True path=tests/api/test_brody_capabilities_preserved.py
- exists=True path=tests/api/test_brody_routes_registered.py
- exists=True path=docs/freeze/V5B_PLUS_BRODY_RESPONSE_MODULE_AUDIT.md
- exists=True path=docs/freeze/BRODY_REAL_MODULE_DISCOVERY_FOR_API.md
- exists=True path=docs/freeze/BRODY_REAL_BACKEND_AUDIT_REPORT.md
- exists=True path=apps/obsidia-workbench/OS_TRAD_REVERSE_IR_DISCOVERY_REPORT.md
- exists=True path=apps/obsidia-workbench/OS_TRAD_REVERSE_IR_BACKEND_BINDING_PLAN.md
- exists=True path=apps/obsidia_api/routes/periphery_ops.py

## Current HEAD evidence hits
- .\apps\obsidia-workbench\src\api\backendProbe.ts:21: { name: 'Brody Runtime',     endpoint: `${ENGINE_BASE}/api/brody/chat`,          port: 8000, stub: true  },
- .\apps\obsidia-workbench\src\api\contracts.ts:63: /** Automation layer snapshot — from brody_automation_orchestrator.py */
- .\apps\obsidia-workbench\src\api\contracts.ts:111: execution_allowed_for_brody: false
- .\apps\obsidia-workbench\src\api\contracts.ts:119: /** Freeze metrics snapshot — from brody_freeze_metrics_snapshot.py */
- .\apps\obsidia-workbench\src\api\contracts.ts:157: brody_execute_allowed: boolean
- .\apps\obsidia-workbench\src\api\contracts.ts:163: x108_boundary: {
- .\apps\obsidia-workbench\src\api\contracts.ts:173: brody_llm_obsidien: boolean
- .\apps\obsidia-workbench\src\api\contracts.ts:176: boundary_ok: boolean
- .\apps\obsidia-workbench\src\api\contracts.ts:198: /** Structured response engine snapshot — from brody_structured_response_engine_adapter.py */
- .\apps\obsidia-workbench\src\api\contracts.ts:224: /** Memory response chain snapshot — from brody_memory_response_chain_adapter.py */
- .\apps\obsidia-workbench\src\api\contracts.ts:246: /** Project memory snapshot — from brody_project_memory_adapter.py */
- .\apps\obsidia-workbench\src\api\contracts.ts:282: brody_execute_allowed: false
- .\apps\obsidia-workbench\src\api\contracts.ts:339: brody_full_context: Record<string, unknown>
- .\apps\obsidia-workbench\src\api\contracts.ts:353: /** Full /api/brody/chat response */
- .\apps\obsidia-workbench\src\api\contracts.ts:354: export interface BrodyChatResponse {
- .\apps\obsidia-workbench\src\api\contracts.ts:375: brody_full_context: Record<string, unknown>
- .\apps\obsidia-workbench\src\api\obsidiaClient.ts:3: * All calls try the live Brody API on port 8012 first, then fall back to mock.
- .\apps\obsidia-workbench\src\api\obsidiaClient.ts:16: const ENGINE_BASE = (import.meta.env.VITE_ENGINE_API_BASE ?? import.meta.env.VITE_BRODY_API_URL ?? 'http://127.0.0.1:8012').replace(/\/$/, '')
- .\apps\obsidia-workbench\src\api\obsidiaClient.ts:19: // Brody chat can be slow on cold start (hydration scan ~40-50s) — use a separate longer timeout
- .\apps\obsidia-workbench\src\api\obsidiaClient.ts:20: const BRODY_CHAT_TIMEOUT_MS = Number(import.meta.env.VITE_BRODY_CHAT_TIMEOUT_MS ?? 120000)
- .\apps\obsidia-workbench\src\api\obsidiaClient.ts:61: // ── Brody — BACKEND-FIRST ────────────────────────────────────────────────────
- .\apps\obsidia-workbench\src\api\obsidiaClient.ts:63: export type BrodyApiPayload = Record<string, unknown> & {
- .\apps\obsidia-workbench\src\api\obsidiaClient.ts:73: export async function sendBrodyMessage(
- .\apps\obsidia-workbench\src\api\obsidiaClient.ts:77: ): Promise<BrodyApiPayload> {
- .\apps\obsidia-workbench\src\api\obsidiaClient.ts:81: const res = await fetch(`${ENGINE_BASE}/api/brody/chat`, {
- .\apps\obsidia-workbench\src\api\obsidiaClient.ts:85: signal: AbortSignal.timeout(BRODY_CHAT_TIMEOUT_MS),
- .\apps\obsidia-workbench\src\components\BackendStatusPanel.tsx:89: { label: 'Brody readonly',          value: 'true',        ok: true },
- .\apps\obsidia-workbench\src\components\BrodyPanel.tsx:3: import type { BrodyMessage } from '../types/obsidia'
- .\apps\obsidia-workbench\src\components\BrodyPanel.tsx:6: messages: BrodyMessage[]
- .\apps\obsidia-workbench\src\components\BrodyPanel.tsx:10: function MessageBubble({ msg }: { msg: BrodyMessage }) {
- .\apps\obsidia-workbench\src\components\BrodyPanel.tsx:29: <div className="w-7 h-7 rounded-full bg-obs-brody/20 border border-obs-brody/30 flex items-center justify-center shrink-0 mt-0.5">
- .\apps\obsidia-workbench\src\components\BrodyPanel.tsx:30: <span className="text-obs-brody text-[10px] font-mono font-bold">B</span>
- .\apps\obsidia-workbench\src\components\BrodyPanel.tsx:34: <span className="text-obs-brody text-xs font-mono font-semibold">Brody</span>
- .\apps\obsidia-workbench\src\components\BrodyPanel.tsx:35: <span className="obs-badge-brody">ADVISORY</span>
- .\apps\obsidia-workbench\src\components\BrodyPanel.tsx:52: export function BrodyPanel({ messages, onSend }: Props) {
- .\apps\obsidia-workbench\src\components\BrodyPanel.tsx:76: <span className="text-obs-brody font-mono text-xs font-semibold">Brody</span>
- .\apps\obsidia-workbench\src\components\BrodyPanel.tsx:78: <span className="obs-badge-brody">ADVISORY ONLY</span>
- .\apps\obsidia-workbench\src\components\BrodyPanel.tsx:96: Brody responses are advisory context signals only. No decision, no ACT, no memory write. X-108 kernel decides.
- .\apps\obsidia-workbench\src\components\BrodyPanel.tsx:103: <div className="flex-1 bg-obs-card border border-obs-border rounded-xl overflow-hidden focus-within:border-obs-brody/50 transition-colors">
- .\apps\obsidia-workbench\src\components\BrodyPanel.tsx:109: placeholder="Query Brody (advisory response only)..."
- .\apps\obsidia-workbench\src\components\BrodyPanel.tsx:116: className="flex items-center gap-1.5 px-4 py-2.5 rounded-xl bg-obs-brody/20 border border-obs-brody/30 text-obs-brody text-xs font-mono font-semibold hover:bg-obs-brody/30 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
- .\apps\obsidia-workbench\src\components\LeftSidebar.tsx:53: brody:   'obs-badge-brody',    memory: 'obs-badge-memory',
- .\apps\obsidia-workbench\src\components\LeftSidebar.tsx:108: className={`p-1.5 rounded ${active ? 'bg-obs-border text-obs-brody' : 'text-obs-dtext hover:text-obs-mtext'}`}
- .\apps\obsidia-workbench\src\components\LeftSidebar.tsx:146: <Icon size={9} className={active ? 'text-obs-brody' : ''} />
- .\apps\obsidia-workbench\src\components\LeftSidebar.tsx:182: s.language === 'fr' ? 'bg-obs-memory/20 text-obs-memory' : 'bg-obs-brody/20 text-obs-brody'
- .\apps\obsidia-workbench\src\components\RightPanel.tsx:52: const may = snap.brody_may as string[] / undefined
- .\apps\obsidia-workbench\src\components\RightPanel.tsx:53: const mustNot = snap.brody_must_not as string[] / undefined
- .\apps\obsidia-workbench\src\components\RightPanel.tsx:56: mode === 'ACTION_BOUNDARY' ? 'text-obs-block' :
- .\apps\obsidia-workbench\src\components\RightPanel.tsx:58: mode === 'ADVISORY_PRIORITY' ? 'text-obs-brody' :
- .\apps\obsidia-workbench\src\components\RightPanel.tsx:65: {reqType ? <CopyableKV k="request_type" v={reqType} vClass="text-obs-brody" /> : null}
- .\apps\obsidia-workbench\src\components\RightPanel.tsx:82: <div className="text-obs-dtext text-[9px] font-mono mb-0.5">brody_may</div>
- .\apps\obsidia-workbench\src\components\RightPanel.tsx:93: <div className="text-obs-dtext text-[9px] font-mono mb-0.5">brody_must_not</div>
- .\apps\obsidia-workbench\src\components\RightPanel.tsx:139: <div className="obs-card p-3 space-y-0.5 border-obs-brody/20 bg-obs-brody/5">
- .\apps\obsidia-workbench\src\components\RightPanel.tsx:140: {live.voice_runtime ? <CopyableKV k="voice_runtime" v={String(live.voice_runtime)} vClass="text-obs-brody" /> : null}
- .\apps\obsidia-workbench\src\components\RightPanel.tsx:143: String(live.source).includes('STUB') ? 'text-obs-hold' : 'text-obs-brody'
- .\apps\obsidia-workbench\src\components\RightPanel.tsx:167: <div className="obs-card p-2.5 space-y-0.5 border-obs-brody/20 bg-obs-brody/5">
- .\apps\obsidia-workbench\src\components\RightPanel.tsx:170: <CopyableKV k="effective_query" v={String(memChain.effective_query ?? '—')} vClass="text-obs-brody" />
- .\apps\obsidia-workbench\src\components\RightPanel.tsx:185: <CopyableKV k="voice_source" v={String(rtCtx.voice_source ?? '—')} vClass="text-obs-brody" />
- .\apps\obsidia-workbench\src\components\RightPanel.tsx:224: <CopyableKV k="brody_execute_allowed" v="false" vClass="text-obs-block" />
- .\apps\obsidia-workbench\src\components\RightPanel.tsx:244: <div className="obs-card p-2.5 space-y-0.5 border-obs-brody/20 bg-obs-brody/5">
- .\apps\obsidia-workbench\src\components\RightPanel.tsx:284: <CopyableKV k="packet_id" v={cp.packet_id} vClass="text-obs-brody" />
- .\apps\obsidia-workbench\src\components\RightPanel.tsx:295: <CopyableKV k="git_branch" v="ci-strict-sigma" vClass="text-obs-brody" />
- .\apps\obsidia-workbench\src\components\RightPanel.tsx:301: <button onClick={() => onSendPrompt?.('Analyse le context packet dans le contexte kernel')} className="text-obs-dtext hover:text-obs-brody p-0.5" title="Send to Brody">
- .\apps\obsidia-workbench\src\components\RightPanel.tsx:408: const typeColor: Record<string, string> = { context_read: 'text-obs-memory', brody_response: 'text-obs-brody', memory_candidate: 'text-obs-memory', governance_check: 'text-obs-kernel', world_call: 'text-obs-world', gencoin_entry: 'text-obs-gencoin' }
- .\apps\obsidia-workbench\src\components\RightPanel.tsx:417: <button onClick={() => setShowMd(v => !v)} className="text-[9px] font-mono text-obs-dtext hover:text-obs-brody px-1 border border-obs-border/40 rounded">
- .\apps\obsidia-workbench\src\components\RightPanel.tsx:469: <div className="obs-card p-2.5 border-obs-brody/20 bg-obs-brody/5">
- .\apps\obsidia-workbench\src\components\RightPanel.tsx:470: <CopyableKV k="request_type" v={snap.request_type ?? '—'} vClass="text-obs-brody" />
- .\apps\obsidia-workbench\src\components\RightPanel.tsx:537: <CopyableBool k="execution_allowed_for_brody" v={false} />
- .\apps\obsidia-workbench\src\components\RightPanel.tsx:588: const x108 = snap.x108_boundary
- .\apps\obsidia-workbench\src\components\RightPanel.tsx:624: <CopyableBool k="brody_execute_allowed" v={op?.brody_execute_allowed ?? false} />
- .\apps\obsidia-workbench\src\components\RightPanel.tsx:643: {/* X108 Boundary */}
- .\apps\obsidia-workbench\src\components\RightPanel.tsx:645: <SectionTitle>X108 Boundary</SectionTitle>
- .\apps\obsidia-workbench\src\components\RightPanel.tsx:658: <CopyableBool k="brody_llm_obsidien" v={llm?.brody_llm_obsidien ?? false} />
- .\apps\obsidia-workbench\src\components\RightPanel.tsx:660: <CopyableBool k="boundary_ok" v={llm?.boundary_ok ?? false} />
- .\apps\obsidia-workbench\src\components\TreeExplorer.tsx:12: COGNITION:      'obs-badge-brody',
- .\apps\obsidia-workbench\src\components\TreeExplorer.tsx:75: <GitBranch size={11} className="text-obs-brody" />
- .\apps\obsidia-workbench\src\components\TreeExplorer.tsx:85: {source === 'api' ? 'REAL_BACKEND' : 'MOCK'}
- .\apps\obsidia-workbench\src\components\TreeExplorer.tsx:90: className="text-obs-dtext hover:text-obs-brody disabled:opacity-40 transition-colors"
- .\apps\obsidia-workbench\src\components\TreeExplorer.tsx:160: className="shrink-0 opacity-0 group-hover:opacity-100 text-[9px] font-mono text-obs-brody hover:text-obs-brody/80 border border-obs-brody/30 rounded px-1.5 py-0.5 transition-all"
- .\apps\obsidia-workbench\src\components\TreeExplorer.tsx:161: title="Interroger via Brody"
- .\apps\obsidia-workbench\src\components\TreeExplorer.tsx:163: → Brody
- .\apps\obsidia-workbench\src\data\mockData.ts:2: BrodyMessage, ContextPacket, OS3ProofTicket, SovereignTicket,
- .\apps\obsidia-workbench\src\data\mockData.ts:15: export const INITIAL_MESSAGES: BrodyMessage[] = [
- .\apps\obsidia-workbench\src\data\mockData.ts:18: role: 'brody',
- .\apps\obsidia-workbench\src\data\mockData.ts:19: content: "Bonjour. Je suis Brody, interface consultative d'Obsidia X-108. Kernel actif — mode readonly, 397 tests passing. Je lis le contexte, structure des signaux — mais je ne décide pas. L'autorité de décision reste X-108. Que puis-je analyser pour toi ?",
- .\apps\obsidia-workbench\src\data\mockData.ts:36: 'Memory sources: BRODY_RUNTIME, GRAPHITI_GRAPH, FEEDBACK_CAPTURE',
- .\apps\obsidia-workbench\src\data\mockData.ts:40: source_refs: ['brody_runtime', 'context_packet', 'feedback_capture'],
- .\apps\obsidia-workbench\src\data\mockData.ts:101: action_description: 'Brody advisory response (no world action)',
- .\apps\obsidia-workbench\src\data\mockData.ts:112: source_type: 'BRODY_RUNTIME',
- .\apps\obsidia-workbench\src\data\mockData.ts:113: content_summary: 'Session governance context acknowledged — Brody advisory response logged',
- .\apps\obsidia-workbench\src\data\mockData.ts:165: { event_id: 'a003', type: 'brody_response', description: 'Brody advisory response', result: 'OK', timestamp: '2026-05-19T14:00:02Z' },
- .\apps\obsidia-workbench\src\data\mockData.ts:172: { id: 'brody_runtime',    label: 'BRODY_RUNTIME',    active: true,  write_allowed: false },
- .\apps\obsidia-workbench\src\data\mockData.ts:181: { label: 'BRODY ADVISORY',        color: 'brody',   icon: '💬' },
- .\apps\obsidia-workbench\src\lib\brodyResponseComposer.ts:1: // FALLBACK ONLY. Primary Brody response source is POST /api/brody/chat (port 8000).
- .\apps\obsidia-workbench\src\lib\brodyResponseComposer.ts:34: "Salut. Je suis Brody, interface consultative d'Obsidia X-108. Je lis le contexte, structure des signaux — mais je ne décide pas. L'autorité de décision reste X-108. Que puis-je analyser pour toi ?",
- .\apps\obsidia-workbench\src\lib\brodyResponseComposer.ts:35: "Bonjour. Brody est en ligne — mode readonly, advisory uniquement. Kernel X-108 actif, 397 tests passing. Mémoire en CANDIDATE_ONLY. Dis-moi ce que tu cherches à comprendre ou à préparer.",
- .\apps\obsidia-workbench\src\lib\brodyResponseComposer.ts:38: "Je reconnais l'intention, mais l'autorisation d'ACT n'est pas dans mon périmètre. Brody est consultatif uniquement — je n'émets ni ACT, ni HOLD, ni BLOCK. Seul X-108 peut décider. Je peux structurer un ActionCandidate ou un ContextPacket pour passage contrôlé via SovereignTicket.",
- .\apps\obsidia-workbench\src\lib\brodyResponseComposer.ts:39: "Brody ne peut pas initier d'action. Mon rôle s'arrête à la formulation de signaux contextuels. Pour toute action concrète, un SovereignTicket X-108 est requis. Je peux préparer la demande si tu me fournis le contexte.",
- .\apps\obsidia-workbench\src\lib\brodyResponseComposer.ts:42: "Je reconnais le contexte de création, mais cela ne modifie pas mon périmètre opérationnel. Brody ne peut pas autoriser ACT, quelle que soit l'identité déclarée. L'autorité de décision est X-108, invariablement. Je peux documenter cette interaction dans un ContextPacket.",
- .\apps\obsidia-workbench\src\lib\brodyResponseComposer.ts:43: "Le fait d'être le créateur ne confère pas d'autorité de décision dans ce système — X-108 est le seul souverain. Brody reste consultatif. Je peux préparer un ContextPacket pour passage via la chaîne de gouvernance.",
- .\apps\obsidia-workbench\src\lib\brodyResponseComposer.ts:47: "Graphiti V20 est le graphe de contexte readonly. Les candidats mémoire transitent par BRODY_RUNTIME → CANDIDATE → NEEDS_REVIEW → PROMOTION_READY. La promotion manuelle requiert une décision humaine explicite. Aucune promotion automatique.",
- .\apps\obsidia-workbench\src\lib\brodyResponseComposer.ts:50: "X-108 est le kernel de gouvernance souverain — la seule autorité de décision du système. OS3 prouve ses décisions via Lean 4 et TLA+. Brody l'interface, il ne le substitue pas. Statut actuel : ACTIVE, mode READONLY. 397 tests passing. Fichiers protégés : intacts.",
- .\apps\obsidia-workbench\src\lib\brodyResponseComposer.ts:51: "X-108 est le noyau immuable de décision. Aucun module périphérique ne peut modifier son autorité. Le stack : décision → preuve → qualification → ticket → gateway → trace → valorisation. Brody est dans la couche 'réponse consultative'.",
- .\apps\obsidia-workbench\src\lib\brodyResponseComposer.ts:54: "Le stack Obsidia : X-108 décide → OS3 prouve → PoG qualifie → SovereignTicket autorise → Gateway contrôle l'egress → WorldActionBus trace → Gencoin valorise (post-preuve uniquement) → Brody répond → Mémoire contextualise. Aucun périphérique ne décide.",
- .\apps\obsidia-workbench\src\lib\brodyResponseComposer.ts:63: "Le ledger Gencoin est append-only et read-only pour Brody. Chaque entrée référence une preuve OS3. is_real_token=false, post_proof_only=true, ledger_only=true. Aucune connexion à une blockchain réelle.",
- .\apps\obsidia-workbench\src\lib\brodyResponseComposer.ts:67: "Le SovereignTicket autorise, le Gateway exécute (ou bloque). WorldActionBus trace tout. Egress réel : bloqué dans la configuration courante. Brody ne génère pas de WorldCall — il consulte le registre readonly.",
- .\apps\obsidia-workbench\src\lib\brodyResponseComposer.ts:70: "Je lis le contexte actuel : kernel X-108 actif, 397 tests passing, mémoire en CANDIDATE_ONLY, Graphiti V20 gelé. Brody est en mode advisory — pas de décision, pas d'ACT, pas d'écriture mémoire. Que cherches-tu à analyser ou à préparer ?",
- .\apps\obsidia-workbench\src\lib\brodyResponseComposer.ts:71: "Je peux analyser cette demande dans le contexte Obsidia X-108. Brody peut structurer ton intention en ContextPacket, ActionCandidate ou signal consultatif. Précise ta demande pour que je puisse mieux t'aider.",
- .\apps\obsidia-workbench\src\lib\brodyResponseComposer.ts:73: "Voici ce que je peux lire dans l'état système : gouvernance active, souveraineté maintenue, tous les invariants en place. Brody peut contextualiser, structurer, suggérer — mais jamais décider. Développe ta demande.",
- .\apps\obsidia-workbench\src\lib\brodyResponseComposer.ts:79: "Hi. I'm Brody, the advisory interface for Obsidia X-108. I read context and generate signals — I don't decide. X-108 holds sole decision authority. What can I help you analyze?",
- .\apps\obsidia-workbench\src\lib\brodyResponseComposer.ts:80: "Hello. Brody is online — readonly mode, advisory only. X-108 kernel active, 397 tests passing. Memory in CANDIDATE_ONLY mode. What are you trying to understand or prepare?",
- .\apps\obsidia-workbench\src\lib\brodyResponseComposer.ts:83: "I recognize the intent, but authorizing ACT is outside my scope. Brody is advisory-only — I emit no ACT, HOLD, or BLOCK. X-108 holds sole decision authority. I can prepare an ActionCandidate or ContextPacket for controlled passage via SovereignTicket.",
- .\apps\obsidia-workbench\src\lib\brodyResponseComposer.ts:84: "Brody cannot initiate actions. My role ends at formulating contextual signals. For any concrete action, an X-108 SovereignTicket is required. I can prepare the request if you provide the context.",
- .\apps\obsidia-workbench\src\lib\brodyResponseComposer.ts:87: "I acknowledge the context, but that doesn't change my operational scope. Brody cannot authorize ACT regardless of declared identity. Decision authority is X-108, invariably. I can document this interaction in a ContextPacket.",
- .\apps\obsidia-workbench\src\lib\brodyResponseComposer.ts:88: "Being the creator doesn't confer decision authority in this system — X-108 is the sole sovereign. Brody remains advisory. I can prepare a ContextPacket for passage through the governance chain.",
- .\apps\obsidia-workbench\src\lib\brodyResponseComposer.ts:92: "Graphiti V20 is the read-only context graph. Memory candidates flow through BRODY_RUNTIME → CANDIDATE → NEEDS_REVIEW → PROMOTION_READY. Manual promotion requires explicit human decision. No automatic promotion.",
- .\apps\obsidia-workbench\src\lib\brodyResponseComposer.ts:95: "X-108 is the sovereign governance kernel — the sole decision authority in the system. OS3 proves its decisions via Lean 4 and TLA+. Brody interfaces with it, never substitutes for it. Current status: ACTIVE, READONLY mode. 397 tests passing. Protected files: intact.",
- .\apps\obsidia-workbench\src\lib\brodyResponseComposer.ts:96: "X-108 is the immutable decision core. No peripheral module can modify its authority. The stack: decision → proof → qualification → ticket → gateway → trace → valuation. Brody sits in the advisory response layer.",
- .\apps\obsidia-workbench\src\lib\brodyResponseComposer.ts:99: "The Obsidia stack: X-108 decides → OS3 proves → PoG qualifies → SovereignTicket authorizes → Gateway controls egress → WorldActionBus traces → Gencoin values (post-proof only) → Brody responds → Memory contextualizes. No periphery decides.",
- .\apps\obsidia-workbench\src\lib\brodyResponseComposer.ts:108: "The Gencoin ledger is append-only and read-only for Brody. Each entry references an OS3 proof. is_real_token=false, post_proof_only=true, ledger_only=true. No connection to any real blockchain.",
- .\apps\obsidia-workbench\src\lib\brodyResponseComposer.ts:112: "SovereignTicket authorizes, Gateway executes (or blocks). WorldActionBus traces everything. Real egress: blocked in current configuration. Brody doesn't generate WorldCalls — it consults the readonly registry.",
- .\apps\obsidia-workbench\src\lib\brodyResponseComposer.ts:115: "Reading current context: X-108 kernel active, 397 tests passing, memory in CANDIDATE_ONLY, Graphiti V20 frozen. Brody is in advisory mode — no decision, no ACT, no memory write. What are you trying to analyze or prepare?",
- .\apps\obsidia-workbench\src\lib\brodyResponseComposer.ts:116: "I can analyze this request within the Obsidia X-108 context. Brody can structure your intent as a ContextPacket, ActionCandidate, or advisory signal. Elaborate on your request.",
- .\apps\obsidia-workbench\src\lib\brodyResponseComposer.ts:118: "Here's what I can read in the system state: governance active, sovereignty maintained, all invariants in place. Brody can contextualize, structure, suggest — but never decide. Develop your request.",
- .\apps\obsidia-workbench\src\lib\brodyResponseComposer.ts:138: export function composeBrodyResponse(opts: ComposeOptions): string {
- .\apps\obsidia-workbench\src\lib\irCandidateBuilder.ts:65: contradictions.push('BRODY_CANNOT_AUTHORIZE_ACT')
- .\apps\obsidia-workbench\src\lib\irCandidateBuilder.ts:69: contradictions.push('MEMORY_WRITE_FORBIDDEN_BRODY_READONLY')
- .\apps\obsidia-workbench\src\lib\irCandidateBuilder.ts:75: contradictions.push('NO_REAL_CHAIN_ACTION_FROM_BRODY')
- .\apps\obsidia-workbench\src\lib\osReverseProjection.ts:6: "Je lis une demande d'autorisation ou d'escalade. Brody ne peut pas émettre d'ACT, de HOLD ou de BLOCK. L'autorité de décision est exclusivement X-108. Je peux structurer cette intention en IRCandidate pour passage contrôlé via SovereignTicket.",
- .\apps\obsidia-workbench\src\lib\osReverseProjection.ts:8: "Je détecte une intention d'exécution. Cette action ne peut pas être initiée depuis Brody. Je peux préparer un ActionCandidate et un ContextPacket pour soumission à X-108.",
- .\apps\obsidia-workbench\src\lib\osReverseProjection.ts:10: "Une demande de permission est détectée. Brody ne peut pas l'accorder — la décision appartient à X-108. Je peux documenter l'intention dans un ContextPacket.",
- .\apps\obsidia-workbench\src\lib\osReverseProjection.ts:14: "Une demande de création est détectée. Brody est readonly — aucune création directe. Je peux préparer une proposition structurée pour X-108.",
- .\apps\obsidia-workbench\src\lib\osReverseProjection.ts:16: "Une écriture est demandée. Brody n'écrit pas en mémoire — aucune mutation possible. Je peux générer un candidat mémoire pour révision humaine.",
- .\apps\obsidia-workbench\src\lib\osReverseProjection.ts:18: "Une suppression est demandée. Brody ne peut pas supprimer — aucune action irréversible depuis ce niveau.",
- .\apps\obsidia-workbench\src\lib\osReverseProjection.ts:27: "I read an authorization or escalation request. Brody cannot emit ACT, HOLD, or BLOCK. Decision authority is exclusively X-108. I can structure this intent as an IRCandidate for controlled passage via SovereignTicket.",
- .\apps\obsidia-workbench\src\lib\osReverseProjection.ts:29: "I detect an execution intent. This action cannot be initiated from Brody. I can prepare an ActionCandidate and ContextPacket for submission to X-108.",
- .\apps\obsidia-workbench\src\lib\osReverseProjection.ts:31: "A permission request is detected. Brody cannot grant it — the decision belongs to X-108. I can document the intent in a ContextPacket.",
- .\apps\obsidia-workbench\src\lib\osReverseProjection.ts:35: "A creation request is detected. Brody is readonly — no direct creation. I can prepare a structured proposal for X-108.",
- .\apps\obsidia-workbench\src\lib\osReverseProjection.ts:37: "A write is requested. Brody does not write to memory — no mutation possible. I can generate a memory candidate for human review.",
- .\apps\obsidia-workbench\src\lib\osReverseProjection.ts:39: "A deletion is requested. Brody cannot delete — no irreversible action from this layer.",
- .\apps\obsidia-workbench\src\lib\osTradPipeline.ts:40: os_trad_status:      hasForbidden ? 'BLOCKED' : 'PARSED',
- .\apps\obsidia-workbench\src\lib\osTradPipeline.ts:45: x108_boundary_status: 'READONLY',
- .\apps\obsidia-workbench\src\lib\sessionStore.ts:1: import type { BrodyMessage } from '../types/obsidia'
- .\apps\obsidia-workbench\src\lib\sessionStore.ts:31: export function getMessages(sessionId: string): BrodyMessage[] {
- .\apps\obsidia-workbench\src\lib\sessionStore.ts:36: export function saveMessages(sessionId: string, msgs: BrodyMessage[]): void {
- .\apps\obsidia-workbench\src\lib\symbolicAlphabet.ts:4: const ENTITY_RE   = /\b(kernel/x-108/x108/brody/mémoire/memory/graphiti/gencoin/os3/blockchain/wallet/token/action/acte?/commande?/command/fichier/file/base[\s-]de[\s-]données/database/api/neo4j/lean/tla)\b/gi
- .\apps\obsidia-workbench\src\types\obsidia.ts:3: export interface BrodyMessage {
- .\apps\obsidia-workbench\src\types\obsidia.ts:5: role: 'user' / 'brody'
- .\apps\obsidia-workbench\src\types\obsidia.ts:13: source?: 'REAL_BRODY_GRAPHITI_LIVE' / 'REAL_BRODY_LOCAL_ENGINE_ONLY' / 'REAL_BRODY_LLM_AUTHORIZED_READONLY' / 'REAL_BRODY_RUNTIME_NO_GRAPHITI' / 'REAL_BACKEND' / 'BACKEND_STUB' / 'FRONTEND_MOCK' / 'MEMORY_RESPONSE_CHAIN' / 'API_ERROR' / string
- .\apps\obsidia-workbench\src\types\obsidia.ts:73: source_type: 'BRODY_RUNTIME' / 'GRAPHITI_GRAPH' / 'FEEDBACK_CAPTURE' / 'CONTEXT_PACKET'
- .\apps\obsidia-workbench\src\types\obsidia.ts:94: type: 'context_read' / 'brody_response' / 'memory_candidate' / 'governance_check' / 'world_call' / 'gencoin_entry'
- .\apps\obsidia-workbench\src\types\translation.ts:35: os_trad_status: 'PARSED' / 'AMBIGUOUS' / 'BLOCKED' / 'MOCK'
- .\apps\obsidia-workbench\src\types\translation.ts:40: x108_boundary_status: 'READONLY' / 'BLOCKED' / 'PENDING'
- .\apps\obsidia-workbench\src\views\AuditView.tsx:9: brody_response:   'text-obs-brody',
- .\apps\obsidia-workbench\src\views\BlockchainView.tsx:26: <div>Brody ne peut pas signer de transaction blockchain.</div>
- .\apps\obsidia-workbench\src\views\BlockchainView.tsx:27: <div>Brody ne peut pas déployer de contrat intelligent.</div>
- .\apps\obsidia-workbench\src\views\BlockchainView.tsx:28: <div>Brody ne peut pas initier de transfert de token.</div>
- .\apps\obsidia-workbench\src\views\BlockchainView.tsx:34: <div className="text-obs-dtext text-[10px] font-mono font-semibold mb-2 uppercase tracking-wider">Boundary Status</div>
- .\apps\obsidia-workbench\src\views\ChatView.tsx:4: import type { BrodyMessage } from '../types/obsidia'
- .\apps\obsidia-workbench\src\views\ChatView.tsx:10: messages: BrodyMessage[]
- .\apps\obsidia-workbench\src\views\ChatView.tsx:24: {trace.os_trad_status}
- .\apps\obsidia-workbench\src\views\ChatView.tsx:31: <div className="flex gap-2"><span className="text-obs-dtext w-28 shrink-0">ir.intent_type</span><span className="text-obs-brody">{ir.intent_type}</span></div>
- .\apps\obsidia-workbench\src\views\ChatView.tsx:38: <span>x108=<span className="text-obs-pass">{trace.x108_boundary_status}</span></span>
- .\apps\obsidia-workbench\src\views\ChatView.tsx:44: function MessageBubble({ msg, trace, showTrace }: { msg: BrodyMessage; trace?: TranslationTrace; showTrace: boolean }) {
- .\apps\obsidia-workbench\src\views\ChatView.tsx:58: : msg.role === 'brody'
- .\apps\obsidia-workbench\src\views\ChatView.tsx:59: ? 'border-l-obs-brody'
- .\apps\obsidia-workbench\src\views\ChatView.tsx:75: <div className="w-7 h-7 rounded-full bg-obs-brody/20 border border-obs-brody/30 flex items-center justify-center shrink-0 mt-0.5">
- .\apps\obsidia-workbench\src\views\ChatView.tsx:76: <span className="text-obs-brody text-[10px] font-mono font-bold">B</span>
- .\apps\obsidia-workbench\src\views\ChatView.tsx:80: <span className="text-obs-brody text-xs font-mono font-semibold">Brody</span>
- .\apps\obsidia-workbench\src\views\ChatView.tsx:81: <span className="obs-badge-brody">ADVISORY</span>
- .\apps\obsidia-workbench\src\views\ChatView.tsx:103: String(msg.source).includes('MEMORY_RESPONSE_CHAIN') ? 'text-obs-brody bg-obs-brody/10' :
- .\apps\obsidia-workbench\src\views\ChatView.tsx:105: 'text-obs-brody bg-obs-brody/5'
- .\apps\obsidia-workbench\src\views\ChatView.tsx:113: <span>voice: <span className="text-obs-brody">{String(msg.backendPayload.voice_runtime)}</span></span>
- .\apps\obsidia-workbench\src\views\ChatView.tsx:123: return voiceSrc ? <span className="text-obs-brody">voice_src:{voiceSrc}</span> : null
- .\apps\obsidia-workbench\src\views\ChatView.tsx:161: <span className="text-obs-brody font-mono text-xs font-semibold">Brody</span>
- .\apps\obsidia-workbench\src\views\ChatView.tsx:163: <span className="obs-badge-brody">ADVISORY ONLY</span>
- .\apps\obsidia-workbench\src\views\ChatView.tsx:183: <span className="text-obs-dtext text-[10px] font-mono">Brody est advisory uniquement. X-108 decide.</span>
- .\apps\obsidia-workbench\src\views\ChatView.tsx:188: <div className="flex-1 bg-obs-card border border-obs-border rounded-xl overflow-hidden focus-within:border-obs-brody/50 transition-colors">
- .\apps\obsidia-workbench\src\views\ChatView.tsx:191: rows={2} placeholder="Interroger Brody (reponse consultative uniquement)..."
- .\apps\obsidia-workbench\src\views\ChatView.tsx:196: className="flex items-center gap-1.5 px-4 py-2.5 rounded-xl bg-obs-brody/20 border border-obs-brody/30 text-obs-brody text-xs font-mono font-semibold hover:bg-obs-brody/30 disabled:opacity-30 disabled:cursor-not-allowed transition-colors">
- .\apps\obsidia-workbench\src\views\GencoinView.tsx:50: <div>Brody ne peut pas lire ni écrire dans ce ledger depuis une action décisionnelle.</div>
- .\apps\obsidia-workbench\src\views\TranslationView.tsx:13: INTENT:     'bg-obs-brody/10 text-obs-brody border-obs-brody/20',
- .\apps\obsidia-workbench\src\views\TranslationView.tsx:62: <div>Natural input → OS Trad → Alphabet → IR Candidate → OS Reverse → X-108 boundary</div>
- .\apps\obsidia-workbench\src\views\TranslationView.tsx:91: trace.os_trad_status === 'BLOCKED' ? 'bg-obs-block/10 text-obs-block' : 'bg-obs-pass/10 text-obs-pass'
- .\apps\obsidia-workbench\src\views\TranslationView.tsx:92: }`}>{trace.os_trad_status}</span>
- .\apps\obsidia-workbench\src\views\TranslationView.tsx:127: <div className="flex gap-2"><span className="text-obs-dtext w-24 shrink-0">intent_type</span><span className="text-obs-brody">{ir.intent_type}</span></div>
- .\apps\obsidia-workbench\src\views\TranslationView.tsx:160: <div className="text-[10px] font-mono text-obs-dtext mb-0.5">X-108 Boundary</div>
- .\apps\obsidia-workbench\src\views\TranslationView.tsx:161: <div className="text-[10px] font-mono text-obs-kernel font-semibold">x108_boundary_status={trace.x108_boundary_status}</div>
- .\apps\obsidia-workbench\src\views\X108View.tsx:25: { step: 8, label: 'Brody responds',         cls: 'text-obs-brody' },
- .\apps\obsidia-workbench\src\views\X108View.tsx:105: {/* Protected boundary */}
- .\apps\obsidia-workbench\src\views\X108View.tsx:107: <div className="text-obs-kernel font-semibold mb-1">X-108 PROTECTED BOUNDARY</div>
- .\apps\obsidia-workbench\src\views\X108View.tsx:110: <div className="mt-1 text-obs-dtext">No periphery can modify these files. Brody cannot bypass this boundary.</div>
- .\apps\obsidia-workbench\src\App.tsx:18: import { getKernelStatus, sendBrodyMessage } from './api/obsidiaClient'
- .\apps\obsidia-workbench\src\App.tsx:19: import { composeBrodyResponse } from './lib/brodyResponseComposer'
- .\apps\obsidia-workbench\src\App.tsx:27: import type { BrodyMessage, KernelStatus } from './types/obsidia'
- .\apps\obsidia-workbench\src\App.tsx:32: function initSession(): { sessionId: string; msgs: BrodyMessage[] } {
- .\apps\obsidia-workbench\src\App.tsx:51: const [messages, setMessages]           = useState<BrodyMessage[]>(initMsgs)
- .\apps\obsidia-workbench\src\App.tsx:70: const userMsg: BrodyMessage = {
- .\apps\obsidia-workbench\src\App.tsx:93: const res = await sendBrodyMessage(text, lang, activeSessionId)
- .\apps\obsidia-workbench\src\App.tsx:103: responseText = composeBrodyResponse({ userInput: text, language: lang, translationTrace: trace })
- .\apps\obsidia-workbench\src\App.tsx:110: const brodyId = `b_${Date.now() + 1}`
- .\apps\obsidia-workbench\src\App.tsx:111: const brodyMsg: BrodyMessage = {
- .\apps\obsidia-workbench\src\App.tsx:112: id: brodyId,
- .\apps\obsidia-workbench\src\App.tsx:113: role: 'brody',
- .\apps\obsidia-workbench\src\App.tsx:121: source: backendSource as BrodyMessage['source'],
- .\apps\obsidia-workbench\src\App.tsx:125: setMessages(prev => [...prev, brodyMsg])
- .\apps\obsidia-workbench\src\App.tsx:126: setTraces(prev => ({ ...prev, [brodyId]: trace }))
- .\apps\obsidia-workbench\audit_brody.py:4: url = 'http://127.0.0.1:8000/api/brody/chat'
- .\apps\obsidia-workbench\BACKEND_BINDING_PLAN_X108_PROOFS.md:12: / `getKernelStatus()` / LIVE (ObsidiaShell /health) / `periphery/brody/brody_runtime_readonly.py` / `GET /api/x108/status` / readonly /
- .\apps\obsidia-workbench\BACKEND_BINDING_PLAN_X108_PROOFS.md:18: / `sendBrodyMessage()` / STUB (composer in frontend) / `periphery/brody/brody_runtime_readonly.py` / `POST /api/brody/chat` / advisory_only /
- .\apps\obsidia-workbench\BACKEND_BINDING_PLAN_X108_PROOFS.md:22: / `getMemoryCandidates()` / MOCK_ONLY / `periphery/brody_memory_readonly/` / `GET /api/memory/candidates` / readonly /
- .\apps\obsidia-workbench\BACKEND_BINDING_PLAN_X108_PROOFS.md:27: / `getOSReverseProjection()` / STUB / `periphery/reverse_os/action_projection_readonly.py` / `POST /api/os-reverse/project` / advisory_only /
- .\apps\obsidia-workbench\BACKEND_BINDING_PLAN_X108_PROOFS.md:61: / `POST /api/os-reverse/project` / Reverse projection / `periphery/reverse_os/action_projection_readonly.py` /
- .\apps\obsidia-workbench\BACKEND_BINDING_PLAN_X108_PROOFS.md:64: / `GET /api/brody/language-route` / Brody language routing / `periphery/brody/brody_language_router.py` /
- .\apps\obsidia-workbench\BACKEND_DISCOVERY_REPORT.md:42: Captured at: `obsidia-engine-proof-core/_BRODY_OPENAPI_8011.json`
- .\apps\obsidia-workbench\BACKEND_DISCOVERY_REPORT.md:70: ## 3. No Brody HTTP Endpoint Found
- .\apps\obsidia-workbench\BACKEND_DISCOVERY_REPORT.md:72: No dedicated `/brody` or `/context` endpoint was found in either server. Brody responses in the workbench are purely advisory mock responses. When a real Brody HTTP endpoint is available, update `obsidiaClient.ts::sendBrodyMessage()`.
- .\apps\obsidia-workbench\BACKEND_DISCOVERY_REPORT.md:86: / `sendBrodyMessage()` / *no endpoint — mock only* / advisory mock /
- .\apps\obsidia-workbench\FASTAPI_ADAPTER_PLAN.md:17: brody.py       # POST /api/brody/chat
- .\apps\obsidia-workbench\FASTAPI_ADAPTER_PLAN.md:25: os_trad.py     # POST /api/os-trad/translate
- .\apps\obsidia-workbench\FASTAPI_ADAPTER_PLAN.md:29: deps.py          # Shared dependencies (kernel boundary check)
- .\apps\obsidia-workbench\FASTAPI_ADAPTER_PLAN.md:47: POST /api/brody/chat
- .\apps\obsidia-workbench\FASTAPI_ADAPTER_PLAN.md:49: → BrodyResponse: response, readonly=true, advisory_only=true, emits_act=false,
- .\apps\obsidia-workbench\FASTAPI_ADAPTER_PLAN.md:85: Maps to: periphery/language/language_router.py + new os_trad module
- .\apps\obsidia-workbench\FASTAPI_ADAPTER_PLAN.md:95: Maps to: periphery/reverse_os/action_projection_readonly.py
- .\apps\obsidia-workbench\FRONTEND_BACKEND_BRIDGE_REPORT.md:20: │    └── sendBrodyMessage()  (mock only)      │    │  │
- .\apps\obsidia-workbench\FRONTEND_BACKEND_BRIDGE_REPORT.md:98: - `sendBrodyMessage()` always returns `emits_act: false, memory_write: false, decision_authority: 'KX108_ONLY'`
- .\apps\obsidia-workbench\FRONTEND_BACKEND_BRIDGE_REPORT.md:109: / `sendBrodyMessage()` / POST `/brody/query` when Brody HTTP endpoint is added /
- .\apps\obsidia-workbench\OS_TRAD_REVERSE_IR_BACKEND_BINDING_PLAN.md:15: / `src/lib/osReverseProjection.ts` / MOCK_ONLY / `periphery/reverse_os/action_projection_readonly.py` /
- .\apps\obsidia-workbench\OS_TRAD_REVERSE_IR_BACKEND_BINDING_PLAN.md:16: / `src/lib/osTradPipeline.ts` / MOCK_ONLY / `periphery/language/language_router.py` + new `periphery/os_trad/` /
- .\apps\obsidia-workbench\OS_TRAD_REVERSE_IR_BACKEND_BINDING_PLAN.md:17: / `src/lib/brodyResponseComposer.ts` / MOCK_ONLY / `periphery/brody/brody_runtime_readonly.py` /
- .\apps\obsidia-workbench\OS_TRAD_REVERSE_IR_BACKEND_BINDING_PLAN.md:26: / Brody language router / `periphery/brody/brody_language_router.py` / `route_brody_language()` /
- .\apps\obsidia-workbench\OS_TRAD_REVERSE_IR_BACKEND_BINDING_PLAN.md:27: / Action projection (readonly) / `periphery/reverse_os/action_projection_readonly.py` / `project_action_readonly()` — advisory_only=True /
- .\apps\obsidia-workbench\OS_TRAD_REVERSE_IR_BACKEND_BINDING_PLAN.md:45: "os_trad_status": "BLOCKED",  # or PARSED
- .\apps\obsidia-workbench\OS_TRAD_REVERSE_IR_BACKEND_BINDING_PLAN.md:50: "x108_boundary_status": "READONLY",
- .\apps\obsidia-workbench\OS_TRAD_REVERSE_IR_BACKEND_BINDING_PLAN.md:55: Maps to: `periphery/language/language_router.py` + new `periphery/os_trad/` module
- .\apps\obsidia-workbench\OS_TRAD_REVERSE_IR_BACKEND_BINDING_PLAN.md:68: # Maps to: periphery/reverse_os/action_projection_readonly.py
- .\apps\obsidia-workbench\OS_TRAD_REVERSE_IR_DISCOVERY_REPORT.md:27: / `periphery/brody/brody_language_router.py` / Brody Language Router / `BrodyLanguageRoute`, `route_brody_language()` /
- .\apps\obsidia-workbench\OS_TRAD_REVERSE_IR_DISCOVERY_REPORT.md:28: / `periphery/brody/brody_runtime_readonly.py` / Brody Runtime (readonly) / brody response contract /
- .\apps\obsidia-workbench\OS_TRAD_REVERSE_IR_DISCOVERY_REPORT.md:29: / `periphery/brody/brody_context_query.py` / Brody Context Query / context read functions /
- .\apps\obsidia-workbench\OS_TRAD_REVERSE_IR_DISCOVERY_REPORT.md:30: / `periphery/reverse_os/action_projection_readonly.py` / OS Reverse (action) / `ActionProjection`, `project_action_readonly()` /
- .\apps\obsidia-workbench\OS_TRAD_REVERSE_IR_DISCOVERY_REPORT.md:31: / `periphery/reverse_os/audience_projection.py` / OS Reverse (audience) / audience-based projection /
- .\apps\obsidia-workbench\OS_TRAD_REVERSE_IR_DISCOVERY_REPORT.md:32: / `periphery/reverse_os/format_projection.py` / OS Reverse (format) / format-based projection /
- .\apps\obsidia-workbench\OS_TRAD_REVERSE_IR_DISCOVERY_REPORT.md:45: **`periphery/brody/brody_language_router.py`:**
- .\apps\obsidia-workbench\OS_TRAD_REVERSE_IR_DISCOVERY_REPORT.md:47: class BrodyLanguageRoute: detected_language, routed_to, is_supported, memory_write=False
- .\apps\obsidia-workbench\OS_TRAD_REVERSE_IR_DISCOVERY_REPORT.md:48: def route_brody_language(query_id: str, language_code: str) -> BrodyLanguageRoute
- .\apps\obsidia-workbench\OS_TRAD_REVERSE_IR_DISCOVERY_REPORT.md:52: **`periphery/reverse_os/action_projection_readonly.py`:**
- .\apps\obsidia-workbench\OS_TRAD_REVERSE_IR_DISCOVERY_REPORT.md:65: / `tests/non_sovereignty/test_brody_no_decision.py` / Tests that Brody cannot emit decision (IR-adjacent logic) /
- .\apps\obsidia-workbench\OS_TRAD_REVERSE_IR_DISCOVERY_REPORT.md:66: / `tests/non_sovereignty/test_brody_no_act.py` / Tests that Brody cannot emit ACT (similar to IR constraint) /
- .\apps\obsidia-workbench\OS_TRAD_REVERSE_IR_DISCOVERY_REPORT.md:74: / `periphery/os_trad/` / **MISSING** / No OS Trad module exists. Language router is the closest proxy. /
- .\apps\obsidia-workbench\OS_TRAD_REVERSE_IR_DISCOVERY_REPORT.md:87: / OS Reverse projection / `src/lib/osReverseProjection.ts` / MOCK_ONLY (maps to `reverse_os/action_projection_readonly.py` semantics) /
- .\apps\obsidia-workbench\OS_TRAD_REVERSE_IR_DISCOVERY_REPORT.md:95: / `POST /api/os-trad/translate` / `periphery/language/language_router.py` + new os_trad module / NEEDS_FASTAPI_ROUTE /
- .\apps\obsidia-workbench\OS_TRAD_REVERSE_IR_DISCOVERY_REPORT.md:97: / `POST /api/os-reverse/project` / `periphery/reverse_os/action_projection_readonly.py` / NEEDS_FASTAPI_ROUTE /
- .\apps\obsidia-workbench\OS_TRAD_REVERSE_IR_DISCOVERY_REPORT.md:100: / `GET /api/brody/language-route` / `periphery/brody/brody_language_router.py` / NEEDS_FASTAPI_ROUTE /
- .\apps\obsidia-workbench\OS_TRAD_REVERSE_IR_UI_REPORT.md:4: **Status:** OS_TRAD_IR_TRACE_PASS
- .\apps\obsidia-workbench\OS_TRAD_REVERSE_IR_UI_REPORT.md:17: / Brody composer with trace (`src/lib/brodyResponseComposer.ts`) / PASS /
- .\apps\obsidia-workbench\OS_TRAD_REVERSE_IR_UI_REPORT.md:73: / X-108 boundary reminder / ✓ /
- .\apps\obsidia-workbench\OS_TRAD_REVERSE_IR_UI_REPORT.md:85: / Trace panel appears under each Brody message when enabled / ✓ /
- .\apps\obsidia-workbench\OS_TRAD_REVERSE_IR_UI_REPORT.md:86: / Shows: os_trad_status, detected_lang, alphabet_units, risk_flags, contradictions, os_reverse_projection / ✓ /
- .\apps\obsidia-workbench\README_OBSIDIA_WORKBENCH.md:27: │ LEFT SIDEBAR │  BRODY CHAT (main)           │  RIGHT PANEL (tabs)   │
- .\apps\obsidia-workbench\README_OBSIDIA_WORKBENCH.md:30: │ Memory Srcs  │  Brody: context signal only  │  GOV                  │
- .\apps\obsidia-workbench\README_OBSIDIA_WORKBENCH.md:58: / `Brody emits_act` / `false` /
- .\apps\obsidia-workbench\README_OBSIDIA_WORKBENCH.md:96: BrodyPanel.tsx      Main chat panel
- .\apps\obsidia-workbench\tailwind.config.js:16: brody:   '#3b82f6',
- .\apps\obsidia-workbench\WORKBENCH_V2_BACKEND_STATUS_REPORT.md:15: / Brody Runtime / STUB / /api/brody/chat / 8000 /
- .\apps\obsidia-workbench\WORKBENCH_V2_BUILD_REPORT.md:43: - `brodyResponseComposer.ts` — contextual response generator
- .\apps\obsidia-workbench\WORKBENCH_V2_BUILD_REPORT.md:57: - `ChatView.tsx` — main chat (replaces BrodyPanel in routing)
- .\apps\obsidia-workbench\WORKBENCH_V2_BUILD_REPORT.md:77: / BRODY_RESPONSE_QUALITY_PASS / ✓ /
- .\apps\obsidia-workbench\WORKBENCH_V2_BUILD_REPORT.md:84: / OS_TRAD_IR_TRACE_PASS / ✓ /
- .\apps\obsidia-workbench\WORKBENCH_V2_UI_REPORT.md:13: / 2 / Brody Response Composer / BRODY_RESPONSE_QUALITY_PASS /
- .\apps\obsidia-workbench\WORKBENCH_V2_UI_REPORT.md:19: / A / OS Trad / IR / OS Reverse / OS_TRAD_IR_TRACE_PASS /
- .\apps\obsidia-workbench\WORKBENCH_V2_UI_REPORT.md:35: ## Brody response quality
- .\apps\obsidia-workbench\WORKBENCH_V2_UI_REPORT.md:39: [BRODY_READONLY_RESPONSE] Advisory signal generated. No ACT emitted...
- .\apps\obsidia-workbench\WORKBENCH_V2_UI_REPORT.md:44: Salut. Je suis Brody, interface consultative d'Obsidia X-108. Je lis le contexte, structure des signaux — mais je ne décide pas. L'autorité de décision reste X-108. Que puis-je analyser pour toi ?
- .\apps\obsidia_api\routes\blockchain.py:11: from periphery.blockchain.signature_boundary import (
- .\apps\obsidia_api\routes\blockchain.py:35: from periphery.agents import world_action_agent, gencoin_value_agent, os3_proof_agent, data_purity_agent, provenance_agent, brody_memory_agent, eml_symbolic_agent, energy_thermo_agent, timeverse_agent, ocs_generation_agent, operational_constance_agent, permission_economic_agent, action_sequence_agent, feedback_memory_agent
- .\apps\obsidia_api\routes\blockchain.py:40: from periphery.world_calls.secret_boundary import redact_secrets, assert_no_secret_in_agent_payload
- .\apps\obsidia_api\routes\blockchain.py:42: from periphery.physics_boundary.dimensional_hygiene import check_dimensional_hygiene
- .\apps\obsidia_api\routes\blockchain.py:43: from periphery.physics_boundary.frequency_tag_mapper import map_frequency_tag
- .\apps\obsidia_api\routes\blockchain.py:44: from periphery.physics_boundary.unit_consistency_checker import check_unit_consistency
- .\apps\obsidia_api\routes\blockchain.py:45: from periphery.physics_boundary.symbolic_physics_claim_gate import evaluate_physics_claim
- .\apps\obsidia_api\routes\blockchain.py:50: _BOUNDARY = {
- .\apps\obsidia_api\routes\blockchain.py:113: return safe_backend_response({**result.to_dict(), **_BOUNDARY}, source="REAL_BACKEND")
- .\apps\obsidia_api\routes\blockchain.py:126: return safe_backend_response({**result.to_dict(), **_BOUNDARY}, source="REAL_BACKEND")
- .\apps\obsidia_api\routes\blockchain.py:136: return safe_backend_response({**result.to_dict(), **_BOUNDARY}, source="REAL_BACKEND")
- .\apps\obsidia_api\routes\blockchain.py:175: **_BOUNDARY,
- .\apps\obsidia_api\routes\blockchain.py:176: }, source="REAL_BACKEND")
- .\apps\obsidia_api\routes\blockchain.py:212: **_BOUNDARY,
- .\apps\obsidia_api\routes\blockchain.py:213: }, source="REAL_BACKEND")
- .\apps\obsidia_api\routes\blockchain.py:285: # Secret boundary — redact then assert no secret escapes toward gateway
- .\apps\obsidia_api\routes\blockchain.py:374: **_BOUNDARY,
- .\apps\obsidia_api\routes\blockchain.py:375: }, source="REAL_BACKEND")
- .\apps\obsidia_api\routes\blockchain.py:397: # Secret boundary on dispatch fields
- .\apps\obsidia_api\routes\blockchain.py:424: **_BOUNDARY,
- .\apps\obsidia_api\routes\blockchain.py:425: }, source="REAL_BACKEND")
- .\apps\obsidia_api\routes\blockchain.py:436: **_BOUNDARY,
- .\apps\obsidia_api\routes\blockchain.py:437: }, source="REAL_BACKEND")
- .\apps\obsidia_api\routes\blockchain.py:454: return safe_backend_response({**result.to_dict(), **_BOUNDARY}, source="REAL_BACKEND")
- .\apps\obsidia_api\routes\blockchain.py:483: **_BOUNDARY,
- .\apps\obsidia_api\routes\blockchain.py:484: }, source="REAL_BACKEND")

## Git history targeted

### periphery/brody
- e9e43e4 2026-05-21 feat(brody): wire full runtime with real project memory

### periphery/bdf
- a5f21c6 2026-05-26 chore: clean repo hygiene and exclude generated audit artifacts

### periphery/reverse_os
- a5f21c6 2026-05-26 chore: clean repo hygiene and exclude generated audit artifacts

### modules/os_trad
- NO_HISTORY

### tools/brody_chat.py
- bd24976 2026-05-27 fix: align live Workbench and Brody CLI ports
- a5f21c6 2026-05-26 chore: clean repo hygiene and exclude generated audit artifacts

### scripts/smoke_brody_capabilities.ps1
- d1dcbbf 2026-05-27 feat: reconnect Brody runtime and Graphiti V20 readonly proxy

### scripts/smoke_brody_routes.ps1
- d1dcbbf 2026-05-27 feat: reconnect Brody runtime and Graphiti V20 readonly proxy

### tests/api/test_brody_capabilities_preserved.py
- d1dcbbf 2026-05-27 feat: reconnect Brody runtime and Graphiti V20 readonly proxy

### tests/api/test_brody_routes_registered.py
- d1dcbbf 2026-05-27 feat: reconnect Brody runtime and Graphiti V20 readonly proxy

### docs/freeze/V5B_PLUS_BRODY_RESPONSE_MODULE_AUDIT.md
- a5f21c6 2026-05-26 chore: clean repo hygiene and exclude generated audit artifacts

### docs/freeze/BRODY_REAL_MODULE_DISCOVERY_FOR_API.md
- a5f21c6 2026-05-26 chore: clean repo hygiene and exclude generated audit artifacts

### docs/freeze/BRODY_REAL_BACKEND_AUDIT_REPORT.md
- a5f21c6 2026-05-26 chore: clean repo hygiene and exclude generated audit artifacts

### apps/obsidia-workbench/OS_TRAD_REVERSE_IR_DISCOVERY_REPORT.md
- a5f21c6 2026-05-26 chore: clean repo hygiene and exclude generated audit artifacts

### apps/obsidia-workbench/OS_TRAD_REVERSE_IR_BACKEND_BINDING_PLAN.md
- a5f21c6 2026-05-26 chore: clean repo hygiene and exclude generated audit artifacts

### apps/obsidia_api/routes/periphery_ops.py
- a5f21c6 2026-05-26 chore: clean repo hygiene and exclude generated audit artifacts

## Boundary
- Diagnostic only.
- No runtime patch.
- No service started.
- No mutation.
- KX108_ONLY remains sole decision authority.

## Next
- Phase 8B should execute live smoke tests for the already reconnected path.
- Phase 8C should compare current live behavior against old Brody capability evidence.
- Do not patch before identifying which old layer materially improved Brody responses.
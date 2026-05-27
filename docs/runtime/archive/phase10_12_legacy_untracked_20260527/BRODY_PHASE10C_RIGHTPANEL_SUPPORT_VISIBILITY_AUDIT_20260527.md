# BRODY_PHASE10C_RIGHTPANEL_SUPPORT_VISIBILITY_AUDIT_20260527

Status: DIAGNOSTIC_ONLY

## Scope
Audit why UI real-user test does not visibly expose support_routes / backend_support after Phase 9B4.

## Files inspected
- exists=True length=42577 path=apps/obsidia-workbench/src/components/RightPanel.tsx
- exists=True length=9653 path=apps/obsidia-workbench/src/App.tsx
- exists=True length=1225 path=apps/obsidia-workbench/src/types/translation.ts
- exists=True length=3054 path=apps/obsidia-workbench/src/types/obsidia.ts
- exists=True length=13141 path=apps/obsidia-workbench/src/api/obsidiaClient.ts

## Evidence hits
- .\apps\obsidia-workbench\src\components\RightPanel.tsx:1: // OBSIDIA-UI-IMPROVEMENT: RightPanel — clickable copy, tree_X prompts, v18 hash, git branch, refresh context
- .\apps\obsidia-workbench\src\components\RightPanel.tsx:63: <SectionTitle>Authority Snapshot</SectionTitle>
- .\apps\obsidia-workbench\src\components\RightPanel.tsx:138: <SectionTitle>Live Backend — Last Response</SectionTitle>
- .\apps\obsidia-workbench\src\components\RightPanel.tsx:175: <CopyableKV k="attempted_queries" v={JSON.stringify((memChain.attempted_queries as unknown[]).slice(0, 4))} />
- .\apps\obsidia-workbench\src\components\RightPanel.tsx:273: <SectionTitle>Context Packet — Live</SectionTitle>
- .\apps\obsidia-workbench\src\components\RightPanel.tsx:276: <CopyableKV key={k} k={k} v={typeof v === 'object' ? JSON.stringify(v) : String(v ?? '')} />
- .\apps\obsidia-workbench\src\components\RightPanel.tsx:282: <SectionTitle>Context Packet</SectionTitle>
- .\apps\obsidia-workbench\src\components\RightPanel.tsx:301: <button onClick={() => onSendPrompt?.('Analyse le context packet dans le contexte kernel')} className="text-obs-dtext hover:text-obs-brody p-0.5" title="Send to Brody">
- .\apps\obsidia-workbench\src\components\RightPanel.tsx:744: interface RightPanelProps { onSendPrompt?: (text: string) => void; lastBackendPayload?: Record<string, unknown> }
- .\apps\obsidia-workbench\src\components\RightPanel.tsx:746: export function RightPanel({ onSendPrompt, lastBackendPayload }: RightPanelProps) {
- .\apps\obsidia-workbench\src\components\RightPanel.tsx:748: const automationSnap = lastBackendPayload?.automation_snapshot as AutomationSnapshot / undefined
- .\apps\obsidia-workbench\src\components\RightPanel.tsx:749: const structuredSnap = lastBackendPayload?.structured_response_snapshot as StructuredResponseSnapshot / undefined
- .\apps\obsidia-workbench\src\components\RightPanel.tsx:750: const freezeSnap = lastBackendPayload?.freeze_metrics_snapshot as FreezeMetricsSnapshot / undefined
- .\apps\obsidia-workbench\src\components\RightPanel.tsx:753: context:    <ContextTab onSendPrompt={onSendPrompt} live={lastBackendPayload} />,
- .\apps\obsidia-workbench\src\components\RightPanel.tsx:757: audit:      <AuditTab live={lastBackendPayload} />,
- .\apps\obsidia-workbench\src\App.tsx:5: import { RightPanel } from './components/RightPanel'
- .\apps\obsidia-workbench\src\App.tsx:53: const [lastBackendPayload, setLastBackendPayload] = useState<Record<string, unknown> / undefined>()
- .\apps\obsidia-workbench\src\App.tsx:92: let backendPayload: Record<string, unknown> / undefined
- .\apps\obsidia-workbench\src\App.tsx:99: backendPayload = res as Record<string, unknown>
- .\apps\obsidia-workbench\src\App.tsx:100: setLastBackendPayload(backendPayload)
- .\apps\obsidia-workbench\src\App.tsx:144: source: 'REAL_BACKEND_SUPPORT',
- .\apps\obsidia-workbench\src\App.tsx:150: if (backendPayload) {
- .\apps\obsidia-workbench\src\App.tsx:151: backendPayload = {
- .\apps\obsidia-workbench\src\App.tsx:152: ...backendPayload,
- .\apps\obsidia-workbench\src\App.tsx:153: support_routes: supportPayload,
- .\apps\obsidia-workbench\src\App.tsx:155: setLastBackendPayload(backendPayload)
- .\apps\obsidia-workbench\src\App.tsx:163: if (backendPayload) {
- .\apps\obsidia-workbench\src\App.tsx:164: backendPayload = {
- .\apps\obsidia-workbench\src\App.tsx:165: ...backendPayload,
- .\apps\obsidia-workbench\src\App.tsx:166: support_routes: supportPayload,
- .\apps\obsidia-workbench\src\App.tsx:168: setLastBackendPayload(backendPayload)
- .\apps\obsidia-workbench\src\App.tsx:174: const baseTrace: TranslationTrace = backendPayload?.translation_trace as TranslationTrace ?? runOSTradPipeline(text, lang)
- .\apps\obsidia-workbench\src\App.tsx:176: ? ({ ...baseTrace, backend_support: supportPayload } as unknown as TranslationTrace)
- .\apps\obsidia-workbench\src\App.tsx:191: backendPayload,
- .\apps\obsidia-workbench\src\App.tsx:242: <RightPanel lastBackendPayload={lastBackendPayload} />
- .\apps\obsidia-workbench\src\types\obsidia.ts:14: backendPayload?: Record<string, unknown>
- .\apps\obsidia-workbench\src\api\obsidiaClient.ts:84: body: JSON.stringify({ message: text, language: lang, session_id: sessionId, mode: 'readonly' }),
- .\apps\obsidia-workbench\src\api\obsidiaClient.ts:293: body: JSON.stringify(body),

## UI test observation
- Boundary is visible.
- RightPanel shows backend/governance/memory/tree/context packets.
- support_routes is not visibly exposed.
- backend_support is not visibly exposed.
- Therefore Phase 10B remains PARTIAL.

## Boundary
- No patch.
- No runtime mutation.
- No kernel mutation.
- No X108 mutation.
- No memory write.
- No Graphiti write.
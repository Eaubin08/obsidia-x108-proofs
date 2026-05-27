// OBSIDIA-UI-IMPROVEMENT: ChatView — colored border, copy button, hover timestamp, metadata footer
import { useState, useRef, useEffect } from 'react'
import { Send, Lock, AlertCircle, ChevronDown, ChevronRight, Copy, Check } from 'lucide-react'
import type { BrodyMessage } from '../types/obsidia'
import type { TranslationTrace } from '../types/translation'
import type { DetectedLanguage } from '../lib/language'
import { config } from '../api/obsidiaClient'

interface Props {
  messages: BrodyMessage[]
  traces: Record<string, TranslationTrace>
  onSend: (text: string) => void
  sessionLanguage: DetectedLanguage
}

function TracePanel({ trace }: { trace: TranslationTrace }) {
  const ir = trace.ir_candidate
  const hasRisk = ir.risk_flags.length > 0
  return (
    <div className="mt-2 rounded-lg border border-obs-proof/20 bg-obs-proof/5 p-2.5 space-y-1">
      <div className="text-obs-proof text-[9px] font-mono font-semibold flex items-center gap-1.5 mb-1">
        OS TRAD → IR → OS REVERSE
        <span className={`px-1 rounded ${hasRisk ? 'bg-obs-block/20 text-obs-block' : 'bg-obs-pass/20 text-obs-pass'}`}>
          {trace.os_trad_status}
        </span>
        <span className="ml-auto text-obs-dtext">{trace.source}</span>
      </div>
      <div className="text-[9px] font-mono space-y-0.5">
        <div className="flex gap-2"><span className="text-obs-dtext w-28 shrink-0">detected_lang</span><span className="text-obs-mtext">{trace.detected_language}</span></div>
        <div className="flex gap-2"><span className="text-obs-dtext w-28 shrink-0">response_lang</span><span className="text-obs-mtext">{trace.response_language}</span></div>
        <div className="flex gap-2"><span className="text-obs-dtext w-28 shrink-0">ir.intent_type</span><span className="text-obs-brody">{ir.intent_type}</span></div>
      </div>
      {ir.risk_flags.length > 0 && <div className="flex flex-wrap gap-1">{ir.risk_flags.map(f => <span key={f} className="px-1.5 py-0.5 rounded bg-obs-block/10 text-obs-block border border-obs-block/20 text-[9px] font-mono">{f}</span>)}</div>}
      {ir.contradictions.length > 0 && <div className="text-[9px] font-mono text-obs-hold space-y-0.5">{ir.contradictions.map(c => <div key={c}>⚠ {c}</div>)}</div>}
      <div className="pt-1 border-t border-obs-proof/10 text-[9px] font-mono text-obs-dtext flex gap-3">
        <span>allowed_to_decide=<span className="text-obs-block">false</span></span>
        <span>allowed_to_act=<span className="text-obs-block">false</span></span>
        <span>x108=<span className="text-obs-pass">{trace.x108_boundary_status}</span></span>
      </div>
    </div>
  )
}

function BrodyTerminalView({ payload }: { payload?: Record<string, unknown> }) {
  const op = payload?.operator_view_packet as Record<string, unknown> | undefined
  if (!op) return null

  const summary = op["summary"] as Record<string, unknown> | undefined
  const blocked = op["blocked"] as Record<string, unknown> | undefined
  const evidence = op["evidence"] as Record<string, unknown> | undefined
  const hardRisks = Array.isArray(blocked?.["hard_risks"]) ? blocked?.["hard_risks"] as unknown[] : []
  const missingPackets = Array.isArray(blocked?.["missing_packets"]) ? blocked?.["missing_packets"] as unknown[] : []

  const lines = [
    `OBSIDIA_TERMINAL_VIEW_V1`,
    `system_status=${String(op["system_status"] ?? "-")}`,
    `next_safe_action=${String(op["next_safe_action"] ?? "-")}`,
    `decision_authority=${String(op["decision_authority"] ?? "KX108_ONLY")}`,
    `readonly=${String(op["readonly"] ?? true)}`,
    `emits_act=${String(op["emits_act"] ?? false)}`,
    `emits_verdict=${String(op["emits_verdict"] ?? false)}`,
    `safe_boundary_ok=${String(summary?.["safe_boundary_ok"] ?? false)}`,
    `operator_can_write=${String(summary?.["operator_can_write"] ?? false)}`,
    `operator_can_decide=${String(summary?.["operator_can_decide"] ?? false)}`,
    `hard_risks=${JSON.stringify(hardRisks.slice(0, 8))}`,
    `missing_packets=${JSON.stringify(missingPackets.slice(0, 8))}`,
    `memory_guard_status=${String(evidence?.["memory_guard_status"] ?? "-")}`,
    `value_layer_scores_null=${String(evidence?.["value_layer_scores_null"] ?? "-")}`,
  ]

  return (
    <div className="mt-2 rounded-lg border border-obs-proof/20 bg-black/30 p-2.5">
      <div className="text-obs-proof text-[9px] font-mono font-semibold mb-1 flex items-center gap-2">
        BRODY TERMINAL — TRANSVERSE STACK
        <span className="ml-auto text-obs-dtext">readonly / no ACT / no write</span>
      </div>
      <pre className="text-[9px] leading-relaxed font-mono text-obs-mtext whitespace-pre-wrap break-words max-h-56 overflow-y-auto">
        {lines.join("\n")}
      </pre>
    </div>
  )
}

function MessageBubble({ msg, trace, showTrace }: { msg: BrodyMessage; trace?: TranslationTrace; showTrace: boolean }) {
  const isUser = msg.role === 'user'
  const ts = new Date(msg.timestamp).toLocaleTimeString()
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    await navigator.clipboard.writeText(msg.content)
    setCopied(true)
    setTimeout(() => setCopied(false), 1500)
  }

  // Border color: blue for advisory, orange for kernel, red for act
  const borderColor = msg.emits_act
    ? 'border-l-obs-block'
    : msg.role === 'brody'
    ? 'border-l-obs-brody'
    : 'border-l-transparent'

  if (isUser) {
    return (
      <div className="flex justify-end mb-4">
        <div className="max-w-[72%]">
          <div className="bg-obs-border/80 text-obs-text rounded-2xl rounded-tr-sm px-4 py-2.5 text-sm">{msg.content}</div>
          <div className="text-obs-dtext text-[10px] font-mono text-right mt-1 pr-1 opacity-0 hover:opacity-100 transition-opacity">{ts}</div>
        </div>
      </div>
    )
  }

  return (
    <div className={`flex gap-3 mb-4 border-l-2 ${borderColor} pl-2`}>
      <div className="w-7 h-7 rounded-full bg-obs-brody/20 border border-obs-brody/30 flex items-center justify-center shrink-0 mt-0.5">
        <span className="text-obs-brody text-[10px] font-mono font-bold">B</span>
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1.5">
          <span className="text-obs-brody text-xs font-mono font-semibold">Brody</span>
          <span className="obs-badge-brody">ADVISORY</span>
          <span className="obs-badge-muted">readonly=true</span>
          <span className="obs-badge-muted">emits_act=false</span>
          <div className="ml-auto flex items-center gap-1">
            <button onClick={handleCopy} className="opacity-0 group-hover:opacity-100 p-0.5 text-obs-dtext hover:text-obs-text" title="Copy response">
              {copied ? <Check size={10} className="text-obs-pass" /> : <Copy size={10} />}
            </button>
          </div>
        </div>
        <div className="group bg-obs-card border border-obs-border rounded-2xl rounded-tl-sm px-4 py-3">
          <p className="text-obs-text text-sm leading-relaxed whitespace-pre-wrap">{msg.content}</p>
          {showTrace && trace && <TracePanel trace={trace} />}
        </div>

        {/* Metadata footer — Sovereignty Matrix */}
        <div className="flex items-center gap-3 mt-1.5 pl-1 flex-wrap text-[9px] text-[#4a5568] font-mono">
          <span className="opacity-0 hover:opacity-100 transition-opacity">{ts}</span>
          {msg.source && (
            <span className={`text-[8px] font-semibold px-1 rounded ${
              String(msg.source).includes('GRAPHITI') ? 'text-obs-pass bg-obs-pass/5' :
              String(msg.source).includes('MOCK') ? 'text-obs-block bg-obs-block/5' :
              String(msg.source).includes('API_ERROR') ? 'text-obs-block bg-obs-block/10' :
              String(msg.source).includes('MEMORY_RESPONSE_CHAIN') ? 'text-obs-brody bg-obs-brody/10' :
              String(msg.source).includes('NO_GRAPHITI') || String(msg.source).includes('STUB') ? 'text-obs-hold bg-obs-hold/5' :
              'text-obs-brody bg-obs-brody/5'
            }`}>{msg.source}</span>
          )}
          <span>decision_authority: <span className="text-obs-kernel">{String((msg.backendPayload?.decision_authority as string) ?? 'KX108_ONLY')}</span></span>
          <span>readonly: <span className="text-obs-pass">{String((msg.backendPayload?.readonly as boolean) ?? true)}</span></span>
          <span>memory_write: <span className="text-obs-block">{String((msg.backendPayload?.memory_write as boolean) ?? false)}</span></span>
          <span>emits_act: <span className="text-obs-block">{String((msg.backendPayload?.emits_act as boolean) ?? false)}</span></span>
          {msg.backendPayload?.voice_runtime ? (
            <span>voice: <span className="text-obs-brody">{String(msg.backendPayload.voice_runtime)}</span></span>
          ) : null}
        </div>

        {/* Backend status row — real API fields */}
        {msg.backendPayload && (
          <div className="flex items-center gap-2 mt-0.5 pl-1 flex-wrap text-[8px] font-mono text-[#4a5568]">
            {(() => {
              const tv = msg.backendPayload.true_voice_snapshot as Record<string, unknown> | undefined
              const voiceSrc = tv?.final_answer_source as string || tv?.voice_source as string
              return voiceSrc ? <span className="text-obs-brody">voice_src:{voiceSrc}</span> : null
            })()}
            {msg.backendPayload.graphiti_status ? (
              <span className={String(msg.backendPayload.graphiti_status).includes('LIVE') ? 'text-obs-pass' : 'text-obs-hold'}>
                graphiti:{String(msg.backendPayload.graphiti_status).slice(-16)}
              </span>
            ) : null}
            {msg.backendPayload.neo4j_status ? (
              <span className={String(msg.backendPayload.neo4j_status) === 'ONLINE' ? 'text-obs-pass' : ''}>
                neo4j:{String(msg.backendPayload.neo4j_status)}
              </span>
            ) : null}
            {msg.backendPayload.action_risk ? <span className="text-obs-block">ACTION_RISK</span> : null}
          </div>
        )}

        <BrodyTerminalView payload={msg.backendPayload as Record<string, unknown> | undefined} />
      </div>
    </div>
  )
}

export function ChatView({ messages, traces, onSend, sessionLanguage }: Props) {
  const [input, setInput] = useState('')
  const [showTraces, setShowTraces] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)
  const backendMode = config.USE_MOCK ? 'MOCK' : 'LIVE'

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  const handleSend = () => {
    const t = input.trim()
    if (!t) return
    onSend(t)
    setInput('')
  }

  return (
    <div className="flex-1 flex flex-col min-w-0 bg-obs-bg">
      <div className="h-10 bg-obs-surface border-b border-obs-border flex items-center px-4 gap-3 shrink-0">
        <span className="text-obs-brody font-mono text-xs font-semibold">Brody</span>
        <div className="h-3 w-px bg-obs-border" />
        <span className="obs-badge-brody">ADVISORY ONLY</span>
        <span className="obs-badge-muted">context_signal_only=true</span>
        <span className="text-obs-dtext text-[9px] font-mono">LANG: <span className="text-obs-memory font-semibold">{sessionLanguage.toUpperCase()}</span></span>
        <span className="text-obs-dtext text-[9px] font-mono">BACKEND: <span className={backendMode === 'LIVE' ? 'text-obs-pass' : 'text-obs-hold'}>{backendMode}</span></span>
        <div className="ml-auto flex items-center gap-2">
          <button onClick={() => setShowTraces(v => !v)} className="flex items-center gap-1 text-[9px] font-mono text-obs-dtext hover:text-obs-proof transition-colors px-1.5 py-0.5 rounded border border-obs-border/40 hover:border-obs-proof/30">
            {showTraces ? <ChevronDown size={9} /> : <ChevronRight size={9} />} OS TRAD trace
          </button>
          <Lock size={10} className="text-obs-dtext" />
          <span className="text-obs-dtext text-[10px] font-mono">no real action</span>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-6 py-4">
        {messages.map(m => <MessageBubble key={m.id} msg={m} trace={traces[m.id]} showTrace={showTraces} />)}
        <div ref={bottomRef} />
      </div>

      <div className="px-6 py-1.5 flex items-center gap-2 border-t border-obs-border/40">
        <AlertCircle size={10} className="text-obs-dtext shrink-0" />
        <span className="text-obs-dtext text-[10px] font-mono">Brody est advisory uniquement. X-108 decide.</span>
      </div>

      <div className="px-4 py-3 bg-obs-surface border-t border-obs-border">
        <div className="flex gap-2 items-end">
          <div className="flex-1 bg-obs-card border border-obs-border rounded-xl overflow-hidden focus-within:border-obs-brody/50 transition-colors">
            <textarea value={input} onChange={e => setInput(e.target.value)}
              onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend() } }}
              rows={2} placeholder="Interroger Brody (reponse consultative uniquement)..."
              className="w-full bg-transparent text-obs-text text-sm font-mono px-4 py-2.5 resize-none outline-none placeholder:text-obs-dtext"
            />
          </div>
          <button onClick={handleSend} disabled={!input.trim()}
            className="flex items-center gap-1.5 px-4 py-2.5 rounded-xl bg-obs-brody/20 border border-obs-brody/30 text-obs-brody text-xs font-mono font-semibold hover:bg-obs-brody/30 disabled:opacity-30 disabled:cursor-not-allowed transition-colors">
            <Send size={12} /> SUBMIT
          </button>
        </div>
      </div>
    </div>
  )
}
